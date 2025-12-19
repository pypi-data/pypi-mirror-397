"""PDF exporter for Kytchen recipe results.

Generates printable audit documents from RecipeResult.

Requires optional dependencies:
- weasyprint: pip install weasyprint (preferred)
- OR markdown + weasyprint: pip install markdown weasyprint

Falls back to basic text-based PDF if dependencies unavailable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kytchen.recipe import RecipeResult

from kytchen.exporters.markdown import render_markdown


# CSS styles for the PDF
PDF_STYLES = """
@page {
    size: A4;
    margin: 2cm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 10px;
        color: #666;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}

h1 {
    color: #1a1a2e;
    border-bottom: 2px solid #e94560;
    padding-bottom: 0.3em;
    margin-top: 0;
}

h2 {
    color: #16213e;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.2em;
    margin-top: 1.5em;
}

h3 {
    color: #0f3460;
    margin-top: 1em;
}

code {
    background-color: #f4f4f4;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'SF Mono', Monaco, monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
    font-size: 0.85em;
}

pre code {
    background: none;
    padding: 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em 0.75em;
    text-align: left;
}

th {
    background-color: #f4f4f4;
    font-weight: 600;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

blockquote {
    border-left: 4px solid #e94560;
    margin: 1em 0;
    padding: 0.5em 1em;
    background-color: #fff8f8;
    color: #555;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}

em {
    color: #666;
}

.success { color: #28a745; }
.failure { color: #dc3545; }
"""


def _markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML."""
    try:
        import markdown
        # Use common extensions for better rendering
        extensions = ['tables', 'fenced_code', 'codehilite']
        html = markdown.markdown(md_content, extensions=extensions)
        return html
    except ImportError:
        # Fallback: basic conversion without markdown library
        import html as html_lib

        # Escape HTML first
        content = html_lib.escape(md_content)

        # Basic markdown-like conversions
        lines = content.split('\n')
        result_lines = []

        in_code_block = False
        in_table = False

        for line in lines:
            # Code blocks
            if line.startswith('```'):
                if in_code_block:
                    result_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    result_lines.append('<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                result_lines.append(line)
                continue

            # Headers
            if line.startswith('# '):
                result_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                result_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                result_lines.append(f'<h3>{line[4:]}</h3>')
            # Tables
            elif line.startswith('|'):
                if not in_table:
                    result_lines.append('<table>')
                    in_table = True
                if '---' in line:
                    continue  # Skip separator row
                cells = [c.strip() for c in line.split('|')[1:-1]]
                tag = 'th' if result_lines[-1] == '<table>' else 'td'
                row = ''.join(f'<{tag}>{c}</{tag}>' for c in cells)
                result_lines.append(f'<tr>{row}</tr>')
            else:
                if in_table:
                    result_lines.append('</table>')
                    in_table = False
                # Blockquotes
                if line.startswith('> '):
                    result_lines.append(f'<blockquote>{line[2:]}</blockquote>')
                # Horizontal rules
                elif line.startswith('---'):
                    result_lines.append('<hr>')
                # Lists
                elif line.startswith('- '):
                    result_lines.append(f'<li>{line[2:]}</li>')
                # Bold
                elif '**' in line:
                    import re
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    result_lines.append(f'<p>{line}</p>')
                # Inline code
                elif '`' in line:
                    import re
                    line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
                    result_lines.append(f'<p>{line}</p>')
                elif line.strip():
                    result_lines.append(f'<p>{line}</p>')

        if in_table:
            result_lines.append('</table>')

        return '\n'.join(result_lines)


def _create_html_document(md_content: str) -> str:
    """Create a complete HTML document from markdown content."""
    html_body = _markdown_to_html(md_content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kytchen Analysis Report</title>
    <style>
{PDF_STYLES}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""


def export_pdf(result: RecipeResult, path: str | Path) -> Path:
    """Export a RecipeResult to a PDF file.

    Args:
        result: The recipe result to export
        path: Output file path

    Returns:
        Path to the created file

    Raises:
        ImportError: If weasyprint is not installed
    """
    p = Path(path)

    # Generate markdown first
    md_content = render_markdown(result)

    # Convert to HTML
    html_content = _create_html_document(md_content)

    # Try weasyprint (preferred)
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(str(p))
        return p
    except ImportError:
        pass

    # Try fpdf2 as fallback (simpler, fewer system deps)
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Use built-in font
        pdf.set_font("Helvetica", size=10)

        # Simple text rendering
        for line in md_content.split('\n'):
            # Handle headers
            if line.startswith('# '):
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(0, 10, line[2:], ln=True)
                pdf.set_font("Helvetica", size=10)
            elif line.startswith('## '):
                pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(0, 8, line[3:], ln=True)
                pdf.set_font("Helvetica", size=10)
            elif line.startswith('### '):
                pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(0, 7, line[4:], ln=True)
                pdf.set_font("Helvetica", size=10)
            elif line.startswith('---'):
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
            elif line.startswith('|'):
                # Skip table formatting, just render as text
                clean = line.replace('|', ' ').strip()
                if clean and '---' not in clean:
                    pdf.cell(0, 5, clean, ln=True)
            elif line.strip():
                # Remove markdown formatting for plain text
                clean = line.replace('**', '').replace('`', '').replace('*', '')
                pdf.multi_cell(0, 5, clean)
            else:
                pdf.ln(3)

        pdf.output(str(p))
        return p

    except ImportError:
        pass

    # No PDF library available
    raise ImportError(
        "PDF export requires weasyprint or fpdf2. Install with:\n"
        "  pip install weasyprint  # Full-featured, requires system deps\n"
        "  pip install fpdf2       # Simpler, pure Python"
    )


def export_html(result: RecipeResult, path: str | Path) -> Path:
    """Export a RecipeResult to an HTML file.

    This is useful as a preview or when PDF generation isn't available.

    Args:
        result: The recipe result to export
        path: Output file path

    Returns:
        Path to the created file
    """
    p = Path(path)
    md_content = render_markdown(result)
    html_content = _create_html_document(md_content)
    p.write_text(html_content, encoding="utf-8")
    return p
