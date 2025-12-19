"""MCP server integration - Kytchen Prep Station.

Too many cooks in the kitchen? Let us handle the prep.

The MCP server is an optional feature. Install with:

    pip install kytchen[mcp]

Then run:

    # Thick client - API-free mode (host AI provides reasoning)
    python -m kytchen.mcp.local_server
    # or
    kytchen-local

    # Thin client - Cloud mode (connects to api.kytchen.dev)
    kytchen
"""

from .cloud_client import KytchenCloudMCPServer
from .server import KytchenMCPServer
from .local_server import KytchenMCPServerLocal

__all__ = [
    "KytchenCloudMCPServer",
    "KytchenMCPServer",
    "KytchenMCPServerLocal",
]
