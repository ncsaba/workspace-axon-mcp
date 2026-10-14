#!/usr/bin/env bash
set -uo pipefail
# NOTE: no `set -e` here on purpose. A single failing step must never abort
# the rest of container setup -- see run_step() in lib_step_runner.sh.
#
# Usage: init_all.sh [--bootstrap]
#   --bootstrap  also (re)install the Python venv and UI npm dependencies;
#                passed from postCreateCommand only, so container starts stay fast.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/lib_step_runner.sh"

WITH_BOOTSTRAP=false
[[ "${1:-}" == "--bootstrap" ]] && WITH_BOOTSTRAP=true

step_set_timezone() {
  sudo ln -snf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
  printf 'Europe/Berlin\n' | sudo tee /etc/timezone >/dev/null
}

step_sync_claude_json() {
  # ~/.claude.json is mounted at .claude.json.host (not the live path) because Claude Code
  # saves config via rename(), which gets EBUSY if the live path is itself a bind-mount target.
  local host_json="/home/vscode/.claude.json.host"
  local live_json="/home/vscode/.claude.json"
  if [[ -f "${host_json}" ]]; then
    if [[ ! -f "${live_json}" ]] || [[ "${host_json}" -nt "${live_json}" ]]; then
      cp "${host_json}" "${live_json}"
    elif [[ "${live_json}" -nt "${host_json}" ]]; then
      cp "${live_json}" "${host_json}"
    fi
  fi
}

step_link_bash_history() {
  # The services volume starts empty; seed it once from the host-side copy
  # (visible through the workspace mount) so earlier history is kept.
  local target="/home/vscode/services/bash_history"
  local seed="/workspaces/axon-mcp/.devcontainer/services/bash_history"
  local dest="/home/vscode/.bash_history"
  install -d -m 0755 "$(dirname "${target}")"
  if [[ ! -e "${target}" ]]; then
    if [[ -f "${seed}" ]]; then
      cp "${seed}" "${target}"
    else
      touch "${target}"
    fi
  fi
  if [[ ! -L "${dest}" ]]; then
    ln -sf "${target}" "${dest}"
  fi
}

step_bootstrap() {
  bash "${SCRIPT_DIR}/bootstrap.sh"
}

step_init_postgres() {
  bash "${SCRIPT_DIR}/init_postgres.sh"
}

step_init_redis() {
  bash "${SCRIPT_DIR}/init_redis.sh"
}

step_init_prometheus() {
  bash "${SCRIPT_DIR}/init_prometheus.sh"
}

init_warnings_reset
run_step "install shell startup warnings banner"   init_warnings_install_shell_banner

run_step "set container timezone"                 step_set_timezone
run_step "sync ~/.claude.json with host copy"      step_sync_claude_json
run_step "link ~/.bash_history to persisted services copy" step_link_bash_history
if [[ "${WITH_BOOTSTRAP}" == "true" ]]; then
  run_step "bootstrap Python venv and UI dependencies" step_bootstrap
fi
run_step "init PostgreSQL"                         step_init_postgres
run_step "init Redis"                              step_init_redis
run_step "init Prometheus"                         step_init_prometheus

init_warnings_summary
exit 0
