from __future__ import annotations

import io


def convert_image_bytes(data: bytes) -> dict:
    try:
        from PIL import Image
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Image OCR requires `pillow`. Install with `pip install 'kytchen[ocr]'`.") from e

    try:
        import pytesseract
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Image OCR requires `pytesseract`. Install with `pip install 'kytchen[ocr]'`.") from e

    img = Image.open(io.BytesIO(data))
    text = pytesseract.image_to_string(img) or ""

    return {
        "type": "image",
        "text": text.strip(),
    }
