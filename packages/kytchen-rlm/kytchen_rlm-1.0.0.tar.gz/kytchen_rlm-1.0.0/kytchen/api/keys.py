"""API key utilities for Kytchen Cloud.

Production stores only hashed keys. Plaintext keys are shown once at creation.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Final


KEY_PREFIX: Final[str] = "kyt_sk_"


@dataclass(frozen=True, slots=True)
class GeneratedKey:
    plaintext: str
    prefix: str
    key_hash: str


def generate_api_key() -> str:
    # 32 bytes -> 43ish base64url chars; plenty for uniqueness.
    return f"{KEY_PREFIX}{secrets.token_urlsafe(32)}"


def key_prefix(key: str, visible_chars: int = 8) -> str:
    if not key.startswith(KEY_PREFIX):
        return key[: max(0, visible_chars)]
    return key[: len(KEY_PREFIX) + max(0, visible_chars)]


def hash_api_key(key: str, pepper: str) -> str:
    # NOTE: This is a simple hash suitable for DB lookup; production can upgrade
    # to HMAC or argon2/bcrypt if desired, but fast lookup is useful for API keys.
    h = hashlib.sha256()
    h.update(pepper.encode("utf-8"))
    h.update(b"\x00")
    h.update(key.encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


def generate_and_hash_api_key(*, pepper: str) -> GeneratedKey:
    key = generate_api_key()
    return GeneratedKey(plaintext=key, prefix=key_prefix(key), key_hash=hash_api_key(key, pepper))

