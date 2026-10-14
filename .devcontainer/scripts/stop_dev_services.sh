#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/dev_services_env.sh"

PGDATA_DEFAULT="${SERVICES_DIR}/postgres/17/main"
PGDATA="${PGDATA:-$PGDATA_DEFAULT}"
PGSOCKET_DIR="${PGSOCKET_DIR:-/tmp/pgsocket}"

PG_PID_FILE="${PID_DIR}/postgres.pid"
if [[ -f "${PG_PID_FILE}" ]]; then
  PG_PID="$(cat "${PG_PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${PG_PID}" ]] && kill -0 "${PG_PID}" 2>/dev/null; then
    /usr/lib/postgresql/17/bin/pg_ctl -D "${PGDATA}" -o "-k ${PGSOCKET_DIR}" -l "${LOG_DIR}/postgres.log" -m fast -w stop || true
  fi
fi
rm -f "${PG_PID_FILE}"

stop_pid "Redis" "${PID_DIR}/redis.pid"
stop_pid "Prometheus" "${SERVICES_DIR}/prometheus/prometheus.pid"
echo "Dev services stopped."
