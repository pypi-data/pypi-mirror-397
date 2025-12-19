"""Authentication commands for Kytchen CLI.

Handles login, logout, and authentication status for Kytchen Cloud.
"""

from __future__ import annotations

import sys

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
    print_panel,
    prompt,
)
from .utils.credentials import (
    get_api_key,
    set_api_key,
    delete_api_key,
    get_auth_token,
    set_auth_token,
    delete_auth_token,
    is_using_keyring,
)

import httpx
import os

app = typer.Typer(
    name="auth",
    help="Authentication management for Kytchen Cloud",
    no_args_is_help=True,
)


# =============================================================================
# Login command
# =============================================================================

@app.command(name="login")
def login_command(
    api_key: str = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API key (or enter interactively)",
    ),
    token: str = typer.Option(
        None,
        "--token",
        "-t",
        help="Auth token (alternative to API key)",
    ),
) -> None:
    """
    Log in to Kytchen Cloud.

    You can authenticate using either an API key or auth token:

    - API key: Get from https://kytchen.dev/dashboard/keys
    - Auth token: OAuth token from web login flow

    Examples:

        kytchen auth login
        kytchen auth login --api-key kyt_sk_...
        kytchen auth login --token kyt_tok_...
    """
    print_header("Kytchen Cloud Login", "Authenticate to use cloud features")

    # Check if already logged in
    existing_key = get_api_key()
    existing_token = get_auth_token()

    if existing_key or existing_token:
        print_warning("You are already logged in.")
        from .utils.output import confirm

        if not confirm("Do you want to login again?", default=False):
            print_info("Login cancelled")
            raise typer.Exit()

    # Get credentials
    if not api_key and not token:
        print_info("\nYou can authenticate using:")
        print_info("  1. API key from https://kytchen.dev/dashboard/keys")
        print_info("  2. Auth token from web login\n")

        choice = prompt("Choose authentication method", default="1")

        if choice == "1":
            api_key = prompt("Enter your API key", password=True)
            if not api_key:
                print_error("API key is required")
                raise typer.Exit(1)
        elif choice == "2":
            token = prompt("Enter your auth token", password=True)
            if not token:
                print_error("Auth token is required")
                raise typer.Exit(1)
        else:
            print_error("Invalid choice")
            raise typer.Exit(1)

    # Validate format
    if api_key:
        if not api_key.startswith("kyt_sk_"):
            print_error("Invalid API key format. Should start with 'kyt_sk_'")
            raise typer.Exit(1)

    if token:
        if not token.startswith("kyt_tok_"):
            print_error("Invalid token format. Should start with 'kyt_tok_'")
            raise typer.Exit(1)

    # Store credentials
    try:
        if api_key:
            set_api_key(api_key)
            print_success("API key stored securely")
        elif token:
            set_auth_token(token)
            print_success("Auth token stored securely")

        # Show storage location
        if is_using_keyring():
            print_info("Credentials stored in system keyring")
        else:
            print_warning("Keyring not available - using file-based storage")
            print_info("Consider installing keyring: pip install keyring")

        print_success("\nSuccessfully logged in to Kytchen Cloud")
        print_info("Run 'kytchen auth whoami' to verify your identity")

    except Exception as e:
        print_error(f"Failed to store credentials: {e}")
        raise typer.Exit(1)


# =============================================================================
# Logout command
# =============================================================================

@app.command(name="logout")
def logout_command(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Log out from Kytchen Cloud.

    Removes stored API keys and auth tokens from secure storage.

    Examples:

        kytchen auth logout
        kytchen auth logout --force
    """
    # Check if logged in
    has_key = get_api_key() is not None
    has_token = get_auth_token() is not None

    if not has_key and not has_token:
        print_warning("You are not logged in")
        raise typer.Exit()

    # Confirm logout
    if not force:
        from .utils.output import confirm

        if not confirm("Are you sure you want to log out?", default=False):
            print_info("Logout cancelled")
            raise typer.Exit()

    # Remove credentials
    try:
        if has_key:
            delete_api_key()
        if has_token:
            delete_auth_token()

        print_success("Successfully logged out from Kytchen Cloud")

    except Exception as e:
        print_error(f"Failed to remove credentials: {e}")
        raise typer.Exit(1)


# =============================================================================
# Whoami command
# =============================================================================

@app.command(name="whoami")
def whoami_command(
    show_token: bool = typer.Option(
        False,
        "--show-token",
        help="Show the actual API key/token (security risk!)",
    ),
) -> None:
    """
    Show current authentication status.

    Displays information about the currently logged-in user and
    which credentials are being used.

    Examples:

        kytchen auth whoami
        kytchen auth whoami --show-token
    """
    api_key = get_api_key()
    auth_token = get_auth_token()

    if not api_key and not auth_token:
        print_warning("Not logged in")
        print_info("\nTo log in, run: kytchen auth login")
        raise typer.Exit()

    print_header("Authentication Status")

    # Determine auth method
    if api_key:
        auth_method = "API Key"
        credential = api_key
    else:
        auth_method = "Auth Token"
        credential = auth_token

    # Show masked credential by default
    if show_token:
        display_cred = credential
        print_warning("Showing full credential - keep this secret!")
    else:
        # Show first 12 chars + last 4 chars
        if len(credential) > 20:
            display_cred = f"{credential[:12]}...{credential[-4:]}"
        else:
            display_cred = credential[:8] + "..."

    # Build info panel
    info_lines = [
        f"[cyan]Method:[/cyan] {auth_method}",
        f"[cyan]Credential:[/cyan] {display_cred}",
        f"[cyan]Storage:[/cyan] {'System Keyring' if is_using_keyring() else 'File-based'}",
    ]

    # Verify credentials against API
    api_url = os.getenv("KYTCHEN_API_URL", "https://api.kytchen.dev").rstrip("/")
    verified = False

    try:
        with httpx.Client(timeout=5.0) as client:
            headers = {"Authorization": f"Bearer {credential}"}
            response = client.get(f"{api_url}/v1/auth/whoami", headers=headers)

            if response.status_code == 200:
                data = response.json()
                verified = True
                workspace = data.get("workspace", {})

                info_lines.append(f"[cyan]Status:[/cyan] [green]Verified[/green]")
                info_lines.append(f"[cyan]Workspace ID:[/cyan] {workspace.get('id', 'Unknown')}")
                info_lines.append(f"[cyan]Plan:[/cyan] {workspace.get('plan', 'free')}")
            else:
                info_lines.append(f"[cyan]Status:[/cyan] [red]Failed ({response.status_code})[/red]")
                if response.status_code == 401:
                    info_lines.append(f"[red]Error:[/red] Invalid credentials")

    except Exception as e:
        info_lines.append(f"[cyan]Status:[/cyan] [yellow]Verification failed (Network Error)[/yellow]")
        info_lines.append(f"[yellow]Error:[/yellow] {str(e)}")

    print_panel("\n".join(info_lines), title="Current Credentials")

    if verified:
        print_info("\nYour credentials are valid and ready to use.")
    else:
        print_info("\nTo verify your credentials manually, try running a query:")
        print_info("  kytchen query 'What is 2+2?'")


# =============================================================================
# Helper to check if authenticated (for other commands)
# =============================================================================

def require_auth() -> str:
    """
    Check if user is authenticated and return API key.

    Raises:
        typer.Exit: If not authenticated

    Returns:
        API key or auth token
    """
    api_key = get_api_key()
    auth_token = get_auth_token()

    if not api_key and not auth_token:
        print_error("Not authenticated. Please log in first.")
        print_info("Run: kytchen auth login")
        raise typer.Exit(1)

    return api_key or auth_token


if __name__ == "__main__":
    app()
