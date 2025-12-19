"""Configuration management commands for Kytchen CLI.

Provides commands to view and modify configuration at global and project levels.
"""

from __future__ import annotations

import sys
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
    print_header,
    print_table,
    print_json,
)
from .utils.config_loader import (
    find_global_config,
    find_project_config,
    load_global_config,
    load_project_config,
    load_merged_config,
    get_config_value,
    set_config_value,
    delete_config_value,
)

app = typer.Typer(
    name="config",
    help="Configuration management",
    no_args_is_help=True,
)


# =============================================================================
# List command
# =============================================================================

@app.command(name="list")
def list_command(
    global_only: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Show only global config",
    ),
    project_only: bool = typer.Option(
        False,
        "--project",
        "-p",
        help="Show only project config",
    ),
    merged: bool = typer.Option(
        False,
        "--merged",
        "-m",
        help="Show merged config (default)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output as JSON",
    ),
) -> None:
    """
    List all configuration values.

    Shows configuration from global (~/.kytchen/config.yaml) and/or
    project (./kytchenfile.yaml) config files.

    Examples:

        kytchen config list
        kytchen config list --global
        kytchen config list --project
        kytchen config list --merged --json
    """
    if global_only and project_only:
        print_error("Cannot use both --global and --project")
        raise typer.Exit(1)

    # Determine which configs to show
    if global_only:
        config = load_global_config()
        source = "Global"
        path = find_global_config()
    elif project_only:
        config = load_project_config()
        source = "Project"
        path = find_project_config()
    else:
        config = load_merged_config()
        source = "Merged"
        path = None

    if not config:
        if path:
            print_warning(f"No configuration found at: {path}")
        else:
            print_warning("No configuration found")
        print_info("\nTo create a config file, run:")
        if global_only:
            print_info("  kytchen config set <key> <value> --global")
        else:
            print_info("  kytchen init")
        raise typer.Exit()

    # Output
    if json_output:
        print_json(config)
    else:
        print_header(f"{source} Configuration", str(path) if path else "Multiple sources")

        # Flatten config for table display
        rows = []

        def flatten(d: dict, prefix: str = "") -> None:
            for key, value in d.items():
                full_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, dict):
                    flatten(value, f"{full_key}.")
                else:
                    rows.append([full_key, str(value)])

        flatten(config)

        if rows:
            print_table(
                title="",
                columns=[("Key", "cyan"), ("Value", "green")],
                rows=rows,
            )
        else:
            print_warning("Configuration is empty")


# =============================================================================
# Get command
# =============================================================================

@app.command(name="get")
def get_command(
    key: str = typer.Argument(..., help="Configuration key (supports dot notation)"),
    default: Optional[str] = typer.Option(
        None,
        "--default",
        "-d",
        help="Default value if key not found",
    ),
    no_env: bool = typer.Option(
        False,
        "--no-env",
        help="Don't check environment variables",
    ),
) -> None:
    """
    Get a configuration value.

    Supports dot notation for nested keys (e.g., "provider.model").

    Precedence (highest to lowest):
    1. Environment variable (KYTCHEN_<KEY>)
    2. Project config
    3. Global config
    4. Default value

    Examples:

        kytchen config get provider
        kytchen config get max_cost_usd --default 5.0
        kytchen config get provider.model --no-env
    """
    value = get_config_value(key, default=default, use_env=not no_env)

    if value is None:
        print_error(f"Configuration key not found: {key}")
        print_info("\nTo set this value, run:")
        print_info(f"  kytchen config set {key} <value>")
        raise typer.Exit(1)

    # Output the value
    if isinstance(value, (dict, list)):
        print_json(value)
    else:
        print(value)


# =============================================================================
# Set command
# =============================================================================

@app.command(name="set")
def set_command(
    key: str = typer.Argument(..., help="Configuration key (supports dot notation)"),
    value: str = typer.Argument(..., help="Value to set"),
    global_config: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Set in global config instead of project config",
    ),
    type_hint: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Value type (string, int, float, bool, json)",
    ),
) -> None:
    """
    Set a configuration value.

    Supports dot notation for nested keys (e.g., "provider.model").

    By default, sets in project config. Use --global to set in global config.

    Examples:

        kytchen config set provider anthropic
        kytchen config set max_cost_usd 10.0 --type float
        kytchen config set root_model claude-sonnet-4 --global
        kytchen config set enable_caching true --type bool
    """
    # Parse value based on type hint
    parsed_value: str | int | float | bool | dict | list

    if type_hint == "int":
        try:
            parsed_value = int(value)
        except ValueError:
            print_error(f"Invalid integer value: {value}")
            raise typer.Exit(1)
    elif type_hint == "float":
        try:
            parsed_value = float(value)
        except ValueError:
            print_error(f"Invalid float value: {value}")
            raise typer.Exit(1)
    elif type_hint == "bool":
        parsed_value = value.lower() in ("true", "1", "yes", "y")
    elif type_hint == "json":
        import json

        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON value: {e}")
            raise typer.Exit(1)
    else:
        # Auto-detect type
        if value.lower() in ("true", "false"):
            parsed_value = value.lower() == "true"
        elif value.isdigit():
            parsed_value = int(value)
        else:
            try:
                parsed_value = float(value)
            except ValueError:
                parsed_value = value

    # Set the value
    try:
        set_config_value(key, parsed_value, global_config=global_config)

        scope = "global" if global_config else "project"
        print_success(f"Set {key} = {parsed_value} ({scope} config)")

        # Show where it was saved
        if global_config:
            path = find_global_config()
        else:
            path = find_project_config()

        if path:
            print_info(f"Saved to: {path}")

    except Exception as e:
        print_error(f"Failed to set config value: {e}")
        raise typer.Exit(1)


# =============================================================================
# Delete command
# =============================================================================

@app.command(name="delete")
def delete_command(
    key: str = typer.Argument(..., help="Configuration key to delete"),
    global_config: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Delete from global config instead of project config",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Delete a configuration value.

    Supports dot notation for nested keys (e.g., "provider.model").

    Examples:

        kytchen config delete max_tokens
        kytchen config delete provider.model --global
        kytchen config delete old_key --force
    """
    # Confirm deletion
    if not force:
        from .utils.output import confirm

        scope = "global" if global_config else "project"
        if not confirm(f"Delete '{key}' from {scope} config?", default=False):
            print_info("Deletion cancelled")
            raise typer.Exit()

    # Delete the value
    success = delete_config_value(key, global_config=global_config)

    if success:
        scope = "global" if global_config else "project"
        print_success(f"Deleted '{key}' from {scope} config")
    else:
        print_error(f"Configuration key not found: {key}")
        raise typer.Exit(1)


# =============================================================================
# Path command
# =============================================================================

@app.command(name="path")
def path_command(
    global_config: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Show global config path",
    ),
) -> None:
    """
    Show the path to the configuration file.

    Examples:

        kytchen config path
        kytchen config path --global
    """
    if global_config:
        path = find_global_config()
        scope = "Global"
    else:
        path = find_project_config()
        scope = "Project"

    if path:
        print_success(f"{scope} config: {path}")
    else:
        print_warning(f"No {scope.lower()} config file found")
        print_info("\nTo create a config file, run:")
        if global_config:
            print_info("  kytchen config set <key> <value> --global")
        else:
            print_info("  kytchen init")


if __name__ == "__main__":
    app()
