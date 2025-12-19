"""Dataset processing pipeline for Kytchen Cloud.

Handles async processing of uploaded datasets:
1. Convert binary files (PDF, DOCX, XLSX) to text
2. Store converted text in storage
3. Update dataset status
4. Emit audit events

Usage:
    from kytchen.api.processing import process_dataset_background

    # In upload endpoint:
    background_tasks.add_task(
        process_dataset_background,
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        content=content,
        mime_type=mime_type,
        db_url=settings.database_url,
    )
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from .storage import StorageBackend

logger = logging.getLogger(__name__)


# MIME type to converter mapping
CONVERTER_MAP: dict[str, str] = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/msword": "docx",  # Legacy .doc (best effort)
    "application/vnd.ms-excel": "xlsx",  # Legacy .xls (best effort)
}

# Text-based MIME types that don't need conversion
TEXT_MIME_TYPES = {
    "text/plain",
    "text/csv",
    "text/markdown",
    "text/html",
    "application/json",
    "application/xml",
    "text/xml",
}


def convert_to_text(content: bytes, mime_type: str | None) -> tuple[str, str]:
    """Convert file content to text.

    Args:
        content: Raw file bytes
        mime_type: MIME type of the file

    Returns:
        Tuple of (converted_text, format_type)

    Raises:
        ValueError: If conversion fails
    """
    mime_type = mime_type or "application/octet-stream"

    # Text files: decode directly
    if mime_type in TEXT_MIME_TYPES:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ("latin-1", "cp1252", "iso-8859-1"):
                try:
                    text = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Unable to decode text file with MIME type {mime_type}")
        return text, "text"

    # Binary files: use converters
    converter_type = CONVERTER_MAP.get(mime_type)
    if converter_type is None:
        # Unknown type - try to decode as text as fallback
        try:
            text = content.decode("utf-8")
            return text, "text"
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

    if converter_type == "pdf":
        try:
            from kytchen.converters import convert_pdf_bytes
        except ImportError as e:
            raise ValueError("PDF conversion requires pypdf. Install with: pip install 'kytchen[converters]'") from e
        result = convert_pdf_bytes(content)
        return result["text"], "pdf"

    elif converter_type == "docx":
        try:
            from kytchen.converters import convert_docx_bytes
        except ImportError as e:
            raise ValueError("DOCX conversion requires python-docx. Install with: pip install 'kytchen[converters]'") from e
        result = convert_docx_bytes(content)
        return result["text"], "docx"

    elif converter_type == "xlsx":
        try:
            from kytchen.converters import convert_xlsx_bytes
        except ImportError as e:
            raise ValueError("XLSX conversion requires openpyxl. Install with: pip install 'kytchen[converters]'") from e
        result = convert_xlsx_bytes(content)
        return result["text"], "xlsx"

    raise ValueError(f"Converter not implemented for type: {converter_type}")


async def update_dataset_status(
    db: "AsyncSession",
    dataset_id: str,
    status: str,
    error: str | None = None,
) -> None:
    """Update dataset status in database.

    Args:
        db: Database session
        dataset_id: Dataset UUID
        status: New status ('processing', 'ready', 'failed')
        error: Optional error message (for 'failed' status)
        converted_text_size: Size of converted text (for 'ready' status)
    """
    from sqlalchemy import text

    updates = ["status = :status"]
    params: dict = {"dataset_id": dataset_id, "status": status}

    if error is not None:
        updates.append("processing_error = :error")
        params["error"] = error

    query = f"UPDATE public.datasets SET {', '.join(updates)} WHERE id = :dataset_id"
    await db.execute(text(query), params)
    await db.commit()


async def process_dataset(
    dataset_id: str,
    workspace_id: str,
    content: bytes,
    mime_type: str | None,
    db: "AsyncSession",
    storage: "StorageBackend",
    audit_logger: object | None = None,
) -> bool:
    """Process an uploaded dataset.

    This function:
    1. Updates status to 'processing'
    2. Converts the file to text (if needed)
    3. Stores the converted text
    4. Updates status to 'ready' (or 'failed' on error)
    5. Emits audit events

    Args:
        dataset_id: Dataset UUID
        workspace_id: Workspace UUID
        content: Raw file bytes
        mime_type: MIME type of uploaded file
        db: Async database session
        storage: Storage backend for converted text
        audit_logger: Optional audit logger for events

    Returns:
        True if processing succeeded, False otherwise
    """
    # Import here to avoid circular imports
    from .audit import EventType

    logger.info(f"Processing dataset {dataset_id} ({mime_type})")

    # 1. Update status to 'processing'
    await update_dataset_status(db, dataset_id, "processing")

    try:
        # 2. Convert to text
        converted_text, format_type = convert_to_text(content, mime_type)
        text_bytes = converted_text.encode("utf-8")

        # 3. Store converted text with suffix
        await storage.write_dataset(
            workspace_id=workspace_id,
            dataset_id=f"{dataset_id}.txt",
            content=text_bytes,
        )

        # 4. Update status to 'ready'
        await update_dataset_status(
            db,
            dataset_id,
            "ready",
        )

        # 5. Emit audit event
        if audit_logger is not None:
            await audit_logger.log(
                workspace_id=workspace_id,
                event_type=EventType.DATASET_PROCESSED,
                actor_type="system",
                description=f"Dataset {dataset_id} processed successfully",
                resource_type="dataset",
                resource_id=dataset_id,
                metadata={
                    "format": format_type,
                    "original_size": len(content),
                    "converted_size": len(text_bytes),
                },
            )

        logger.info(f"Dataset {dataset_id} processed: {len(content)} -> {len(text_bytes)} bytes")
        return True

    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Failed to process dataset {dataset_id}: {error_msg}")

        # Update status to 'failed'
        await update_dataset_status(db, dataset_id, "failed", error=error_msg)

        # Emit failure audit event
        if audit_logger is not None:
            try:
                await audit_logger.log(
                    workspace_id=workspace_id,
                    event_type=EventType.RUN_FAILED,  # Reuse run.failed for now
                    actor_type="system",
                    description=f"Dataset {dataset_id} processing failed",
                    resource_type="dataset",
                    resource_id=dataset_id,
                    metadata={"error": error_msg},
                )
            except Exception:
                pass  # Don't fail on audit logging errors

        return False


async def get_converted_text(
    workspace_id: str,
    dataset_id: str,
    storage: "StorageBackend",
) -> str | None:
    """Retrieve converted text for a dataset.

    Args:
        workspace_id: Workspace UUID
        dataset_id: Dataset UUID
        storage: Storage backend

    Returns:
        Converted text or None if not found
    """
    try:
        content = await storage.read_dataset(workspace_id, f"{dataset_id}.txt")
        return content.decode("utf-8")
    except FileNotFoundError:
        return None
