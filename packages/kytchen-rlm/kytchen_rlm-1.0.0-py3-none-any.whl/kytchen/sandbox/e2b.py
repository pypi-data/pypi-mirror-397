"""E2B sandbox provider for production-grade isolation.

This sandbox runs code in a remote E2B environment, providing:
- Complete process isolation
- Network isolation (configurable)
- Resource limits enforced at VM level
- No local filesystem access

Requires: pip install e2b-code-interpreter
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..types import ContextType
    from . import SandboxConfig

# Import E2B SDK - this will fail gracefully if not installed
try:
    from e2b_code_interpreter import Sandbox as E2BSandboxSDK
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    E2BSandboxSDK = None  # type: ignore[misc, assignment]

from ..types import ExecutionResult


@dataclass(slots=True)
class E2BExecutionError:
    """Error from E2B execution."""
    name: str
    value: str
    traceback: str


class E2BSandbox:
    """E2B remote sandbox for production-grade isolation.

    This implementation uses the E2B Code Interpreter SDK to run code
    in a remote sandboxed environment. Each sandbox is isolated and
    automatically cleaned up after the timeout.

    Attributes:
        workspace_id: Workspace this sandbox belongs to
        config: Sandbox configuration
    """

    def __init__(
        self,
        workspace_id: str,
        config: SandboxConfig,
        e2b_sandbox: E2BSandboxSDK,
        sandbox_id: str,
    ) -> None:
        """Private constructor - use create() instead."""
        self.workspace_id = workspace_id
        self.config = config
        self._e2b = e2b_sandbox
        self._sandbox_id = sandbox_id
        self._context_var_name = "ctx"
        self._closed = False

    @classmethod
    async def create(
        cls,
        workspace_id: str,
        config: SandboxConfig | None = None,
    ) -> E2BSandbox:
        """Create a new E2B sandbox instance.

        Args:
            workspace_id: Workspace ID for tracking
            config: Sandbox configuration

        Returns:
            Initialized E2BSandbox ready for use

        Raises:
            RuntimeError: If E2B SDK not installed or API key not set
        """
        if not E2B_AVAILABLE:
            raise RuntimeError(
                "E2B SDK not installed. Install with: pip install e2b-code-interpreter"
            )

        api_key = os.getenv("E2B_API_KEY")
        if not api_key:
            raise RuntimeError("E2B_API_KEY environment variable not set")

        from . import SandboxConfig as SandboxConfigClass
        config = config or SandboxConfigClass()

        # Generate sandbox ID
        sandbox_id = f"e2b-{uuid.uuid4().hex[:12]}"

        # Create E2B sandbox with timeout
        e2b_sandbox = E2BSandboxSDK(
            api_key=api_key,
            timeout=config.e2b_timeout_seconds,
            metadata={
                "workspace_id": workspace_id,
                "sandbox_id": sandbox_id,
            },
        )

        # Initialize sandbox with helper functions
        init_code = cls._get_init_code(config)
        e2b_sandbox.run_code(init_code)

        return cls(
            workspace_id=workspace_id,
            config=config,
            e2b_sandbox=e2b_sandbox,
            sandbox_id=sandbox_id,
        )

    @staticmethod
    def _get_init_code(config: SandboxConfig) -> str:
        """Generate initialization code for the E2B sandbox."""
        return '''
import json
import re
from collections import Counter
from typing import Any

# Context storage
ctx = None
_evidence = []

# Helper functions that mirror the local sandbox
def peek(start: int = 0, end: int | None = None) -> str:
    """View a character range of the context."""
    if ctx is None:
        return ""
    text = str(ctx)
    return text[start:end]

def lines(start: int = 0, end: int | None = None) -> str:
    """View a line range of the context."""
    if ctx is None:
        return ""
    text = str(ctx)
    all_lines = text.split("\\n")
    selected = all_lines[start:end]
    return "\\n".join(selected)

def search(pattern: str, context_lines: int = 2, max_results: int = 20) -> list[dict]:
    """Search context with regex pattern."""
    if ctx is None:
        return []
    text = str(ctx)
    results = []
    lines_list = text.split("\\n")
    regex = re.compile(pattern)

    for i, line in enumerate(lines_list):
        if regex.search(line):
            start = max(0, i - context_lines)
            end = min(len(lines_list), i + context_lines + 1)
            context = "\\n".join(lines_list[start:end])
            results.append({
                "line_number": i + 1,
                "match": line,
                "context": context,
            })
            if len(results) >= max_results:
                break
    return results

def chunk(chunk_size: int, overlap: int = 0) -> list[dict]:
    """Split context into chunks."""
    if ctx is None:
        return []
    text = str(ctx)
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append({
            "index": idx,
            "start": start,
            "end": min(end, len(text)),
            "text": text[start:end],
        })
        start = end - overlap if overlap > 0 else end
        idx += 1
    return chunks

def cite(snippet: str, line_range: tuple[int, int] | None = None, note: str | None = None) -> dict:
    """Cite evidence for provenance tracking."""
    citation = {
        "snippet": snippet[:200],
        "line_range": line_range,
        "note": note,
    }
    _evidence.append(citation)
    return citation

def word_count() -> int:
    """Count words in context."""
    if ctx is None:
        return 0
    return len(str(ctx).split())

def line_count() -> int:
    """Count lines in context."""
    if ctx is None:
        return 0
    return str(ctx).count("\\n") + 1

def head(n: int = 10) -> str:
    """Get first n lines."""
    return lines(0, n)

def tail(n: int = 10) -> str:
    """Get last n lines."""
    return lines(-n, None)

def grep(pattern: str) -> list[str]:
    """Return lines matching pattern."""
    if ctx is None:
        return []
    regex = re.compile(pattern)
    return [line for line in str(ctx).split("\\n") if regex.search(line)]

def contains(pattern: str) -> bool:
    """Check if context contains pattern."""
    if ctx is None:
        return False
    return bool(re.search(pattern, str(ctx)))

def word_frequency(top_n: int = 20) -> list[tuple[str, int]]:
    """Get most common words."""
    if ctx is None:
        return []
    words = re.findall(r"\\b\\w+\\b", str(ctx).lower())
    return Counter(words).most_common(top_n)

print("Kytchen sandbox initialized")
'''

    @property
    def sandbox_id(self) -> str:
        """Unique identifier for this sandbox instance."""
        return self._sandbox_id

    async def load_context(self, context: ContextType, var_name: str = "ctx") -> None:
        """Load context into the E2B sandbox.

        Args:
            context: The context data to load
            var_name: Variable name to bind context to (default: "ctx")
        """
        if self._closed:
            raise RuntimeError("Sandbox is closed")

        self._context_var_name = var_name

        # Serialize context for transfer
        if isinstance(context, (str, int, float, bool, type(None))):
            # Simple types can be repr'd
            context_repr = repr(context)
        elif isinstance(context, (dict, list)):
            # JSON-serializable types
            context_repr = f"json.loads({repr(json.dumps(context))})"
        elif isinstance(context, bytes):
            # Bytes need special handling
            context_repr = repr(context)
        else:
            # Fallback to string representation
            context_repr = repr(str(context))

        code = f"{var_name} = {context_repr}"
        self._e2b.run_code(code)

    async def execute(self, code: str) -> ExecutionResult:
        """Execute code in the E2B sandbox.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult with stdout, stderr, return value, etc.
        """
        if self._closed:
            return ExecutionResult(
                stdout="",
                stderr="Sandbox is closed",
                return_value=None,
                variables_updated=[],
                truncated=False,
                execution_time_ms=0.0,
                error="Sandbox is closed",
            )

        start = time.time()

        try:
            # Execute with timeout
            result = self._e2b.run_code(
                code,
                timeout=self.config.timeout_seconds,
            )

            # Extract outputs
            stdout_parts = []
            stderr_parts = []
            return_value: Any = None

            for output in result.logs.stdout:
                stdout_parts.append(output)
            for output in result.logs.stderr:
                stderr_parts.append(output)

            # Check for results
            if result.results:
                last_result = result.results[-1]
                if hasattr(last_result, 'text'):
                    return_value = last_result.text

            # Check for errors
            error_msg = None
            if result.error:
                error_msg = f"{result.error.name}: {result.error.value}"
                stderr_parts.append(result.error.traceback or "")

            stdout = "\n".join(stdout_parts)
            stderr = "\n".join(stderr_parts)

            # Truncate if needed
            truncated = False
            if len(stdout) > self.config.max_output_chars:
                stdout = stdout[:self.config.max_output_chars] + "\n... [OUTPUT TRUNCATED]"
                truncated = True
            if len(stderr) > self.config.max_output_chars:
                stderr = stderr[:self.config.max_output_chars] + "\n... [OUTPUT TRUNCATED]"
                truncated = True

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                return_value=return_value,
                variables_updated=[],  # E2B doesn't track this
                truncated=truncated,
                execution_time_ms=(time.time() - start) * 1000.0,
                error=error_msg,
            )

        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                return_value=None,
                variables_updated=[],
                truncated=False,
                execution_time_ms=(time.time() - start) * 1000.0,
                error=str(e),
            )

    async def get_variable(self, name: str) -> object | None:
        """Get a variable from the E2B sandbox.

        Args:
            name: Variable name to retrieve

        Returns:
            Variable value or None if not found
        """
        if self._closed:
            return None

        try:
            result = self._e2b.run_code(f"json.dumps({name}) if {name} is not None else 'null'")
            if result.results:
                text = result.results[-1].text if hasattr(result.results[-1], 'text') else None
                if text:
                    return json.loads(text)
        except Exception:
            pass
        return None

    async def set_variable(self, name: str, value: object) -> None:
        """Set a variable in the E2B sandbox.

        Args:
            name: Variable name
            value: Value to set
        """
        if self._closed:
            return

        if isinstance(value, (str, int, float, bool, type(None))):
            value_repr = repr(value)
        elif isinstance(value, (dict, list)):
            value_repr = f"json.loads({repr(json.dumps(value))})"
        else:
            value_repr = repr(str(value))

        self._e2b.run_code(f"{name} = {value_repr}")

    async def close(self) -> None:
        """Clean up E2B sandbox resources."""
        if not self._closed:
            self._closed = True
            try:
                self._e2b.kill()
            except Exception:
                pass  # Best effort cleanup

    def get_evidence(self) -> list[dict[str, Any]]:
        """Get collected evidence/citations from the E2B sandbox."""
        if self._closed:
            return []

        try:
            result = self._e2b.run_code("json.dumps(_evidence)")
            if result.results:
                text = result.results[-1].text if hasattr(result.results[-1], 'text') else None
                if text:
                    return json.loads(text)
        except Exception:
            pass
        return []

    def clear_evidence(self) -> None:
        """Clear collected evidence/citations in the E2B sandbox."""
        if not self._closed:
            try:
                self._e2b.run_code("_evidence.clear()")
            except Exception:
                pass

    def __del__(self) -> None:
        """Ensure sandbox is cleaned up."""
        if hasattr(self, '_closed') and not self._closed:
            try:
                self._e2b.kill()
            except Exception:
                pass
