#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="/home/vscode/.venv-dev"
SRC_DIR="/workspaces/axon-mcp/axon-src"

python3 -m venv "${VENV_DIR}" 2>/dev/null || true
"${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel

if [[ -d "${SRC_DIR}" ]]; then
  "${VENV_DIR}/bin/pip" install -r "${SRC_DIR}/requirements.txt" -r "${SRC_DIR}/requirements-dev.txt"

  if [[ -f "${SRC_DIR}/ui/package.json" ]]; then
    cd "${SRC_DIR}/ui"
    if command -v npm >/dev/null 2>&1; then
      npm install
    else
      echo "npm is not available in container; skipping UI dependency install." >&2
    fi
  fi
fi
