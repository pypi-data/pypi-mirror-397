"""CLI installer for Kytchen MCP servers.

DEPRECATED: This CLI is being replaced with the new Typer-based CLI in kytchen.cli package.

The `kytchen-rlm` command will continue to work for MCP installation, but new features
will only be available in the new CLI. Consider migrating to:
    - `kytchen mcp install` instead of `kytchen-rlm install`
    - `kytchen mcp doctor` instead of `kytchen-rlm doctor`

Provides easy installation of Kytchen into various MCP clients:
- Claude Desktop (macOS/Windows)
- Cursor (global/project)
- Windsurf
- Claude Code
- VSCode

Usage:
    kytchen-rlm install           # Interactive mode, detects all clients
    kytchen-rlm install claude-desktop
    kytchen-rlm install cursor
    kytchen-rlm install windsurf
    kytchen-rlm install claude-code
    kytchen-rlm install --all     # Configure all detected clients
    kytchen-rlm uninstall <client>
    kytchen-rlm doctor            # Verify installation
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
from typing import Callable

__all__ = ["main"]

# Try to import rich for colored output, fall back to plain text
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


# =============================================================================
# Output helpers (with/without rich)
# =============================================================================

def print_success(msg: str) -> None:
    """Print success message in green."""
    if RICH_AVAILABLE:
        console.print(f"[green]{msg}[/green]")
    else:
        print(f"SUCCESS: {msg}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    if RICH_AVAILABLE:
        console.print(f"[red]{msg}[/red]")
    else:
        print(f"ERROR: {msg}", file=sys.stderr)


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    if RICH_AVAILABLE:
        console.print(f"[yellow]{msg}[/yellow]")
    else:
        print(f"WARNING: {msg}")


def print_info(msg: str) -> None:
    """Print info message in blue."""
    if RICH_AVAILABLE:
        console.print(f"[blue]{msg}[/blue]")
    else:
        print(msg)


def print_header(title: str) -> None:
    """Print a header/title."""
    if RICH_AVAILABLE:
        console.print(Panel(title, style="bold cyan"))
    else:
        print(f"\n{'=' * 50}")
        print(f"  {title}")
        print(f"{'=' * 50}\n")


def print_table(title: str, rows: list[tuple[str, str, str]]) -> None:
    """Print a table with Client, Status, Path columns."""
    if RICH_AVAILABLE:
        table = Table(title=title)
        table.add_column("Client", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Path")
        for row in rows:
            table.add_row(*row)
        console.print(table)
    else:
        print(f"\n{title}")
        print("-" * 70)
        print(f"{'Client':<20} {'Status':<15} {'Path'}")
        print("-" * 70)
        for client, status, path in rows:
            print(f"{client:<20} {status:<15} {path}")
        print()


# =============================================================================
# Client configuration
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
        # XDG-compliant path
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
    # Placeholder; users should replace with their real key (prefix: kyt_sk_...)
    "env": {"KYTCHEN_API_KEY": "kyt_sk_...", "KYTCHEN_API_URL": "https://api.kytchen.dev"},
}
KYTCHEN_LOCAL_MCP_CONFIG = {
    "command": "kytchen-local",
    "args": [],
}


# =============================================================================
# Detection and installation logic
# =============================================================================

def is_client_installed(client: ClientConfig) -> bool:
    """Check if a client appears to be installed."""
    if client.is_cli:
        # Check if claude CLI is available
        return shutil.which("claude") is not None

    path = client.get_path()
    if path is None:
        return False

    # Check if the config directory exists (client is likely installed)
    # For Claude Desktop, check the parent directory
    if client.name == "claude-desktop":
        return path.parent.exists()

    # For editors, we check if the global config dir exists
    if client.name == "cursor":
        return path.parent.exists()

    if client.name == "windsurf":
        return path.parent.exists()

    # For project-level configs, always return True (user may want to create)
    return True


def is_kytchen_configured(client: ClientConfig) -> bool:
    """Check if Kytchen is already configured in a client."""
    if client.is_cli:
        # Check claude mcp list
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


def validate_json(path: Path) -> bool:
    """Validate that a JSON file is well-formed."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, OSError):
        return False


def install_to_config_file(
    client: ClientConfig,
    dry_run: bool = False,
) -> bool:
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

    # Add cloud + local configs (idempotent).
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

    # Validate
    if not validate_json(path):
        print_error(f"Written JSON is invalid! Check {path}")
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


def uninstall_from_config_file(
    client: ClientConfig,
    dry_run: bool = False,
) -> bool:
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

    # Remove cloud + local entries if present.
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


def install_client(client: ClientConfig, dry_run: bool = False) -> bool:
    """Install Kytchen to a specific client."""
    if client.is_cli:
        return install_to_claude_code(dry_run)
    else:
        return install_to_config_file(client, dry_run)


def uninstall_client(client: ClientConfig, dry_run: bool = False) -> bool:
    """Uninstall Kytchen from a specific client."""
    if client.is_cli:
        return uninstall_from_claude_code(dry_run)
    else:
        return uninstall_from_config_file(client, dry_run)


# =============================================================================
# Doctor command
# =============================================================================

def doctor() -> bool:
    """Verify Kytchen installation and diagnose issues."""
    print_header("Kytchen Doctor")

    all_ok = True

    # Check if entry points are available
    print_info("Checking `kytchen` / `kytchen-local` commands...")
    if shutil.which("kytchen") and shutil.which("kytchen-local"):
        print_success("kytchen and kytchen-local are in PATH")
    elif shutil.which("kytchen-local"):
        print_warning("kytchen-local is in PATH, but kytchen is not")
    else:
        print_error("kytchen-local not found in PATH")
        print_info("Try reinstalling: pip install 'kytchen[mcp]'")
        all_ok = False

    # Check MCP dependency
    print_info("\nChecking MCP dependency...")
    try:
        import mcp  # noqa: F401
        print_success("MCP package is installed")
    except ImportError:
        print_error("MCP package not installed")
        print_info("Install with: pip install 'kytchen[mcp]'")
        all_ok = False

    # Check each client
    print_info("\nChecking client configurations...")
    rows = []

    for name, client in CLIENTS.items():
        if client.is_cli:
            if shutil.which("claude"):
                if is_kytchen_configured(client):
                    status = "Configured"
                else:
                    status = "Not configured"
                path_str = "(CLI)"
            else:
                status = "Not installed"
                path_str = "-"
        else:
            path = client.get_path()
            if path is None:
                status = "N/A"
                path_str = "-"
            elif not is_client_installed(client):
                status = "Not installed"
                path_str = str(path)
            elif is_kytchen_configured(client):
                status = "Configured"
                path_str = str(path)
            else:
                status = "Not configured"
                path_str = str(path)

        rows.append((client.display_name, status, path_str))

    print_table("MCP Client Status", rows)

    # Test MCP server startup
    print_info("Testing MCP server startup...")
    try:
        import kytchen.mcp.local_server  # noqa: F401
        print_success("Kytchen MCP server module loads correctly")
    except ImportError as e:
        print_error(f"Failed to import MCP server: {e}")
        all_ok = False
    except RuntimeError as e:
        if "mcp" in str(e).lower():
            print_error(f"MCP dependency issue: {e}")
            print_info("Install with: pip install 'kytchen[mcp]'")
        else:
            print_error(f"Server error: {e}")
        all_ok = False

    print()
    if all_ok:
        print_success("All checks passed!")
    else:
        print_error("Some checks failed. See above for details.")

    return all_ok


# =============================================================================
# Interactive mode
# =============================================================================

def interactive_install(dry_run: bool = False) -> None:
    """Interactive installation mode."""
    print_header("Kytchen MCP Server Installer")

    # Detect installed clients
    detected = []
    for name, client in CLIENTS.items():
        if is_client_installed(client):
            configured = is_kytchen_configured(client)
            detected.append((name, client, configured))

    if not detected:
        print_warning("No MCP clients detected!")
        print_info("Supported clients: Claude Desktop, Cursor, Windsurf, VSCode, Claude Code")
        return

    print_info(f"Detected {len(detected)} MCP client(s):\n")

    rows = []
    for name, client, configured in detected:
        status = "Already configured" if configured else "Not configured"
        path = client.get_path()
        path_str = "(CLI)" if client.is_cli else str(path) if path else "-"
        rows.append((client.display_name, status, path_str))

    print_table("Detected Clients", rows)

    # Ask user which to configure
    to_configure = []
    for name, client, configured in detected:
        if configured:
            print_info(f"{client.display_name}: Already configured, skipping")
            continue

        try:
            response = input(f"Configure {client.display_name}? [Y/n]: ").strip().lower()
            if response in ("", "y", "yes"):
                to_configure.append(client)
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return

    if not to_configure:
        print_info("No clients to configure.")
        return

    print()
    for client in to_configure:
        install_client(client, dry_run)
        print()


def install_all(dry_run: bool = False) -> None:
    """Install Kytchen to all detected clients."""
    print_header("Installing Kytchen to All Detected Clients")

    for name, client in CLIENTS.items():
        if not is_client_installed(client):
            print_info(f"Skipping {client.display_name} (not installed)")
            continue

        if is_kytchen_configured(client):
            print_info(f"Skipping {client.display_name} (already configured)")
            continue

        install_client(client, dry_run)
        print()


# =============================================================================
# CLI entry point
# =============================================================================

def print_usage() -> None:
    """Print CLI usage information."""
    print("""
Kytchen MCP Server Installer

Usage:
    kytchen-rlm install              Interactive mode - detect and configure clients
    kytchen-rlm install <client>     Configure a specific client
    kytchen-rlm install --all        Configure all detected clients
    kytchen-rlm uninstall <client>   Remove Kytchen from a client
    kytchen-rlm doctor               Verify installation

Clients:
    claude-desktop     Claude Desktop app
    cursor             Cursor editor (global config)
    cursor-project     Cursor editor (project config)
    windsurf           Windsurf editor
    vscode             VSCode (project config)
    claude-code        Claude Code CLI

Options:
    --dry-run          Preview changes without writing
    --help, -h         Show this help message

Examples:
    kytchen-rlm install                     # Interactive mode
    kytchen-rlm install claude-desktop      # Configure Claude Desktop
    kytchen-rlm install --all --dry-run     # Preview all installations
    kytchen-rlm uninstall cursor            # Remove from Cursor
    kytchen-rlm doctor                      # Check installation status
""")


def main() -> None:
    """CLI entry point."""
    # Show deprecation warning
    print_warning("DEPRECATED: kytchen-rlm is being replaced with the new Typer-based CLI")
    print_info("Use 'kytchen mcp install' instead of 'kytchen-rlm install'")
    print_info("This command will be removed in a future version\n")

    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h", "help"):
        print_usage()
        return

    dry_run = "--dry-run" in args
    if dry_run:
        args = [a for a in args if a != "--dry-run"]

    command = args[0] if args else ""

    if command == "doctor":
        success = doctor()
        sys.exit(0 if success else 1)

    elif command == "install":
        if len(args) == 1:
            # Interactive mode
            interactive_install(dry_run)
        elif args[1] == "--all":
            install_all(dry_run)
        elif args[1] in CLIENTS:
            client = CLIENTS[args[1]]
            success = install_client(client, dry_run)
            sys.exit(0 if success else 1)
        else:
            print_error(f"Unknown client: {args[1]}")
            print_info(f"Available clients: {', '.join(CLIENTS.keys())}")
            sys.exit(1)

    elif command == "uninstall":
        if len(args) < 2:
            print_error("Please specify a client to uninstall from")
            print_info(f"Available clients: {', '.join(CLIENTS.keys())}")
            sys.exit(1)

        client_name = args[1]
        if client_name not in CLIENTS:
            print_error(f"Unknown client: {client_name}")
            print_info(f"Available clients: {', '.join(CLIENTS.keys())}")
            sys.exit(1)

        client = CLIENTS[client_name]
        success = uninstall_client(client, dry_run)
        sys.exit(0 if success else 1)

    else:
        print_error(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
