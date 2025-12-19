from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class KytchenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Kytchen name")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly slug (auto-generated if not provided)",
    )
    description: str | None = Field(None, max_length=2000, description="Kytchen description")
    visibility: Literal["public", "private", "unlisted"] = Field(
        "private", description="Kytchen visibility"
    )
    fork_from: str | None = Field(None, description="Kytchen ID to fork from")
    recipe_id: str | None = Field(None, description="Recipe ID to create from")


class KytchenUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255, description="Kytchen name")
    description: str | None = Field(None, max_length=2000, description="Kytchen description")
    visibility: Literal["public", "private", "unlisted"] | None = Field(
        None, description="Kytchen visibility"
    )


class KytchenResponse(BaseModel):
    id: str = Field(..., description="Kytchen ID")
    slug: str = Field(..., description="URL-friendly slug")
    name: str = Field(..., description="Kytchen name")
    description: str | None = Field(None, description="Kytchen description")
    visibility: Literal["public", "private", "unlisted"] = Field(..., description="Visibility")
    forked_from: str | None = Field(None, description="Kytchen ID this was forked from")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    dataset_count: int = Field(0, ge=0, description="Number of datasets in pantry")
    total_size_bytes: int = Field(0, ge=0, description="Total pantry size")


class KytchenListResponse(BaseModel):
    kytchens: list[KytchenResponse] = Field(..., description="List of kytchens")
    total: int = Field(..., ge=0, description="Total count")
    has_more: bool = Field(False, description="More results available")
