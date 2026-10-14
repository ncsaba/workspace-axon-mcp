#!/usr/bin/env bash
# Shared variables and helper functions. Source this file; do not execute it directly.

PID_DIR="/home/vscode/pid"
LOG_DIR="/home/vscode/services/log"
SERVICES_DIR="/home/vscode/services"

stop_pid() {
  local name="$1"
  local pid_file="$2"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "Stopping ${name} (pid=${pid})"
      kill "${pid}" 2>/dev/null || true
      for _ in {1..10}; do
        if kill -0 "${pid}" 2>/dev/null; then
          sleep 1
        else
          break
        fi
      done
      if kill -0 "${pid}" 2>/dev/null; then
        echo "${name} did not stop; sending SIGKILL"
        kill -9 "${pid}" 2>/dev/null || true
      fi
    fi
    rm -f "${pid_file}"
  fi
}

check_pid() {
  local name="$1"
  local pid_file="$2"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "OK:   ${name} (pid=${pid})"
      return 0
    fi
  fi
  echo "FAIL: ${name} not running"
  return 1
}
