#!/usr/bin/env bash
set -euo pipefail

# Expects init_redis.sh to have run (init_all.sh does this before start_dev_services.sh starts services).

REDIS_HOME="${REDIS_HOME:-${HOME:-/home/vscode}}"
REDIS_SERVICES_DIR="${REDIS_SERVICES_DIR:-${REDIS_HOME}/services}"
REDIS_DIR="${REDIS_SERVICES_DIR}/redis"
REDIS_CONF="${REDIS_DIR}/redis.conf"
REDIS_PID_DIR="${REDIS_PID_DIR:-${REDIS_HOME}/pid}"
REDIS_PID_FILE="${REDIS_PID_DIR}/redis.pid"
REDIS_PORT="${REDIS_PORT:-6379}"

if [[ -f "${REDIS_PID_FILE}" ]] && kill -0 "$(cat "${REDIS_PID_FILE}")" 2>/dev/null; then
  echo "Redis already running (pid=$(cat "${REDIS_PID_FILE}"))"
else
  redis-server "${REDIS_CONF}"
fi

echo "Redis started (port=${REDIS_PORT})."

