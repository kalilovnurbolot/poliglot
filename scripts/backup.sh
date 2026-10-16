#!/bin/sh
# Database backups, run inside the `backup` service (docker-compose*.yml).
#   sh /backup.sh        - a backup now, then every day at BACKUP_HOUR (UTC)
#   sh /backup.sh once   - a single backup, e.g. before a risky change
# Files: /backups/poliglot-YYYY-MM-DD_HHMM.sql.gz, older than BACKUP_KEEP_DAYS are removed.
# Connection comes from the PG* environment variables of the service.
set -eu
set -o pipefail

KEEP_DAYS=${BACKUP_KEEP_DAYS:-14}
HOUR=${BACKUP_HOUR:-3}

backup() {
  file="/backups/poliglot-$(date -u +%Y-%m-%d_%H%M).sql.gz"
  # Write to a temporary name first, so a failed dump never looks like a good backup.
  if pg_dump --no-owner | gzip > "$file.part"; then
    mv "$file.part" "$file"
    echo "backup: $file ($(du -h "$file" | cut -f1))"
  else
    rm -f "$file.part"
    echo "backup FAILED at $(date -u)" >&2
    return 1
  fi
  find /backups -name 'poliglot-*.sql.gz' -mtime +"$KEEP_DAYS" -exec rm -f {} + -exec echo "removed old backups" \;
}

if [ "${1:-}" = once ]; then
  backup
  exit
fi

while true; do
  backup || true
  # Sleep until the next BACKUP_HOUR:00 UTC (strip leading zeros: 08 is not octal).
  now=$(( $(date -u +%H | sed 's/^0//') * 3600 + $(date -u +%M | sed 's/^0//') * 60 ))
  wait=$(( (HOUR * 3600 - now + 86400) % 86400 ))
  [ "$wait" -gt 600 ] || wait=$(( wait + 86400 ))
  sleep "$wait"
done
