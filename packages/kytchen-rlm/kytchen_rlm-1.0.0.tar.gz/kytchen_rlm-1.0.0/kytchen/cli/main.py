"""Main Typer application for Kytchen CLI.

This module defines the root CLI app and registers all command groups.
Inspired by Vercel's CLI design patterns.
"""

from __future__ import annotations

import sys
from typing import Optional

try:
    import typer
    from typer import Context
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import console, print_error, print_info

# Create the main Typer app
app = typer.Typer(
    name="kytchen",
    help="Kytchen - Production-grade Recursive Language Models (RLMs)",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


# =============================================================================
# Version callback
# =============================================================================

def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        try:
            from kytchen import __version__
            version = __version__
        except ImportError:
            version = "unknown"

        console.print(f"[bold cyan]Kytchen[/bold cyan] v{version}")
        console.print("https://kytchen.dev")
        raise typer.Exit()


@app.callback()
def main(
    ctx: Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    Kytchen - Production-grade Recursive Language Models (RLMs)

    Store context in a sandboxed Python REPL and let AI models write code
    to explore and process it. No more cramming context into prompts.
    """
    pass


# =============================================================================
# Command groups (registered in order)
# =============================================================================

# Import command groups lazily to avoid import overhead
def register_commands() -> None:
    """Register all command groups with the main app."""

    # Auth commands
    try:
        from .auth import app as auth_app
        app.add_typer(auth_app, name="auth", help="Authentication management")
    except ImportError:
        pass

    # Git commands
    try:
        from .git import app as git_app
        app.add_typer(git_app, name="git", help="Git commands")
    except ImportError:
        pass

    # Config commands
    try:
        from .config_cmd import app as config_app
        app.add_typer(config_app, name="config", help="Configuration management")
    except ImportError:
        pass

    # Init command
    try:
        from .init_cmd import init_command
        app.command(name="init", help="Initialize a new Kytchen project")(init_command)
    except ImportError:
        pass

    # Query commands
    try:
        from .query import query_command, run_command
        app.command(name="query", help="Execute a one-off query")(query_command)
        app.command(name="run", help="Run a kytchenfile")(run_command)
    except ImportError:
        pass

    # Export commands
    try:
        from .export_cmd import app as export_app
        app.add_typer(export_app, name="export", help="Export recipe results (sauce packs)")
    except ImportError:
        pass

    # MCP commands
    try:
        from .mcp import app as mcp_app
        app.add_typer(mcp_app, name="mcp", help="MCP server management")
    except ImportError:
        pass

    # Workspace commands
    try:
        from .workspace import app as workspace_app
        app.add_typer(workspace_app, name="workspace", help="Workspace management")
    except ImportError:
        pass

    # Keys commands
    try:
        from .keys import app as keys_app
        app.add_typer(keys_app, name="keys", help="API key management")
    except ImportError:
        pass

    # Doctor command
    try:
        from .doctor import doctor_command
        app.command(name="doctor", help="Diagnose Kytchen installation")(doctor_command)
    except ImportError:
        pass

    # Completion command
    try:
        from .completion import completion_command
        app.command(name="completion", help="Generate shell completion script")(completion_command)
    except ImportError:
        pass


# =============================================================================
# Main entry point
# =============================================================================

def cli_main() -> None:
    """Main entry point for the CLI."""
    try:
        # Register all commands
        register_commands()

        # Run the app
        app()
    except KeyboardInterrupt:
        print_info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
