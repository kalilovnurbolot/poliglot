#!/bin/sh
# Database versions, run inside the `backup` service (docker-compose*.yml).
#   sh /backup.sh        - a backup now and every day at BACKUP_HOUR (UTC); also runs
#                          jobs the admin panel queues (apps/web/backups.py)
#   sh /backup.sh once   - a single backup, e.g. before a risky change
#
# Files in /backups:
#   poliglot-YYYY-MM-DD_HHMMSS-<kind>.sql.gz   kind: auto, manual, before-restore, uploaded
#   <backup>.meta          schema fingerprint (migrations applied) of that backup
#   .queue/*.job           jobs from the admin panel: "backup" or "restore <file>"
#   .status.json           what the service is doing / last job result
#   history.log            one line per finished job
#   .migrate-request/-done/-failed  handoff with the site when a restored version needs
#                          migrations (see restore below)
# Backups older than BACKUP_KEEP_DAYS are removed, except uploaded ones.
# Connection: PG* environment variables.
set -eu
set -o pipefail

DIR=/backups
KEEP_DAYS=${BACKUP_KEEP_DAYS:-14}
HOUR=${BACKUP_HOUR:-3}
KEEP_OLD_DATABASES=2  # databases left behind by restores (poliglot_before_*)

q() { psql -v ON_ERROR_STOP=1 -qtA "$@"; }

# Same fingerprint as apps/web/backups.py: md5 of the applied migrations, byte order
# (COLLATE "C") so that Python computes the same one for an uploaded dump.
fingerprint() {
  q -d "$1" -c "SELECT md5(string_agg(app || '.' || name, ',' ORDER BY app COLLATE \"C\", name COLLATE \"C\")) FROM django_migrations"
}

log() {
  echo "$*"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$DIR/history.log"
}

status() {  # state job message (no double quotes in arguments)
  printf '{"state": "%s", "job": "%s", "message": "%s", "updated": "%s"}\n' \
    "$1" "$2" "$3" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$DIR/.status.json.part"
  mv "$DIR/.status.json.part" "$DIR/.status.json"
}

backup() {  # kind
  file="$DIR/poliglot-$(date -u +%Y-%m-%d_%H%M%S)-$1.sql.gz"
  # Write to a temporary name first, so a failed dump never looks like a good backup.
  if pg_dump --no-owner -d poliglot | gzip > "$file.part"; then
    mv "$file.part" "$file"
    fingerprint poliglot > "$file.meta" || rm -f "$file.meta"
    log "бэкап $(basename "$file") ($(du -h "$file" | cut -f1))"
  else
    rm -f "$file.part"
    log "ОШИБКА: бэкап не удался"
    return 1
  fi
  find "$DIR" -maxdepth 1 -name 'poliglot-*.sql.gz' ! -name '*-uploaded.sql.gz' -mtime +"$KEEP_DAYS" | while read -r old; do
    rm -f "$old" "$old.meta"
    log "удалён старый бэкап $(basename "$old")"
  done
}

restore() {  # file name inside /backups
  name=$1
  case "$name" in
    poliglot-*.sql.gz) ;;
    *) log "ОШИБКА восстановления: неверное имя файла"; return 1 ;;
  esac
  case "$name" in */*) log "ОШИБКА восстановления: неверное имя файла"; return 1 ;; esac
  [ -f "$DIR/$name" ] || { log "ОШИБКА восстановления: нет файла $name"; return 1; }

  # Functions called from `if` don't stop on errors (set -e is off there): check each step.
  status running "restore $name" "Сохраняем текущую версию"
  backup before-restore || { log "ОШИБКА восстановления: не удалось сохранить текущую базу"; return 1; }

  status running "restore $name" "Загружаем $name"
  q -d postgres -c "DROP DATABASE IF EXISTS poliglot_restore" -c "CREATE DATABASE poliglot_restore" ||
    { log "ОШИБКА восстановления: не удалось создать базу"; return 1; }
  if ! gunzip -c "$DIR/$name" | tr -d '\r' | q -d poliglot_restore > /dev/null; then
    q -d postgres -c "DROP DATABASE IF EXISTS poliglot_restore"
    log "ОШИБКА восстановления: не удалось загрузить $name"
    return 1
  fi

  # The running site expects the current schema. A version made by an older site needs
  # its migrations, which only Django can run: the site does it on poliglot_restore while
  # the «База данных» page is open (apps/web/backups.py, run_requested_migrations).
  if [ "$(fingerprint poliglot_restore)" != "$(fingerprint poliglot)" ]; then
    status running "restore $name" "Обновляем структуру базы до текущей версии сайта, не закрывайте страницу"
    rm -f "$DIR/.migrate-done" "$DIR/.migrate-failed"
    echo "$name" > "$DIR/.migrate-request"
    waited=0
    while [ ! -f "$DIR/.migrate-done" ] && [ ! -f "$DIR/.migrate-failed" ] && [ "$waited" -lt 600 ]; do
      sleep 2
      waited=$(( waited + 2 ))
    done
    rm -f "$DIR/.migrate-request"
    if [ ! -f "$DIR/.migrate-done" ]; then
      reason=$(cat "$DIR/.migrate-failed" 2>/dev/null || echo "сайт не ответил: откройте вкладку «База данных»")
      rm -f "$DIR/.migrate-done" "$DIR/.migrate-failed"
      q -d postgres -c "DROP DATABASE IF EXISTS poliglot_restore"
      log "ОШИБКА восстановления: не удалось обновить структуру базы ($reason)"
      return 1
    fi
    rm -f "$DIR/.migrate-done"
    # Still different: the version is newer than this site.
    if [ "$(fingerprint poliglot_restore)" != "$(fingerprint poliglot)" ]; then
      q -d postgres -c "DROP DATABASE IF EXISTS poliglot_restore"
      log "ОТКАЗ: $name сделан более новой версией сайта, сначала обновите сайт"
      return 2
    fi
    log "структура $name обновлена до текущей версии сайта"
  fi

  status running "restore $name" "Переключаем базу"
  kept="poliglot_before_$(date -u +%Y%m%d_%H%M%S)"
  # No new connections while renaming; the site reconnects to the restored database.
  q -d postgres \
    -c "ALTER DATABASE poliglot WITH ALLOW_CONNECTIONS false" \
    -c "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity WHERE datname = 'poliglot'" \
    -c "ALTER DATABASE poliglot RENAME TO $kept" \
    -c "ALTER DATABASE poliglot_restore RENAME TO poliglot" > /dev/null ||
    { q -d postgres -c "ALTER DATABASE poliglot WITH ALLOW_CONNECTIONS true" > /dev/null 2>&1; log "ОШИБКА восстановления: не удалось переключить базу"; return 1; }
  log "восстановлено из $name (прежняя база сохранена как $kept)"

  q -d postgres -c "SELECT datname FROM pg_database WHERE datname LIKE 'poliglot_before_%' ORDER BY datname DESC OFFSET $KEEP_OLD_DATABASES" |
    while read -r old; do
      q -d postgres -c "DROP DATABASE \"$old\"" && log "удалена старая база $old"
    done
}

run_job() {  # job file
  job=$(cat "$1")
  rm -f "$1"
  case "$job" in
    backup)
      status running backup "Делаем бэкап"
      if backup manual; then status idle backup "Бэкап готов"; else status failed backup "Бэкап не удался"; fi
      ;;
    "restore "*)
      name=${job#restore }
      if restore "$name"; then
        status idle "restore $name" "Восстановлено из $name"
      elif [ $? -eq 2 ]; then
        status failed "restore $name" "Бэкап сделан более новой версией сайта: сначала обновите сайт"
      else
        status failed "restore $name" "Не удалось восстановить $name"
      fi
      ;;
    *) log "неизвестная задача: $job" ;;
  esac
}

if [ "${1:-}" = once ]; then
  backup manual
  exit
fi

mkdir -p "$DIR/.queue"
backup auto || true
status idle "" "Готов"

# Seconds since midnight UTC of the next scheduled backup (strip zeros: 08 is not octal).
next_run() {
  now=$(( $(date -u +%H | sed 's/^0//') * 3600 + $(date -u +%M | sed 's/^0//') * 60 ))
  wait=$(( (HOUR * 3600 - now + 86400) % 86400 ))
  [ "$wait" -gt 600 ] || wait=$(( wait + 86400 ))
  echo $(( $(date -u +%s) + wait ))
}
due=$(next_run)

while true; do
  for job in $(ls "$DIR/.queue/"*.job 2>/dev/null | sort); do
    run_job "$job" || true
  done
  if [ "$(date -u +%s)" -ge "$due" ]; then
    backup auto || true
    due=$(next_run)
  fi
  sleep 3
done
