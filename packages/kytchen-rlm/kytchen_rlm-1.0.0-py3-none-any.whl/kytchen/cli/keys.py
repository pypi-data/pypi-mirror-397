"""API key management commands for Kytchen CLI.

Manages API keys for Kytchen Cloud.
"""

from __future__ import annotations

import sys
import asyncio

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from kytchen_sdk import KytchenClient, KytchenError
from .utils.output import (
    print_info,
    print_warning,
    print_header,
    print_error,
    print_success,
    print_table,
    print_panel,
    Spinner,
)
from .auth import require_auth
from .utils.api_client import KytchenClient

app = typer.Typer(
    name="keys",
    help="API key management for Kytchen Cloud",
    no_args_is_help=True,
)


@app.command(name="list")
def list_command() -> None:
    """
    List API keys for your account.

    Requires authentication.

    Examples:

        kytchen keys list
    """
    # Ensure authenticated
    api_key = require_auth()

    print_header("API Keys", "Manage your Kytchen Cloud API keys")

    async def _list_keys():
        try:
            with Spinner("Fetching API keys"):
                async with KytchenClient(api_key=api_key) as client:
                    keys = await client.keys.list()

            if not keys:
                print_info("No API keys found.")
                return

            rows = []
            for k in keys:
                status = "[green]Active[/green]"
                if k.expires_at:
                    # TODO: Check expiration date
                    pass

                rows.append([
                    k.name,
                    f"{k.prefix}...",
                    k.created_at[:10], # Show date only
                    k.last_used_at[:10] if k.last_used_at else "-",
                    k.expires_at[:10] if k.expires_at else "Never",
                    k.id,
                ])

            print_table(
                "Your API Keys",
                [
                    ("Name", "cyan"),
                    ("Prefix", "white"),
                    ("Created", "dim"),
                    ("Last Used", "dim"),
                    ("Expires", "yellow"),
                    ("ID", "dim"),
                ],
                rows
            )

            print_info("\nManage keys at: https://kytchen.dev/dashboard/keys")

        except KytchenError as e:
            print_error(f"Failed to fetch keys: {e}")
            raise typer.Exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            raise typer.Exit(1)

    asyncio.run(_list_keys())


@app.command(name="create")
def create_command(
    name: str = typer.Argument(..., help="Key name/description"),
    expires_in: int = typer.Option(
        90,
        "--expires-in",
        "-e",
        help="Days until expiration (0 for no expiration)",
    ),
) -> None:
    """
    Create a new API key.

    Requires authentication.

    Examples:

        kytchen keys create "Production Server"
        kytchen keys create "Development" --expires-in 30
        kytchen keys create "CI/CD" --expires-in 0
    """
    # Ensure authenticated
    api_key = require_auth()

    print_header("Create API Key", f"Creating key: {name}")

    async def _create_key():
        try:
            with Spinner("Creating API key"):
                async with KytchenClient(api_key=api_key) as client:
                    result = await client.keys.create(name=name, expires_in=expires_in)

            secret_key = result.get("secret_key")
            key_id = result.get("id")

            print_success(f"API key created successfully! (ID: {key_id})")
            print_warning("Make sure to copy your new API key now. You won't be able to see it again!")

            print_panel(
                f"[bold green]{secret_key}[/bold green]",
                title="API Key",
                style="green"
            )

        except KytchenError as e:
            print_error(f"Failed to create key: {e}")
            raise typer.Exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            raise typer.Exit(1)

    asyncio.run(_create_key())


@app.command(name="revoke")
def revoke_command(
    key_id: str = typer.Argument(..., help="Key ID to revoke"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Revoke an API key.

    Requires authentication.

    Examples:

        kytchen keys revoke kyt_sk_abc123
        kytchen keys revoke kyt_sk_xyz789 --force
    """
    # Ensure authenticated
    api_key = require_auth()

    # Confirm revocation
    if not force:
        from .utils.output import confirm

        if not confirm(f"Revoke API key {key_id}?", default=False):
            print_info("Revocation cancelled")
            raise typer.Exit()

    print_header("Revoke API Key", f"Revoking: {key_id}")

    async def _revoke_key():
        try:
            with Spinner(f"Revoking key {key_id}"):
                async with KytchenClient(api_key=api_key) as client:
                    await client.keys.revoke(key_id=key_id)

            print_success(f"API key {key_id} revoked successfully")

        except KytchenError as e:
            print_error(f"Failed to revoke key: {e}")
            raise typer.Exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            raise typer.Exit(1)

    asyncio.run(_revoke_key())


if __name__ == "__main__":
    app()
