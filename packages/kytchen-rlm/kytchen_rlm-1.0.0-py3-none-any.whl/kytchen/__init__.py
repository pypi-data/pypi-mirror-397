"""Kytchen - Too many cooks in the kitchen. Let us do the prep.

Kytchen lets an LLM *programmatically interact* with context (the "prep") stored
as a variable inside a sandboxed Python REPL, enabling scalable reasoning over
large inputs without stuffing tokens into prompts.

BYOLLM Cloud Platform - We handle the pantry (storage) and prep (compute).
Your LLM does the cooking.

Exports:
- Kytchen: main class (the kitchen)
- create_kytchen: factory
- KytchenConfig: configuration dataclass
"""

from __future__ import annotations

from .core import Kytchen
from .config import KytchenConfig, create_kytchen
from .types import (
    ContentFormat,
    ContextType,
    ContextMetadata,
    ContextCollection,
    ExecutionResult,
    SubQueryResult,
    ActionType,
    ParsedAction,
    TrajectoryStep,
    KytchenResponse,
    Budget,
    BudgetStatus,
)

__all__ = [
    "Kytchen",
    "KytchenConfig",
    "create_kytchen",
    "KytchenResponse",
    # Types
    "ContentFormat",
    "ContextType",
    "ContextMetadata",
    "ContextCollection",
    "ExecutionResult",
    "SubQueryResult",
    "ActionType",
    "ParsedAction",
    "TrajectoryStep",
    "Budget",
    "BudgetStatus",
]

__version__ = "1.0.0"
