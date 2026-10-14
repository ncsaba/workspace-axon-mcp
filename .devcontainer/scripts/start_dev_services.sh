#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/dev_services_env.sh"
install -d -m 0755 "${PID_DIR}" "${LOG_DIR}" "${SERVICES_DIR}"

"${SCRIPT_DIR}/init_all.sh"

start_service() {
  local script="$1"
  "${script}" || echo "Warning: ${script##*/} failed (non-critical); check ${LOG_DIR}/" >&2
}

start_service "${SCRIPT_DIR}/start_postgres.sh"
start_service "${SCRIPT_DIR}/start_redis.sh"
start_service "${SCRIPT_DIR}/start_prometheus.sh"

echo "Dev services started."
