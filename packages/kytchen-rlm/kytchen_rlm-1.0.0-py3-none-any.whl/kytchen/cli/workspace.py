"""Workspace management commands for Kytchen CLI.

Manages multiple workspaces for organizing projects.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

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
    print_table,
    confirm,
)

app = typer.Typer(
    name="workspace",
    help="Workspace management",
    no_args_is_help=True,
)

WORKSPACES_FILE = Path.home() / ".kytchen" / "workspaces.json"


def _load_workspaces() -> dict:
    """Load workspaces from file."""
    import json

    if not WORKSPACES_FILE.exists():
        return {"current": None, "workspaces": {}}

    try:
        with open(WORKSPACES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"current": None, "workspaces": {}}


def _save_workspaces(data: dict) -> None:
    """Save workspaces to file."""
    import json

    WORKSPACES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACES_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.command(name="list")
def list_command() -> None:
    """
    List all workspaces.

    Examples:

        kytchen workspace list
    """
    data = _load_workspaces()
    workspaces = data.get("workspaces", {})
    current = data.get("current")

    if not workspaces:
        print_warning("No workspaces configured")
        print_info("\nTo create a workspace, run:")
        print_info("  kytchen workspace create <name> <path>")
        raise typer.Exit()

    rows = []
    for name, path in workspaces.items():
        is_current = "✓" if name == current else ""
        rows.append([is_current, name, path])

    print_table(
        title="Workspaces",
        columns=[("Current", "green"), ("Name", "cyan"), ("Path", "blue")],
        rows=rows,
    )


@app.command(name="create")
def create_command(
    name: str = typer.Argument(..., help="Workspace name"),
    path: Optional[str] = typer.Argument(None, help="Workspace path (default: current directory)"),
) -> None:
    """
    Create a new workspace.

    Examples:

        kytchen workspace create myproject
        kytchen workspace create prod /path/to/prod
    """
    data = _load_workspaces()
    workspaces = data.get("workspaces", {})

    if name in workspaces:
        print_error(f"Workspace '{name}' already exists")
        raise typer.Exit(1)

    workspace_path = Path(path) if path else Path.cwd()
    workspace_path = workspace_path.resolve()

    if not workspace_path.exists():
        print_error(f"Path does not exist: {workspace_path}")
        raise typer.Exit(1)

    workspaces[name] = str(workspace_path)
    data["workspaces"] = workspaces

    # Set as current if it's the first workspace
    if not data.get("current"):
        data["current"] = name

    _save_workspaces(data)

    print_success(f"Created workspace '{name}' at {workspace_path}")


@app.command(name="switch")
def switch_command(
    name: str = typer.Argument(..., help="Workspace name"),
) -> None:
    """
    Switch to a workspace.

    Examples:

        kytchen workspace switch myproject
    """
    data = _load_workspaces()
    workspaces = data.get("workspaces", {})

    if name not in workspaces:
        print_error(f"Workspace '{name}' not found")
        print_info("\nAvailable workspaces:")
        for ws_name in workspaces:
            print_info(f"  {ws_name}")
        raise typer.Exit(1)

    data["current"] = name
    _save_workspaces(data)

    print_success(f"Switched to workspace '{name}'")
    print_info(f"Path: {workspaces[name]}")


@app.command(name="delete")
def delete_command(
    name: str = typer.Argument(..., help="Workspace name"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Delete a workspace.

    Note: This only removes the workspace reference, not the actual files.

    Examples:

        kytchen workspace delete myproject
        kytchen workspace delete old --force
    """
    data = _load_workspaces()
    workspaces = data.get("workspaces", {})

    if name not in workspaces:
        print_error(f"Workspace '{name}' not found")
        raise typer.Exit(1)

    if not force:
        if not confirm(f"Delete workspace '{name}'?", default=False):
            print_info("Deletion cancelled")
            raise typer.Exit()

    del workspaces[name]
    data["workspaces"] = workspaces

    # Clear current if deleting the current workspace
    if data.get("current") == name:
        data["current"] = None

    _save_workspaces(data)

    print_success(f"Deleted workspace '{name}'")
    print_info("Note: Files were not deleted, only the workspace reference")


@app.command(name="current")
def current_command() -> None:
    """
    Show the current workspace.

    Examples:

        kytchen workspace current
    """
    data = _load_workspaces()
    current = data.get("current")
    workspaces = data.get("workspaces", {})

    if not current or current not in workspaces:
        print_warning("No current workspace set")
        print_info("\nTo switch to a workspace, run:")
        print_info("  kytchen workspace switch <name>")
        raise typer.Exit()

    print_success(f"Current workspace: {current}")
    print_info(f"Path: {workspaces[current]}")


if __name__ == "__main__":
    app()
