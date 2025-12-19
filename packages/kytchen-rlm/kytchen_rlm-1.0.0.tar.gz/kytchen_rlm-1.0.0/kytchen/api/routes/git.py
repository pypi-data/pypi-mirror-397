"""Git API routes for Kytchen workspaces."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import WorkspaceAuth
from ..db import get_db
from .kytchens import _resolve_kytchen, get_auth


router = APIRouter(prefix="/v1/kytchens", tags=["git"])


class GitCommandResult(BaseModel):
    """Result of a git command."""
    stdout: str
    stderr: str
    exit_code: int


def _detect_workspace_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd


async def _run_git(args: list[str], cwd: Path | None = None) -> GitCommandResult:
    """Run a git command asynchronously."""
    import asyncio

    proc = await asyncio.create_subprocess_exec(
        "git", *args,
        cwd=cwd or Path.cwd(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    return GitCommandResult(
        stdout=stdout.decode("utf-8", errors="replace"),
        stderr=stderr.decode("utf-8", errors="replace"),
        exit_code=proc.returncode or 0,
    )


@router.get("/{kytchen_id}/git/status", response_model=GitCommandResult)
async def git_status(
    kytchen_id: str,
    short: bool = Query(False, description="Use short format"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show repository status."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["status", "--branch"]
    if short:
        args.append("-s")

    return await _run_git(args, cwd=_detect_workspace_root())


@router.get("/{kytchen_id}/git/diff", response_model=GitCommandResult)
async def git_diff(
    kytchen_id: str,
    target: Optional[str] = Query(None, description="Commit/branch to diff against"),
    staged: bool = Query(False, description="Show staged changes"),
    stat: bool = Query(False, description="Show diffstat"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show diff between commits/files."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["diff"]
    if staged:
        args.append("--staged")
    if stat:
        args.append("--stat")
    if target:
        args.append(target)

    return await _run_git(args, cwd=_detect_workspace_root())


@router.get("/{kytchen_id}/git/log", response_model=GitCommandResult)
async def git_log(
    kytchen_id: str,
    limit: int = Query(10, description="Number of commits to show"),
    oneline: bool = Query(False, description="Use one-line format"),
    author: Optional[str] = Query(None, description="Filter by author"),
    since: Optional[str] = Query(None, description="Show commits since date"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show commit history."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["log", f"-{limit}"]
    if oneline:
        args.append("--oneline")
    if author:
        args.extend(["--author", author])
    if since:
        args.extend(["--since", since])

    return await _run_git(args, cwd=_detect_workspace_root())


@router.get("/{kytchen_id}/git/blame", response_model=GitCommandResult)
async def git_blame(
    kytchen_id: str,
    path: str = Query(..., description="File path to blame"),
    line_start: Optional[int] = Query(None, description="Start line"),
    line_end: Optional[int] = Query(None, description="End line"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show per-line commit info for a file."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["blame"]
    if line_start is not None and line_end is not None:
        args.extend(["-L", f"{line_start},{line_end}"])
    elif line_start is not None:
        args.extend(["-L", f"{line_start},"])
    args.append(path)

    return await _run_git(args, cwd=_detect_workspace_root())


@router.get("/{kytchen_id}/git/show", response_model=GitCommandResult)
async def git_show(
    kytchen_id: str,
    ref: str = Query("HEAD", description="Commit reference to show"),
    stat: bool = Query(False, description="Show diffstat"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show contents of a specific commit."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["show", ref]
    if stat:
        args.append("--stat")

    return await _run_git(args, cwd=_detect_workspace_root())


@router.get("/{kytchen_id}/git/branch", response_model=GitCommandResult)
async def git_branch(
    kytchen_id: str,
    all_branches: bool = Query(False, alias="all", description="Show all branches"),
    verbose: bool = Query(False, description="Show last commit"),
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
):
    """List branches."""
    await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    args = ["branch"]
    if all_branches:
        args.append("-a")
    if verbose:
        args.append("-v")

    return await _run_git(args, cwd=_detect_workspace_root())
