"""Rich-based output utilities for Kytchen CLI.

Provides consistent, beautiful output with fallback to plain text when Rich is unavailable.
Inspired by Vercel CLI's output patterns.
"""

from __future__ import annotations

import sys
from typing import Any

# Try to import Rich, fall back to plain text
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
    Panel = None
    Table = None
    Progress = None
    Syntax = None
    Markdown = None


# =============================================================================
# Basic output functions
# =============================================================================

def print_success(msg: str) -> None:
    """Print success message in green."""
    if RICH_AVAILABLE:
        console.print(f"✓ [green]{msg}[/green]")
    else:
        print(f"✓ SUCCESS: {msg}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    if RICH_AVAILABLE:
        # rich.Console.print does not accept 'file' argument.
        # It prints to stdout by default, or stderr if stderr=True in Console constructor.
        # Here we assume the console was created with default args.
        # If we want to print to stderr, we should use sys.stderr explicitly or create another console.
        # But for now, let's just remove the invalid argument as 'file' is not a valid kwarg for console.print.
        console.print(f"✗ [red]{msg}[/red]")
    else:
        print(f"✗ ERROR: {msg}", file=sys.stderr)


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    if RICH_AVAILABLE:
        console.print(f"⚠ [yellow]{msg}[/yellow]")
    else:
        print(f"⚠ WARNING: {msg}")


def print_info(msg: str) -> None:
    """Print info message in blue."""
    if RICH_AVAILABLE:
        console.print(f"[blue]{msg}[/blue]")
    else:
        print(msg)


def print_dim(msg: str) -> None:
    """Print dimmed/muted text."""
    if RICH_AVAILABLE:
        console.print(f"[dim]{msg}[/dim]")
    else:
        print(f"  {msg}")


# =============================================================================
# Structured output
# =============================================================================

def print_header(title: str, subtitle: str | None = None) -> None:
    """Print a styled header."""
    if RICH_AVAILABLE:
        if subtitle:
            content = f"[bold]{title}[/bold]\n[dim]{subtitle}[/dim]"
        else:
            content = f"[bold]{title}[/bold]"
        console.print(Panel(content, style="cyan", expand=False))
    else:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        if subtitle:
            print(f"  {subtitle}")
        print(f"{'=' * 60}\n")


def print_panel(content: str, title: str | None = None, style: str = "cyan") -> None:
    """Print content in a panel."""
    if RICH_AVAILABLE:
        console.print(Panel(content, title=title, style=style, expand=False))
    else:
        if title:
            print(f"\n{title}")
        print("-" * 60)
        print(content)
        print("-" * 60)


def print_table(
    title: str,
    columns: list[tuple[str, str]],  # [(name, style), ...]
    rows: list[list[str]],
    show_header: bool = True,
) -> None:
    """Print a formatted table."""
    if RICH_AVAILABLE:
        table = Table(title=title, show_header=show_header)
        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)
        for row in rows:
            table.add_row(*row)
        console.print(table)
    else:
        # Plain text fallback
        if title:
            print(f"\n{title}")
        print("-" * 80)

        if show_header:
            header = " | ".join(col_name for col_name, _ in columns)
            print(header)
            print("-" * 80)

        for row in rows:
            print(" | ".join(str(cell) for cell in row))

        print()


def print_code(code: str, language: str = "python", title: str | None = None) -> None:
    """Print syntax-highlighted code."""
    if RICH_AVAILABLE:
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        if title:
            console.print(Panel(syntax, title=title, expand=False))
        else:
            console.print(syntax)
    else:
        if title:
            print(f"\n{title}")
            print("-" * 60)
        print(code)
        if title:
            print("-" * 60)


def print_markdown(content: str) -> None:
    """Print markdown content."""
    if RICH_AVAILABLE:
        console.print(Markdown(content))
    else:
        print(content)


def print_json(data: dict[str, Any]) -> None:
    """Print formatted JSON."""
    import json

    if RICH_AVAILABLE:
        console.print_json(json.dumps(data))
    else:
        print(json.dumps(data, indent=2))


# =============================================================================
# Interactive elements
# =============================================================================

def confirm(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    default_str = "Y/n" if default else "y/N"

    if RICH_AVAILABLE:
        response = console.input(f"[yellow]?[/yellow] {message} [{default_str}]: ")
    else:
        response = input(f"? {message} [{default_str}]: ")

    response = response.strip().lower()

    if not response:
        return default

    return response in ("y", "yes")


def prompt(message: str, default: str | None = None, password: bool = False) -> str:
    """Prompt for user input."""
    default_display = f" [{default}]" if default else ""

    if RICH_AVAILABLE:
        if password:
            value = console.input(f"[yellow]?[/yellow] {message}{default_display}: ", password=True)
        else:
            value = console.input(f"[yellow]?[/yellow] {message}{default_display}: ")
    else:
        if password:
            import getpass
            value = getpass.getpass(f"? {message}{default_display}: ")
        else:
            value = input(f"? {message}{default_display}: ")

    return value.strip() or (default or "")


# =============================================================================
# Progress indicators
# =============================================================================

class Spinner:
    """Context manager for showing a spinner during long operations."""

    def __init__(self, message: str):
        self.message = message
        self.progress = None
        self.task = None

    def __enter__(self) -> Spinner:
        if RICH_AVAILABLE:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            )
            self.progress.start()
            self.task = self.progress.add_task(self.message, total=None)
        else:
            print(f"{self.message}...", end="", flush=True)
        return self

    def __exit__(self, *args: Any) -> None:
        if RICH_AVAILABLE and self.progress:
            self.progress.stop()
        else:
            print(" done")

    def update(self, message: str) -> None:
        """Update spinner message."""
        if RICH_AVAILABLE and self.progress and self.task is not None:
            self.progress.update(self.task, description=message)
        else:
            print(f"\n{message}...", end="", flush=True)


# =============================================================================
# Utility functions
# =============================================================================

def clear_line() -> None:
    """Clear the current line."""
    if RICH_AVAILABLE:
        console.control("\r\033[K")
    else:
        print("\r" + " " * 80 + "\r", end="", flush=True)


def rule(title: str | None = None, style: str = "dim") -> None:
    """Print a horizontal rule."""
    if RICH_AVAILABLE:
        from rich.rule import Rule
        console.print(Rule(title, style=style))
    else:
        if title:
            print(f"\n{'-' * 30} {title} {'-' * 30}\n")
        else:
            print("-" * 80)
