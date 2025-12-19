"""Git commands for Kytchen CLI.

Mirrors the MCP git tools, but runs locally within a selected workspace.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import print_error

app = typer.Typer(
    name="git",
    help="Git commands (run inside the current workspace)",
    no_args_is_help=True,
)

WORKSPACES_FILE = Path.home() / ".kytchen" / "workspaces.json"


def _load_workspaces() -> dict[str, Any]:
    if not WORKSPACES_FILE.exists():
        return {"current": None, "workspaces": {}}

    try:
        return json.loads(WORKSPACES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"current": None, "workspaces": {}}


def _resolve_workspace_path(workspace: str | None) -> Path | None:
    data = _load_workspaces()
    workspaces = data.get("workspaces", {})

    name = workspace or data.get("current")
    if not name:
        return None

    raw = workspaces.get(name)
    if not raw:
        return None

    p = Path(str(raw)).expanduser().resolve()
    return p


def _resolve_cwd(cwd: str | None, workspace: str | None) -> Path:
    if cwd:
        return Path(cwd).expanduser().resolve()

    ws_path = _resolve_workspace_path(workspace)
    if ws_path is not None:
        return ws_path

    return Path.cwd().resolve()


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

    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "stdout": stdout,
        "stderr": stderr,
    }


def _run_git(argv: list[str], cwd: Path, timeout_seconds: float) -> dict[str, Any]:
    try:
        return asyncio.run(_run_subprocess(argv=argv, cwd=cwd, timeout_seconds=timeout_seconds))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(_run_subprocess(argv=argv, cwd=cwd, timeout_seconds=timeout_seconds))
        finally:
            loop.close()


def _print_git_result(payload: dict[str, Any]) -> None:
    exit_code = int(payload.get("exit_code") or 0)
    timed_out = bool(payload.get("timed_out"))
    stdout = str(payload.get("stdout") or "")
    stderr = str(payload.get("stderr") or "")

    if timed_out:
        print_error("Git command timed out")

    if stdout:
        sys.stdout.write(stdout)
        if not stdout.endswith("\n"):
            sys.stdout.write("\n")
    if stderr:
        sys.stderr.write(stderr)
        if not stderr.endswith("\n"):
            sys.stderr.write("\n")

    if exit_code != 0:
        raise typer.Exit(exit_code)


@app.command(name="status")
def status_command(
    short: bool = typer.Option(False, "--short", "-s", help="Use short format"),
    branch: bool = typer.Option(True, "--branch/--no-branch", help="Show branch info"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)
    argv = ["git", "status"]
    if short:
        argv.append("-s")
    if branch:
        argv.append("--branch")

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


@app.command(name="diff")
def diff_command(
    target: Optional[str] = typer.Argument(None, help="Commit, branch, or range (e.g. HEAD~1)"),
    staged: bool = typer.Option(False, "--staged", help="Show staged changes"),
    name_only: bool = typer.Option(False, "--name-only", help="Only show changed file names"),
    stat: bool = typer.Option(False, "--stat", help="Show diffstat summary"),
    path: Optional[str] = typer.Option(None, "--path", help="Limit diff to a path"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)
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
        argv.extend(["--", path])

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


@app.command(name="log")
def log_command(
    limit: int = typer.Option(10, "--limit", "-n", help="Max commits to show"),
    oneline: bool = typer.Option(False, "--oneline", help="Use one-line format"),
    all_branches: bool = typer.Option(False, "--all", help="Show all branches"),
    author: Optional[str] = typer.Option(None, "--author", help="Filter by author"),
    since: Optional[str] = typer.Option(None, "--since", help="Show commits since date"),
    until: Optional[str] = typer.Option(None, "--until", help="Show commits until date"),
    grep: Optional[str] = typer.Option(None, "--grep", help="Filter by commit message"),
    path: Optional[str] = typer.Option(None, "--path", help="Limit to a path"),
    format: Optional[str] = typer.Option(None, "--format", help="Custom format string"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)

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
        argv.extend(["--", path])

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


@app.command(name="blame")
def blame_command(
    file: str = typer.Argument(..., help="File path to blame"),
    line_start: Optional[int] = typer.Option(None, "--line-start", help="Start line for range"),
    line_end: Optional[int] = typer.Option(None, "--line-end", help="End line for range"),
    show_email: bool = typer.Option(False, "--email", "-e", help="Show author email"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)

    argv = ["git", "blame"]
    if show_email:
        argv.append("-e")
    if line_start is not None and line_end is not None:
        argv.extend(["-L", f"{line_start},{line_end}"])
    elif line_start is not None:
        argv.extend(["-L", f"{line_start},"])

    argv.append(file)

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


@app.command(name="show")
def show_command(
    ref: str = typer.Argument("HEAD", help="Commit, tag, or branch (default: HEAD)"),
    stat: bool = typer.Option(False, "--stat", help="Show summary"),
    name_only: bool = typer.Option(False, "--name-only", help="Show only file names"),
    path: Optional[str] = typer.Option(None, "--path", help="Limit to a path"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)

    argv = ["git", "show", ref]
    if stat:
        argv.append("--stat")
    if name_only:
        argv.append("--name-only")
    if path:
        argv.extend(["--", path])

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


@app.command(name="branch")
def branch_command(
    all_branches: bool = typer.Option(False, "--all", "-a", help="Show remote branches too"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show last commit on each branch"),
    merged: bool = typer.Option(False, "--merged", help="Show merged branches"),
    no_merged: bool = typer.Option(False, "--no-merged", help="Show unmerged branches"),
    contains: Optional[str] = typer.Option(None, "--contains", help="Show branches containing commit"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace name"),
    cwd: Optional[str] = typer.Option(None, "--cwd", help="Working directory (overrides workspace)"),
    timeout: float = typer.Option(10.0, "--timeout", help="Timeout in seconds"),
) -> None:
    cwd_path = _resolve_cwd(cwd=cwd, workspace=workspace)

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

    payload = _run_git(argv=argv, cwd=cwd_path, timeout_seconds=timeout)
    _print_git_result(payload)


if __name__ == "__main__":
    app()
