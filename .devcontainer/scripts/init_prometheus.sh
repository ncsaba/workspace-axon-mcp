#!/bin/bash
# Initialize Prometheus for dev-container

set -e

PROMETHEUS_DATA_DIR="${HOME}/services/prometheus"
PROMETHEUS_CONFIG_DIR="/workspaces/axon-mcp/.devcontainer/services/prometheus"
PROMETHEUS_MULTIPROC_DIR="${HOME}/services/prometheus/multiproc"

echo "Initializing Prometheus..."

# Create data directory
mkdir -p "${PROMETHEUS_DATA_DIR}"
mkdir -p "${PROMETHEUS_MULTIPROC_DIR}"
mkdir -p "${HOME}/services/log"

# Create default config if not exists
if [ ! -f "${PROMETHEUS_CONFIG_DIR}/prometheus.yml" ]; then
    mkdir -p "${PROMETHEUS_CONFIG_DIR}"
    cat > "${PROMETHEUS_CONFIG_DIR}/prometheus.yml" << 'EOF'
# Prometheus configuration for Axon MCP dev-container
# Scrape targets for API and workers

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'dev-container'

scrape_configs:
  # API server metrics
  - job_name: 'axon-api'
    static_configs:
      - targets: ['host.docker.internal:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
fi

echo "Prometheus initialized."
echo "PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR}"
