"""Pydantic schemas for Kitchen CRUD operations."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class KitchenCreate(BaseModel):
    """Request body for creating a Kitchen."""

    name: str = Field(..., min_length=1, max_length=255, description="Kitchen name")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly slug (auto-generated if not provided)",
    )
    description: str | None = Field(None, max_length=2000, description="Kitchen description")
    visibility: Literal["public", "private", "unlisted"] = Field(
        "private", description="Kitchen visibility"
    )
    fork_from: str | None = Field(None, description="Kitchen ID to fork from")
    recipe_id: str | None = Field(None, description="Recipe ID to create from")


class KitchenUpdate(BaseModel):
    """Request body for updating a Kitchen."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Kitchen name")
    description: str | None = Field(None, max_length=2000, description="Kitchen description")
    visibility: Literal["public", "private", "unlisted"] | None = Field(
        None, description="Kitchen visibility"
    )


class KitchenResponse(BaseModel):
    """Response for a single Kitchen."""

    id: str = Field(..., description="Kitchen ID")
    slug: str = Field(..., description="URL-friendly slug")
    name: str = Field(..., description="Kitchen name")
    description: str | None = Field(None, description="Kitchen description")
    visibility: Literal["public", "private", "unlisted"] = Field(..., description="Visibility")
    forked_from: str | None = Field(None, description="Kitchen ID this was forked from")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Stats
    dataset_count: int = Field(0, ge=0, description="Number of datasets in pantry")
    total_size_bytes: int = Field(0, ge=0, description="Total pantry size")


class KitchenListResponse(BaseModel):
    """Response for listing Kitchens."""

    kitchens: list[KitchenResponse] = Field(..., description="List of kitchens")
    total: int = Field(..., ge=0, description="Total count")
    has_more: bool = Field(False, description="More results available")
