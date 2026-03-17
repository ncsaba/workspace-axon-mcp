#!/bin/bash
# Start Prometheus server for dev-container

set -e

PROMETHEUS_DATA_DIR="${HOME}/services/prometheus"
PROMETHEUS_CONFIG_DIR="/workspaces/axon-mcp/.devcontainer/services/prometheus"
PROMETHEUS_LOG="${HOME}/services/log/prometheus.log"
PROMETHEUS_PID="${HOME}/services/prometheus/prometheus.pid"

# Check if Prometheus is already running
if [ -f "${PROMETHEUS_PID}" ]; then
    PID=$(cat "${PROMETHEUS_PID}")
    if kill -0 "${PID}" 2>/dev/null; then
        echo "Prometheus already running (PID: ${PID})"
        exit 0
    else
        rm -f "${PROMETHEUS_PID}"
    fi
fi

echo "Starting Prometheus..."

# Create data directory if needed
mkdir -p "${PROMETHEUS_DATA_DIR}"

# Start Prometheus in background
prometheus \
    --config.file="${PROMETHEUS_CONFIG_DIR}/prometheus.yml" \
    --storage.tsdb.path="${PROMETHEUS_DATA_DIR}/tsdb" \
    --web.listen-address="0.0.0.0:9090" \
    --web.console.templates=/usr/share/prometheus/consoles \
    --web.console.libraries=/usr/share/prometheus/console_libraries \
    --log.level=info \
    > "${PROMETHEUS_LOG}" 2>&1 &

PROM_PID=$!
echo ${PROM_PID} > "${PROMETHEUS_PID}"

# Wait briefly and verify
sleep 2
if kill -0 ${PROM_PID} 2>/dev/null; then
    echo "Prometheus started (PID: ${PROM_PID})"
    echo "Dashboard: http://localhost:9090"
else
    echo "Failed to start Prometheus. Check ${PROMETHEUS_LOG} for details."
    exit 1
fi
