# Axon MCP Workspace Wrapper

This folder contains the Dev Container wrapper for the Axon MCP project.
The source repository is mounted as a sub-folder and is not modified by wrapper setup files.

## Prerequisites

Before setting up this workspace, ensure you have the following installed:

| Requirement | Description | Installation |
|-------------|-------------|--------------|
| **Container Engine** | Docker or Podman | [Docker](https://docs.docker.com/get-docker/) or [Podman](https://podman.io/getting-started/installation) |
| **VS Code** | Visual Studio Code | [Download VS Code](https://code.visualstudio.com/) |
| **Dev Containers Extension** | VS Code extension for containers | Install via VS Code Extensions marketplace |
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

### 3. Open in VS Code

```bash
code .
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

The script automatically checks if the container image `devcontainer/axon-mcp:latest` already exists:

- **Image exists**: Skips build (use `--force-build` to rebuild)
- **Image missing**: Builds automatically using detected container engine
- **Build command**: `cd .devcontainer && <engine> build -t devcontainer/axon-mcp:latest -f Dockerfile .`

## Configuration Options

The setup script configures the following options:

### Axon Source Directory (Mandatory)

The path to your local Axon.MCP.Server repository. This directory will be mounted at `/workspaces/axon-mcp/axon-src` inside the container.

### AI Assistant Integration

| Assistant | Extension | Description |
|-----------|-----------|-------------|
| **Codex** | `chatgpt.chatgpt-vscode` | OpenAI Codex assistant integration. Optionally mounts `~/.codex` config folder. |
| **Kilo Code** | `kilocode.kilo-code` | Kilo Code AI assistant extension |

### Optional VS Code Extensions

| Extension | ID | Description |
|-----------|-----|-------------|
| Highlight | `fabiospampinato.vscode-highlight` | Highlight words and patterns in editor |
| Markdown Preview | `shd101wyy.markdown-preview-enhanced` | Enhanced Markdown preview with diagrams and math |
| Rainbow CSV | `mechatroner.rainbow-csv` | CSV/TSV file highlighting and alignment |
| Bookmarks | `alefragnani.Bookmarks` | Bookmark lines in files for quick navigation |

### Config File Format

For non-interactive mode, create a JSON config file:

```json
{
  "axon_src_path": "/path/to/Axon.MCP.Server",
  "ai_config": {
    "codex": {
      "enabled": true,
      "path": "~/.codex"
    },
    "kilocode": {
      "enabled": false
    }
  },
  "optional_extensions": [
    "fabiospampinato.vscode-highlight",
    "shd101wyy.markdown-preview-enhanced"
  ]
}
```

## Container Engine Support

The setup script automatically detects and validates your container engine.

### Docker Support

- **Detection**: Checks if `docker` command is available and daemon is running
- **Validation**: Runs `docker info` to verify daemon connectivity
- **Troubleshooting**: 
  - macOS/Windows: Start Docker Desktop
  - Linux: Run `sudo systemctl start docker`

### Podman Support

- **Detection**: Checks if `podman` command is available
- **Validation**: 
  - Linux: Runs `podman info` (rootless mode supported)
  - macOS/Windows: Checks for running machine via `podman machine list`
- **Troubleshooting**:
  - macOS/Windows: Run `podman machine start`
  - Linux: Ensure Podman is properly configured for rootless operation

### Engine Selection Priority

When both Docker and Podman are available and running, Docker is preferred by default.

## Project Structure

```
axon-mcp/
├── .devcontainer/           # Dev Container configuration
│   ├── Dockerfile           # Container image definition
│   ├── devcontainer.json    # Container configuration (generated)
│   ├── templates/           # Configuration templates
│   └── scripts/             # Initialization scripts
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
- **vscode-customizations** - VS Code settings and extensions
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

## Notes

- First container create runs `.devcontainer/scripts/bootstrap.sh`.
- Python venv path: `/home/vscode/.venv-dev`.
- Dev Container uses fixed image `devcontainer/axon-mcp:latest` (no dynamic build at startup).
