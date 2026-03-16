#!/usr/bin/env bash
set -euo pipefail

if ! command -v redis-server >/dev/null 2>&1; then
  echo "redis-server not found in PATH. Install redis-server in the image first." >&2
  exit 1
fi

REDIS_HOME="${REDIS_HOME:-${HOME:-/home/vscode}}"
REDIS_SERVICES_DIR="${REDIS_SERVICES_DIR:-${REDIS_HOME}/services}"
REDIS_DIR="${REDIS_SERVICES_DIR}/redis"
REDIS_DATA_DIR="${REDIS_DIR}/data"
REDIS_CONF="${REDIS_DIR}/redis.conf"
REDIS_LOG_DIR="${REDIS_LOG_DIR:-${REDIS_SERVICES_DIR}/log}"
REDIS_PID_DIR="${REDIS_PID_DIR:-${REDIS_HOME}/pid}"
REDIS_PID_FILE="${REDIS_PID_DIR}/redis.pid"

REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_BIND_ADDRESS="${REDIS_BIND_ADDRESS:-0.0.0.0}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

install -d -m 0755 "${REDIS_DIR}" "${REDIS_DATA_DIR}" "${REDIS_LOG_DIR}" "${REDIS_PID_DIR}"

{
  echo "bind ${REDIS_BIND_ADDRESS}"
  echo "port ${REDIS_PORT}"
  echo "daemonize yes"
  echo "dir ${REDIS_DATA_DIR}"
  echo "pidfile ${REDIS_PID_FILE}"
  echo "logfile ${REDIS_LOG_DIR}/redis.log"
  echo "appendonly yes"
  echo "protected-mode yes"
  if [[ -n "${REDIS_PASSWORD}" ]]; then
    echo "requirepass ${REDIS_PASSWORD}"
  fi
} > "${REDIS_CONF}"

echo "Redis config initialized at ${REDIS_CONF}."

