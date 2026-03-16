#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/init_postgres.sh"

SERVICES_DIR="/home/vscode/services"
PGDATA_DEFAULT="${SERVICES_DIR}/postgres/17/main"
PGDATA="${PGDATA:-$PGDATA_DEFAULT}"
PGSOCKET_DIR="${PGSOCKET_DIR:-/tmp/pgsocket}"
DB_PORT="${PGPORT:-5432}"

PID_DIR="${POSTGRES_PID_DIR:-/home/vscode/pid}"
LOG_DIR="${POSTGRES_LOG_DIR:-/home/vscode/services/log}"
install -d -m 0755 "${PID_DIR}" "${LOG_DIR}" "${SERVICES_DIR}"

PG_PID_FILE="${PID_DIR}/postgres.pid"
if [[ -f "${PG_PID_FILE}" ]] && kill -0 "$(cat "${PG_PID_FILE}")" 2>/dev/null; then
  echo "Postgres already running (pid=$(cat "${PG_PID_FILE}"))"
else
  /usr/lib/postgresql/17/bin/pg_ctl -D "${PGDATA}" -o "-p ${DB_PORT} -h 0.0.0.0 -k ${PGSOCKET_DIR}" -l "${LOG_DIR}/postgres.log" start
  echo "$(head -n1 "${PGDATA}/postmaster.pid")" > "${PG_PID_FILE}"
fi

echo "PostgreSQL started (port=${DB_PORT})."

