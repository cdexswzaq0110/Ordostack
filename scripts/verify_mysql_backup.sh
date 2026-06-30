#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/verify_mysql_backup.sh <backup.sql>" >&2
  exit 2
fi

backup_path="$1"

if [[ ! -s "${backup_path}" ]]; then
  echo "Backup file is empty or missing: ${backup_path}" >&2
  exit 1
fi

if ! grep -q "CREATE TABLE" "${backup_path}"; then
  echo "Backup does not contain schema definitions." >&2
  exit 1
fi

if grep -Eq "DROP DATABASE|DROP TABLE|TRUNCATE TABLE" "${backup_path}"; then
  echo "Backup contains forbidden destructive statements." >&2
  exit 1
fi

printf '{"status":"ok","path":"%s","bytes":%s,"contains_schema":true,"destructive_statements":"none"}\n' \
  "${backup_path}" \
  "$(wc -c < "${backup_path}")"
