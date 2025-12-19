"""API Client for Kytchen Cloud.

Handles communication with the Kytchen API.
"""
from __future__ import annotations

import os
import requests
from typing import Any, Dict, Optional

DEFAULT_API_URL = "https://api.kytchen.dev"

class KytchenClient:
    def __init__(self, api_key: str, api_url: Optional[str] = None):
        self.api_key = api_key
        self.api_url = (api_url or os.getenv("KYTCHEN_API_URL", DEFAULT_API_URL)).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "kytchen-cli/1.0.0"
        })

    def revoke_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke an API key."""
        url = f"{self.api_url}/v1/keys/{key_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()
