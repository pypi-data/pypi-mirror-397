"""Tests for Kytchen exporters (sauce pack export)."""

import json
import tempfile
from pathlib import Path

import pytest

from kytchen.recipe import (
    DatasetInput,
    RecipeConfig,
    RecipeMetrics,
    RecipeResult,
    SauceBundle,
    SauceItem,
)


@pytest.fixture
def sample_recipe_result() -> RecipeResult:
    """Create a sample RecipeResult for testing."""
    config = RecipeConfig(
        query="Analyze the security policy document for SOC2 compliance gaps",
        datasets=[
            DatasetInput(
                id="policy-doc",
                source="inline",
                content="Security Policy Document\n\nSection 1: Access Control\nAll users must use MFA...",
                content_hash="sha256:abc123",
                format="text",
                size_bytes=1024,
                size_tokens_estimate=256,
            ),
        ],
        model="claude-sonnet-4-20250514",
        max_iterations=20,
    )

    metrics = RecipeMetrics(
        tokens_used=1500,
        tokens_baseline=15000,
        tokens_saved=13500,
        efficiency_ratio=0.9,
        iterations=5,
        evidence_count=3,
        wall_time_seconds=12.5,
        cost_usd=0.0045,
    )

    sauce = [
        SauceItem(
            source="search",
            line_range=(10, 15),
            pattern="access control",
            snippet="All users must use MFA for system access...",
            note="Found access control policy",
            timestamp="2025-01-15T10:30:00",
            dataset_id="policy-doc",
        ),
        SauceItem(
            source="peek",
            line_range=(25, 30),
            pattern=None,
            snippet="Data encryption at rest using AES-256...",
            note="Encryption policy section",
            timestamp="2025-01-15T10:30:05",
            dataset_id="policy-doc",
        ),
        SauceItem(
            source="exec",
            line_range=None,
            pattern=None,
            snippet="# Extracted 12 control statements",
            note="Python analysis result",
            timestamp="2025-01-15T10:30:10",
            dataset_id=None,
        ),
    ]

    bundle = SauceBundle(
        recipe_hash="sha256:def456",
        sauce=sauce,
        signature="sha256:sig789",
        signed_at="2025-01-15T10:31:00",
        signed_by="kytchen-local",
    )

    return RecipeResult(
        recipe=config,
        recipe_hash="sha256:def456",
        answer="The security policy covers most SOC2 controls but has gaps in:\n1. Incident response procedures\n2. Vendor management\n3. Change management documentation",
        success=True,
        metrics=metrics,
        sauce_bundle=bundle,
        started_at="2025-01-15T10:30:00",
        completed_at="2025-01-15T10:30:12",
        trace=[
            {"timestamp": "2025-01-15T10:30:01", "tool": "load_context", "args": {}},
            {"timestamp": "2025-01-15T10:30:02", "tool": "search_context", "args": {"pattern": "access"}},
            {"timestamp": "2025-01-15T10:30:05", "tool": "peek_context", "args": {"start": 25, "end": 30}},
            {"timestamp": "2025-01-15T10:30:08", "tool": "exec_python", "args": {}},
            {"timestamp": "2025-01-15T10:30:11", "tool": "finalize", "args": {}},
        ],
    )


class TestMarkdownExporter:
    """Tests for the Markdown exporter."""

    def test_render_markdown(self, sample_recipe_result: RecipeResult) -> None:
        """Test rendering RecipeResult to markdown string."""
        from kytchen.exporters.markdown import render_markdown

        md = render_markdown(sample_recipe_result)

        # Check headers
        assert "# Kytchen Analysis Report" in md
        assert "## Status:" in md
        assert "## Query" in md
        assert "## Answer" in md
        assert "## Metrics" in md
        assert "## Evidence (Sauce)" in md

        # Check content
        assert "SOC2 compliance gaps" in md  # Query
        assert "Incident response procedures" in md  # Answer
        assert "90.0%" in md  # Efficiency
        assert "access control" in md  # Evidence snippet

        # Check metrics table
        assert "Tokens Used" in md
        assert "Tokens Baseline" in md
        assert "Efficiency" in md

    def test_render_markdown_failed_result(self, sample_recipe_result: RecipeResult) -> None:
        """Test rendering a failed result."""
        from kytchen.exporters.markdown import render_markdown

        sample_recipe_result.success = False
        sample_recipe_result.error = "Budget exceeded"

        md = render_markdown(sample_recipe_result)

        assert "Failed" in md
        assert "Budget exceeded" in md

    def test_export_markdown_to_file(self, sample_recipe_result: RecipeResult) -> None:
        """Test exporting to a markdown file."""
        from kytchen.exporters.markdown import export_markdown

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"
            result_path = export_markdown(sample_recipe_result, output_path)

            assert result_path == output_path
            assert output_path.exists()

            content = output_path.read_text()
            assert "# Kytchen Analysis Report" in content

    def test_render_markdown_no_evidence(self, sample_recipe_result: RecipeResult) -> None:
        """Test rendering with no evidence."""
        from kytchen.exporters.markdown import render_markdown

        sample_recipe_result.sauce_bundle.sauce = []

        md = render_markdown(sample_recipe_result)

        assert "No evidence collected" in md

    def test_render_markdown_with_signature(self, sample_recipe_result: RecipeResult) -> None:
        """Test rendering includes signature verification section."""
        from kytchen.exporters.markdown import render_markdown

        md = render_markdown(sample_recipe_result)

        assert "## Verification" in md
        assert "sha256:sig789" in md
        assert "kytchen-local" in md


class TestHTMLExporter:
    """Tests for the HTML exporter."""

    def test_export_html(self, sample_recipe_result: RecipeResult) -> None:
        """Test exporting to HTML file."""
        from kytchen.exporters.pdf import export_html

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.html"
            result_path = export_html(sample_recipe_result, output_path)

            assert result_path == output_path
            assert output_path.exists()

            content = output_path.read_text()
            assert "<!DOCTYPE html>" in content
            assert "<title>Kytchen Analysis Report</title>" in content
            assert "Kytchen Analysis Report" in content


class TestPDFExporter:
    """Tests for the PDF exporter."""

    def test_export_pdf_requires_dependency(self, sample_recipe_result: RecipeResult) -> None:
        """Test that PDF export raises ImportError without dependencies."""
        from kytchen.exporters.pdf import export_pdf

        # This test will pass if either weasyprint or fpdf2 is installed
        # Otherwise it should raise ImportError
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.pdf"

            try:
                export_pdf(sample_recipe_result, output_path)
                # If we get here, a PDF library is installed
                assert output_path.exists()
            except ImportError as e:
                # Expected if no PDF library is installed
                assert "weasyprint" in str(e).lower() or "fpdf" in str(e).lower()


class TestExportRoundTrip:
    """Test export and re-import consistency."""

    def test_json_to_markdown_roundtrip(self, sample_recipe_result: RecipeResult) -> None:
        """Test that JSON -> RecipeResult -> Markdown works."""
        from kytchen.exporters.markdown import render_markdown

        # Serialize to JSON
        json_data = sample_recipe_result.to_dict()
        json_str = json.dumps(json_data)

        # Deserialize back
        loaded = RecipeResult.from_dict(json.loads(json_str))

        # Export to markdown
        md = render_markdown(loaded)

        # Verify key content preserved
        assert loaded.answer in md
        assert str(loaded.metrics.efficiency_ratio * 100)[:4] in md  # 90.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_result(self) -> None:
        """Test rendering an empty/minimal result."""
        from kytchen.exporters.markdown import render_markdown

        result = RecipeResult()

        md = render_markdown(result)

        assert "# Kytchen Analysis Report" in md
        assert "No answer provided" in md

    def test_result_with_no_recipe(self) -> None:
        """Test rendering result without recipe config."""
        from kytchen.exporters.markdown import render_markdown

        result = RecipeResult(
            answer="Some answer",
            success=True,
        )

        md = render_markdown(result)

        assert "Some answer" in md
        # Should not crash

    def test_long_evidence_snippet(self, sample_recipe_result: RecipeResult) -> None:
        """Test that long snippets are handled."""
        from kytchen.exporters.markdown import render_markdown

        # Add a long snippet
        long_snippet = "x" * 1000
        sample_recipe_result.sauce_bundle.sauce[0].snippet = long_snippet

        md = render_markdown(sample_recipe_result)

        # Should not crash, snippet should be present (possibly truncated)
        assert "xxx" in md
