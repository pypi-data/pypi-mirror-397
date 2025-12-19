from __future__ import annotations

import pytest


def test_convert_pdf_missing_dependency() -> None:
    pytest.importorskip("pypdf")
    # If pypdf is installed, this test will proceed; otherwise it's skipped.
    from kytchen.converters.pdf import convert_pdf_bytes

    # Minimal valid PDF bytes are hard to hand-roll; this is just a smoke test
    # that the function is importable when deps are installed.
    assert callable(convert_pdf_bytes)


def test_convert_docx_missing_dependency() -> None:
    pytest.importorskip("docx")
    from kytchen.converters.docx import convert_docx_bytes

    assert callable(convert_docx_bytes)


def test_convert_xlsx_missing_dependency() -> None:
    pytest.importorskip("openpyxl")
    from kytchen.converters.xlsx import convert_xlsx_bytes

    assert callable(convert_xlsx_bytes)


def test_convert_image_missing_dependency() -> None:
    pytest.importorskip("PIL")
    pytest.importorskip("pytesseract")
    from kytchen.converters.image import convert_image_bytes

    assert callable(convert_image_bytes)
