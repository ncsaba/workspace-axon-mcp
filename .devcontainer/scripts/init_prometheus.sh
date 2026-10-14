#!/bin/bash
# Initialize Prometheus for dev-container

set -e

PROMETHEUS_DATA_DIR="${HOME}/services/prometheus"
PROMETHEUS_CONFIG_DIR="/workspaces/axon-mcp/.devcontainer/prometheus"
PROMETHEUS_MULTIPROC_DIR="${HOME}/services/prometheus/multiproc"

echo "Initializing Prometheus..."

# Create data directory
mkdir -p "${PROMETHEUS_DATA_DIR}"
mkdir -p "${PROMETHEUS_MULTIPROC_DIR}"
mkdir -p "${HOME}/services/log"

# Config is git-tracked, not generated
if [ ! -f "${PROMETHEUS_CONFIG_DIR}/prometheus.yml" ]; then
    echo "Missing ${PROMETHEUS_CONFIG_DIR}/prometheus.yml" >&2
    exit 1
fi

echo "Prometheus initialized."
echo "PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR}"
