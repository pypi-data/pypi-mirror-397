"""Markdown exporter for Kytchen recipe results.

Generates human-readable audit documents from RecipeResult.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kytchen.recipe import RecipeResult, SauceItem


def _format_timestamp(iso_str: str) -> str:
    """Format ISO timestamp for display."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return iso_str


def _format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = seconds / 60
        return f"{mins:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def _format_tokens(count: int) -> str:
    """Format token count with K/M suffix."""
    if count < 1000:
        return str(count)
    elif count < 1_000_000:
        return f"{count / 1000:.1f}K"
    else:
        return f"{count / 1_000_000:.1f}M"


def _render_sauce_item(item: SauceItem, index: int) -> str:
    """Render a single sauce/evidence item."""
    lines = []
    lines.append(f"### Evidence #{index + 1}")
    lines.append("")

    # Source and location
    source_info = f"**Source:** `{item.source}`"
    if item.dataset_id:
        source_info += f" (dataset: `{item.dataset_id}`)"
    lines.append(source_info)

    if item.line_range:
        lines.append(f"**Lines:** {item.line_range[0]}-{item.line_range[1]}")

    if item.pattern:
        lines.append(f"**Pattern:** `{item.pattern}`")

    lines.append(f"**Collected:** {_format_timestamp(item.timestamp)}")
    lines.append("")

    # Snippet
    if item.snippet:
        lines.append("**Content:**")
        lines.append("```")
        lines.append(item.snippet.strip())
        lines.append("```")
        lines.append("")

    # Note
    if item.note:
        lines.append(f"**Note:** {item.note}")
        lines.append("")

    return "\n".join(lines)


def render_markdown(result: RecipeResult) -> str:
    """Render a RecipeResult to Markdown format.

    Args:
        result: The recipe result to render

    Returns:
        Markdown string
    """
    lines: list[str] = []

    # Header
    lines.append("# Kytchen Analysis Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"**Schema:** `{result.schema}`")
    lines.append(f"**Recipe Hash:** `{result.recipe_hash[:16]}...`" if result.recipe_hash else "")
    lines.append("")

    # Status
    status_emoji = "✅" if result.success else "❌"
    lines.append(f"## Status: {status_emoji} {'Success' if result.success else 'Failed'}")
    lines.append("")

    if result.error:
        lines.append(f"> **Error:** {result.error}")
        lines.append("")

    # Query
    if result.recipe:
        lines.append("## Query")
        lines.append("")
        lines.append(f"> {result.recipe.query}")
        lines.append("")

    # Answer
    lines.append("## Answer")
    lines.append("")
    if result.answer:
        lines.append(result.answer)
    else:
        lines.append("*No answer provided*")
    lines.append("")

    # Metrics
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")

    metrics = result.metrics
    lines.append(f"| Tokens Used | {_format_tokens(metrics.tokens_used)} |")
    lines.append(f"| Tokens Baseline | {_format_tokens(metrics.tokens_baseline)} |")
    lines.append(f"| Tokens Saved | {_format_tokens(metrics.tokens_saved)} |")
    lines.append(f"| Efficiency | {metrics.efficiency_ratio * 100:.1f}% |")
    lines.append(f"| Iterations | {metrics.iterations} |")
    lines.append(f"| Evidence Count | {metrics.evidence_count} |")
    lines.append(f"| Wall Time | {_format_duration(metrics.wall_time_seconds)} |")
    lines.append(f"| Cost | ${metrics.cost_usd:.4f} |")
    lines.append("")

    # Token arbitrage summary
    if metrics.tokens_baseline > 0 and metrics.tokens_saved > 0:
        lines.append("### Token Arbitrage")
        lines.append("")
        lines.append("By using Kytchen's tool-driven approach instead of context-stuffing,")
        lines.append(f"this analysis saved **{_format_tokens(metrics.tokens_saved)} tokens** ")
        lines.append(f"({metrics.efficiency_ratio * 100:.1f}% reduction).")
        lines.append("")

    # Datasets/Ingredients
    if result.recipe and result.recipe.datasets:
        lines.append("## Datasets (Ingredients)")
        lines.append("")
        lines.append("| ID | Source | Format | Size | Hash |")
        lines.append("|----|--------|--------|------|------|")

        for ds in result.recipe.datasets:
            size = f"{ds.size_bytes:,} bytes" if ds.size_bytes else "N/A"
            hash_preview = ds.content_hash[:16] + "..." if ds.content_hash else "N/A"
            lines.append(f"| `{ds.id}` | {ds.source} | {ds.format} | {size} | `{hash_preview}` |")

        lines.append("")

    # Sauce/Evidence
    lines.append("## Evidence (Sauce)")
    lines.append("")

    if result.sauce_bundle and result.sauce_bundle.sauce:
        lines.append(f"*{len(result.sauce_bundle.sauce)} pieces of evidence collected*")
        lines.append("")

        for i, item in enumerate(result.sauce_bundle.sauce):
            lines.append(_render_sauce_item(item, i))
    else:
        lines.append("*No evidence collected*")
        lines.append("")

    # Signature
    if result.sauce_bundle and result.sauce_bundle.signature:
        lines.append("## Verification")
        lines.append("")
        lines.append(f"**Signature:** `{result.sauce_bundle.signature}`")
        if result.sauce_bundle.signed_at:
            lines.append(f"**Signed At:** {_format_timestamp(result.sauce_bundle.signed_at)}")
        if result.sauce_bundle.signed_by:
            lines.append(f"**Signed By:** {result.sauce_bundle.signed_by}")
        lines.append("")

    # Execution timeline
    lines.append("## Execution Timeline")
    lines.append("")
    lines.append(f"- **Started:** {_format_timestamp(result.started_at)}")
    lines.append(f"- **Completed:** {_format_timestamp(result.completed_at)}")
    lines.append("")

    # Trace (condensed)
    if result.trace:
        lines.append("### Tool Calls")
        lines.append("")
        lines.append("| # | Tool | Timestamp |")
        lines.append("|---|------|-----------|")

        for i, trace_item in enumerate(result.trace[:20]):  # Limit to 20
            tool = trace_item.get("tool", "unknown")
            ts = trace_item.get("timestamp", "")
            ts_short = ts.split("T")[1][:8] if "T" in ts else ts
            lines.append(f"| {i + 1} | `{tool}` | {ts_short} |")

        if len(result.trace) > 20:
            lines.append(f"| ... | *{len(result.trace) - 20} more* | |")

        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by [Kytchen](https://kytchen.dev) - BYOLLM Orchestration Layer*")
    lines.append("")

    return "\n".join(lines)


def export_markdown(result: RecipeResult, path: str | Path) -> Path:
    """Export a RecipeResult to a Markdown file.

    Args:
        result: The recipe result to export
        path: Output file path

    Returns:
        Path to the created file
    """
    p = Path(path)
    content = render_markdown(result)
    p.write_text(content, encoding="utf-8")
    return p
