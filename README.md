# Axon MCP Workspace Wrapper

This folder contains the Dev Container wrapper for the Axon MCP project.
The source repository is mounted as a sub-folder and is not modified by wrapper setup files.

## Prerequisites

Before setting up this workspace, ensure you have the following installed:

| Requirement | Description | Installation |
|-------------|-------------|--------------|
| **Container Engine** | Apple Container (preferred), Docker or Podman, reachable as `docker` | Apple Container is wired in via the `docker_bridge.py` shim |
| **VSCodium** | Editor | [Download VSCodium](https://vscodium.com/) |
| **Dev Containers Extension** | Editor extension for containers | Install from Open VSX |
| **Python 3.11+** | For running the setup script | [Python Downloads](https://www.python.org/downloads/) |
| **Git** | Version control | [Git Downloads](https://git-scm.com/downloads) |

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd axon-mcp
```

### 2. Run the Setup Script

```bash
python setup_workspace.py
```

The script will guide you through configuration options interactively.

### 3. Open in VSCodium

```bash
codium .
```

When prompted, click **"Reopen in Container"** or run the command:
- **Dev Containers: Reopen in Container** from the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)

## Setup Script Options

The [`setup_workspace.py`](setup_workspace.py) script supports several command-line options:

| Option | Description |
|--------|-------------|
| (default) | Interactive mode with guided prompts |
| `--non-interactive` | Run without prompts, use environment variables or config file |
| `--config <file>` | Path to JSON config file for non-interactive mode |
| `--dry-run` | Show what would be generated without writing files |
| `--skip-build` | Skip building the container image (useful when image already exists) |
| `--force-build` | Force rebuild even if image already exists |

### Examples

```bash
# Interactive mode (default)
python setup_workspace.py

# Non-interactive mode (requires AXON_SRC_PATH env var)
export AXON_SRC_PATH=/path/to/Axon.MCP.Server
python setup_workspace.py --non-interactive

# Use a config file
python setup_workspace.py --config my-config.json

# Preview changes without writing
python setup_workspace.py --dry-run

# Skip container build (image already exists)
python setup_workspace.py --skip-build

# Force rebuild of container image
python setup_workspace.py --force-build
```

### Image Build Behavior

The script automatically checks if the container image `localhost/devcontainer/axon-mcp:latest` already exists:

- **Image exists**: Skips build (use `--force-build` to rebuild)
- **Image missing**: Builds by running [`.devcontainer/build-image.sh`](.devcontainer/build-image.sh)
- **Build script**: stages only the `Dockerfile` and Node tarballs under `~/tmp/container-build` and builds from there,
  then tags `localhost/devcontainer/axon-mcp:latest` plus the bare alias `devcontainer/axon-mcp:latest`.
  The `localhost/` tag is the one `devcontainer.json` references (required by Apple Container's exact-string image lookup).

## Configuration Options

The setup script configures the following options:

### Axon Source Directory (Mandatory)

The path to your local Axon.MCP.Server repository. This directory will be mounted at `/workspaces/axon-mcp/axon-src` inside the container.

### AI Assistant Integration

| Assistant | Description |
|-----------|-------------|
| **Codex** | Optionally mounts the `~/.codex` config folder. |

No editor extensions are preinstalled; install what you need inside the container.

### Extra Mounts

Optional additional bind mounts, e.g. a kilocode checkout mounted read-only at
`/workspaces/axon-mcp/external-inspiration/kilocode`. In config files, list them under `extra_mounts`.

### Config File Format

For non-interactive mode, create a JSON config file (`.workspace-config.json` is gitignored for this purpose):

```json
{
  "axon_src_path": "/path/to/Axon.MCP.Server",
  "ai_config": {
    "codex": {
      "enabled": true,
      "path": "~/.codex"
    }
  },
  "extra_mounts": [
    {
      "source": "/path/to/kilocode",
      "target": "/workspaces/axon-mcp/external-inspiration/kilocode",
      "readonly": true
    }
  ]
}
```

## Container Engine Support

The setup script and `build-image.sh` call `docker` and do no engine detection of their own.
On this workspace's hosts `docker` is wired to Apple Container (via `docker_bridge.py`); a real
Docker or Podman `docker` CLI works too.

## Project Structure

```
axon-mcp/
├── .devcontainer/           # Dev Container configuration
│   ├── Dockerfile           # Container image definition
│   ├── build-image.sh       # Staged image build
│   ├── devcontainer.json    # Container configuration (generated)
│   ├── prometheus/          # Prometheus config (git-tracked)
│   ├── templates/           # Configuration templates
│   └── scripts/             # Lifecycle and service scripts
├── axon-src/                # Mounted Axon source (read-write)
├── external-inspiration/    # Reference code (read-only)
│   └── kilocode/            # Kilocode parser patterns
├── docs/                    # Workspace documentation
├── setup_workspace.py       # Setup script
├── AGENTS.md                # Agent instructions and guidelines
└── README.md                # This file
```

For detailed project structure and development guidelines, see [`AGENTS.md`](AGENTS.md).

## Mounted Source Paths

| Description | Host Path | Container Path |
|-------------|-----------|----------------|
| Axon Source | (configured by user) | `/workspaces/axon-mcp/axon-src` |
| External Inspiration | (configured by user) | `/workspaces/axon-mcp/external-inspiration/kilocode` |

## Included Features

The dev container includes the following features:

- **devcontainer-foundation** - Base container setup
- **workspace-persistence-mounts** - Persistent workspace storage
- **python-venv-setup** - Python virtual environment at `/home/vscode/.venv-dev`
- **vscode-customizations** - Editor settings (no preinstalled extensions)
- **devcontainer-init-resilience** - Non-aborting init steps with a warnings log
- **staged-image-build** - Minimal build context, `localhost/` image tag
- **postgresql-readiness** - PostgreSQL database
- **redis-readiness** - Redis cache

## Development Workflow

- Workflow definition: [`docs/development-model.md`](docs/development-model.md)
- This workspace uses iterative agile delivery with dependency-graph-driven feature ordering and real-condition validation.

## Service Configuration

### PostgreSQL

| Setting | Value |
|---------|-------|
| User | `indexer` |
| Password | `indexer` |
| Database | `indexer` |
| Port | `5432` |

Initialization scripts:
- `.devcontainer/scripts/init_postgres.sh`
- `.devcontainer/scripts/start_postgres.sh`

### Redis

| Setting | Value |
|---------|-------|
| Port | `6379` |

Initialization scripts:
- `.devcontainer/scripts/init_redis.sh`
- `.devcontainer/scripts/start_redis.sh`

### Prometheus

| Setting | Value |
|---------|-------|
| Port | `9090` |
| Config | `.devcontainer/prometheus/prometheus.yml` |

## Container Lifecycle

| Hook | Script | Does |
|------|--------|------|
| `postCreateCommand` | `init_all.sh --bootstrap` | Init steps plus venv/npm bootstrap |
| `postStartCommand` | `start_dev_services.sh` | `init_all.sh`, then starts Postgres, Redis, Prometheus |

- `init_all.sh` runs each step via `run_step`: a failing step is logged to
  `/home/vscode/services/log/init_warnings.log` and shown as a banner in new terminals, but never aborts startup.
- `stop_dev_services.sh` / `check_dev_services.sh` stop or check all services.
- Service state, logs and editor server data live in named volumes (`axon-mcp-services`,
  `axon-mcp-vscodium-server`), not host folders. `~/.bash_history` is a symlink into the services volume,
  seeded once from `.devcontainer/services/bash_history` if present.

## Notes

- Python venv path: `/home/vscode/.venv-dev`.
- Dev Container uses fixed image `localhost/devcontainer/axon-mcp:latest` (no dynamic build at startup).
