"""Pydantic schemas for Tickets API.

A Ticket is a query fired into a Kitchen. It uses the Kitchen's
Pantry data and produces a Receipt (run result) with Sauce (evidence).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    """Request body for creating a ticket (firing a query)."""

    query: str = Field(..., description="The question to ask")
    dataset_ids: list[str] | None = Field(
        None, description="Specific datasets to use (default: all in pantry)"
    )
    provider: str | None = Field(None, description="LLM provider (anthropic, openai)")
    model: str | None = Field(None, description="Model name")
    provider_api_key: str | None = Field(None, description="BYOLLM API key")
    budget: dict[str, Any] | None = Field(None, description="Budget overrides")


class TicketMetrics(BaseModel):
    """Token savings and cost metrics."""

    baseline_tokens: int = Field(0, description="Tokens if context-stuffing")
    tokens_served: int = Field(0, description="Actual tokens used")
    iterations: int = Field(0, description="Number of iterations")
    cost_usd: float = Field(0.0, description="Total cost in USD")

    @property
    def tokens_saved(self) -> int:
        """Tokens saved vs context-stuffing approach."""
        return max(0, self.baseline_tokens - self.tokens_served)

    @property
    def efficiency_ratio(self) -> float:
        """Efficiency ratio (higher is better)."""
        if self.baseline_tokens == 0:
            return 1.0
        return self.tokens_saved / self.baseline_tokens


class TicketResponse(BaseModel):
    """Response for a completed ticket (receipt)."""

    id: str = Field(..., description="Ticket/Run ID")
    kytchen_id: str = Field(..., description="Kytchen ID")
    query: str = Field(..., description="Original query")
    status: Literal["pending", "running", "completed", "failed"] = Field(
        "pending", description="Ticket status"
    )
    answer: str | None = Field(None, description="Final answer")
    evidence: list[dict[str, Any]] | None = Field(None, description="Sauce (evidence)")
    error: str | None = Field(None, description="Error message if failed")
    metrics: TicketMetrics | None = Field(None, description="Token savings metrics")
    created_at: datetime = Field(..., description="When ticket was created")
    completed_at: datetime | None = Field(None, description="When ticket completed")


class TicketListResponse(BaseModel):
    """Response for listing tickets."""

    tickets: list[TicketResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total count")
    has_more: bool = Field(False, description="Whether more results exist")


class TicketStreamEvent(BaseModel):
    """SSE event during ticket execution."""

    type: Literal["started", "step", "completed", "error"] = Field(
        ..., description="Event type"
    )
    data: dict[str, Any] = Field(default_factory=dict, description="Event data")
    timestamp: float = Field(..., description="Unix timestamp")
