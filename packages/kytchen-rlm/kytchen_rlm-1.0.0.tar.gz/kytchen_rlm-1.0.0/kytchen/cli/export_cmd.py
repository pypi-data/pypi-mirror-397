"""Export command for Kytchen CLI.

Export recipe results (sauce packs) to various formats:
- JSON (default)
- Markdown (human-readable)
- HTML (web-viewable)
- PDF (printable)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import print_error, print_info, print_success

app = typer.Typer(
    name="export",
    help="Export recipe results (sauce packs) to various formats",
    no_args_is_help=True,
)


def _load_result(input_path: Path) -> dict:
    """Load a recipe result from JSON file."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        raise typer.Exit(1)
    except OSError as e:
        print_error(f"Could not read file: {e}")
        raise typer.Exit(1)


@app.command(name="markdown")
def export_markdown_cmd(
    input_file: Path = typer.Argument(
        ...,
        help="Path to recipe result JSON file",
        exists=True,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="Output file path (defaults to input_file.md)",
    ),
) -> None:
    """Export a recipe result to Markdown format."""
    from kytchen.exporters import export_markdown
    from kytchen.recipe import RecipeResult

    data = _load_result(input_file)
    result = RecipeResult.from_dict(data)

    output_path = output or input_file.with_suffix(".md")

    try:
        export_markdown(result, output_path)
        print_success(f"Exported to: {output_path}")
    except Exception as e:
        print_error(f"Export failed: {e}")
        raise typer.Exit(1)


@app.command(name="html")
def export_html_cmd(
    input_file: Path = typer.Argument(
        ...,
        help="Path to recipe result JSON file",
        exists=True,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="Output file path (defaults to input_file.html)",
    ),
) -> None:
    """Export a recipe result to HTML format."""
    from kytchen.exporters import export_html
    from kytchen.recipe import RecipeResult

    data = _load_result(input_file)
    result = RecipeResult.from_dict(data)

    output_path = output or input_file.with_suffix(".html")

    try:
        export_html(result, output_path)
        print_success(f"Exported to: {output_path}")
    except Exception as e:
        print_error(f"Export failed: {e}")
        raise typer.Exit(1)


@app.command(name="pdf")
def export_pdf_cmd(
    input_file: Path = typer.Argument(
        ...,
        help="Path to recipe result JSON file",
        exists=True,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="Output file path (defaults to input_file.pdf)",
    ),
) -> None:
    """Export a recipe result to PDF format.

    Requires weasyprint or fpdf2:
        pip install weasyprint   # Full-featured, requires system deps
        pip install fpdf2        # Simpler, pure Python
    """
    from kytchen.exporters import export_pdf
    from kytchen.recipe import RecipeResult

    data = _load_result(input_file)
    result = RecipeResult.from_dict(data)

    output_path = output or input_file.with_suffix(".pdf")

    try:
        export_pdf(result, output_path)
        print_success(f"Exported to: {output_path}")
    except ImportError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Export failed: {e}")
        raise typer.Exit(1)


@app.command(name="all")
def export_all_cmd(
    input_file: Path = typer.Argument(
        ...,
        help="Path to recipe result JSON file",
        exists=True,
        readable=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-d", "--output-dir",
        help="Output directory (defaults to same as input file)",
    ),
    skip_pdf: bool = typer.Option(
        False,
        "--skip-pdf",
        help="Skip PDF export (useful if deps not installed)",
    ),
) -> None:
    """Export a recipe result to all formats (JSON, MD, HTML, PDF)."""
    from kytchen.exporters import export_html, export_markdown
    from kytchen.recipe import RecipeResult

    data = _load_result(input_file)
    result = RecipeResult.from_dict(data)

    out_dir = output_dir or input_file.parent
    base_name = input_file.stem

    # Markdown
    md_path = out_dir / f"{base_name}.md"
    export_markdown(result, md_path)
    print_success(f"Exported Markdown: {md_path}")

    # HTML
    html_path = out_dir / f"{base_name}.html"
    export_html(result, html_path)
    print_success(f"Exported HTML: {html_path}")

    # PDF (optional)
    if not skip_pdf:
        try:
            from kytchen.exporters import export_pdf
            pdf_path = out_dir / f"{base_name}.pdf"
            export_pdf(result, pdf_path)
            print_success(f"Exported PDF: {pdf_path}")
        except ImportError as e:
            print_info(f"Skipped PDF: {e}")

    print_success(f"Export complete: {out_dir}")


# Standalone export command for main CLI
def export_command(
    input_file: Path = typer.Argument(
        ...,
        help="Path to recipe result JSON file",
    ),
    format: str = typer.Option(
        "markdown",
        "-f", "--format",
        help="Output format: markdown, html, pdf, all",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="Output file or directory path",
    ),
) -> None:
    """Export a recipe result (sauce pack) to various formats.

    Examples:
        kytchen export result.json                    # Export to markdown
        kytchen export result.json -f pdf            # Export to PDF
        kytchen export result.json -f all            # Export to all formats
        kytchen export result.json -o report.md      # Custom output path
    """
    if not input_file.exists():
        print_error(f"File not found: {input_file}")
        raise typer.Exit(1)

    format_lower = format.lower()

    if format_lower == "markdown" or format_lower == "md":
        export_markdown_cmd(input_file, output)
    elif format_lower == "html":
        export_html_cmd(input_file, output)
    elif format_lower == "pdf":
        export_pdf_cmd(input_file, output)
    elif format_lower == "all":
        export_all_cmd(input_file, output)
    else:
        print_error(f"Unknown format: {format}")
        print_info("Available formats: markdown, html, pdf, all")
        raise typer.Exit(1)
