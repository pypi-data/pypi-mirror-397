"""Diagnostic command for Kytchen CLI.

Verifies installation and diagnoses issues.
"""

from __future__ import annotations

import shutil

from .utils.output import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    print_table,
)
from .mcp import CLIENTS, is_client_installed, is_kytchen_configured


def doctor_command() -> None:
    """
    Diagnose Kytchen installation.

    Checks:
    - Entry points (kytchen, kytchen-local commands)
    - Dependencies (MCP package)
    - MCP client configurations
    - Module imports

    Examples:

        kytchen doctor
    """
    print_header("Kytchen Doctor", "Verifying installation and configuration")

    all_ok = True

    # Check entry points
    print_info("Checking entry points...")
    if shutil.which("kytchen") and shutil.which("kytchen-local"):
        print_success("kytchen and kytchen-local are in PATH")
    elif shutil.which("kytchen-local"):
        print_warning("kytchen-local is in PATH, but kytchen is not")
        all_ok = False
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

    # Check Rich dependency
    print_info("\nChecking Rich dependency...")
    try:
        import rich  # noqa: F401

        print_success("Rich package is installed")
    except ImportError:
        print_warning("Rich package not installed (optional)")
        print_info("Install with: pip install 'kytchen[rich]' for better output")

    # Check Typer dependency
    print_info("\nChecking Typer dependency...")
    try:
        import typer  # noqa: F401

        print_success("Typer package is installed")
    except ImportError:
        print_error("Typer package not installed")
        print_info("Install with: pip install 'kytchen[cli]'")
        all_ok = False

    # Check each MCP client
    print_info("\nChecking MCP client configurations...")
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

    print_table(
        title="MCP Client Status",
        columns=[("Client", "cyan"), ("Status", "green"), ("Path", "blue")],
        rows=rows,
    )

    # Test MCP server startup
    print_info("\nTesting MCP server module...")
    try:
        import kytchen.mcp.local_server  # noqa: F401

        print_success("Kytchen MCP server module loads correctly")
    except ImportError as e:
        print_error(f"Failed to import MCP server: {e}")
        all_ok = False

    # Test core Kytchen module
    print_info("\nTesting core Kytchen module...")
    try:
        import kytchen  # noqa: F401

        print_success("Kytchen core module loads correctly")
    except ImportError as e:
        print_error(f"Failed to import Kytchen: {e}")
        all_ok = False

    # Check config files
    print_info("\nChecking config files...")
    from .utils.config_loader import find_global_config, find_project_config

    global_config = find_global_config()
    if global_config:
        print_success(f"Global config found: {global_config}")
    else:
        print_info("No global config found (this is OK)")

    project_config = find_project_config()
    if project_config:
        print_success(f"Project config found: {project_config}")
    else:
        print_info("No project config found (this is OK)")

    # Final verdict
    print()
    if all_ok:
        print_success("All checks passed!")
    else:
        print_error("Some checks failed. See above for details.")
        raise typer.Exit(1)


if __name__ == "__main__":
    doctor_command()
