#!/usr/bin/env python3
"""
Workspace Setup Script for Axon MCP Dev Container

This script personalizes the devcontainer configuration for each developer.
It generates a devcontainer.json file from a template based on user preferences,
then builds the container image via .devcontainer/build-image.sh.

Usage:
    python setup_workspace.py [--non-interactive] [--config CONFIG_FILE]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


IMAGE_NAME = "localhost/devcontainer/axon-mcp:latest"
WORKSPACE_TARGET = "/workspaces/axon-mcp"


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


def get_build_script_path() -> Path:
    """Get the path to the staged image build script."""
    return get_workspace_root() / ".devcontainer" / "build-image.sh"


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


def format_bind_mount(source: str, target: str, readonly: bool = False) -> str:
    """Format a bind mount entry, including the leading separator for the template."""
    entry = f"source={format_mount_source_path(expand_path(source))},target={target},type=bind"
    if readonly:
        entry += ",readonly"
    return f',\n    "{entry}"'


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


def prompt_ai_assistants() -> dict:
    """Prompt for AI assistant configuration."""
    print("\nAI Assistant Integration:")
    print("-" * 40)

    config = {
        "codex": {"enabled": False, "path": None},
    }

    # Codex
    if prompt_yes_no("  Mount OpenAI Codex config folder?", default=False):
        config["codex"]["enabled"] = True
        codex_path = input(f"  Codex config path [~/.codex]: ").strip()
        if not codex_path:
            codex_path = "~/.codex"
        config["codex"]["path"] = expand_path(codex_path)

    return config


def prompt_extra_mounts() -> list[dict]:
    """Prompt for optional extra bind mounts (e.g. read-only reference code)."""
    print("\nExtra Mounts:")
    print("-" * 40)

    mounts = []
    if prompt_yes_no("  Mount a kilocode checkout as read-only external inspiration?", default=False):
        kilocode_path = prompt_path("  Path to the kilocode checkout", must_exist=True)
        mounts.append({
            "source": str(kilocode_path),
            "target": f"{WORKSPACE_TARGET}/external-inspiration/kilocode",
            "readonly": True,
        })
    return mounts


def build_container_image(force_rebuild: bool = False) -> bool:
    """
    Build the container image via .devcontainer/build-image.sh.

    The build script stages a minimal build context and relies on `docker`
    being wired to the right engine (Apple Container via docker_bridge.py,
    Docker or Podman), so no engine detection happens here.

    Returns:
        True if build succeeded or image already exists, False otherwise
    """
    build_script = get_build_script_path()
    if not build_script.exists():
        print(f"\n❌ Error: Build script not found: {build_script}")
        return False

    if not force_rebuild and image_exists(IMAGE_NAME):
        print(f"✅ Image already exists: {IMAGE_NAME}")
        print("   Use --force-build to rebuild")
        return True

    print(f"\nRunning: {build_script}")
    print("-" * 40)
    try:
        result = subprocess.run(["bash", str(build_script)], check=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        return False

    if result.returncode == 0:
        print("-" * 40)
        print(f"✅ Successfully built image: {IMAGE_NAME}")
        return True

    print("-" * 40)
    print(f"\n❌ Build failed with exit code: {result.returncode}")
    print(f"   Retry manually with: {build_script}")
    return False


def image_exists(image_name: str) -> bool:
    """Check if a container image already exists locally."""
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def generate_devcontainer(
    axon_src_path: str,
    ai_config: dict,
    extra_mounts: list[dict],
) -> str:
    """
    Generate devcontainer.json content from template.

    Args:
        axon_src_path: Path to the Axon source directory
        ai_config: AI assistant configuration dict
        extra_mounts: List of {"source", "target", "readonly"} bind mounts

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
    codex = ai_config.get("codex", {})
    if codex.get("enabled"):
        codex_mount = format_bind_mount(codex["path"], "/home/vscode/.codex")

    axon_src_mount = format_bind_mount(axon_src_path, f"{WORKSPACE_TARGET}/axon-src")

    extra_mounts_str = "".join(
        format_bind_mount(m["source"], m["target"], m.get("readonly", False))
        for m in extra_mounts
    )

    # Replace placeholders
    content = template_content.replace("{{ codex_mount }}", codex_mount)
    content = content.replace("{{ axon_src_mount }}", axon_src_mount)
    content = content.replace("{{ extra_mounts }}", extra_mounts_str)

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
    print(f"This directory will be mounted as {WORKSPACE_TARGET}/axon-src")

    axon_src_path = prompt_path(
        "Enter the path to your Axon source directory",
        must_exist=True,
        create_if_missing=False,
    )

    # Step 2: AI Assistants
    print("\nStep 2: AI Assistant Integration")
    print("-" * 40)
    ai_config = prompt_ai_assistants()

    # Step 3: Extra mounts
    print("\nStep 3: Extra Mounts")
    print("-" * 40)
    extra_mounts = prompt_extra_mounts()

    return {
        "axon_src_path": str(axon_src_path),
        "ai_config": ai_config,
        "extra_mounts": extra_mounts,
    }


def run_non_interactive(config_file: Optional[str] = None) -> dict:
    """Run in non-interactive mode using config file or defaults."""
    if config_file:
        with open(config_file, "r") as f:
            config = json.load(f)
        config.setdefault("ai_config", {"codex": {"enabled": False, "path": None}})
        config.setdefault("extra_mounts", [])
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
        },
        "extra_mounts": [],
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
        extra_mounts=config["extra_mounts"],
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
        build_success = build_container_image(force_rebuild=args.force_build)
    else:
        print("\n⏭️  Skipping container image build (--skip-build)")

    # Summary
    print("\nConfiguration Summary:")
    print("-" * 40)
    print(f"  Image: {IMAGE_NAME}")
    print(f"  Axon source: {config['axon_src_path']}")
    print(f"  Codex enabled: {config['ai_config']['codex']['enabled']}")
    if config['ai_config']['codex']['enabled']:
        print(f"    Codex path: {config['ai_config']['codex']['path']}")
    for mount in config["extra_mounts"]:
        mode = " (read-only)" if mount.get("readonly") else ""
        print(f"  Extra mount: {mount['source']} -> {mount['target']}{mode}")

    print("\nNext Steps:")
    print("-" * 40)
    if build_success and not args.skip_build:
        print("✅ Container image built successfully!")
        print("1. Open the workspace in VSCodium")
        print("2. When prompted, click 'Reopen in Container'")
    elif args.skip_build:
        print("1. Build the dev container image (if not already built):")
        print(f"   {get_build_script_path()}")
        print("2. Open the workspace in VSCodium")
        print("3. When prompted, click 'Reopen in Container'")
    else:
        print("⚠️  Container image build failed. Please fix the errors and retry:")
        print(f"   {get_build_script_path()}")


if __name__ == "__main__":
    main()
