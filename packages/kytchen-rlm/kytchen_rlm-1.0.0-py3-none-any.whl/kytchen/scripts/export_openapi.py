#!/usr/bin/env python3
"""Export OpenAPI schema from Kytchen Cloud API.

Usage:
    python -m kytchen.scripts.export_openapi [output_path]
    kytchen-openapi [output_path]

If no output path is provided, defaults to docs/api/openapi.json

Requirements:
    pip install 'kytchen[api]'
"""

import json
import os
import sys
from pathlib import Path


def export_openapi(output_path: str | None = None) -> None:
    """Export OpenAPI JSON schema from the FastAPI app."""
    # Set development mode to avoid database requirements during import
    os.environ.setdefault("KYTCHEN_DEV_MODE", "1")

    try:
        from kytchen.api.app import app
    except ImportError as e:
        print(f"Error: Could not import kytchen.api.app: {e}")
        print("Make sure you have installed the API dependencies:")
        print("  pip install 'kytchen[api]'")
        sys.exit(1)

    schema = app.openapi()

    # Default output path
    if output_path is None:
        output_path = "docs/api/openapi.json"

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)

    print(f"OpenAPI schema exported to: {output_file}")
    print(f"  - Title: {schema.get('info', {}).get('title', 'N/A')}")
    print(f"  - Version: {schema.get('info', {}).get('version', 'N/A')}")
    print(f"  - Paths: {len(schema.get('paths', {}))}")


def main() -> None:
    """CLI entry point."""
    path = sys.argv[1] if len(sys.argv) > 1 else None
    export_openapi(path)


if __name__ == "__main__":
    main()
