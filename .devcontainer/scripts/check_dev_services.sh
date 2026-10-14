#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/dev_services_env.sh"

rc=0
check_pid "Postgres" "${PID_DIR}/postgres.pid" || rc=1
check_pid "Redis" "${PID_DIR}/redis.pid" || rc=1
check_pid "Prometheus" "${SERVICES_DIR}/prometheus/prometheus.pid" || rc=1

if command -v ss >/dev/null 2>&1; then
  ss -lntp | grep -E ':5432|:6379|:9090' || true
fi
exit "${rc}"
