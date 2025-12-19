"""Local sandbox provider wrapping REPLEnvironment.

This sandbox runs code in-process with best-effort security:
- AST validation blocks unsafe constructs
- Import allowlist restricts module access
- Execution timeout prevents infinite loops

NOT suitable for untrusted code without additional isolation (containers, etc.).
"""

from __future__ import annotations

import asyncio
import uuid
from typing import TYPE_CHECKING

from ..repl.sandbox import REPLEnvironment, SandboxConfig as REPLSandboxConfig
from ..types import ExecutionResult

if TYPE_CHECKING:
    from ..types import ContextType
    from . import SandboxConfig


class LocalSandbox:
    """Local in-process sandbox using REPLEnvironment.

    This implementation wraps the existing REPLEnvironment class to conform
    to the SandboxProvider protocol. All execution happens in the same
    process with best-effort sandboxing.

    Attributes:
        workspace_id: Workspace this sandbox belongs to
        config: Sandbox configuration
    """

    def __init__(
        self,
        workspace_id: str,
        config: SandboxConfig | None = None,
    ) -> None:
        from . import SandboxConfig as SandboxConfigClass

        self.workspace_id = workspace_id
        self.config = config or SandboxConfigClass()
        self._sandbox_id = f"local-{uuid.uuid4().hex[:12]}"
        self._repl: REPLEnvironment | None = None
        self._context_loaded = False

    @property
    def sandbox_id(self) -> str:
        """Unique identifier for this sandbox instance."""
        return self._sandbox_id

    def _ensure_repl(self, context: ContextType | None = None) -> REPLEnvironment:
        """Ensure REPL environment exists, creating if needed."""
        if self._repl is None:
            # Convert our config to REPL config
            repl_config = REPLSandboxConfig(
                allowed_imports=list(self.config.allowed_imports),
                max_output_chars=self.config.max_output_chars,
                timeout_seconds=self.config.timeout_seconds,
                enable_code_execution=True,
            )
            # Initialize with empty string if no context
            initial_context = context if context is not None else ""
            self._repl = REPLEnvironment(
                context=initial_context,
                context_var_name="ctx",
                config=repl_config,
            )
        return self._repl

    async def load_context(self, context: ContextType, var_name: str = "ctx") -> None:
        """Load context into the sandbox namespace.

        Args:
            context: The context data to load (string, dict, list, etc.)
            var_name: Variable name to bind context to (default: "ctx")
        """
        repl = self._ensure_repl(context)

        # Set the context variable
        repl.set_variable(var_name, context)
        self._context_loaded = True

    async def execute(self, code: str) -> ExecutionResult:
        """Execute code in the sandbox.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult with stdout, stderr, return value, etc.
        """
        repl = self._ensure_repl()

        # Run in thread pool to avoid blocking
        return await repl.execute_async(code)

    async def get_variable(self, name: str) -> object | None:
        """Get a variable from the sandbox namespace.

        Args:
            name: Variable name to retrieve

        Returns:
            Variable value or None if not found
        """
        repl = self._ensure_repl()
        return repl.get_variable(name)

    async def set_variable(self, name: str, value: object) -> None:
        """Set a variable in the sandbox namespace.

        Args:
            name: Variable name
            value: Value to set
        """
        repl = self._ensure_repl()
        repl.set_variable(name, value)

    async def close(self) -> None:
        """Clean up sandbox resources.

        For local sandbox, this just clears references.
        """
        self._repl = None
        self._context_loaded = False

    def inject_sub_query(self, fn: object) -> None:
        """Inject sub_query function into the sandbox.

        Args:
            fn: The sub_query function to inject
        """
        repl = self._ensure_repl()
        repl.inject_sub_query(fn)  # type: ignore[arg-type]

    def inject_sub_kytchen(self, fn: object) -> None:
        """Inject sub_kytchen function into the sandbox.

        Args:
            fn: The sub_kytchen function to inject
        """
        repl = self._ensure_repl()
        repl.inject_sub_kytchen(fn)  # type: ignore[arg-type]

    def set_loop(self, loop: asyncio.AbstractEventLoop | None) -> None:
        """Set event loop for async bridge (sub_query calls).

        Args:
            loop: Event loop to use for bridging async calls
        """
        repl = self._ensure_repl()
        repl.set_loop(loop)

    def get_evidence(self) -> list[object]:
        """Get collected evidence/citations from the sandbox."""
        repl = self._ensure_repl()
        return list(repl._evidence)

    def clear_evidence(self) -> None:
        """Clear collected evidence/citations."""
        repl = self._ensure_repl()
        repl._evidence.clear()
        repl._citations.clear()
