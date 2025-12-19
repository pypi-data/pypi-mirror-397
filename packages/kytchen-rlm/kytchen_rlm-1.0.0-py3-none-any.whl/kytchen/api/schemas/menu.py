"""Pydantic schemas for Menu API (SHA-107).

The Menu API returns OpenAI-compatible tool schemas so ANY agent
(Cursor, Windsurf, AutoGen, CrewAI) can plug in without custom code.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class KytchenMeta(BaseModel):
    """Kytchen metadata in Menu response."""

    id: str = Field(..., description="Kytchen ID (kyt_...)")
    name: str = Field(..., description="Human-readable name")
    description: str | None = Field(None, description="Kytchen description")
    chef: str | None = Field(None, description="Chef handle (@username)")
    visibility: Literal["public", "private", "unlisted"] = Field(
        "private", description="Kytchen visibility"
    )
    forked_from: str | None = Field(None, description="Kytchen ID this was forked from")
    created_at: datetime = Field(..., description="Creation timestamp")


class DatasetInfo(BaseModel):
    """Dataset info within Pantry status."""

    id: str = Field(..., description="Dataset ID")
    name: str = Field(..., description="Human-readable name")
    format: Literal["text", "code", "json", "csv", "pdf", "docx", "markdown"] = Field(
        "text", description="Content format"
    )
    size_bytes: int = Field(0, ge=0, description="Size in bytes")
    size_tokens_estimate: int = Field(0, ge=0, description="Estimated token count")
    indexed: bool = Field(False, description="Whether indexed for search")
    content_hash: str | None = Field(None, description="Content hash (sha256:...)")


class PantryStatus(BaseModel):
    """Pantry (indexed data) status in Menu response."""

    datasets: list[DatasetInfo] = Field(default_factory=list, description="Available datasets")
    total_size_bytes: int = Field(0, ge=0, description="Total size")
    total_tokens_estimate: int = Field(0, ge=0, description="Total estimated tokens")
    indexed_at: datetime | None = Field(None, description="Last indexing timestamp")


class ToolParameter(BaseModel):
    """JSON Schema for a tool parameter."""

    type: str = Field("object", description="Parameter type")
    properties: dict[str, Any] = Field(default_factory=dict, description="Parameter properties")
    required: list[str] = Field(default_factory=list, description="Required parameters")


class ToolFunction(BaseModel):
    """OpenAI-compatible function definition."""

    name: str = Field(..., description="Function name (snake_case)")
    description: str = Field(..., description="What this function does")
    parameters: ToolParameter = Field(..., description="JSON Schema for parameters")


class ToolDefinition(BaseModel):
    """OpenAI-compatible tool definition."""

    type: Literal["function"] = Field("function", description="Tool type")
    function: ToolFunction = Field(..., description="Function definition")


class BudgetDefaults(BaseModel):
    """Default budget constraints for tickets."""

    max_tokens: int = Field(50000, ge=1, description="Max tokens")
    max_cost_usd: float = Field(1.0, ge=0, description="Max cost in USD")
    max_iterations: int = Field(20, ge=1, description="Max iterations")
    timeout_seconds: float = Field(120, ge=1, description="Timeout in seconds")


class Endpoints(BaseModel):
    """API endpoints for this Kytchen."""

    menu: str = Field(..., description="This menu endpoint")
    query: str = Field(..., description="Fire a ticket (POST)")
    stream: str | None = Field(None, description="Fire ticket with SSE streaming")
    pantry: str | None = Field(None, description="Pantry management endpoint")


class MenuResponse(BaseModel):
    """Full Menu API response - OpenAI-compatible tool discovery."""

    schema_url: str = Field(
        "https://kytchen.dev/schemas/menu.v1.json",
        alias="$schema",
        description="JSON Schema URL",
    )
    version: str = Field("1.0.0", description="Menu schema version")
    kytchen: KytchenMeta = Field(..., description="Kytchen metadata")
    pantry: PantryStatus = Field(..., description="Pantry (data) status")
    tools: list[ToolDefinition] = Field(..., description="Available tools")
    budget_defaults: BudgetDefaults = Field(
        default_factory=BudgetDefaults, description="Default budget"
    )
    endpoints: Endpoints = Field(..., description="API endpoints")

    class Config:
        populate_by_name = True


# Default tools available in every Kitchen
DEFAULT_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="peek",
            description="Read a specific portion of the context by character or line range",
            parameters=ToolParameter(
                type="object",
                properties={
                    "start": {"type": "integer", "description": "Start position (0-indexed)"},
                    "end": {"type": "integer", "description": "End position"},
                    "unit": {
                        "type": "string",
                        "enum": ["chars", "lines"],
                        "default": "chars",
                        "description": "Unit for start/end",
                    },
                },
                required=["start", "end"],
            ),
        ),
    ),
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="search",
            description="Regex search across all pantry data",
            parameters=ToolParameter(
                type="object",
                properties={
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "max_results": {"type": "integer", "default": 10, "description": "Max results"},
                    "context_lines": {
                        "type": "integer",
                        "default": 2,
                        "description": "Context lines around matches",
                    },
                },
                required=["pattern"],
            ),
        ),
    ),
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="lines",
            description="Get specific line range from context",
            parameters=ToolParameter(
                type="object",
                properties={
                    "start": {"type": "integer", "description": "Start line (0-indexed)"},
                    "end": {"type": "integer", "description": "End line"},
                },
                required=["start", "end"],
            ),
        ),
    ),
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="chunk",
            description="Split context into chunks for processing",
            parameters=ToolParameter(
                type="object",
                properties={
                    "chunk_size": {"type": "integer", "default": 2000, "description": "Chars per chunk"},
                    "overlap": {"type": "integer", "default": 200, "description": "Overlap between chunks"},
                },
                required=[],
            ),
        ),
    ),
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="exec_python",
            description="Execute Python code in the sandboxed REPL with access to context",
            parameters=ToolParameter(
                type="object",
                properties={
                    "code": {"type": "string", "description": "Python code to execute"},
                },
                required=["code"],
            ),
        ),
    ),
]
