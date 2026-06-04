#!/usr/bin/env bash
set -euo pipefail

output_directory="${OUTPUT_DIRECTORY:-artifacts/backups}"
database="${DB_NAME:-ordostack}"
user="${DB_USER:-root}"
password="${DB_PASSWORD:-}"
compose_service="${COMPOSE_SERVICE:-mysql}"

mkdir -p "${output_directory}"
timestamp="$(date +%Y%m%d-%H%M%S)"
backup_path="${output_directory}/ordostack-${timestamp}.sql"

docker_arguments=(
  compose
  exec
  -T
)

if [[ -n "${password}" ]]; then
  docker_arguments+=(-e "MYSQL_PWD=${password}")
fi

docker_arguments+=(
  "${compose_service}"
  mysqldump
  --single-transaction
  --routines
  --events
  --skip-add-drop-table
  --skip-comments
  --no-tablespaces
  -u
  "${user}"
  "${database}"
)

docker "${docker_arguments[@]}" > "${backup_path}"

if [[ ! -s "${backup_path}" ]]; then
  echo "Backup file is empty: ${backup_path}" >&2
  exit 1
fi

printf '{"status":"ok","database":"%s","path":"%s","bytes":%s}\n' \
  "${database}" \
  "${backup_path}" \
  "$(wc -c < "${backup_path}")"
