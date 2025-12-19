"""MCP server management commands for Kytchen CLI.

Migrated from kytchen/cli.py with enhanced Typer integration.
Provides easy installation of Kytchen into various MCP clients.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    print_table,
    confirm,
)

app = typer.Typer(
    name="mcp",
    help="MCP server installation and management",
    no_args_is_help=True,
)


# =============================================================================
# Client configuration (migrated from old cli.py)
# =============================================================================

@dataclass
class ClientConfig:
    """Configuration for an MCP client."""

    name: str
    display_name: str
    config_path: Callable[[], Path | None]
    is_cli: bool = False  # True for Claude Code which uses CLI commands
    restart_instruction: str = ""

    def get_path(self) -> Path | None:
        """Get the config path, returns None if not applicable."""
        return self.config_path()


def _get_claude_desktop_path() -> Path | None:
    """Get Claude Desktop config path based on platform."""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        config_home = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        return Path(config_home) / "Claude" / "claude_desktop_config.json"
    return None


def _get_cursor_global_path() -> Path | None:
    """Get Cursor global config path."""
    return Path.home() / ".cursor" / "mcp.json"


def _get_cursor_project_path() -> Path | None:
    """Get Cursor project-level config path (current directory)."""
    return Path.cwd() / ".cursor" / "mcp.json"


def _get_windsurf_path() -> Path | None:
    """Get Windsurf config path."""
    return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"


def _get_vscode_path() -> Path | None:
    """Get VSCode project-level config path."""
    return Path.cwd() / ".vscode" / "mcp.json"


def _get_claude_code_path() -> Path | None:
    """Claude Code uses CLI, not a config file."""
    return None


# Define all supported clients
CLIENTS: dict[str, ClientConfig] = {
    "claude-desktop": ClientConfig(
        name="claude-desktop",
        display_name="Claude Desktop",
        config_path=_get_claude_desktop_path,
        restart_instruction="Restart Claude Desktop to load Kytchen",
    ),
    "cursor": ClientConfig(
        name="cursor",
        display_name="Cursor (Global)",
        config_path=_get_cursor_global_path,
        restart_instruction="Restart Cursor to load Kytchen",
    ),
    "cursor-project": ClientConfig(
        name="cursor-project",
        display_name="Cursor (Project)",
        config_path=_get_cursor_project_path,
        restart_instruction="Restart Cursor to load Kytchen",
    ),
    "windsurf": ClientConfig(
        name="windsurf",
        display_name="Windsurf",
        config_path=_get_windsurf_path,
        restart_instruction="Restart Windsurf to load Kytchen",
    ),
    "vscode": ClientConfig(
        name="vscode",
        display_name="VSCode (Project)",
        config_path=_get_vscode_path,
        restart_instruction="Restart VSCode to load Kytchen",
    ),
    "claude-code": ClientConfig(
        name="claude-code",
        display_name="Claude Code",
        config_path=_get_claude_code_path,
        is_cli=True,
        restart_instruction="Run 'claude' to use Kytchen",
    ),
}

# The JSON configurations to inject
KYTCHEN_CLOUD_MCP_CONFIG = {
    "command": "kytchen",
    "args": [],
    "env": {"KYTCHEN_API_KEY": "kyt_sk_...", "KYTCHEN_API_URL": "https://api.kytchen.dev"},
}
KYTCHEN_LOCAL_MCP_CONFIG = {
    "command": "kytchen-local",
    "args": [],
}


# =============================================================================
# Helper functions (migrated from old cli.py)
# =============================================================================

def is_client_installed(client: ClientConfig) -> bool:
    """Check if a client appears to be installed."""
    if client.is_cli:
        return shutil.which("claude") is not None

    path = client.get_path()
    if path is None:
        return False

    if client.name == "claude-desktop":
        return path.parent.exists()

    if client.name in ("cursor", "windsurf"):
        return path.parent.exists()

    return True


def is_kytchen_configured(client: ClientConfig) -> bool:
    """Check if Kytchen is already configured in a client."""
    if client.is_cli:
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            out = result.stdout.lower()
            return ("kytchen" in out) or ("kytchen-local" in out)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    path = client.get_path()
    if path is None or not path.exists():
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        servers = config.get("mcpServers", {})
        return ("kytchen" in servers) or ("kytchen-local" in servers)
    except (json.JSONDecodeError, OSError):
        return False


def backup_config(path: Path) -> Path | None:
    """Create a backup of the config file."""
    if not path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".backup_{timestamp}.json")

    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except OSError as e:
        print_warning(f"Could not create backup: {e}")
        return None


def install_to_config_file(client: ClientConfig, dry_run: bool = False) -> bool:
    """Install Kytchen to a JSON config file."""
    path = client.get_path()
    if path is None:
        print_error(f"Could not determine config path for {client.display_name}")
        return False

    # Load existing config or create new
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in {path}: {e}")
            return False
        except OSError as e:
            print_error(f"Could not read {path}: {e}")
            return False
    else:
        config = {}

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add cloud + local configs
    already = []
    if "kytchen" in config["mcpServers"]:
        already.append("kytchen")
    if "kytchen-local" in config["mcpServers"]:
        already.append("kytchen-local")
    if already:
        print_warning(f"Already configured in {client.display_name}: {', '.join(already)}")

    config["mcpServers"].setdefault("kytchen", KYTCHEN_CLOUD_MCP_CONFIG.copy())
    config["mcpServers"].setdefault("kytchen-local", KYTCHEN_LOCAL_MCP_CONFIG.copy())

    if dry_run:
        print_info(f"[DRY RUN] Would write to: {path}")
        print_info(f"[DRY RUN] New config:\n{json.dumps(config, indent=2)}")
        return True

    # Create parent directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing config
    if path.exists():
        backup = backup_config(path)
        if backup:
            print_info(f"Backed up existing config to: {backup}")

    # Write new config
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print_error(f"Could not write to {path}: {e}")
        return False

    print_success(f"Configured Kytchen in {client.display_name}")
    print_info(f"Config file: {path}")
    if client.restart_instruction:
        print_info(client.restart_instruction)

    return True


def install_to_claude_code(dry_run: bool = False) -> bool:
    """Install Kytchen to Claude Code using CLI."""
    if not shutil.which("claude"):
        print_error("Claude Code CLI not found. Install it first: https://claude.ai/code")
        return False

    if dry_run:
        print_info("[DRY RUN] Would run: claude mcp add kytchen kytchen")
        print_info("[DRY RUN] Would run: claude mcp add kytchen-local kytchen-local")
        return True

    try:
        results = []
        for name, command in [("kytchen", "kytchen"), ("kytchen-local", "kytchen-local")]:
            result = subprocess.run(
                ["claude", "mcp", "add", name, command],
                capture_output=True,
                text=True,
                timeout=30,
            )
            results.append((name, result))

        ok = True
        for name, result in results:
            if result.returncode == 0:
                continue
            if "already exists" in (result.stderr or "").lower():
                continue
            ok = False
            print_error(f"Failed to add {name} to Claude Code: {result.stderr}")

        if ok:
            print_success("Configured Kytchen in Claude Code")
            print_info("Run 'claude' to use Kytchen")
        return ok
    except subprocess.TimeoutExpired:
        print_error("Command timed out")
        return False
    except FileNotFoundError:
        print_error("Claude Code CLI not found")
        return False


def uninstall_from_config_file(client: ClientConfig, dry_run: bool = False) -> bool:
    """Remove Kytchen from a JSON config file."""
    path = client.get_path()
    if path is None:
        print_error(f"Could not determine config path for {client.display_name}")
        return False

    if not path.exists():
        print_warning(f"Config file does not exist: {path}")
        return True

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print_error(f"Could not read {path}: {e}")
        return False

    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict) or not (("kytchen" in servers) or ("kytchen-local" in servers)):
        print_warning(f"Kytchen is not configured in {client.display_name}")
        return True

    if dry_run:
        print_info(f"[DRY RUN] Would remove 'kytchen' and 'kytchen-local' from mcpServers in: {path}")
        return True

    # Backup before removing
    backup = backup_config(path)
    if backup:
        print_info(f"Backed up existing config to: {backup}")

    # Remove cloud + local entries
    config["mcpServers"].pop("kytchen", None)
    config["mcpServers"].pop("kytchen-local", None)

    # Clean up empty mcpServers
    if not config["mcpServers"]:
        del config["mcpServers"]

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print_error(f"Could not write to {path}: {e}")
        return False

    print_success(f"Removed Kytchen from {client.display_name}")
    return True


def uninstall_from_claude_code(dry_run: bool = False) -> bool:
    """Remove Kytchen from Claude Code using CLI."""
    if not shutil.which("claude"):
        print_error("Claude Code CLI not found")
        return False

    if dry_run:
        print_info("[DRY RUN] Would run: claude mcp remove kytchen")
        print_info("[DRY RUN] Would run: claude mcp remove kytchen-local")
        return True

    try:
        ok = True
        for name in ["kytchen", "kytchen-local"]:
            result = subprocess.run(
                ["claude", "mcp", "remove", name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                continue
            if "not found" in (result.stderr or "").lower():
                continue
            ok = False
            print_error(f"Failed to remove {name} from Claude Code: {result.stderr}")

        if ok:
            print_success("Removed Kytchen from Claude Code")
        return ok
    except subprocess.TimeoutExpired:
        print_error("Command timed out")
        return False
    except FileNotFoundError:
        print_error("Claude Code CLI not found")
        return False


# =============================================================================
# Typer commands
# =============================================================================

@app.command(name="install")
def install_command(
    client: Optional[str] = typer.Argument(
        None,
        help="Client to install to (or interactive mode)",
    ),
    all_clients: bool = typer.Option(
        False,
        "--all",
        help="Install to all detected clients",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without writing",
    ),
) -> None:
    """
    Install Kytchen MCP server to a client.

    Supported clients: claude-desktop, cursor, cursor-project, windsurf, vscode, claude-code

    Examples:

        kytchen mcp install                  # Interactive mode
        kytchen mcp install claude-desktop
        kytchen mcp install --all
        kytchen mcp install cursor --dry-run
    """
    print_header("Kytchen MCP Server Installer")

    # Install all detected clients
    if all_clients:
        for name, client_config in CLIENTS.items():
            if not is_client_installed(client_config):
                print_info(f"Skipping {client_config.display_name} (not installed)")
                continue

            if is_kytchen_configured(client_config):
                print_info(f"Skipping {client_config.display_name} (already configured)")
                continue

            if client_config.is_cli:
                install_to_claude_code(dry_run)
            else:
                install_to_config_file(client_config, dry_run)
            print()
        return

    # Install specific client
    if client:
        if client not in CLIENTS:
            print_error(f"Unknown client: {client}")
            print_info(f"Available clients: {', '.join(CLIENTS.keys())}")
            raise typer.Exit(1)

        client_config = CLIENTS[client]

        if client_config.is_cli:
            success = install_to_claude_code(dry_run)
        else:
            success = install_to_config_file(client_config, dry_run)

        if not success:
            raise typer.Exit(1)
        return

    # Interactive mode
    detected = []
    for name, client_config in CLIENTS.items():
        if is_client_installed(client_config):
            configured = is_kytchen_configured(client_config)
            detected.append((name, client_config, configured))

    if not detected:
        print_warning("No MCP clients detected!")
        print_info("Supported clients: Claude Desktop, Cursor, Windsurf, VSCode, Claude Code")
        raise typer.Exit()

    print_info(f"Detected {len(detected)} MCP client(s):\n")

    rows = []
    for name, client_config, configured in detected:
        status = "Already configured" if configured else "Not configured"
        path = client_config.get_path()
        path_str = "(CLI)" if client_config.is_cli else str(path) if path else "-"
        rows.append((client_config.display_name, status, path_str))

    print_table(
        title="Detected Clients",
        columns=[("Client", "cyan"), ("Status", "green"), ("Path", "blue")],
        rows=rows,
    )

    # Ask which to configure
    to_configure = []
    for name, client_config, configured in detected:
        if configured:
            print_info(f"{client_config.display_name}: Already configured, skipping")
            continue

        if confirm(f"Configure {client_config.display_name}?", default=True):
            to_configure.append(client_config)

    if not to_configure:
        print_info("No clients to configure.")
        return

    print()
    for client_config in to_configure:
        if client_config.is_cli:
            install_to_claude_code(dry_run)
        else:
            install_to_config_file(client_config, dry_run)
        print()


@app.command(name="uninstall")
def uninstall_command(
    client: str = typer.Argument(..., help="Client to uninstall from"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without writing",
    ),
) -> None:
    """
    Uninstall Kytchen MCP server from a client.

    Examples:

        kytchen mcp uninstall claude-desktop
        kytchen mcp uninstall cursor --dry-run
    """
    if client not in CLIENTS:
        print_error(f"Unknown client: {client}")
        print_info(f"Available clients: {', '.join(CLIENTS.keys())}")
        raise typer.Exit(1)

    client_config = CLIENTS[client]

    if client_config.is_cli:
        success = uninstall_from_claude_code(dry_run)
    else:
        success = uninstall_from_config_file(client_config, dry_run)

    if not success:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
