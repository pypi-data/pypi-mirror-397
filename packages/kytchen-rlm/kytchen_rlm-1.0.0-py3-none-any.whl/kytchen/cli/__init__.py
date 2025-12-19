"""Kytchen CLI - Vercel-style developer experience.

This package provides the new Typer-based CLI for Kytchen v1.0.

Command Structure:
    kytchen auth (login, logout, whoami)
    kytchen init
    kytchen config (list, get, set, delete)
    kytchen query "..." [--context]
    kytchen run [--watch]
    kytchen mcp (install, uninstall, doctor)
    kytchen workspace (list, switch, create)
    kytchen keys (list, create, revoke)
    kytchen doctor
"""

from __future__ import annotations

__all__ = ["cli"]

# Lazy import to avoid import overhead
def cli() -> None:
    """Main CLI entry point."""
    from .main import app
    app()
