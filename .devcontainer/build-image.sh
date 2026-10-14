#!/usr/bin/env bash
# Template: builds a devcontainer image from a staged, minimal build context.
# Copy into <project>/.devcontainer/build-image.sh and customize the
# variables below. Do not run a build directly from .devcontainer — that
# folder also holds vscode-server/ (or vscodium-server/) and services/,
# which can grow to multiple gigabytes and get tar'd into the build context
# on every build even though the Dockerfile never COPYs them.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_TAG="localhost/devcontainer/axon-mcp:latest"
# Convenience alias for manually typing `docker run devcontainer/axon-mcp:latest`.
BARE_ALIAS="devcontainer/axon-mcp:latest"

# Paths relative to $SCRIPT_DIR that the Dockerfile's COPY instructions
# actually need. List individual files, not whole directories with
# unrelated large content mixed in.
BUILD_INPUTS=(
  "Dockerfile"
  "assets/node-v24.13.0-linux-amd64.tar.gz"
  "assets/node-v24.13.0-linux-arm64.tar.gz"
)

# This workspace wires `docker` to the right container engine already
# (see docs/patterns for the current setup) — no per-script engine
# detection needed. Just make sure it's actually on PATH.
if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found on PATH — this workspace expects docker to be wired to the right container engine." >&2
  exit 1
fi

# Stage under ~/tmp/container-build, not the system TMPDIR (/var/folders/...
# on macOS). Confirmed empirically: the underlying build backend cannot
# read local build-context files from macOS's per-user TMPDIR — every COPY
# fails with a "not found" checksum error even though the files are
# verifiably present — but the same staged directory builds fine from
# under $HOME.
STAGE_ROOT="$HOME/tmp/container-build"
mkdir -p "$STAGE_ROOT"
STAGE_DIR="$(mktemp -d "$STAGE_ROOT/devcontainer-build.XXXXXX")"
cleanup() {
  rm -rf "$STAGE_DIR"
}
trap cleanup EXIT

for input in "${BUILD_INPUTS[@]}"; do
  src="$SCRIPT_DIR/$input"
  dest="$STAGE_DIR/$input"
  mkdir -p "$(dirname "$dest")"
  cp -R "$src" "$dest"
done

echo "Building $IMAGE_TAG from staged context $STAGE_DIR"
docker build -t "$IMAGE_TAG" -f "$STAGE_DIR/Dockerfile" "$STAGE_DIR"

# Also tag a bare alias for convenience (`docker run devcontainer/axon-mcp:latest`).
# devcontainer.json must reference the "localhost/" tag above, not this alias:
# the underlying engine behind the docker wrapper may match image references
# by exact literal string rather than normalizing "localhost/<name>" the way
# Docker proper does; if the image were only ever tagged bare, a rewritten
# "localhost/<name>" lookup would miss and fall through to a registry pull
# attempt instead. Keeping both tags avoids that.
docker tag "$IMAGE_TAG" "$BARE_ALIAS"

echo "Built $IMAGE_TAG (alias: $BARE_ALIAS)"
