"""Database versions for the admin panel (owners only, admin_views.database).

The backups themselves are made and restored by the `backup` service
(scripts/backup.sh) in the shared BACKUP_DIR: the site only lists them, serves
downloads and queues jobs there, since it has no rights over other containers.
"""

import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.db import connection

NAME_RE = re.compile(r'^poliglot-(\d{4}-\d{2}-\d{2})_(\d{4})(\d{2})?(?:-([a-z-]+))?\.sql\.gz$')
KINDS = {
    'auto': 'Автоматический', 'manual': 'Ручной', 'before-restore': 'Перед восстановлением', 'uploaded': 'Загруженный',
}
MAX_UPLOAD_BYTES = 500 * 1024 * 1024  # uncompressed dump
DUMP_HEADER = [b'--\n', b'-- PostgreSQL database dump']  # first two lines of a pg_dump file
RESTORE_DATABASE = 'poliglot_restore'  # scripts/backup.sh loads versions there first


class UploadError(Exception):
    pass


def backup_dir():
    """The shared folder, or None when backups aren't set up for this site."""
    path = Path(settings.BACKUP_DIR) if settings.BACKUP_DIR else None
    return path if path and path.is_dir() else None


def fingerprint(migrations):
    """md5 of "app.name" in byte order: the same as fingerprint() in scripts/backup.sh."""
    return hashlib.md5(','.join(f'{app}.{name}' for app, name in sorted(migrations)).encode()).hexdigest()


def current_fingerprint():
    with connection.cursor() as cursor:
        cursor.execute('SELECT app, name FROM django_migrations')
        return fingerprint(cursor.fetchall())


def list_backups():
    folder = backup_dir()
    if folder is None:
        return []
    fingerprint = current_fingerprint()
    backups = []
    for path in folder.iterdir():
        match = NAME_RE.match(path.name)
        if not match:
            continue
        day, hhmm, seconds, kind = match.groups()
        meta = path.with_name(path.name + '.meta')
        saved = meta.read_text().strip() if meta.exists() else None
        backups.append({
            'name': path.name,
            'created': datetime.strptime(f'{day} {hhmm}{seconds or "00"}', '%Y-%m-%d %H%M%S').replace(tzinfo=UTC),
            'size': path.stat().st_size,
            'kind': KINDS.get(kind or 'auto', kind),
            # None: made before fingerprints existed, the service checks it on restore.
            'same_version': None if saved is None else saved == fingerprint,
        })
    return sorted(backups, key=lambda b: b['created'], reverse=True)


def backup_path(name):
    """Path of an existing backup by its file name, or None (no other files are served)."""
    folder = backup_dir()
    if folder is None or not NAME_RE.match(name):
        return None
    path = folder / name
    return path if path.is_file() else None


def queue_job(job):
    """`backup` or `restore <file>`; the service picks it up within a few seconds."""
    queue = backup_dir() / '.queue'
    queue.mkdir(exist_ok=True)
    name = f'{time.time_ns()}.job'
    (queue / f'{name}.part').write_text(job)
    (queue / f'{name}.part').rename(queue / name)  # appears complete or not at all


def pending_jobs():
    """[(job, seconds waiting)] not yet picked up by the service."""
    folder = backup_dir()
    if folder is None:
        return []
    jobs = []
    for path in sorted((folder / '.queue').glob('*.job')):
        try:
            jobs.append((path.read_text(), time.time() - int(path.stem) / 1e9))
        except (OSError, ValueError):
            continue  # just taken by the service
    return jobs


def service_status():
    folder = backup_dir()
    try:
        return json.loads((folder / '.status.json').read_text())
    except (TypeError, OSError, ValueError):
        return None


def history(limit=30):
    folder = backup_dir()
    try:
        lines = (folder / 'history.log').read_text().splitlines()
    except (TypeError, OSError):
        return []
    entries = []
    for line in reversed(lines[-limit:]):
        stamp, _, text = line.partition(' ')
        entries.append({'at': stamp, 'text': text})
    return entries


def save_upload(upload):
    """Store an uploaded dump (.sql or .sql.gz) as a version; returns its file name.

    Line endings are fixed on the way (dumps taken through a terminal have \\r\\n) and the
    schema fingerprint is read from the dump's django_migrations data.
    """
    folder = backup_dir()
    moment = datetime.now(UTC).replace(microsecond=0)
    while True:  # two uploads within a second must not overwrite each other
        name = f'poliglot-{moment:%Y-%m-%d_%H%M%S}-uploaded.sql.gz'
        if not (folder / name).exists() and not (folder / f'{name}.part').exists():
            break
        moment += timedelta(seconds=1)
    part = folder / f'{name}.part'
    source = gzip.GzipFile(fileobj=upload) if upload.name.endswith('.gz') else upload
    migrations, in_migrations, size, number = [], False, 0, 0
    try:
        with gzip.open(part, 'wb') as out:
            for line in source:
                line = line.replace(b'\r', b'')
                if number < len(DUMP_HEADER) and not line.startswith(DUMP_HEADER[number]):
                    raise UploadError('Это не дамп PostgreSQL.')
                number += 1
                size += len(line)
                if size > MAX_UPLOAD_BYTES:
                    raise UploadError('Файл слишком большой.')
                if line.startswith(b'COPY public.django_migrations '):
                    in_migrations = True
                elif in_migrations and line == b'\\.\n':
                    in_migrations = False
                elif in_migrations:
                    _, app, migration, *_ = line.decode().split('\t')
                    migrations.append((app, migration))
                out.write(line)
    except (OSError, EOFError, UnicodeDecodeError, ValueError) as e:
        part.unlink(missing_ok=True)
        raise UploadError('Не удалось прочитать файл: он повреждён или это не дамп.') from e
    except UploadError:
        part.unlink(missing_ok=True)
        raise
    if not migrations:
        part.unlink(missing_ok=True)
        raise UploadError('В дампе нет таблиц сайта: это бэкап другой базы.')
    (folder / f'{name}.meta').write_text(fingerprint(migrations))
    part.rename(folder / name)
    return name


def run_requested_migrations():
    """Migrate poliglot_restore when the backup service asks (a version from an older site).

    Runs in a separate process with that database as the default one, so that data
    migrations, which use the default database, change it and not the live one.
    """
    folder = backup_dir()
    if folder is None or not (folder / '.migrate-request').exists():
        return
    try:
        lock = os.open(folder / '.migrate-running', os.O_CREAT | os.O_EXCL)  # one at a time
    except FileExistsError:
        return
    try:
        url = urlsplit(os.environ['DATABASE_URL'])
        env = {**os.environ, 'DATABASE_URL': urlunsplit(url._replace(path=f'/{RESTORE_DATABASE}'))}
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--noinput'],
            cwd=settings.BASE_DIR, env=env, capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0:
            (folder / '.migrate-done').write_text('ok')
        else:
            (folder / '.migrate-failed').write_text(result.stderr.strip().splitlines()[-1][:300])
    except (KeyError, OSError, subprocess.TimeoutExpired, IndexError) as e:
        (folder / '.migrate-failed').write_text(type(e).__name__)
    finally:
        os.close(lock)
        (folder / '.migrate-running').unlink(missing_ok=True)
