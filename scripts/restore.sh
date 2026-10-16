#!/bin/sh
# Restore the database from a backup without deleting anything:
#   scripts/restore.sh backups/poliglot-2026-10-16_0300.sql.gz
# The current database is kept as poliglot_before_<date>; to go back, rename it again.
# With docker-compose.prod.yml: COMPOSE="docker compose -f docker-compose.prod.yml" scripts/restore.sh FILE
set -eu

FILE=${1:?usage: scripts/restore.sh BACKUP_FILE (.sql or .sql.gz)}
COMPOSE=${COMPOSE:-docker compose}
KEPT="poliglot_before_$(date +%Y%m%d_%H%M%S)"
psql() { $COMPOSE exec -T db psql -U poliglot -v ON_ERROR_STOP=1 -q "$@"; }

case "$FILE" in
  *.gz) READ="gunzip -c" ;;
  *) READ="cat" ;;
esac

echo "1/4 loading $FILE into a new database poliglot_restore..."
psql -d postgres -c "DROP DATABASE IF EXISTS poliglot_restore;" -c "CREATE DATABASE poliglot_restore OWNER poliglot;"
# tr: dumps taken through a terminal (exec without -T) have Windows line endings.
$READ "$FILE" | tr -d '\r' | psql -d poliglot_restore > /dev/null

echo "2/4 stopping the site..."
$COMPOSE stop backend

echo "3/4 switching databases (current one is kept as $KEPT)..."
psql -d postgres \
  -c "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity WHERE datname = 'poliglot' AND pid <> pg_backend_pid();" \
  -c "ALTER DATABASE poliglot RENAME TO $KEPT;" \
  -c "ALTER DATABASE poliglot_restore RENAME TO poliglot;"

echo "4/4 starting the site (migrations run on start)..."
$COMPOSE up -d backend
echo "done. Previous database: $KEPT"
echo "drop it when no longer needed: $COMPOSE exec db psql -U poliglot -d postgres -c 'DROP DATABASE $KEPT;'"
