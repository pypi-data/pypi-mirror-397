"""Secure credential storage using system keyring.

Stores API keys and auth tokens securely using the system's credential manager:
- macOS: Keychain
- Windows: Credential Vault
- Linux: Secret Service (gnome-keyring, kwallet, etc.)

Falls back to file-based storage if keyring is unavailable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Try to import keyring, fall back to file-based storage
try:
    import keyring
    import keyring.errors

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    keyring = None

SERVICE_NAME = "kytchen"
FALLBACK_DIR = Path.home() / ".kytchen"
FALLBACK_FILE = FALLBACK_DIR / "credentials.json"


# =============================================================================
# Keyring-based storage (preferred)
# =============================================================================

def _keyring_get(key: str) -> str | None:
    """Get a credential from system keyring."""
    if not KEYRING_AVAILABLE or not keyring:
        return None

    try:
        return keyring.get_password(SERVICE_NAME, key)
    except keyring.errors.KeyringError:
        return None


def _keyring_set(key: str, value: str) -> bool:
    """Store a credential in system keyring."""
    if not KEYRING_AVAILABLE or not keyring:
        return False

    try:
        keyring.set_password(SERVICE_NAME, key, value)
        return True
    except keyring.errors.KeyringError:
        return False


def _keyring_delete(key: str) -> bool:
    """Delete a credential from system keyring."""
    if not KEYRING_AVAILABLE or not keyring:
        return False

    try:
        keyring.delete_password(SERVICE_NAME, key)
        return True
    except keyring.errors.KeyringError:
        return False


# =============================================================================
# File-based storage (fallback)
# =============================================================================

def _load_fallback_credentials() -> dict[str, Any]:
    """Load credentials from fallback file."""
    if not FALLBACK_FILE.exists():
        return {}

    try:
        with open(FALLBACK_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_fallback_credentials(creds: dict[str, Any]) -> None:
    """Save credentials to fallback file."""
    FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

    # Set restrictive permissions (owner read/write only)
    with open(FALLBACK_FILE, "w") as f:
        json.dump(creds, f, indent=2)

    # Make file readable/writable by owner only
    try:
        os.chmod(FALLBACK_FILE, 0o600)
    except OSError:
        pass  # Best effort on Windows


def _fallback_get(key: str) -> str | None:
    """Get a credential from fallback storage."""
    creds = _load_fallback_credentials()
    return creds.get(key)


def _fallback_set(key: str, value: str) -> None:
    """Store a credential in fallback storage."""
    creds = _load_fallback_credentials()
    creds[key] = value
    _save_fallback_credentials(creds)


def _fallback_delete(key: str) -> None:
    """Delete a credential from fallback storage."""
    creds = _load_fallback_credentials()
    if key in creds:
        del creds[key]
        _save_fallback_credentials(creds)


# =============================================================================
# Public API
# =============================================================================

def get_credential(key: str) -> str | None:
    """
    Get a credential from secure storage.

    Args:
        key: Credential key (e.g., "api_key", "auth_token")

    Returns:
        Credential value or None if not found
    """
    # Try keyring first
    value = _keyring_get(key)
    if value is not None:
        return value

    # Fall back to file-based storage
    return _fallback_get(key)


def set_credential(key: str, value: str) -> None:
    """
    Store a credential securely.

    Args:
        key: Credential key (e.g., "api_key", "auth_token")
        value: Credential value to store
    """
    # Try keyring first
    if _keyring_set(key, value):
        return

    # Fall back to file-based storage
    _fallback_set(key, value)


def delete_credential(key: str) -> None:
    """
    Delete a credential from secure storage.

    Args:
        key: Credential key to delete
    """
    # Try keyring first
    if _keyring_delete(key):
        return

    # Fall back to file-based storage
    _fallback_delete(key)


def has_credential(key: str) -> bool:
    """
    Check if a credential exists.

    Args:
        key: Credential key to check

    Returns:
        True if credential exists, False otherwise
    """
    return get_credential(key) is not None


def list_credentials() -> list[str]:
    """
    List all stored credential keys.

    Returns:
        List of credential keys
    """
    # For keyring, we can't enumerate keys, so we check fallback only
    creds = _load_fallback_credentials()
    return list(creds.keys())


def is_using_keyring() -> bool:
    """
    Check if system keyring is available and being used.

    Returns:
        True if keyring is available, False if using fallback storage
    """
    return KEYRING_AVAILABLE


# =============================================================================
# Specific credential helpers
# =============================================================================

def get_api_key() -> str | None:
    """Get the stored Kytchen API key."""
    return get_credential("api_key")


def set_api_key(api_key: str) -> None:
    """Store the Kytchen API key."""
    set_credential("api_key", api_key)


def delete_api_key() -> None:
    """Delete the stored Kytchen API key."""
    delete_credential("api_key")


def get_auth_token() -> str | None:
    """Get the stored auth token."""
    return get_credential("auth_token")


def set_auth_token(token: str) -> None:
    """Store the auth token."""
    set_credential("auth_token", token)


def delete_auth_token() -> None:
    """Delete the stored auth token."""
    delete_credential("auth_token")
