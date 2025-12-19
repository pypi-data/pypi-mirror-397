"""API-free MCP server for use with Claude Desktop, Cursor, Windsurf, etc.

This is the "thick client" - Kytchen Local (kytchen-local).
Too many cooks in the kitchen? Let us handle the prep.

This server exposes Kytchen's prep station (context exploration tools) WITHOUT requiring
external API calls. The host AI (Claude, GPT, etc.) provides the reasoning (the chef).

Tools (the prep station):
- load_context: Load ingredients into sandboxed REPL (mise en place)
- peek_context: View character/line ranges of the prep
- search_context: Regex search with context (find ingredients)
- exec_python: Execute Python code in sandbox (prep work)
- get_variable: Retrieve variables from REPL
- think: Structure a reasoning sub-step
- get_status: Show current session state (ticket status)
- get_evidence: Retrieve collected sauce (citations/evidence)
- finalize: Mark task complete with answer (plate the dish)
- chunk_context: Split prep into chunks with metadata for navigation
- evaluate_progress: Self-evaluate progress with convergence tracking
- summarize_so_far: Compress reasoning history (portion control)

Usage:
    python -m kytchen.mcp.local_server

Or via entry point:
    kytchen-local
"""

from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
import difflib
import json
import os
import re
import shlex
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from ..cache import TTLMemoryCache
from ..repl.sandbox import REPLEnvironment, SandboxConfig
from ..types import ContentFormat, ContextMetadata
from ..recipe import (
    RecipeRunner,
    RecipeResult,
    load_kytchenfile,
    hash_content,
)

__all__ = ["KytchenMCPServerLocal", "main"]


@dataclass
class _Evidence:
    """Provenance tracking for reasoning conclusions."""
    source: Literal["search", "peek", "exec", "manual", "action"]
    line_range: tuple[int, int] | None
    pattern: str | None
    snippet: str
    note: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


def _detect_format(text: str) -> ContentFormat:
    """Detect content format from text."""
    t = text.lstrip()
    if t.startswith("{") or t.startswith("["):
        try:
            json.loads(text)
            return ContentFormat.JSON
        except Exception:
            return ContentFormat.TEXT
    return ContentFormat.TEXT


def _analyze_text_context(text: str, fmt: ContentFormat) -> ContextMetadata:
    """Analyze text and return metadata."""
    return ContextMetadata(
        format=fmt,
        size_bytes=len(text.encode("utf-8", errors="ignore")),
        size_chars=len(text),
        size_lines=text.count("\n") + 1,
        size_tokens_estimate=len(text) // 4,
        structure_hint=None,
        sample_preview=text[:500],
    )


@dataclass
class _Session:
    """Session state for a context."""
    repl: REPLEnvironment
    meta: ContextMetadata
    created_at: datetime = field(default_factory=datetime.now)
    iterations: int = 0
    think_history: list[str] = field(default_factory=list)
    # Provenance tracking
    evidence: list[_Evidence] = field(default_factory=list)
    # Convergence signals
    confidence_history: list[float] = field(default_factory=list)
    information_gain: list[int] = field(default_factory=list)  # evidence count per iteration
    # Chunk metadata for navigation
    chunks: list[dict] | None = None


def _detect_workspace_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd


def _find_chef_guide() -> str | None:
    """Find and load CHEF.md from standard locations.

    Search order:
    1. Current working directory (./CHEF.md)
    2. Workspace root (git root)/CHEF.md
    3. User's home ~/.kytchen/CHEF.md
    4. Package default (kytchen/CHEF.md)

    Returns:
        Content of CHEF.md if found, None otherwise
    """
    search_paths = [
        Path.cwd() / "CHEF.md",
        _detect_workspace_root() / "CHEF.md",
        Path.home() / ".kytchen" / "CHEF.md",
    ]

    # Also check package directory
    package_dir = Path(__file__).parent.parent.parent
    if (package_dir / "CHEF.md").exists():
        search_paths.append(package_dir / "CHEF.md")

    for path in search_paths:
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                continue

    return None


def _scoped_path(workspace_root: Path, path: str) -> Path:
    root = workspace_root.resolve()
    p = Path(path)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (root / p).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path '{path}' escapes workspace root '{root}'")
    return resolved


def _format_payload(payload: dict[str, Any], output: Literal["json", "markdown"]) -> str:
    if output == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return "```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```"

def _to_jsonable(obj: Any) -> Any:
    """Best-effort conversion of MCP/Pydantic objects into JSON-serializable data."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return _to_jsonable(vars(obj))
        except Exception:
            pass
    return str(obj)


@dataclass(slots=True)
class ActionConfig:
    enabled: bool = False
    workspace_root: Path = field(default_factory=_detect_workspace_root)
    require_confirmation: bool = False
    max_cmd_seconds: float = 30.0
    max_output_chars: int = 50_000
    max_read_bytes: int = 1_000_000
    max_write_bytes: int = 1_000_000


@dataclass
class _RemoteServerHandle:
    """A managed remote MCP server connection (stdio transport)."""

    command: str
    args: list[str] = field(default_factory=list)
    cwd: Path | None = None
    env: dict[str, str] | None = None
    allow_tools: list[str] | None = None
    deny_tools: list[str] | None = None

    connected_at: datetime | None = None
    session: Any | None = None  # ClientSession (kept as Any to avoid hard dependency at import time)
    _stack: AsyncExitStack | None = None


class KytchenMCPServerLocal:
    """API-free MCP server for local AI reasoning.

    This server provides context exploration tools that work with any
    MCP-compatible AI host (Claude Desktop, Cursor, Windsurf, etc.).

    The key difference from KytchenMCPServer: NO external API calls.
    The host AI provides all the reasoning.
    """

    def __init__(
        self,
        sandbox_config: SandboxConfig | None = None,
        action_config: ActionConfig | None = None,
    ) -> None:
        self.sandbox_config = sandbox_config or SandboxConfig()
        self.action_config = action_config or ActionConfig()
        self._sessions: dict[str, _Session] = {}
        self._recipes: dict[str, RecipeRunner] = {}
        self._recipe_results: dict[str, RecipeResult] = {}
        self._remote_servers: dict[str, _RemoteServerHandle] = {}

        # Process-local caches (best-effort). Keyed by content hashes.
        self._conversion_cache: TTLMemoryCache[dict[str, Any]] = TTLMemoryCache()
        self._search_cache: TTLMemoryCache[dict[str, Any]] = TTLMemoryCache()

        # Import MCP lazily so it's an optional dependency
        try:
            from mcp.server.fastmcp import FastMCP
        except Exception as e:
            raise RuntimeError(
                "MCP support requires the `mcp` package. Install with `pip install kytchen[mcp]`."
            ) from e

        self.server = FastMCP("kytchen-local")
        self._register_prompts()
        self._register_tools()

    def _register_prompts(self) -> None:
        """Register MCP prompts for auto-injection."""

        @self.server.prompt()
        async def chef() -> str:
            """How to use Kytchen effectively.

            This prompt teaches the AI best practices for using Kytchen's
            context exploration tools. Call this before starting work.
            """
            guide = _find_chef_guide()
            if guide:
                return guide
            return """# Kytchen Quick Guide

**TL;DR: `load_context` → `search_context` → `peek_context` → `finalize`**

Don't stuff your context. Search first, read second, cite always.

You are the chef. Kytchen handles the prep.
"""

    async def _ensure_remote_server(self, server_id: str) -> tuple[bool, str | _RemoteServerHandle]:
        """Ensure a remote MCP server is connected and initialized."""
        if server_id not in self._remote_servers:
            return False, f"Error: Remote server '{server_id}' not registered."

        handle = self._remote_servers[server_id]
        if handle.session is not None:
            return True, handle

        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except Exception as e:  # pragma: no cover
            return False, f"Error: MCP client support is not available: {e}"

        params = StdioServerParameters(
            command=handle.command,
            args=handle.args,
            env=handle.env,
            cwd=str(handle.cwd) if handle.cwd is not None else None,
        )

        stack = AsyncExitStack()
        try:
            read_stream, write_stream = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()
        except Exception as e:
            await stack.aclose()
            return False, f"Error: Failed to connect to remote server '{server_id}': {e}"

        handle._stack = stack
        handle.session = session
        handle.connected_at = datetime.now()
        return True, handle

    async def _close_remote_server(self, server_id: str) -> tuple[bool, str]:
        """Close a remote server connection and terminate the subprocess."""
        if server_id not in self._remote_servers:
            return False, f"Error: Remote server '{server_id}' not registered."

        handle = self._remote_servers[server_id]
        if handle._stack is not None:
            try:
                await handle._stack.aclose()
            finally:
                handle._stack = None
                handle.session = None
                handle.connected_at = None
        return True, f"Closed remote server '{server_id}'."

    async def _remote_list_tools(self, server_id: str) -> tuple[bool, Any]:
        ok, res = await self._ensure_remote_server(server_id)
        if not ok:
            return False, res
        handle = res  # type: ignore[assignment]
        try:
            result = await handle.session.list_tools()  # type: ignore[union-attr]
            return True, _to_jsonable(result)
        except Exception as e:
            return False, f"Error: list_tools failed: {e}"

    async def _remote_call_tool(
        self,
        server_id: str,
        tool: str,
        arguments: dict[str, Any] | None = None,
        timeout_seconds: float | None = 30.0,
        recipe_id: str | None = None,
    ) -> tuple[bool, Any]:
        ok, res = await self._ensure_remote_server(server_id)
        if not ok:
            return False, res
        handle = res  # type: ignore[assignment]

        if not self._remote_tool_allowed(handle, tool):
            return False, f"Error: Tool '{tool}' is not allowed for remote server '{server_id}'."

        try:
            from datetime import timedelta

            read_timeout = timedelta(seconds=float(timeout_seconds or 30.0))
            result = await handle.session.call_tool(  # type: ignore[union-attr]
                name=tool,
                arguments=arguments or {},
                read_timeout_seconds=read_timeout,
            )
        except Exception as e:
            return False, f"Error: call_tool failed: {e}"

        result_jsonable = _to_jsonable(result)

        if recipe_id and recipe_id in self._recipes:
            runner = self._recipes[recipe_id]
            runner.record_trace(
                tool=f"remote:{server_id}:{tool}",
                args={"server_id": server_id, "tool": tool, "arguments": arguments or {}},
                result=result_jsonable,
            )
            runner.add_sauce(
                source="remote",
                snippet=json.dumps(result_jsonable, ensure_ascii=False)[:500],
                pattern=tool,
                note=f"remote server={server_id}",
                dataset_id=f"remote:{server_id}",
            )

        return True, result_jsonable

    def _remote_tool_allowed(self, handle: _RemoteServerHandle, tool_name: str) -> bool:
        if handle.allow_tools is not None:
            return tool_name in handle.allow_tools
        if handle.deny_tools is not None and tool_name in handle.deny_tools:
            return False
        return True

    def _register_tools(self) -> None:
        """Register all MCP tools."""

        @self.server.tool()
        async def get_chef_guide() -> str:
            """Get the chef.md guide for using Kytchen effectively.

            Returns the chef.md file which teaches best practices for:
            - Using Kytchen tools efficiently
            - Exploration patterns (search-first, chunked navigation, etc.)
            - Anti-patterns to avoid
            - The "sauce" (evidence/citation) system

            Call this first if you're new to Kytchen or need a refresher.

            Returns:
                The chef.md guide content, or a brief summary if not found
            """
            guide = _find_chef_guide()
            if guide:
                return guide

            # Fallback if no chef.md found
            return """# Kytchen Quick Guide

You are the **chef**. Kytchen handles the **prep**.

## Core Pattern
1. `load_context` - Load your document/data
2. `search_context` - Find what you need (regex)
3. `peek_context` - Read specific sections
4. `exec_python` - Transform/analyze with code
5. `finalize` - Provide your answer with citations

## Key Principles
- **Don't stuff, explore** - Use tools to find what you need
- **Search before peek** - Narrow down first
- **Collect sauce** - Evidence makes answers trustworthy

For the full guide, create a chef.md file in your project:
  kytchen init

Or see: https://kytchen.dev/docs/chef-guide
"""

        @self.server.tool()
        async def load_context(
            context: str,
            context_id: str = "default",
            format: str = "auto",
        ) -> str:
            """Load context into an in-memory REPL session.

            The context is stored in a sandboxed Python environment as the variable `ctx`.
            You can then use other tools to explore and process this context.

            Args:
                context: The text/data to load
                context_id: Identifier for this context session (default: "default")
                format: Content format - "auto", "text", or "json" (default: "auto")

            Returns:
                Confirmation with context metadata
            """
            fmt = _detect_format(context) if format == "auto" else ContentFormat(format)
            meta = _analyze_text_context(context, fmt)

            repl = REPLEnvironment(
                context=context,
                context_var_name="ctx",
                config=self.sandbox_config,
                loop=asyncio.get_running_loop(),
            )

            self._sessions[context_id] = _Session(repl=repl, meta=meta)

            return f"""## Context Loaded

> **Pattern:** `search_context` → `peek_context` → `finalize`
> Don't read everything. Search for what you need, then peek around matches.

**Session:** `{context_id}` | **Size:** {meta.size_chars:,} chars, {meta.size_lines:,} lines | **~{meta.size_tokens_estimate:,} tokens**

**Preview:**
```
{meta.sample_preview}
```

### Next Steps
- `search_context(pattern="...")` - Find what you need
- `peek_context(start, end)` - Read specific sections
- `exec_python(code)` - Transform/analyze
- `finalize(answer)` - Complete with citations"""

        def _get_session(context_id: str) -> _Session | None:
            return self._sessions.get(context_id)

        def _require_actions(confirm: bool) -> str | None:
            if not self.action_config.enabled:
                return "Error: Action mode is disabled. Start the server with actions enabled to use this tool."
            if self.action_config.require_confirmation and not confirm:
                return "Error: This tool requires confirmation. Re-run with confirm=true."
            return None

        def _record_action(session: _Session | None, note: str, snippet: str) -> None:
            if session is None:
                return
            evidence_before = len(session.evidence)
            session.evidence.append(
                _Evidence(
                    source="action",
                    line_range=None,
                    pattern=None,
                    note=note,
                    snippet=snippet[:200],
                )
            )
            session.information_gain.append(len(session.evidence) - evidence_before)

        def _cache_ttl_seconds() -> float:
            raw = str(os.environ.get("KYTCHEN_CACHE_TTL_SECONDS", "3600"))
            try:
                return max(0.0, float(raw))
            except Exception:
                return 3600.0

        def _cache_enabled() -> bool:
            v = str(os.environ.get("KYTCHEN_CACHE_ENABLED", "1"))
            return v.strip().lower() in {"1", "true", "yes"}

        def _read_binary(path: str) -> tuple[Path | None, bytes | None, str | None]:
            """Read a binary file from within workspace root, enforcing max_read_bytes."""
            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return None, None, f"Error: {e}"
            if not p.exists() or not p.is_file():
                return None, None, f"Error: File not found: {path}"
            data = p.read_bytes()
            if len(data) > self.action_config.max_read_bytes:
                return None, None, f"Error: File too large to read (>{self.action_config.max_read_bytes} bytes): {path}"
            return p, data, None

        async def _run_subprocess(
            argv: list[str],
            cwd: Path,
            timeout_seconds: float,
        ) -> dict[str, Any]:
            start = time.perf_counter()
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            timed_out = False
            try:
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                timed_out = True
                proc.kill()
                stdout_b, stderr_b = await proc.communicate()

            duration_ms = (time.perf_counter() - start) * 1000.0
            stdout = stdout_b.decode("utf-8", errors="replace")
            stderr = stderr_b.decode("utf-8", errors="replace")
            if len(stdout) > self.action_config.max_output_chars:
                stdout = stdout[: self.action_config.max_output_chars] + "\n... (truncated)"
            if len(stderr) > self.action_config.max_output_chars:
                stderr = stderr[: self.action_config.max_output_chars] + "\n... (truncated)"

            return {
                "argv": argv,
                "cwd": str(cwd),
                "exit_code": proc.returncode,
                "timed_out": timed_out,
                "duration_ms": duration_ms,
                "stdout": stdout,
                "stderr": stderr,
            }

        @self.server.tool()
        async def run_command(
            cmd: str,
            cwd: str | None = None,
            timeout_seconds: float | None = None,
            shell: bool = False,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root
            timeout = timeout_seconds if timeout_seconds is not None else self.action_config.max_cmd_seconds

            if shell:
                argv = ["/bin/zsh", "-lc", cmd]
            else:
                argv = shlex.split(cmd)
                if not argv:
                    return "Error: Empty command"

            payload = await _run_subprocess(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
            if session is not None:
                session.repl._namespace["last_command_result"] = payload
            _record_action(session, note="run_command", snippet=(payload.get("stdout") or payload.get("stderr") or "")[:200])
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def read_file(
            path: str,
            start_line: int = 1,
            limit: int = 200,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            if not p.exists() or not p.is_file():
                return f"Error: File not found: {path}"

            data = p.read_bytes()
            if len(data) > self.action_config.max_read_bytes:
                return f"Error: File too large to read (>{self.action_config.max_read_bytes} bytes): {path}"

            text = data.decode("utf-8", errors="replace")
            lines = text.splitlines()
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), start_idx + max(0, limit))
            slice_lines = lines[start_idx:end_idx]
            numbered = "\n".join(f"{i + start_idx + 1:>6}\t{line}" for i, line in enumerate(slice_lines))

            payload: dict[str, Any] = {
                "path": str(p),
                "start_line": start_line,
                "limit": limit,
                "total_lines": len(lines),
                "content": numbered,
            }
            if session is not None:
                session.repl._namespace["last_read_file_result"] = payload
            _record_action(session, note="read_file", snippet=f"{path} ({start_line}-{end_idx})")
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def write_file(
            path: str,
            content: str,
            mode: Literal["overwrite", "append"] = "overwrite",
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            payload_bytes = content.encode("utf-8", errors="replace")
            if len(payload_bytes) > self.action_config.max_write_bytes:
                return f"Error: Content too large to write (>{self.action_config.max_write_bytes} bytes)"

            p.parent.mkdir(parents=True, exist_ok=True)
            file_mode = "ab" if mode == "append" else "wb"
            with open(p, file_mode) as f:
                f.write(payload_bytes)

            payload: dict[str, Any] = {
                "path": str(p),
                "bytes_written": len(payload_bytes),
                "mode": mode,
            }
            if session is not None:
                session.repl._namespace["last_write_file_result"] = payload
            _record_action(session, note="write_file", snippet=f"{path} ({len(payload_bytes)} bytes)")
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def run_tests(
            runner: Literal["auto", "pytest"] = "auto",
            args: list[str] | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            runner_resolved = "pytest" if runner == "auto" else runner
            if runner_resolved != "pytest":
                return f"Error: Unsupported test runner: {runner_resolved}"

            argv = [sys.executable, "-m", "pytest", "-vv", "--tb=short", "--maxfail=20"]
            if args:
                argv.extend(args)

            proc_payload = await _run_subprocess(
                argv=argv,
                cwd=self.action_config.workspace_root,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            raw_output = (proc_payload.get("stdout") or "") + ("\n" + proc_payload.get("stderr") if proc_payload.get("stderr") else "")

            passed = 0
            failed = 0
            duration_ms = float(proc_payload.get("duration_ms") or 0.0)

            m_passed = re.search(r"(\\d+)\\s+passed", raw_output)
            if m_passed:
                passed = int(m_passed.group(1))
            m_failed = re.search(r"(\\d+)\\s+failed", raw_output)
            if m_failed:
                failed = int(m_failed.group(1))

            failures: list[dict[str, Any]] = []
            section_re = re.compile(r"^_{3,}\\s+(?P<name>.+?)\\s+_{3,}\\s*$", re.MULTILINE)
            matches = list(section_re.finditer(raw_output))
            for i, sm in enumerate(matches):
                start = sm.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_output)
                block = raw_output[start:end].strip()
                file = ""
                line = 0
                file_line = re.search(r"^(?P<file>.+?\\.py):(?P<line>\\d+):", block, re.MULTILINE)
                if file_line:
                    file = file_line.group("file")
                    try:
                        line = int(file_line.group("line"))
                    except Exception:
                        line = 0
                msg = ""
                err_line = re.search(r"^E\\s+(.+)$", block, re.MULTILINE)
                if err_line:
                    msg = err_line.group(1).strip()

                failures.append(
                    {
                        "file": file,
                        "line": line,
                        "test_name": sm.group("name").strip(),
                        "message": msg,
                        "traceback": block,
                    }
                )

            result: dict[str, Any] = {
                "passed": passed,
                "failed": failed,
                "failures": failures,
                "duration_ms": duration_ms,
                "raw_output": raw_output,
                "command": proc_payload,
            }

            if session is not None:
                session.repl._namespace["last_test_result"] = result

            summary_snippet = f"passed={passed} failed={failed} failures={len(failures)}"
            _record_action(session, note="run_tests", snippet=summary_snippet)
            for f in failures[:10]:
                _record_action(session, note="test_failure", snippet=(f.get("message") or f.get("test_name") or "")[:200])

            return _format_payload(result, output=output)

        @self.server.tool()
        async def list_contexts(
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            items: list[dict[str, Any]] = []
            for cid, session in self._sessions.items():
                items.append(
                    {
                        "context_id": cid,
                        "created_at": session.created_at.isoformat(),
                        "iterations": session.iterations,
                        "format": session.meta.format.value,
                        "size_chars": session.meta.size_chars,
                        "size_lines": session.meta.size_lines,
                        "estimated_tokens": session.meta.size_tokens_estimate,
                        "evidence_count": len(session.evidence),
                    }
                )

            payload: dict[str, Any] = {
                "count": len(items),
                "items": sorted(items, key=lambda x: x["context_id"]),
            }
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def diff_contexts(
            a: str,
            b: str,
            context_lines: int = 3,
            max_lines: int = 400,
            output: Literal["markdown", "text"] = "markdown",
        ) -> str:
            if a not in self._sessions:
                return f"Error: No context loaded with ID '{a}'. Use load_context first."
            if b not in self._sessions:
                return f"Error: No context loaded with ID '{b}'. Use load_context first."

            sa = self._sessions[a]
            sb = self._sessions[b]
            sa.iterations += 1
            sb.iterations += 1

            a_ctx = sa.repl.get_variable("ctx")
            b_ctx = sb.repl.get_variable("ctx")
            if not isinstance(a_ctx, str) or not isinstance(b_ctx, str):
                return "Error: diff_contexts currently supports only text contexts"

            a_lines = a_ctx.splitlines(keepends=True)
            b_lines = b_ctx.splitlines(keepends=True)
            diff_iter = difflib.unified_diff(
                a_lines,
                b_lines,
                fromfile=a,
                tofile=b,
                n=max(0, context_lines),
            )
            diff_lines = list(diff_iter)
            truncated = False
            if len(diff_lines) > max(0, max_lines):
                diff_lines = diff_lines[: max(0, max_lines)]
                truncated = True

            diff_text = "".join(diff_lines)
            if truncated:
                diff_text += "\n... (truncated)"

            _record_action(sa, note="diff_contexts", snippet=f"{a} vs {b}")
            _record_action(sb, note="diff_contexts", snippet=f"{a} vs {b}")

            if output == "text":
                return diff_text
            return f"```diff\n{diff_text}\n```"

        @self.server.tool()
        async def save_session(
            session_id: str = "default",
            path: str = "kytchen_session.json",
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err
            if session_id not in self._sessions:
                return f"Error: No context loaded with ID '{session_id}'. Use load_context first."

            session = self._sessions[session_id]
            session.iterations += 1

            ctx_val = session.repl.get_variable("ctx")
            if not isinstance(ctx_val, str):
                return "Error: save_session currently supports only text contexts"

            payload: dict[str, Any] = {
                "schema": "kytchen.session.v1",
                "session_id": session_id,
                "created_at": session.created_at.isoformat(),
                "iterations": session.iterations,
                "meta": {
                    "format": session.meta.format.value,
                    "size_bytes": session.meta.size_bytes,
                    "size_chars": session.meta.size_chars,
                    "size_lines": session.meta.size_lines,
                    "size_tokens_estimate": session.meta.size_tokens_estimate,
                    "structure_hint": session.meta.structure_hint,
                    "sample_preview": session.meta.sample_preview,
                },
                "ctx": ctx_val,
                "think_history": list(session.think_history),
                "confidence_history": list(session.confidence_history),
                "information_gain": list(session.information_gain),
                "chunks": session.chunks,
                "evidence": [
                    {
                        "source": ev.source,
                        "line_range": list(ev.line_range) if ev.line_range else None,
                        "pattern": ev.pattern,
                        "snippet": ev.snippet,
                        "note": ev.note,
                        "timestamp": ev.timestamp.isoformat(),
                    }
                    for ev in session.evidence
                ],
            }

            out_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8", errors="replace")
            if len(out_bytes) > self.action_config.max_write_bytes:
                return f"Error: Session file too large to write (>{self.action_config.max_write_bytes} bytes)"

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "wb") as f:
                f.write(out_bytes)

            _record_action(session, note="save_session", snippet=str(p))
            return _format_payload({"path": str(p), "bytes_written": len(out_bytes)}, output=output)

        @self.server.tool()
        async def load_session(
            path: str,
            session_id: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            err = _require_actions(confirm)
            if err:
                return err

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            if not p.exists() or not p.is_file():
                return f"Error: File not found: {path}"

            data = p.read_bytes()
            if len(data) > self.action_config.max_read_bytes:
                return f"Error: Session file too large to read (>{self.action_config.max_read_bytes} bytes): {path}"

            try:
                obj = json.loads(data.decode("utf-8", errors="replace"))
            except Exception as e:
                return f"Error: Failed to parse JSON: {e}"

            if not isinstance(obj, dict):
                return "Error: Invalid session file format"

            ctx = obj.get("ctx")
            if not isinstance(ctx, str):
                return "Error: Invalid session file: ctx must be a string"

            file_session_id = obj.get("session_id")
            if session_id is None:
                session_id = str(file_session_id) if file_session_id else "default"

            meta_obj = obj.get("meta")
            if not isinstance(meta_obj, dict):
                meta_obj = {}

            try:
                fmt = ContentFormat(str(meta_obj.get("format") or "text"))
            except Exception:
                fmt = ContentFormat.TEXT

            meta = ContextMetadata(
                format=fmt,
                size_bytes=int(meta_obj.get("size_bytes") or len(ctx.encode("utf-8", errors="ignore"))),
                size_chars=int(meta_obj.get("size_chars") or len(ctx)),
                size_lines=int(meta_obj.get("size_lines") or (ctx.count("\n") + 1)),
                size_tokens_estimate=int(meta_obj.get("size_tokens_estimate") or (len(ctx) // 4)),
                structure_hint=meta_obj.get("structure_hint"),
                sample_preview=str(meta_obj.get("sample_preview") or ctx[:500]),
            )

            repl = REPLEnvironment(
                context=ctx,
                context_var_name="ctx",
                config=self.sandbox_config,
                loop=asyncio.get_running_loop(),
            )

            created_at = datetime.now()
            created_at_str = obj.get("created_at")
            if isinstance(created_at_str, str):
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except Exception:
                    created_at = datetime.now()

            session = _Session(
                repl=repl,
                meta=meta,
                created_at=created_at,
                iterations=int(obj.get("iterations") or 0),
                think_history=list(obj.get("think_history") or []),
                confidence_history=list(obj.get("confidence_history") or []),
                information_gain=list(obj.get("information_gain") or []),
                chunks=obj.get("chunks"),
            )

            ev_list = obj.get("evidence")
            if isinstance(ev_list, list):
                for ev in ev_list:
                    if not isinstance(ev, dict):
                        continue
                    ts = datetime.now()
                    ts_s = ev.get("timestamp")
                    if isinstance(ts_s, str):
                        try:
                            ts = datetime.fromisoformat(ts_s)
                        except Exception:
                            ts = datetime.now()
                    source = ev.get("source")
                    if source not in {"search", "peek", "exec", "manual", "action"}:
                        source = "manual"
                    lr = ev.get("line_range")
                    line_range: tuple[int, int] | None = None
                    if isinstance(lr, list) and len(lr) == 2 and all(isinstance(x, int) for x in lr):
                        line_range = (int(lr[0]), int(lr[1]))
                    session.evidence.append(
                        _Evidence(
                            source=source,
                            line_range=line_range,
                            pattern=ev.get("pattern"),
                            snippet=str(ev.get("snippet") or ""),
                            note=ev.get("note"),
                            timestamp=ts,
                        )
                    )

            self._sessions[session_id] = session
            _record_action(session, note="load_session", snippet=str(p))
            return _format_payload({"session_id": session_id, "loaded_from": str(p)}, output=output)

        @self.server.tool()
        async def peek_context(
            start: int = 0,
            end: int | None = None,
            context_id: str = "default",
            unit: Literal["chars", "lines"] = "chars",
            around_match: str | None = None,
            around_chars: int = 200,
            match_index: int = 0,
        ) -> str:
            """View a portion of the loaded context.

            Args:
                start: Starting position (0-indexed)
                end: Ending position (None = to the end)
                context_id: Session identifier
                unit: "chars" for character slicing, "lines" for line slicing

            Returns:
                The requested portion of the context
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            if around_match:
                ctx_val = repl.get_variable("ctx")
                if not isinstance(ctx_val, str):
                    return "Error: around_match is only supported for text contexts"
                try:
                    rx = re.compile(str(around_match))
                except re.error as e:
                    return f"Error: Invalid regex pattern `{around_match}`: {e}"
                matches = list(rx.finditer(ctx_val))
                if not matches:
                    return f"No matches found for pattern: `{around_match}`"
                idx = int(match_index)
                if idx < 0 or idx >= len(matches):
                    return f"Error: match_index out of range (0-{len(matches)-1})"
                m = matches[idx]
                pad = max(0, int(around_chars))
                start = max(0, m.start() - pad)
                end = min(len(ctx_val), m.end() + pad)
                unit = "chars"

            if unit == "chars":
                fn = repl.get_variable("peek")
                if not callable(fn):
                    return "Error: peek() helper is not available"
                result = fn(start, end)
            else:
                fn = repl.get_variable("lines")
                if not callable(fn):
                    return "Error: lines() helper is not available"
                result = fn(start, end)

            # Track evidence for provenance
            evidence_before = len(session.evidence)
            if unit == "lines" and result:
                session.evidence.append(_Evidence(
                    source="peek",
                    line_range=(start, end if end is not None else start + result.count('\n') + 1),
                    pattern=None,
                    note=None,
                    snippet=result[:200],
                ))
            elif unit == "chars" and result:
                session.evidence.append(_Evidence(
                    source="peek",
                    line_range=None,  # Character ranges don't map to lines easily
                    pattern=None,
                    note=None,
                    snippet=result[:200],
                ))
            session.information_gain.append(len(session.evidence) - evidence_before)

            # If we have chunk metadata and the peek is large, suggest chunk boundaries.
            hint = ""
            if unit == "chars" and session.chunks and isinstance(result, str) and len(result) > 5000:
                try:
                    start_i = int(start)
                    end_i = int(end) if end is not None else start_i + len(result)
                    overlaps = [c for c in session.chunks if c.get("start_char") <= end_i and c.get("end_char") >= start_i]
                    overlaps = overlaps[:3]
                    if overlaps:
                        hint_lines = ["", "---", "", "**Tip:** Consider chunk-aligned peeks (run `chunk_context` if needed):"]
                        for c in overlaps:
                            hint_lines.append(f"- chunk {c.get('index')} ({c.get('start_char')}-{c.get('end_char')})")
                        hint = "\n".join(hint_lines)
                except Exception:
                    hint = ""

            return f"```\n{result}\n```" + hint

        @self.server.tool()
        async def search_context(
            pattern: str,
            context_id: str = "default",
            max_results: int = 10,
            context_lines: int = 2,
            mode: Literal["regex", "semantic"] = "regex",
            chunk_chars: int = 1000,
            overlap: int = 100,
            use_cache: bool = True,
        ) -> str:
            """Search the context using regex patterns.

            Args:
                pattern: Regular expression pattern to search for
                context_id: Session identifier
                max_results: Maximum number of matches to return
                context_lines: Number of surrounding lines to include

            Returns:
                Matching lines with surrounding context
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            cache_key: str | None = None
            if use_cache and _cache_enabled():
                ctx_val = repl.get_variable("ctx")
                if isinstance(ctx_val, str):
                    ctx_hash = hash_content(ctx_val)
                    cache_key = f"search:{mode}:{ctx_hash}:{pattern}:{context_lines}:{max_results}:{chunk_chars}:{overlap}"
                    cached = self._search_cache.get(cache_key)
                    if isinstance(cached, dict) and "results" in cached and "rendered" in cached:
                        return str(cached["rendered"])

            if mode == "semantic":
                from ..repl import helpers as repl_helpers

                ctx_val = repl.get_variable("ctx")
                results = repl_helpers.semantic_search(
                    ctx_val,
                    query=pattern,
                    chunk_chars=chunk_chars,
                    overlap=overlap,
                    max_results=max_results,
                )
            else:
                fn = repl.get_variable("search")
                if not callable(fn):
                    return "Error: search() helper is not available"

                try:
                    results = fn(pattern, context_lines=context_lines, max_results=max_results)
                except re.error as e:
                    return f"Error: Invalid regex pattern `{pattern}`: {e}"

            if not results:
                return f"No matches found for pattern: `{pattern}`"

            # Track evidence for provenance
            evidence_before = len(session.evidence)
            out: list[str] = []
            for r in results:
                try:
                    line_num = r['line_num']
                    # Record evidence
                    session.evidence.append(_Evidence(
                        source="search",
                        line_range=(max(0, line_num - context_lines), line_num + context_lines),
                        pattern=pattern,
                        note=None,
                        snippet=r['match'][:200],
                    ))
                    score = r.get("score") if isinstance(r, dict) else None
                    score_str = ""
                    if mode == "semantic" and isinstance(score, float):
                        score_str = f" (score={score:.3f})"
                    out.append(f"**Line {line_num}:**{score_str}\n```\n{r['context']}\n```")
                except Exception:
                    out.append(str(r))

            # Track information gain
            session.information_gain.append(len(session.evidence) - evidence_before)

            rendered = f"## Search Results for `{pattern}`\n\nFound {len(results)} match(es):\n\n" + "\n\n---\n\n".join(out)

            if cache_key is not None and _cache_enabled():
                self._search_cache.set(cache_key, {"results": results, "rendered": rendered}, ttl_seconds=_cache_ttl_seconds())

            return rendered

        @self.server.tool()
        async def batch_search(
            patterns: list[str],
            context_id: str = "default",
            max_results_per_pattern: int = 5,
            context_lines: int = 2,
            mode: Literal["regex", "semantic"] = "regex",
        ) -> str:
            """Run multiple searches in one call for efficiency."""
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            ctx_val = repl.get_variable("ctx")
            out: dict[str, Any] = {}

            for p in patterns:
                pat = str(p)
                if mode == "semantic":
                    from ..repl import helpers as repl_helpers

                    results = repl_helpers.semantic_search(
                        ctx_val,
                        query=pat,
                        max_results=int(max_results_per_pattern),
                    )
                else:
                    fn = repl.get_variable("search")
                    if not callable(fn):
                        return "Error: search() helper is not available"
                    try:
                        results = fn(pat, context_lines=context_lines, max_results=int(max_results_per_pattern))
                    except re.error as e:
                        results = [{"error": f"Invalid regex: {e}"}]

                out[pat] = results

            return json.dumps(
                {
                    "context_id": context_id,
                    "mode": mode,
                    "context_lines": context_lines,
                    "max_results_per_pattern": max_results_per_pattern,
                    "results": out,
                },
                ensure_ascii=False,
                indent=2,
            )

        @self.server.tool()
        async def batch_peek(
            ranges: list[dict[str, Any]],
            context_id: str = "default",
            unit: Literal["chars", "lines"] = "chars",
        ) -> str:
            """Peek multiple ranges in one call for efficiency."""
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            if unit == "chars":
                fn = repl.get_variable("peek")
            else:
                fn = repl.get_variable("lines")
            if not callable(fn):
                return "Error: peek()/lines() helper is not available"

            items: list[dict[str, Any]] = []
            for r in ranges:
                start = int(r.get("start", 0))
                end = r.get("end")
                end_i = int(end) if end is not None else None
                try:
                    result = fn(start, end_i)
                except Exception as e:
                    result = f"Error: {e}"
                items.append({"start": start, "end": end_i, "unit": unit, "result": result})

            return json.dumps({"context_id": context_id, "items": items}, ensure_ascii=False, indent=2)

        @self.server.tool()
        async def convert_pdf(
            file_path: str,
            pages: str | None = None,
            context_id: str = "default",
            load_into_context: bool = True,
            return_full_text: bool = False,
            confirm: bool = False,
        ) -> str:
            """Convert PDF to text and optionally load into context."""
            err = _require_actions(confirm)
            if err:
                return err

            p, data, e = _read_binary(file_path)
            if e:
                return e
            assert data is not None
            if p is None or p.suffix.lower() != ".pdf":
                return "Error: file_path must point to a .pdf file"

            cache_key = None
            if _cache_enabled():
                cache_key = f"convert:pdf:{hash_content(data)}:{pages or 'all'}"
                cached = self._conversion_cache.get(cache_key)
                if isinstance(cached, dict) and "text" in cached:
                    result = cached
                else:
                    from ..converters.pdf import convert_pdf_bytes

                    result = convert_pdf_bytes(data, pages=pages)
                    self._conversion_cache.set(cache_key, result, ttl_seconds=_cache_ttl_seconds())
            else:
                from ..converters.pdf import convert_pdf_bytes

                result = convert_pdf_bytes(data, pages=pages)

            text = str(result.get("text") or "")

            if load_into_context:
                await load_context(text, context_id=context_id, format="text")
                # Make it accessible inside the sandbox too.
                sess = self._sessions.get(context_id)
                if sess is not None:
                    sess.repl._namespace["last_converted"] = result

            payload = dict(result)
            if not return_full_text:
                payload["text"] = text[:2000]
                payload["truncated"] = len(text) > 2000
            payload["loaded_context_id"] = context_id if load_into_context else None
            return json.dumps(payload, ensure_ascii=False, indent=2)

        @self.server.tool()
        async def convert_docx(
            file_path: str,
            context_id: str = "default",
            load_into_context: bool = True,
            return_full_text: bool = False,
            confirm: bool = False,
        ) -> str:
            """Convert DOCX to structured text and optionally load into context."""
            err = _require_actions(confirm)
            if err:
                return err

            p, data, e = _read_binary(file_path)
            if e:
                return e
            assert data is not None
            if p is None or p.suffix.lower() != ".docx":
                return "Error: file_path must point to a .docx file"

            cache_key = None
            if _cache_enabled():
                cache_key = f"convert:docx:{hash_content(data)}"
                cached = self._conversion_cache.get(cache_key)
                if isinstance(cached, dict) and "text" in cached:
                    result = cached
                else:
                    from ..converters.docx import convert_docx_bytes

                    result = convert_docx_bytes(data)
                    self._conversion_cache.set(cache_key, result, ttl_seconds=_cache_ttl_seconds())
            else:
                from ..converters.docx import convert_docx_bytes

                result = convert_docx_bytes(data)

            text = str(result.get("text") or "")
            if load_into_context:
                await load_context(text, context_id=context_id, format="text")
                sess = self._sessions.get(context_id)
                if sess is not None:
                    sess.repl._namespace["last_converted"] = result

            payload = dict(result)
            if not return_full_text:
                payload["text"] = text[:2000]
                payload["truncated"] = len(text) > 2000
            payload["loaded_context_id"] = context_id if load_into_context else None
            return json.dumps(payload, ensure_ascii=False, indent=2)

        @self.server.tool()
        async def convert_xlsx(
            file_path: str,
            formulas: Literal["evaluated", "raw"] = "evaluated",
            context_id: str = "default",
            load_into_context: bool = True,
            confirm: bool = False,
        ) -> str:
            """Convert XLSX to JSON-like dicts and optionally load into context."""
            err = _require_actions(confirm)
            if err:
                return err

            p, data, e = _read_binary(file_path)
            if e:
                return e
            assert data is not None
            if p is None or p.suffix.lower() != ".xlsx":
                return "Error: file_path must point to a .xlsx file"

            cache_key = None
            if _cache_enabled():
                cache_key = f"convert:xlsx:{hash_content(data)}:{formulas}"
                cached = self._conversion_cache.get(cache_key)
                if isinstance(cached, dict) and "sheets" in cached:
                    result = cached
                else:
                    from ..converters.xlsx import convert_xlsx_bytes

                    result = convert_xlsx_bytes(data, formulas=formulas)
                    self._conversion_cache.set(cache_key, result, ttl_seconds=_cache_ttl_seconds())
            else:
                from ..converters.xlsx import convert_xlsx_bytes

                result = convert_xlsx_bytes(data, formulas=formulas)

            if load_into_context:
                await load_context(json.dumps(result, ensure_ascii=False, indent=2), context_id=context_id, format="json")
                sess = self._sessions.get(context_id)
                if sess is not None:
                    sess.repl._namespace["last_converted"] = result

            payload = dict(result)
            payload["loaded_context_id"] = context_id if load_into_context else None
            return json.dumps(payload, ensure_ascii=False, indent=2)

        @self.server.tool()
        async def convert_image(
            file_path: str,
            context_id: str = "default",
            load_into_context: bool = True,
            confirm: bool = False,
        ) -> str:
            """OCR an image file and optionally load into context."""
            err = _require_actions(confirm)
            if err:
                return err

            p, data, e = _read_binary(file_path)
            if e:
                return e
            assert data is not None
            if p is None or p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}:
                return "Error: file_path must point to an image file (png/jpg/jpeg/webp/bmp/tiff)"

            cache_key = None
            if _cache_enabled():
                cache_key = f"convert:image:{hash_content(data)}"
                cached = self._conversion_cache.get(cache_key)
                if isinstance(cached, dict) and "text" in cached:
                    result = cached
                else:
                    from ..converters.image import convert_image_bytes

                    result = convert_image_bytes(data)
                    self._conversion_cache.set(cache_key, result, ttl_seconds=_cache_ttl_seconds())
            else:
                from ..converters.image import convert_image_bytes

                result = convert_image_bytes(data)

            text = str(result.get("text") or "")
            if load_into_context:
                await load_context(text, context_id=context_id, format="text")
                sess = self._sessions.get(context_id)
                if sess is not None:
                    sess.repl._namespace["last_converted"] = result

            payload = dict(result)
            payload["loaded_context_id"] = context_id if load_into_context else None
            return json.dumps(payload, ensure_ascii=False, indent=2)

        @self.server.tool()
        async def exec_python(
            code: str,
            context_id: str = "default",
        ) -> str:
            """Execute Python code in the sandboxed REPL.

            The loaded context is available as the variable `ctx`.

            Available helpers:
            - peek(start, end): View characters
            - lines(start, end): View lines
            - search(pattern, context_lines=2, max_results=20): Regex search
            - chunk(chunk_size, overlap=0): Split context into chunks
            - cite(snippet, line_range=None, note=None): Tag evidence for provenance

            Available imports: re, json, csv, math, statistics, collections,
            itertools, functools, datetime, textwrap, difflib

            Args:
                code: Python code to execute
                context_id: Session identifier

            Returns:
                Execution results (stdout, return value, errors)
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            # Track evidence count before execution
            evidence_before = len(session.evidence)

            result = await repl.execute_async(code)

            # Collect citations from REPL and convert to evidence
            if repl._citations:
                for citation in repl._citations:
                    session.evidence.append(_Evidence(
                        source="manual",
                        line_range=citation["line_range"],
                        pattern=None,
                        note=citation["note"],
                        snippet=citation["snippet"][:200],
                    ))
                repl._citations.clear()  # Clear after collecting

            # Track information gain
            session.information_gain.append(len(session.evidence) - evidence_before)

            parts: list[str] = []

            if result.stdout:
                parts.append(f"**Output:**\n```\n{result.stdout}\n```")

            if result.return_value is not None:
                parts.append(f"**Return Value:** `{result.return_value}`")

            if result.variables_updated:
                parts.append(f"**Variables Updated:** {', '.join(f'`{v}`' for v in result.variables_updated)}")

            if result.stderr:
                parts.append(f"**Stderr:**\n```\n{result.stderr}\n```")

            if result.error:
                parts.append(f"**Error:** {result.error}")

            if result.truncated:
                parts.append("*Note: Output was truncated*")

            if not parts:
                parts.append("*(No output)*")

            return "## Execution Result\n\n" + "\n\n".join(parts)

        @self.server.tool()
        async def get_variable(
            name: str,
            context_id: str = "default",
        ) -> str:
            """Retrieve a variable from the REPL namespace.

            Args:
                name: Variable name to retrieve
                context_id: Session identifier

            Returns:
                String representation of the variable's value
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            repl = self._sessions[context_id].repl
            # Check if variable exists in namespace (not just if it's None)
            if name not in repl._namespace:
                return f"Variable `{name}` not found in namespace."
            value = repl._namespace[name]

            # Format nicely for complex types
            if isinstance(value, (dict, list)):
                try:
                    formatted = json.dumps(value, indent=2, ensure_ascii=False)
                    return f"**`{name}`:**\n```json\n{formatted}\n```"
                except Exception:
                    return f"**`{name}`:** `{value}`"

            return f"**`{name}`:** `{value}`"

        @self.server.tool()
        async def think(
            question: str,
            context_slice: str | None = None,
            context_id: str = "default",
        ) -> str:
            """Structure a reasoning sub-step.

            Use this when you need to break down a complex problem into
            smaller questions. This tool helps you organize your thinking -
            YOU provide the reasoning, not an external API.

            Args:
                question: The sub-question to reason about
                context_slice: Optional relevant context excerpt
                context_id: Session identifier

            Returns:
                A structured prompt for you to reason through
            """
            if context_id in self._sessions:
                self._sessions[context_id].iterations += 1
                self._sessions[context_id].think_history.append(question)

            parts = [
                "## Reasoning Step",
                "",
                f"**Question:** {question}",
            ]

            if context_slice:
                parts.extend([
                    "",
                    "**Relevant Context:**",
                    "```",
                    context_slice[:2000],  # Limit context slice
                    "```",
                ])

            parts.extend([
                "",
                "---",
                "",
                "**Your task:** Reason through this step-by-step. Consider:",
                "1. What information do you have?",
                "2. What can you infer?",
                "3. What's the answer to this sub-question?",
                "",
                "*After reasoning, use `exec_python` to verify or `finalize` if done.*",
            ])

            return "\n".join(parts)

        @self.server.tool()
        async def get_status(
            context_id: str = "default",
        ) -> str:
            """Get current session status.

            Shows loaded context info, iteration count, variables, and history.

            Args:
                context_id: Session identifier

            Returns:
                Formatted status report
            """
            if context_id not in self._sessions:
                return f"No session with ID '{context_id}'. Use load_context to start."

            session = self._sessions[context_id]
            meta = session.meta
            repl = session.repl

            # Get all user-defined variables (excluding builtins and helpers)
            excluded = {"ctx", "peek", "lines", "search", "chunk", "cite", "__builtins__"}
            variables = {
                k: type(v).__name__
                for k, v in repl._namespace.items()
                if k not in excluded and not k.startswith("_")
            }

            parts = [
                "## Session Status",
                "",
                f"**Session ID:** `{context_id}`",
                f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Iterations:** {session.iterations}",
                "",
                "### Context Info",
                f"- Format: {meta.format.value}",
                f"- Size: {meta.size_chars:,} characters",
                f"- Lines: {meta.size_lines:,}",
                f"- Est. tokens: ~{meta.size_tokens_estimate:,}",
            ]

            if variables:
                parts.extend([
                    "",
                    "### User Variables",
                ])
                for name, vtype in variables.items():
                    parts.append(f"- `{name}`: {vtype}")

            if session.think_history:
                parts.extend([
                    "",
                    "### Reasoning History",
                ])
                for i, q in enumerate(session.think_history[-5:], 1):
                    parts.append(f"{i}. {q[:100]}{'...' if len(q) > 100 else ''}")

            # Convergence metrics
            parts.extend([
                "",
                "### Convergence Metrics",
                f"- Evidence collected: {len(session.evidence)}",
            ])

            if session.confidence_history:
                latest_conf = session.confidence_history[-1]
                parts.append(f"- Latest confidence: {latest_conf:.1%}")
                if len(session.confidence_history) >= 2:
                    trend = session.confidence_history[-1] - session.confidence_history[-2]
                    trend_str = "↑" if trend > 0 else "↓" if trend < 0 else "→"
                    parts.append(f"- Confidence trend: {trend_str} ({trend:+.1%})")
                parts.append(f"- Confidence history: {[f'{c:.0%}' for c in session.confidence_history[-5:]]}")

            if session.information_gain:
                total_gain = sum(session.information_gain)
                recent_gain = sum(session.information_gain[-3:]) if len(session.information_gain) >= 3 else total_gain
                parts.append(f"- Total information gain: {total_gain} evidence pieces")
                parts.append(f"- Recent gain (last 3): {recent_gain}")

            if session.chunks:
                parts.append(f"- Chunks mapped: {len(session.chunks)}")

            if session.evidence:
                parts.extend([
                    "",
                    "*Use `get_evidence()` to view citations.*",
                ])

            return "\n".join(parts)

        @self.server.tool()
        async def get_evidence(
            context_id: str = "default",
            limit: int = 20,
            offset: int = 0,
            source: Literal["any", "search", "peek", "exec", "manual", "action"] = "any",
            output: Literal["markdown", "json"] = "markdown",
        ) -> str:
            """Retrieve collected evidence/citations for a session.

            Args:
                context_id: Session identifier
                limit: Max number of evidence items to return (default: 20)
                offset: Starting index (default: 0)
                source: Optional source filter (default: "any")
                output: "markdown" or "json" (default: "markdown")

            Returns:
                Evidence list, formatted for inspection or programmatic parsing.
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            evidence = session.evidence
            if source != "any":
                evidence = [e for e in evidence if e.source == source]

            total = len(evidence)
            offset = max(0, offset)
            limit = 20 if limit <= 0 else limit

            page = evidence[offset : offset + limit]

            if output == "json":
                payload = [
                    {
                        "index": offset + i,
                        "source": ev.source,
                        "line_range": ev.line_range,
                        "pattern": ev.pattern,
                        "note": ev.note,
                        "snippet": ev.snippet,
                        "timestamp": ev.timestamp.isoformat(),
                    }
                    for i, ev in enumerate(page, 1)
                ]
                return json.dumps(
                    {"context_id": context_id, "total": total, "items": payload},
                    ensure_ascii=False,
                    indent=2,
                )

            parts = [
                "## Evidence",
                "",
                f"**Session ID:** `{context_id}`",
                f"**Total items:** {total}",
                f"**Showing:** {len(page)} (offset={offset}, limit={limit})",
            ]
            if source != "any":
                parts.append(f"**Source filter:** `{source}`")
            parts.append("")

            if not page:
                parts.append("*(No evidence collected yet)*")
                return "\n".join(parts)

            for i, ev in enumerate(page, offset + 1):
                source_info = f"[{ev.source}]"
                if ev.line_range:
                    source_info += f" lines {ev.line_range[0]}-{ev.line_range[1]}"
                if ev.pattern:
                    source_info += f" pattern: `{ev.pattern}`"
                if ev.note:
                    source_info += f" note: {ev.note}"
                snippet = ev.snippet.strip()
                parts.append(f"{i}. {source_info}: \"{snippet}\"")

            return "\n".join(parts)

        @self.server.tool()
        async def finalize(
            answer: str,
            confidence: Literal["high", "medium", "low"] = "medium",
            reasoning_summary: str | None = None,
            context_id: str = "default",
        ) -> str:
            """Mark the task complete with your final answer.

            Use this when you have arrived at your final answer after
            exploring the context and reasoning through the problem.

            Args:
                answer: Your final answer
                confidence: How confident you are (high/medium/low)
                reasoning_summary: Optional brief summary of your reasoning
                context_id: Session identifier

            Returns:
                Formatted final answer
            """
            parts = [
                "## Final Answer",
                "",
                answer,
            ]

            if reasoning_summary:
                parts.extend([
                    "",
                    "---",
                    "",
                    f"**Reasoning:** {reasoning_summary}",
                ])

            if context_id in self._sessions:
                session = self._sessions[context_id]
                parts.extend([
                    "",
                    f"*Completed after {session.iterations} iterations.*",
                ])

            parts.append(f"\n**Confidence:** {confidence}")

            # Add evidence citations if available
            if context_id in self._sessions:
                session = self._sessions[context_id]
                if session.evidence:
                    parts.extend([
                        "",
                        "---",
                        "",
                        "### Evidence Citations",
                    ])
                    for i, ev in enumerate(session.evidence[-10:], 1):  # Last 10 pieces of evidence
                        source_info = f"[{ev.source}]"
                        if ev.line_range:
                            source_info += f" lines {ev.line_range[0]}-{ev.line_range[1]}"
                        if ev.pattern:
                            source_info += f" pattern: `{ev.pattern}`"
                        if ev.note:
                            source_info += f" note: {ev.note}"
                        parts.append(f"{i}. {source_info}: \"{ev.snippet[:80]}...\"" if len(ev.snippet) > 80 else f"{i}. {source_info}: \"{ev.snippet}\"")

            return "\n".join(parts)

        # =====================================================================
        # Remote MCP orchestration (v0.5 last mile)
        # =====================================================================

        def _require_actions(confirm: bool) -> str | None:
            if not self.action_config.enabled:
                return "Error: Actions are disabled. Start the server with `--enable-actions`."
            if self.action_config.require_confirmation and not confirm:
                return "Error: Confirmation required. Re-run with `confirm=true`."
            return None

        @self.server.tool()
        async def add_remote_server(
            server_id: str,
            command: str,
            args: list[str] | None = None,
            cwd: str | None = None,
            env: dict[str, str] | None = None,
            allow_tools: list[str] | None = None,
            deny_tools: list[str] | None = None,
            connect: bool = True,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Register a remote MCP server (stdio transport) for orchestration.

            This spawns a subprocess and speaks MCP over stdin/stdout.

            Args:
                server_id: Local identifier for the remote server
                command: Executable to run (e.g. 'python3')
                args: Command arguments (e.g. ['-m','some.mcp.server'])
                cwd: Working directory for the subprocess
                env: Extra environment variables for the subprocess
                allow_tools: Optional allowlist of tool names
                deny_tools: Optional denylist of tool names
                connect: If true, connect immediately and cache tool list
                confirm: Required if actions are enabled
                output: Output format
            """
            err = _require_actions(confirm)
            if err:
                return err

            if server_id in self._remote_servers:
                return f"Error: Remote server '{server_id}' already exists."

            handle = _RemoteServerHandle(
                command=command,
                args=args or [],
                cwd=Path(cwd) if cwd else None,
                env=env,
                allow_tools=allow_tools,
                deny_tools=deny_tools,
            )
            self._remote_servers[server_id] = handle

            tools: list[dict[str, Any]] | None = None
            if connect:
                ok, res = await self._ensure_remote_server(server_id)
                if not ok:
                    return str(res)
                handle = res  # type: ignore[assignment]
                try:
                    r = await handle.session.list_tools()  # type: ignore[union-attr]
                    tools = _to_jsonable(r)
                except Exception:
                    tools = None

            payload: dict[str, Any] = {
                "server_id": server_id,
                "command": command,
                "args": args or [],
                "cwd": str(handle.cwd) if handle.cwd else None,
                "allow_tools": allow_tools,
                "deny_tools": deny_tools,
                "connected": handle.session is not None,
                "tools": tools,
            }
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def list_remote_servers(
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            """List all registered remote MCP servers."""
            items = []
            for sid, h in self._remote_servers.items():
                items.append(
                    {
                        "server_id": sid,
                        "command": h.command,
                        "args": h.args,
                        "cwd": str(h.cwd) if h.cwd else None,
                        "connected": h.session is not None,
                        "connected_at": h.connected_at.isoformat() if h.connected_at else None,
                        "allow_tools": h.allow_tools,
                        "deny_tools": h.deny_tools,
                    }
                )
            return _format_payload({"count": len(items), "items": items}, output=output)

        @self.server.tool()
        async def list_remote_tools(
            server_id: str,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            """List tools available on a remote MCP server."""
            err = _require_actions(confirm)
            if err:
                return err

            ok, res = await self._ensure_remote_server(server_id)
            if not ok:
                return str(res)
            ok2, tools = await self._remote_list_tools(server_id)
            if not ok2:
                return str(tools)
            return _format_payload(tools, output=output)

        @self.server.tool()
        async def call_remote_tool(
            server_id: str,
            tool: str,
            arguments: dict[str, Any] | None = None,
            timeout_seconds: float | None = 30.0,
            recipe_id: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Call a tool on a remote MCP server and record it in the run trace.

            Args:
                server_id: Registered remote server ID
                tool: Tool name
                arguments: Tool arguments object
                timeout_seconds: Tool call timeout (best-effort)
                recipe_id: If provided, attaches call to a recipe trace/evidence
                confirm: Required if actions are enabled
                output: Output format
            """
            err = _require_actions(confirm)
            if err:
                return err

            ok, res = await self._ensure_remote_server(server_id)
            if not ok:
                return str(res)
            ok2, result_jsonable = await self._remote_call_tool(
                server_id=server_id,
                tool=tool,
                arguments=arguments,
                timeout_seconds=timeout_seconds,
                recipe_id=recipe_id,
            )
            if not ok2:
                return str(result_jsonable)

            if output == "json":
                return json.dumps(result_jsonable, ensure_ascii=False, indent=2)

            parts = [
                "## Remote Tool Result",
                "",
                f"**Server:** `{server_id}`",
                f"**Tool:** `{tool}`",
                "",
                "```json",
                json.dumps(result_jsonable, ensure_ascii=False, indent=2)[:10_000],
                "```",
            ]
            return "\n".join(parts)

        @self.server.tool()
        async def close_remote_server(
            server_id: str,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Close a remote MCP server connection (terminates subprocess)."""
            err = _require_actions(confirm)
            if err:
                return err

            ok, msg = await self._close_remote_server(server_id)
            if output == "json":
                return json.dumps({"ok": ok, "message": msg}, indent=2)
            return msg

        @self.server.tool()
        async def chunk_context(
            chunk_size: int = 2000,
            overlap: int = 200,
            context_id: str = "default",
        ) -> str:
            """Split context into chunks and return metadata for navigation.

            Use this to understand how to navigate large documents systematically.
            Returns chunk boundaries so you can peek specific chunks.

            Args:
                chunk_size: Characters per chunk (default: 2000)
                overlap: Overlap between chunks (default: 200)
                context_id: Session identifier

            Returns:
                JSON with chunk metadata (index, start_char, end_char, preview)
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]
            repl = session.repl
            session.iterations += 1

            fn = repl.get_variable("chunk")
            if not callable(fn):
                return "Error: chunk() helper is not available"

            try:
                chunks = fn(chunk_size, overlap)
            except ValueError as e:
                return f"Error: {e}"

            # Build chunk metadata
            chunk_meta = []
            pos = 0
            for i, chunk_text in enumerate(chunks):
                chunk_meta.append({
                    "index": i,
                    "start_char": pos,
                    "end_char": pos + len(chunk_text),
                    "size": len(chunk_text),
                    "preview": chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text,
                })
                pos += len(chunk_text) - overlap if i < len(chunks) - 1 else len(chunk_text)

            # Store in session for reference
            session.chunks = chunk_meta

            parts = [
                "## Context Chunks",
                "",
                f"**Total chunks:** {len(chunks)}",
                f"**Chunk size:** {chunk_size} chars",
                f"**Overlap:** {overlap} chars",
                "",
                "### Chunk Map",
                "",
            ]

            for cm in chunk_meta:
                parts.append(f"- **Chunk {cm['index']}** ({cm['start_char']}-{cm['end_char']}): {cm['preview'][:60]}...")

            parts.extend([
                "",
                "*Use `peek_context(start, end, unit='chars')` to view specific chunks.*",
            ])

            return "\n".join(parts)

        @self.server.tool()
        async def evaluate_progress(
            current_understanding: str,
            remaining_questions: list[str] | None = None,
            confidence_score: float = 0.5,
            context_id: str = "default",
        ) -> str:
            """Self-evaluate your progress to decide whether to continue or finalize.

            Use this periodically to assess whether you have enough information
            to answer the question, or if more exploration is needed.

            Args:
                current_understanding: Summary of what you've learned so far
                remaining_questions: List of unanswered questions (if any)
                confidence_score: Your confidence 0.0-1.0 in current understanding
                context_id: Session identifier

            Returns:
                Structured evaluation with recommendation (continue/finalize)
            """
            if context_id in self._sessions:
                session = self._sessions[context_id]
                session.iterations += 1
                session.confidence_history.append(confidence_score)

            parts = [
                "## Progress Evaluation",
                "",
                "**Current Understanding:**",
                current_understanding,
                "",
            ]

            if remaining_questions:
                parts.extend([
                    "**Remaining Questions:**",
                ])
                for q in remaining_questions:
                    parts.append(f"- {q}")
                parts.append("")

            parts.append(f"**Confidence Score:** {confidence_score:.1%}")

            # Analyze convergence
            if context_id in self._sessions:
                session = self._sessions[context_id]
                parts.extend([
                    "",
                    "### Convergence Analysis",
                    f"- Iterations: {session.iterations}",
                    f"- Evidence collected: {len(session.evidence)}",
                ])

                if len(session.confidence_history) >= 2:
                    trend = session.confidence_history[-1] - session.confidence_history[-2]
                    trend_str = "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
                    parts.append(f"- Confidence trend: {trend_str} ({trend:+.1%})")

                if session.information_gain:
                    recent_gain = sum(session.information_gain[-3:]) if len(session.information_gain) >= 3 else sum(session.information_gain)
                    parts.append(f"- Recent information gain: {recent_gain} evidence pieces (last 3 ops)")

            # Recommendation
            parts.extend([
                "",
                "---",
                "",
                "### Recommendation",
            ])

            if confidence_score >= 0.8:
                parts.append("**READY TO FINALIZE** - High confidence achieved. Use `finalize()` to provide your answer.")
            elif confidence_score >= 0.5 and not remaining_questions:
                parts.append("**CONSIDER FINALIZING** - Moderate confidence with no remaining questions. You may finalize or continue exploring.")
            else:
                parts.append("**CONTINUE EXPLORING** - More investigation needed. Use `search_context`, `peek_context`, or `think` to gather more evidence.")

            return "\n".join(parts)

        @self.server.tool()
        async def summarize_so_far(
            include_evidence: bool = True,
            include_variables: bool = True,
            clear_history: bool = False,
            context_id: str = "default",
        ) -> str:
            """Compress reasoning history to manage context window.

            Use this when your conversation is getting long to create a
            condensed summary of your progress that can replace earlier context.

            Args:
                include_evidence: Include evidence citations in summary
                include_variables: Include computed variables
                clear_history: Clear think_history after summarizing (to save memory)
                context_id: Session identifier

            Returns:
                Compressed reasoning trace
            """
            if context_id not in self._sessions:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session = self._sessions[context_id]

            parts = [
                "## Session Summary",
                "",
                f"**Session ID:** `{context_id}`",
                f"**Duration:** {datetime.now() - session.created_at}",
                f"**Iterations:** {session.iterations}",
                "",
            ]

            # Reasoning history
            if session.think_history:
                parts.extend([
                    "### Reasoning Steps",
                ])
                for i, q in enumerate(session.think_history[-5:], 1):
                    parts.append(f"{i}. {q[:150]}{'...' if len(q) > 150 else ''}")
                parts.append("")

            # Evidence summary
            if include_evidence and session.evidence:
                parts.extend([
                    "### Evidence Collected",
                    f"Total: {len(session.evidence)} pieces",
                    "",
                ])
                # Group by source
                by_source: dict[str, int] = {}
                for ev in session.evidence:
                    by_source[ev.source] = by_source.get(ev.source, 0) + 1
                for source, count in by_source.items():
                    parts.append(f"- {source}: {count}")
                parts.append("")

                # Show key evidence
                parts.append("**Key Evidence:**")
                for ev in session.evidence[-5:]:  # Last 5
                    snippet = ev.snippet[:100] + ("..." if len(ev.snippet) > 100 else "")
                    note = f" (note: {ev.note})" if ev.note else ""
                    parts.append(f"- [{ev.source}] {snippet}{note}")
                parts.append("")

            # Variables
            if include_variables:
                repl = session.repl
                excluded = {"ctx", "peek", "lines", "search", "chunk", "cite", "__builtins__"}
                variables = {
                    k: v for k, v in repl._namespace.items()
                    if k not in excluded and not k.startswith("_")
                }
                if variables:
                    parts.extend([
                        "### Computed Variables",
                    ])
                    for name, val in variables.items():
                        val_str = str(val)[:100]
                        parts.append(f"- `{name}` = {val_str}{'...' if len(str(val)) > 100 else ''}")
                    parts.append("")

            # Convergence
            if session.confidence_history:
                latest = session.confidence_history[-1]
                parts.extend([
                    "### Convergence Status",
                    f"- Latest confidence: {latest:.1%}",
                    f"- Confidence history: {[f'{c:.0%}' for c in session.confidence_history[-5:]]}",
                ])

            # Clear history if requested
            if clear_history:
                session.think_history = []
                parts.extend([
                    "",
                    "*Reasoning history cleared to save memory.*",
                ])

            return "\n".join(parts)

        # =====================================================================
        # Recipe/Kytchenfile Tools (v0.5)
        # =====================================================================

        @self.server.tool()
        async def load_recipe(
            path: str,
            recipe_id: str = "default",
            confirm: bool = False,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Load an Kytchenfile recipe for execution.

            An Kytchenfile defines a reproducible analysis run with datasets,
            query, tool config, and budget constraints.

            Args:
                path: Path to the Kytchenfile (JSON or YAML)
                recipe_id: Identifier for this recipe (default: "default")
                confirm: Required if actions are enabled
                output: Output format

            Returns:
                Recipe summary with datasets and configuration
            """
            err = _require_actions(confirm)
            if err:
                return err

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            try:
                config = load_kytchenfile(p)
            except Exception as e:
                return f"Error loading Kytchenfile: {e}"

            runner = RecipeRunner(config)
            runner.start()

            # Load datasets and compute baseline
            try:
                loaded = runner.load_datasets()
            except Exception as e:
                return f"Error loading datasets: {e}"

            self._recipes[recipe_id] = runner

            # Also load datasets into sessions for exploration
            for ds_id, content in loaded.items():
                ctx_id = f"{recipe_id}:{ds_id}"
                fmt = _detect_format(content)
                meta = _analyze_text_context(content, fmt)
                repl = REPLEnvironment(
                    context=content,
                    context_var_name="ctx",
                    config=self.sandbox_config,
                    loop=asyncio.get_running_loop(),
                )
                self._sessions[ctx_id] = _Session(repl=repl, meta=meta)

            if output == "json":
                return _format_payload({
                    "recipe_id": recipe_id,
                    "query": config.query,
                    "datasets": [d.to_dict() for d in config.datasets],
                    "baseline_tokens": runner.metrics.tokens_baseline,
                    "model": config.model,
                    "max_iterations": config.max_iterations,
                }, output="json")

            parts = [
                "## Recipe Loaded",
                "",
                f"**Recipe ID:** `{recipe_id}`",
                f"**Query:** {config.query}",
                "",
                "### Datasets",
            ]
            for ds in config.datasets:
                parts.append(f"- `{ds.id}`: {ds.size_bytes:,} bytes, ~{ds.size_tokens_estimate:,} tokens")
                if ds.content_hash:
                    parts.append(f"  - Hash: `{ds.content_hash[:32]}...`")

            parts.extend([
                "",
                "### Budget",
                f"- Max iterations: {config.max_iterations}",
                f"- Max tokens: {config.max_tokens or 'unlimited'}",
                f"- Timeout: {config.timeout_seconds}s",
                "",
                "### Baseline Estimate",
                f"- Context-stuffing approach would use ~{runner.metrics.tokens_baseline:,} tokens",
                "",
                "*Use `get_metrics(recipe_id)` during execution to track efficiency.*",
            ])
            return "\n".join(parts)

        @self.server.tool()
        async def get_metrics(
            recipe_id: str = "default",
            context_id: str | None = None,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Get token efficiency metrics for a recipe or session.

            Shows tokens used vs baseline (context-stuffing approach) and
            computes efficiency ratio = tokens_saved / tokens_baseline.

            Args:
                recipe_id: Recipe identifier
                context_id: Optional specific context to get metrics for
                output: Output format

            Returns:
                Metrics including tokens_used, tokens_baseline, tokens_saved, efficiency_ratio
            """
            if recipe_id not in self._recipes:
                # Fall back to session-based metrics
                cid = context_id or "default"
                if cid not in self._sessions:
                    return f"Error: No recipe '{recipe_id}' or session '{cid}' found"

                session = self._sessions[cid]
                # Estimate baseline from session metadata
                baseline = session.meta.size_tokens_estimate * 3 + 500 * 3
                # Estimate tokens used from iterations (rough: 500 per iteration)
                used = session.iterations * 500
                saved = max(0, baseline - used)
                ratio = saved / baseline if baseline > 0 else 0.0

                metrics = {
                    "context_id": cid,
                    "tokens_used": used,
                    "tokens_baseline": baseline,
                    "tokens_saved": saved,
                    "efficiency_ratio": round(ratio, 4),
                    "iterations": session.iterations,
                    "evidence_count": len(session.evidence),
                }
            else:
                runner = self._recipes[recipe_id]
                runner.metrics.compute_efficiency()
                metrics = {
                    "recipe_id": recipe_id,
                    **runner.metrics.to_dict(),
                }

            if output == "json":
                return json.dumps(metrics, indent=2)

            parts = [
                "## Token Efficiency Metrics",
                "",
                f"**Tokens Used:** {metrics['tokens_used']:,}",
                f"**Tokens Baseline:** {metrics['tokens_baseline']:,}",
                f"**Tokens Saved:** {metrics['tokens_saved']:,}",
                f"**Efficiency Ratio:** {metrics['efficiency_ratio']:.1%}",
                "",
                f"*Iterations: {metrics['iterations']} | Evidence: {metrics.get('evidence_count', 0)}*",
            ]

            if metrics['efficiency_ratio'] > 0.5:
                parts.append("")
                parts.append(f"🍳 **Kytchen saved {metrics['efficiency_ratio']:.0%} of tokens vs context-stuffing!**")

            return "\n".join(parts)

        @self.server.tool()
        async def finalize_recipe(
            recipe_id: str = "default",
            answer: str = "",
            success: bool = True,
            context_id: str | None = None,
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Finalize a recipe run and generate the result bundle.

            Collects all evidence, computes final metrics, and produces
            a reproducible result that can be exported.

            Args:
                recipe_id: Recipe identifier
                answer: Final answer from the analysis
                success: Whether the analysis succeeded
                context_id: Optional context to pull evidence from
                output: Output format

            Returns:
                Final result summary with metrics and evidence count
            """
            if recipe_id not in self._recipes:
                return f"Error: No recipe '{recipe_id}' found. Use load_recipe first."

            runner = self._recipes[recipe_id]

            # Collect evidence from associated sessions
            for ds in runner.config.datasets:
                ctx_id = f"{recipe_id}:{ds.id}"
                if ctx_id in self._sessions:
                    session = self._sessions[ctx_id]
                    for ev in session.evidence:
                        runner.add_sauce(
                            source=ev.source,
                            snippet=ev.snippet,
                            line_range=ev.line_range,
                            pattern=ev.pattern,
                            note=ev.note,
                            dataset_id=ds.id,
                        )

            # Also collect from specified context_id
            if context_id and context_id in self._sessions:
                session = self._sessions[context_id]
                for ev in session.evidence:
                    runner.add_sauce(
                        source=ev.source,
                        snippet=ev.snippet,
                        line_range=ev.line_range,
                        pattern=ev.pattern,
                        note=ev.note,
                    )

            result = runner.finalize(answer, success)
            self._recipe_results[recipe_id] = result

            if output == "json":
                return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

            parts = [
                "## Recipe Result",
                "",
                f"**Recipe ID:** `{recipe_id}`",
                f"**Success:** {result.success}",
                "",
                "### Answer",
                result.answer,
                "",
                "### Metrics",
                f"- Tokens used: {result.metrics.tokens_used:,}",
                f"- Tokens saved: {result.metrics.tokens_saved:,}",
                f"- Efficiency: {result.metrics.efficiency_ratio:.1%}",
                f"- Iterations: {result.metrics.iterations}",
                f"- Wall time: {result.metrics.wall_time_seconds:.2f}s",
                "",
                "### Sauce",
                f"- Total items: {len(result.sauce_bundle.sauce)}",
                "",
                f"*Use `export_result('{recipe_id}')` to save the full result bundle.*",
            ]
            return "\n".join(parts)

        @self.server.tool()
        async def export_result(
            recipe_id: str = "default",
            path: str = "kytchen_result.json",
            include_trace: bool = True,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            """Export a recipe result to a file.

            Produces a JSON file with the complete reproducible result:
            recipe config, answer, metrics, evidence bundle, and execution trace.

            Args:
                recipe_id: Recipe identifier
                path: Output file path
                include_trace: Whether to include the execution trace
                confirm: Required if actions are enabled

            Returns:
                Confirmation with file path and size
            """
            err = _require_actions(confirm)
            if err:
                return err

            if recipe_id not in self._recipe_results:
                return f"Error: No finalized result for recipe '{recipe_id}'. Use finalize_recipe first."

            result = self._recipe_results[recipe_id]

            try:
                p = _scoped_path(self.action_config.workspace_root, path)
            except Exception as e:
                return f"Error: {e}"

            data = result.to_dict()
            if not include_trace:
                data["trace"] = []

            content = json.dumps(data, indent=2, ensure_ascii=False)
            content_bytes = content.encode("utf-8")

            if len(content_bytes) > self.action_config.max_write_bytes:
                return f"Error: Result too large to export (>{self.action_config.max_write_bytes} bytes)"

            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "wb") as f:
                f.write(content_bytes)

            return _format_payload({
                "path": str(p),
                "bytes_written": len(content_bytes),
                "recipe_id": recipe_id,
                "evidence_count": len(result.sauce_bundle.sauce),
            }, output=output)

        @self.server.tool()
        async def sign_evidence(
            recipe_id: str = "default",
            signer_id: str = "local",
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            """Sign an evidence bundle for verification.

            Creates a cryptographic hash of the evidence bundle that can be
            verified later to ensure the evidence hasn't been tampered with.

            Note: This is a content hash signature, not a PKI signature.
            For full PKI signing, use an external signing service.

            Args:
                recipe_id: Recipe identifier
                signer_id: Identifier for the signer
                output: Output format

            Returns:
                Signed bundle summary with hash
            """
            if recipe_id not in self._recipe_results:
                return f"Error: No finalized result for recipe '{recipe_id}'. Use finalize_recipe first."

            result = self._recipe_results[recipe_id]
            bundle = result.sauce_bundle

            # Compute content hash as signature
            bundle.signature = bundle.compute_hash()
            bundle.signed_at = datetime.now().isoformat()
            bundle.signed_by = signer_id

            if output == "json":
                return json.dumps({
                    "recipe_id": recipe_id,
                    "signature": bundle.signature,
                    "signed_at": bundle.signed_at,
                    "signed_by": bundle.signed_by,
                    "evidence_count": len(bundle.sauce),
                }, indent=2)

            parts = [
                "## Sauce Bundle Signed",
                "",
                f"**Recipe ID:** `{recipe_id}`",
                f"**Signature:** `{bundle.signature}`",
                f"**Signed At:** {bundle.signed_at}",
                f"**Signed By:** {bundle.signed_by}",
                f"**Sauce Items:** {len(bundle.sauce)}",
                "",
                "*This hash can be used to verify the sauce bundle hasn't been modified.*",
            ]
            return "\n".join(parts)

        @self.server.tool()
        async def list_recipes(
            output: Literal["json", "markdown"] = "json",
        ) -> str:
            """List all loaded recipes and their status.

            Returns:
                List of recipes with their current state
            """
            items = []
            for rid, runner in self._recipes.items():
                finalized = rid in self._recipe_results
                items.append({
                    "recipe_id": rid,
                    "query": runner.config.query[:100],
                    "datasets": len(runner.config.datasets),
                    "iterations": runner.metrics.iterations,
                    "evidence_count": runner.metrics.evidence_count,
                    "finalized": finalized,
                })

            if output == "json":
                return json.dumps({"count": len(items), "items": items}, indent=2)

            if not items:
                return "No recipes loaded. Use `load_recipe` to load an Kytchenfile."

            parts = ["## Loaded Recipes", ""]
            for item in items:
                status = "✓ finalized" if item["finalized"] else "⏳ in progress"
                parts.append(f"- `{item['recipe_id']}`: {status}")
                parts.append(f"  - Query: {item['query']}")
                parts.append(f"  - Datasets: {item['datasets']} | Iterations: {item['iterations']} | Evidence: {item['evidence_count']}")

            return "\n".join(parts)

        # ─────────────────────────────────────────────────────────────────────
        # Git Tools
        # ─────────────────────────────────────────────────────────────────────

        @self.server.tool()
        async def git_status(
            short: bool = False,
            branch: bool = True,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """Show repository status.

            Args:
                short: Use short format output (-s flag)
                branch: Show branch information (--branch flag, default True)
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                Repository status including staged/unstaged changes
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            argv = ["git", "status"]
            if short:
                argv.append("-s")
            if branch:
                argv.append("--branch")

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_status", snippet=(payload.get("stdout") or "")[:200])
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def git_diff(
            target: str | None = None,
            staged: bool = False,
            name_only: bool = False,
            stat: bool = False,
            path: str | None = None,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """Show diff between commits/files.

            Args:
                target: Commit, branch, or range to diff against (e.g., "HEAD~1", "main..feature", "abc123")
                staged: Show staged changes (--staged/--cached flag)
                name_only: Only show names of changed files (--name-only)
                stat: Show diffstat summary (--stat)
                path: Limit diff to specific file/directory path
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                Diff output showing changes
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            argv = ["git", "diff"]
            if staged:
                argv.append("--staged")
            if name_only:
                argv.append("--name-only")
            if stat:
                argv.append("--stat")
            if target:
                argv.append(target)
            if path:
                try:
                    validated_path = _scoped_path(workspace_root, path)
                    argv.extend(["--", str(validated_path.relative_to(cwd_path))])
                except ValueError as e:
                    return f"Error: {e}"

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_diff", snippet=(payload.get("stdout") or "")[:200])
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def git_log(
            limit: int = 10,
            oneline: bool = False,
            all_branches: bool = False,
            author: str | None = None,
            since: str | None = None,
            until: str | None = None,
            grep: str | None = None,
            path: str | None = None,
            format: str | None = None,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """Show recent commits with filtering.

            Args:
                limit: Maximum number of commits to show (default: 10)
                oneline: Use one-line format (--oneline)
                all_branches: Show commits from all branches (--all)
                author: Filter by author name/email
                since: Show commits since date (e.g., "2024-01-01", "1 week ago")
                until: Show commits until date
                grep: Filter by commit message pattern
                path: Limit to commits affecting this file/directory
                format: Custom format string (e.g., "%H %s" for hash and subject)
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                Commit history
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            argv = ["git", "log", f"-{limit}"]
            if oneline:
                argv.append("--oneline")
            if all_branches:
                argv.append("--all")
            if author:
                argv.extend(["--author", author])
            if since:
                argv.extend(["--since", since])
            if until:
                argv.extend(["--until", until])
            if grep:
                argv.extend(["--grep", grep])
            if format:
                argv.extend(["--format", format])
            if path:
                try:
                    validated_path = _scoped_path(workspace_root, path)
                    argv.extend(["--", str(validated_path.relative_to(cwd_path))])
                except ValueError as e:
                    return f"Error: {e}"

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_log", snippet=(payload.get("stdout") or "")[:200])
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def git_blame(
            path: str,
            line_start: int | None = None,
            line_end: int | None = None,
            show_email: bool = False,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """Blame a file showing per-line commit info.

            Args:
                path: File path to blame (required)
                line_start: Starting line number for range (-L start,end)
                line_end: Ending line number for range
                show_email: Show author email instead of name (-e)
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                Line-by-line blame output with commit hash, author, date, and content
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            try:
                validated_path = _scoped_path(workspace_root, path)
            except ValueError as e:
                return f"Error: {e}"

            if not validated_path.exists():
                return f"Error: File not found: {path}"

            argv = ["git", "blame"]
            if show_email:
                argv.append("-e")
            if line_start is not None and line_end is not None:
                argv.extend(["-L", f"{line_start},{line_end}"])
            elif line_start is not None:
                argv.extend(["-L", f"{line_start},"])

            try:
                rel_path = validated_path.relative_to(cwd_path)
            except ValueError:
                rel_path = validated_path
            argv.append(str(rel_path))

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_blame", snippet=f"{path}:{line_start or 1}-{line_end or 'end'}")
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def git_show(
            ref: str = "HEAD",
            stat: bool = False,
            name_only: bool = False,
            path: str | None = None,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """Show contents of a specific commit.

            Args:
                ref: Commit hash, tag, or branch to show (default: HEAD)
                stat: Show file change summary (--stat)
                name_only: Show only names of changed files (--name-only)
                path: Limit to specific file path
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                Commit details including message and changes
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            argv = ["git", "show", ref]
            if stat:
                argv.append("--stat")
            if name_only:
                argv.append("--name-only")
            if path:
                try:
                    validated_path = _scoped_path(workspace_root, path)
                    argv.extend(["--", str(validated_path.relative_to(cwd_path))])
                except ValueError as e:
                    return f"Error: {e}"

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_show", snippet=f"ref={ref}")
            return _format_payload(payload, output=output)

        @self.server.tool()
        async def git_branch(
            all_branches: bool = False,
            verbose: bool = False,
            merged: bool = False,
            no_merged: bool = False,
            contains: str | None = None,
            cwd: str | None = None,
            confirm: bool = False,
            output: Literal["json", "markdown"] = "json",
            context_id: str = "default",
        ) -> str:
            """List or show branches.

            Args:
                all_branches: Show remote branches too (-a)
                verbose: Show last commit on each branch (-v)
                merged: Show only branches merged into HEAD (--merged)
                no_merged: Show only branches not merged into HEAD (--no-merged)
                contains: Show only branches containing this commit (--contains)
                cwd: Working directory (default: workspace root)
                confirm: Required if server started with --require-confirmation
                output: Output format ("json" or "markdown")
                context_id: Session identifier

            Returns:
                List of branches with optional details
            """
            err = _require_actions(confirm)
            if err:
                return err

            session = _get_session(context_id)
            if session is not None:
                session.iterations += 1

            workspace_root = self.action_config.workspace_root
            cwd_path = _scoped_path(workspace_root, cwd) if cwd else workspace_root

            argv = ["git", "branch"]
            if all_branches:
                argv.append("-a")
            if verbose:
                argv.append("-v")
            if merged:
                argv.append("--merged")
            if no_merged:
                argv.append("--no-merged")
            if contains:
                argv.extend(["--contains", contains])

            payload = await _run_subprocess(
                argv=argv,
                cwd=cwd_path,
                timeout_seconds=self.action_config.max_cmd_seconds,
            )
            _record_action(session, note="git_branch", snippet=(payload.get("stdout") or "")[:200])
            return _format_payload(payload, output=output)

    async def run(self, transport: str = "stdio") -> None:
        """Run the MCP server."""
        if transport != "stdio":
            raise ValueError("Only stdio transport is supported")

        await self.server.run_stdio_async()


def main() -> None:
    """CLI entry point: `kytchen-local` or `python -m kytchen.mcp.local_server`"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Kytchen as an API-free MCP server for local AI reasoning"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Code execution timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-output",
        type=int,
        default=10000,
        help="Maximum output characters (default: 10000)",
    )
    parser.add_argument(
        "--enable-actions",
        action="store_true",
        help="Enable action tools (run_command/read_file/write_file/run_tests)",
    )
    parser.add_argument(
        "--workspace-root",
        type=str,
        default=None,
        help="Workspace root for action tools (default: auto-detect git root or cwd)",
    )
    parser.add_argument(
        "--require-confirmation",
        action="store_true",
        help="Require confirm=true for action tools",
    )

    args = parser.parse_args()

    config = SandboxConfig(
        timeout_seconds=args.timeout,
        max_output_chars=args.max_output,
    )

    action_cfg = ActionConfig(
        enabled=bool(args.enable_actions),
        workspace_root=Path(args.workspace_root).resolve() if args.workspace_root else _detect_workspace_root(),
        require_confirmation=bool(args.require_confirmation),
    )

    server = KytchenMCPServerLocal(sandbox_config=config, action_config=action_cfg)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
