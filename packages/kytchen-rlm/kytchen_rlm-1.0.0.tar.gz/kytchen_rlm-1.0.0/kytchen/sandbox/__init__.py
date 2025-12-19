"""Sandbox execution providers for Kytchen.

This module provides a protocol-based abstraction for sandboxed code execution.
Implementations include:
- LocalSandbox: In-process REPLEnvironment (best-effort security)
- E2BSandbox: Remote E2B sandbox (production-grade isolation)

Usage:
    from kytchen.sandbox import SandboxProvider, LocalSandbox, get_sandbox

    # Get appropriate sandbox based on environment
    sandbox = await get_sandbox(workspace_id="ws_123", config=config)

    # Execute code
    result = await sandbox.execute("print(ctx[:100])")

    # Clean up
    await sandbox.close()
"""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..types import ContextType, ExecutionResult


@dataclass(slots=True)
class SandboxConfig:
    """Configuration for sandbox providers."""

    # Execution limits
    timeout_seconds: float = 30.0
    max_output_chars: int = 10_000

    # Import allowlist
    allowed_imports: list[str] = field(default_factory=lambda: [
        "re", "json", "csv", "math", "statistics", "collections",
        "itertools", "functools", "datetime", "textwrap", "difflib",
        "random", "string", "hashlib", "base64", "urllib.parse", "html",
    ])

    # E2B-specific
    e2b_template: str = "base"
    e2b_timeout_seconds: int = 300  # Sandbox lifetime


@runtime_checkable
class SandboxProvider(Protocol):
    """Protocol for sandbox implementations.

    All sandbox providers must implement these methods to be used
    interchangeably by the Kytchen API.
    """

    async def load_context(self, context: ContextType, var_name: str = "ctx") -> None:
        """Load context into the sandbox namespace."""
        ...

    async def execute(self, code: str) -> ExecutionResult:
        """Execute code and return results."""
        ...

    async def get_variable(self, name: str) -> object | None:
        """Get a variable from the sandbox namespace."""
        ...

    async def set_variable(self, name: str, value: object) -> None:
        """Set a variable in the sandbox namespace."""
        ...

    async def close(self) -> None:
        """Clean up sandbox resources."""
        ...

    @property
    def sandbox_id(self) -> str:
        """Unique identifier for this sandbox instance."""
        ...


# Import implementations (deferred until after SandboxConfig is defined to avoid circular imports)
LocalSandbox = importlib.import_module(".local", __package__).LocalSandbox

# Conditional E2B import
_e2b_available = False
try:
    E2BSandbox = importlib.import_module(".e2b", __package__).E2BSandbox
    _e2b_available = True
except ImportError:
    E2BSandbox = None  # type: ignore[misc, assignment]


def is_e2b_available() -> bool:
    """Check if E2B SDK is installed."""
    return _e2b_available


def should_use_e2b() -> bool:
    """Determine if E2B should be used based on environment.

    E2B is used when:
    - E2B SDK is installed
    - E2B_API_KEY is set
    - KYTCHEN_DEV_MODE is not enabled
    """
    if not _e2b_available:
        return False
    if not os.getenv("E2B_API_KEY"):
        return False
    if os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes"):
        return False
    return True


async def get_sandbox(
    workspace_id: str,
    config: SandboxConfig | None = None,
    context: ContextType | None = None,
    force_local: bool = False,
) -> SandboxProvider:
    """Factory function to get appropriate sandbox provider.

    Args:
        workspace_id: Workspace ID for isolation/tracking
        config: Sandbox configuration
        context: Optional initial context to load
        force_local: Force local sandbox even if E2B is available

    Returns:
        A SandboxProvider instance ready for use
    """
    config = config or SandboxConfig()

    if not force_local and should_use_e2b():
        if E2BSandbox is None:
            raise RuntimeError("E2B requested but SDK not installed")
        sandbox = await E2BSandbox.create(
            workspace_id=workspace_id,
            config=config,
        )
    else:
        sandbox = LocalSandbox(
            workspace_id=workspace_id,
            config=config,
        )

    if context is not None:
        await sandbox.load_context(context)

    return sandbox


__all__ = [
    "SandboxConfig",
    "SandboxProvider",
    "LocalSandbox",
    "E2BSandbox",
    "get_sandbox",
    "is_e2b_available",
    "should_use_e2b",
]
