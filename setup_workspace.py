#!/usr/bin/env python3
"""
Workspace Setup Script for Axon MCP Dev Container

This script personalizes the devcontainer configuration for each developer.
It generates a devcontainer.json file from a template based on user preferences.

Usage:
    python setup_workspace.py [--non-interactive] [--config CONFIG_FILE]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Extension definitions
BASE_EXTENSIONS = [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
]

OPTIONAL_EXTENSIONS = {
    "highlight": {
        "id": "fabiospampinato.vscode-highlight",
        "description": "Highlight words and patterns in editor",
    },
    "markdown-preview": {
        "id": "shd101wyy.markdown-preview-enhanced",
        "description": "Enhanced Markdown preview with diagrams and math",
    },
    "rainbow-csv": {
        "id": "mechatroner.rainbow-csv",
        "description": "CSV/TSV file highlighting and alignment",
    },
    "bookmarks": {
        "id": "alefragnani.Bookmarks",
        "description": "Bookmark lines in files for quick navigation",
    },
}

AI_ASSISTANT_EXTENSIONS = {
    "codex": {
        "extension_id": "openai.chatgpt",
        "mount_path": "~/.codex",
        "mount_target": "/home/vscode/.codex",
        "description": "OpenAI Codex assistant integration",
    },
    "kilocode": {
        "extension_id": "kilocode.kilo-code",
        "mount_path": None,  # No folder to mount
        "mount_target": None,
        "description": "Kilo Code AI assistant extension",
    },
}


def get_workspace_root() -> Path:
    """Get the workspace root directory."""
    script_dir = Path(__file__).parent.resolve()
    return script_dir


def get_template_path() -> Path:
    """Get the path to the devcontainer template."""
    return get_workspace_root() / ".devcontainer" / "templates" / "devcontainer.json.template"


def get_output_path() -> Path:
    """Get the path for the generated devcontainer.json."""
    return get_workspace_root() / ".devcontainer" / "devcontainer.json"


def expand_path(path_str: str) -> str:
    """Expand ~ and environment variables in a path."""
    return os.path.expanduser(os.path.expandvars(path_str))


def format_mount_source_path(path_str: str) -> str:
    """
    Format a host path for safe insertion into devcontainer mount JSON.

    This normalizes Windows-style backslashes to forward slashes so values like
    C:\\Users\\name\\repo do not create invalid JSON escape sequences. It then
    applies JSON string escaping for extra safety.
    """
    normalized = str(path_str).replace("\\", "/")
    # json.dumps returns a quoted JSON string; strip outer quotes for insertion
    # into an already-quoted template placeholder.
    return json.dumps(normalized)[1:-1]


def validate_path(path_str: str, must_exist: bool = True, create_if_missing: bool = False) -> Optional[Path]:
    """
    Validate a path string.
    
    Args:
        path_str: The path string to validate
        must_exist: If True, the path must exist
        create_if_missing: If True, create the directory if it doesn't exist
    
    Returns:
        Path object if valid, None otherwise
    """
    expanded = expand_path(path_str)
    path = Path(expanded)
    
    if must_exist and not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"  Created directory: {path}")
            except Exception as e:
                print(f"  Error creating directory: {e}")
                return None
        else:
            print(f"  Error: Path does not exist: {path}")
            return None
    
    return path


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Prompt for a yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{question} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("  Please enter 'y' or 'n'.")


def prompt_path(question: str, must_exist: bool = True, create_if_missing: bool = False) -> Optional[Path]:
    """Prompt for a path input."""
    while True:
        response = input(f"{question}: ").strip()
        if not response:
            print("  This field is required. Please enter a path.")
            continue
        
        path = validate_path(response, must_exist=must_exist, create_if_missing=create_if_missing)
        if path is not None:
            return path


def prompt_optional_extensions() -> list[str]:
    """Prompt for optional extensions selection."""
    print("\nOptional Extensions:")
    print("-" * 40)
    
    selected = []
    for key, ext_info in OPTIONAL_EXTENSIONS.items():
        if prompt_yes_no(f"  Install {ext_info['description']}?", default=True):
            selected.append(ext_info["id"])
    
    return selected


def prompt_ai_assistants() -> dict:
    """Prompt for AI assistant configuration."""
    print("\nAI Assistant Integration:")
    print("-" * 40)
    
    config = {
        "codex": {"enabled": False, "path": None},
        "kilocode": {"enabled": False},
    }
    
    # Codex
    if prompt_yes_no("  Enable OpenAI Codex integration?", default=False):
        config["codex"]["enabled"] = True
        codex_path = input(f"  Codex config path [~/.codex]: ").strip()
        if not codex_path:
            codex_path = "~/.codex"
        config["codex"]["path"] = expand_path(codex_path)
    
    # Kilo Code
    if prompt_yes_no("  Enable Kilo Code integration?", default=False):
        config["kilocode"]["enabled"] = True
    
    return config


def detect_container_engine() -> str:
    """
    Detect which container engine is available and running.
    
    Checks for Docker and Podman availability. If both are available,
    checks which one has a running daemon/machine.
    
    Returns:
        The engine name ("docker" or "podman") if available and running.
    
    Raises:
        SystemExit: If no container engine is available or running.
    """
    engines_available = []
    
    # Check for Docker
    docker_path = shutil.which("docker")
    if docker_path:
        engines_available.append("docker")
    
    # Check for Podman
    podman_path = shutil.which("podman")
    if podman_path:
        engines_available.append("podman")
    
    if not engines_available:
        print("\n❌ Error: No container engine found!")
        print("-" * 40)
        print("This workspace requires a container engine to run the devcontainer.")
        print("\nPlease install one of the following:")
        print("  • Docker: https://docs.docker.com/get-docker/")
        print("  • Podman: https://podman.io/getting-started/installation")
        sys.exit(1)
    
    # If only one engine is available, check if it's running
    if len(engines_available) == 1:
        engine = engines_available[0]
        if engine == "docker":
            if _is_docker_running():
                print(f"✅ Detected container engine: Docker")
                return "docker"
            else:
                _print_docker_not_running_error()
                sys.exit(1)
        else:  # podman
            if _is_podman_running():
                print(f"✅ Detected container engine: Podman")
                return "podman"
            else:
                _print_podman_not_running_error()
                sys.exit(1)
    
    # Both engines are available - check which one is running
    docker_running = _is_docker_running()
    podman_running = _is_podman_running()
    
    if docker_running and podman_running:
        # Both running - prefer Docker
        print("✅ Detected container engines: Docker and Podman (using Docker)")
        return "docker"
    elif docker_running:
        print("✅ Detected container engine: Docker")
        return "docker"
    elif podman_running:
        print("✅ Detected container engine: Podman")
        return "podman"
    else:
        # Neither is running
        print("\n❌ Error: No container engine is running!")
        print("-" * 40)
        print("Both Docker and Podman are installed but neither is running.")
        print("\nPlease start one of them:")
        print("  • Docker: Start Docker Desktop or the Docker daemon")
        print("  • Podman: Run 'podman machine start' (on macOS/Windows)")
        sys.exit(1)


def _is_docker_running() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _is_podman_running() -> bool:
    """Check if Podman machine/daemon is running."""
    try:
        # On Linux, Podman can run rootless without a machine
        # Check if podman can communicate with the container runtime
        result = subprocess.run(
            ["podman", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True
        
        # On macOS/Windows, check for a running machine
        result = subprocess.run(
            ["podman", "machine", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Check if any machine is running (look for "running" in output)
            return "running" in result.stdout.lower()
        
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _print_docker_not_running_error():
    """Print error message when Docker is not running."""
    print("\n❌ Error: Docker is installed but not running!")
    print("-" * 40)
    print("Please start Docker:")
    print("  • On macOS/Windows: Start Docker Desktop")
    print("  • On Linux: Run 'sudo systemctl start docker'")
    print("             Or run 'sudo dockerd &' for manual start")


def _print_podman_not_running_error():
    """Print error message when Podman is not running."""
    print("\n❌ Error: Podman is installed but not running!")
    print("-" * 40)
    print("Please start Podman:")
    print("  • On macOS/Windows: Run 'podman machine start'")
    print("  • On Linux: Podman should work rootless without a machine")
    print("              Check if podman is properly configured")


def image_exists(engine: str, image_name: str) -> bool:
    """
    Check if a container image already exists locally.
    
    Args:
        engine: The container engine to use ("docker" or "podman")
        image_name: The image name to check (e.g., "devcontainer/axon-mcp:latest")
    
    Returns:
        True if the image exists, False otherwise
    """
    try:
        result = subprocess.run(
            [engine, "image", "inspect", image_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def build_container_image(
    engine: str,
    dockerfile_path: Path,
    image_name: str,
    context_path: Optional[Path] = None,
    force_rebuild: bool = False,
) -> bool:
    """
    Build a container image using the detected container engine.
    
    Args:
        engine: The container engine to use ("docker" or "podman")
        dockerfile_path: Path to the Dockerfile
        image_name: The tag for the built image (e.g., "devcontainer/axon-mcp:latest")
        context_path: Build context directory (defaults to dockerfile parent)
        force_rebuild: If True, rebuild even if image exists
    
    Returns:
        True if build succeeded or image already exists, False otherwise
    
    Raises:
        FileNotFoundError: If the Dockerfile doesn't exist
    """
    if not dockerfile_path.exists():
        print(f"\n❌ Error: Dockerfile not found: {dockerfile_path}")
        return False
    
    if context_path is None:
        context_path = dockerfile_path.parent
    
    if not context_path.exists():
        print(f"\n❌ Error: Build context not found: {context_path}")
        return False
    
    # Check if image already exists
    if not force_rebuild and image_exists(engine, image_name):
        print(f"✅ Image already exists: {image_name}")
        print("   Use --force-build to rebuild")
        return True
    
    print(f"\nBuilding container image: {image_name}")
    print(f"  Engine: {engine}")
    print(f"  Dockerfile: {dockerfile_path}")
    print(f"  Context: {context_path}")
    print("-" * 40)
    
    # Build the command - run from context directory with -f pointing to Dockerfile
    # The Dockerfile already handles TARGETARCH internally via automatic platform detection
    cmd = [
        engine,
        "build",
        "-t", image_name,
        "-f", "Dockerfile",  # Use relative name since we cd to context
        ".",  # Current directory (context)
    ]
    
    print(f"Running: cd {context_path} && {' '.join(cmd)}")
    print("-" * 40)
    
    try:
        # Run the build from the context directory
        result = subprocess.run(
            cmd,
            cwd=str(context_path),
            check=False,  # Don't raise on non-zero exit
        )
        
        if result.returncode == 0:
            print("-" * 40)
            print(f"✅ Successfully built image: {image_name}")
            return True
        else:
            print("-" * 40)
            print(f"\n❌ Build failed with exit code: {result.returncode}")
            print("\nTroubleshooting tips:")
            print("  • Check the Dockerfile for syntax errors")
            print("  • Ensure all required base images are accessible")
            print("  • Try building manually with:")
            print(f"    cd {context_path} && {engine} build -t {image_name} -f Dockerfile .")
            return False
            
    except FileNotFoundError:
        print(f"\n❌ Error: {engine} command not found!")
        print("The container engine was detected but is no longer available.")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during build: {e}")
        return False


def generate_devcontainer(
    axon_src_path: str,
    ai_config: dict,
    optional_extensions: list[str],
) -> str:
    """
    Generate devcontainer.json content from template.
    
    Args:
        axon_src_path: Path to the Axon source directory
        ai_config: AI assistant configuration dict
        optional_extensions: List of optional extension IDs
    
    Returns:
        Generated JSON string
    """
    template_path = get_template_path()
    
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)
    
    with open(template_path, "r") as f:
        template_content = f.read()
    
    # Build mount strings
    codex_mount = ""
    if ai_config["codex"]["enabled"]:
        codex_path = format_mount_source_path(ai_config["codex"]["path"])
        codex_mount = f',\n    "source={codex_path},target=/home/vscode/.codex,type=bind"'

    axon_src_mount_path = format_mount_source_path(axon_src_path)
    axon_src_mount = f',\n    "source={axon_src_mount_path},target=/workspaces/axon-mcp/axon-src,type=bind"'
    
    kilocode_mount = ""
    if ai_config["kilocode"]["enabled"]:
        # Kilocode has no folder to mount, just extension
        kilocode_mount = ""
    
    # Build extension strings
    codex_extension = ""
    if ai_config["codex"]["enabled"]:
        codex_extension = ',\n        "chatgpt.chatgpt-vscode"'
    
    kilocode_extension = ""
    if ai_config["kilocode"]["enabled"]:
        kilocode_extension = ',\n        "kilocode.kilo-code"'
    
    # Optional extensions
    optional_extensions_str = ""
    if optional_extensions:
        ext_lines = [f',\n        "{ext_id}"' for ext_id in optional_extensions]
        optional_extensions_str = "".join(ext_lines)
    
    # Replace placeholders
    content = template_content.replace("{{ codex_mount }}", codex_mount)
    content = content.replace("{{ axon_src_mount }}", axon_src_mount)
    content = content.replace("{{ kilocode_mount }}", kilocode_mount)
    content = content.replace("{{ codex_extension }}", codex_extension)
    content = content.replace("{{ kilocode_extension }}", kilocode_extension)
    content = content.replace("{{ optional_extensions }}", optional_extensions_str)
    
    # Validate JSON
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error: Generated invalid JSON: {e}")
        print("Content preview:")
        print(content[:500])
        sys.exit(1)
    
    return content


def run_interactive() -> dict:
    """Run the interactive setup wizard."""
    print("=" * 60)
    print("Axon MCP Workspace Setup")
    print("=" * 60)
    
    # Step 1: Axon source path (mandatory)
    print("\nStep 1: Axon Source Directory")
    print("-" * 40)
    print("This is the path to your local Axon.MCP.Server repository.")
    print("This directory will be mounted as /workspaces/axon-mcp/axon-src")
    
    axon_src_path = prompt_path(
        "Enter the path to your Axon source directory",
        must_exist=True,
        create_if_missing=False,
    )
    
    # Step 2: AI Assistants
    print("\nStep 2: AI Assistant Integration")
    print("-" * 40)
    ai_config = prompt_ai_assistants()
    
    # Step 3: Optional extensions
    print("\nStep 3: Optional Extensions")
    print("-" * 40)
    optional_extensions = prompt_optional_extensions()
    
    return {
        "axon_src_path": str(axon_src_path),
        "ai_config": ai_config,
        "optional_extensions": optional_extensions,
    }


def run_non_interactive(config_file: Optional[str] = None) -> dict:
    """Run in non-interactive mode using config file or defaults."""
    if config_file:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    
    # Use defaults for CI/CD
    print("Running in non-interactive mode with defaults...")
    
    axon_src = os.environ.get("AXON_SRC_PATH", "")
    if not axon_src:
        print("Error: AXON_SRC_PATH environment variable must be set in non-interactive mode")
        sys.exit(1)
    
    return {
        "axon_src_path": axon_src,
        "ai_config": {
            "codex": {"enabled": False, "path": None},
            "kilocode": {"enabled": False},
        },
        "optional_extensions": [ext["id"] for ext in OPTIONAL_EXTENSIONS.values()],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Setup workspace for Axon MCP dev container"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompts, use environment variables or config file",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON config file for non-interactive mode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building the container image (useful when image already exists)",
    )
    parser.add_argument(
        "--force-build",
        action="store_true",
        help="Force rebuild even if image already exists",
    )
    
    args = parser.parse_args()
    
    # Detect container engine early (required for devcontainer setup)
    print("\n" + "=" * 60)
    print("Container Engine Detection")
    print("=" * 60)
    container_engine = detect_container_engine()
    
    # Gather configuration
    if args.non_interactive:
        config = run_non_interactive(args.config)
    else:
        config = run_interactive()
    
    # Generate devcontainer.json
    print("\n" + "=" * 60)
    print("Generating devcontainer.json...")
    print("=" * 60)
    
    content = generate_devcontainer(
        axon_src_path=config["axon_src_path"],
        ai_config=config["ai_config"],
        optional_extensions=config["optional_extensions"],
    )
    
    if args.dry_run:
        print("\nGenerated content (dry run):")
        print("-" * 40)
        print(content)
        return
    
    # Write output
    output_path = get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"\n✅ Generated: {output_path}")
    
    # Build container image
    build_success = True  # Assume success if skipped
    if not args.skip_build:
        print("\n" + "=" * 60)
        print("Building Container Image")
        print("=" * 60)
        
        dockerfile_path = get_workspace_root() / ".devcontainer" / "Dockerfile"
        image_name = "devcontainer/axon-mcp:latest"
        
        build_success = build_container_image(
            engine=container_engine,
            dockerfile_path=dockerfile_path,
            image_name=image_name,
            force_rebuild=args.force_build,
        )
    else:
        print("\n⏭️  Skipping container image build (--skip-build)")
    
    # Summary
    print("\nConfiguration Summary:")
    print("-" * 40)
    print(f"  Container engine: {container_engine}")
    print(f"  Axon source: {config['axon_src_path']}")
    print(f"  Codex enabled: {config['ai_config']['codex']['enabled']}")
    if config['ai_config']['codex']['enabled']:
        print(f"    Codex path: {config['ai_config']['codex']['path']}")
    print(f"  Kilo Code enabled: {config['ai_config']['kilocode']['enabled']}")
    print(f"  Optional extensions: {len(config['optional_extensions'])} selected")
    
    print("\nNext Steps:")
    print("-" * 40)
    if build_success and not args.skip_build:
        print("✅ Container image built successfully!")
        print("1. Open the workspace in VS Code")
        print("2. When prompted, click 'Reopen in Container'")
    elif args.skip_build:
        print("1. Build the dev container image (if not already built):")
        print(f"   cd .devcontainer && {container_engine} build -t devcontainer/axon-mcp:latest -f Dockerfile .")
        print("2. Open the workspace in VS Code")
        print("3. When prompted, click 'Reopen in Container'")
    else:
        print("⚠️  Container image build failed. Please fix the errors and retry:")
        print(f"   cd .devcontainer && {container_engine} build -t devcontainer/axon-mcp:latest -f Dockerfile .")
        print("\nAlternatively, you can open VS Code and let it build the image automatically.")


if __name__ == "__main__":
    main()
