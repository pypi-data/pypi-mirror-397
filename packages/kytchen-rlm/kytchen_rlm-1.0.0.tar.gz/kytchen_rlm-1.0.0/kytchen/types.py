"""Shared type definitions for Kytchen.

The library is intentionally type-rich so it works well with pyright/mypy.

Kitchen Terminology:
- Prep: Context/data loaded for analysis (mise en place)
- Pantry: Stored ingredients/datasets
- Sauce: Citations/evidence trail (the source)
- Ticket: A run/request (like kitchen orders)
- 86'd: Error state (item unavailable)
- Portion Control: Token limits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Awaitable, Callable, Literal, TypeAlias


# -----------------------------------------------------------------------------
# Prep Types (Context)
# -----------------------------------------------------------------------------

class ContentFormat(Enum):
    """Detected or specified format of prep (context) data."""

    TEXT = "text"
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    CODE = "code"
    BINARY = "binary"
    MIXED = "mixed"


@dataclass(slots=True)
class ContextMetadata:
    """Metadata about the loaded prep (shown to the LLM chef)."""

    format: ContentFormat
    size_bytes: int
    size_chars: int
    size_lines: int
    size_tokens_estimate: int
    structure_hint: str | None
    sample_preview: str


@dataclass(slots=True)
class ContextCollection:
    """A multi-ingredient prep (e.g., a corpus of files from the pantry)."""

    items: list[tuple[str, ContextType]]
    total_size_bytes: int = 0
    total_size_tokens_estimate: int = 0


# A single context payload can be text, bytes, JSON-like, or a collection.
JsonScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JsonScalar | list["JSONValue"] | dict[str, "JSONValue"]
ContextType: TypeAlias = str | bytes | JSONValue | ContextCollection


# -----------------------------------------------------------------------------
# Execution Types (Prep Station)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class ExecutionResult:
    """Result of executing code in the sandbox REPL (prep station)."""

    stdout: str
    stderr: str
    return_value: object | None
    variables_updated: list[str]
    truncated: bool
    execution_time_ms: float
    error: str | None


@dataclass(slots=True)
class SubQueryResult:
    """Result of a recursive LLM call (sub_query or sub_kytchen)."""

    answer: str
    tokens_input: int
    tokens_output: int
    cost_usd: float
    model_used: str
    depth: int


# -----------------------------------------------------------------------------
# Action Types (parsed from LLM output - the chef's orders)
# -----------------------------------------------------------------------------

class ActionType(Enum):
    CODE_BLOCK = "code"  # execute python (prep work)
    TOOL_CALL = "tool"  # not used by v1 core, but reserved
    FINAL_ANSWER = "final"  # dish is ready
    FINAL_VAR = "final_var"  # serve from variable
    CONTINUE = "continue"  # more prep needed


@dataclass(slots=True)
class ParsedAction:
    """Parsed instruction from the LLM response (chef's ticket)."""

    action_type: ActionType
    content: str
    raw_response: str


# -----------------------------------------------------------------------------
# Trajectory / Observability Types (The Ticket System)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class TrajectoryStep:
    """Single step in the Kytchen execution trace (a line item on the ticket)."""

    step_number: int
    depth: int
    timestamp: datetime

    prompt_tokens: int
    prompt_summary: str

    action: ParsedAction

    result: ExecutionResult | SubQueryResult | str
    result_tokens: int

    cumulative_tokens: int
    cumulative_cost: float


@dataclass(slots=True)
class KytchenResponse:
    """Final response from a Kytchen call (the plated dish)."""

    answer: str
    success: bool

    total_iterations: int
    max_depth_reached: int
    total_tokens: int
    total_cost_usd: float
    wall_time_seconds: float

    trajectory: list[TrajectoryStep]

    error: str | None = None
    error_type: (
        Literal[
            "budget_exceeded",  # Over portion control
            "max_iterations",   # Kitchen backed up
            "execution_error",  # Prep failed
            "provider_error",   # Chef unavailable
            "no_final",         # Dish never plated
        ]
        | None
    ) = None

    evidence: list[dict[str, object]] = field(default_factory=list)


# -----------------------------------------------------------------------------
# Budget Types (Portion Control)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class Budget:
    """Resource limits for a Kytchen call (portion control)."""

    max_tokens: int | None = None
    max_cost_usd: float | None = None
    max_iterations: int | None = 50
    max_depth: int | None = 2
    max_wall_time_seconds: float | None = 300.0
    max_sub_queries: int | None = 100


@dataclass(slots=True)
class BudgetStatus:
    """Current budget consumption (how much of the portion has been used)."""

    tokens_used: int = 0
    cost_used: float = 0.0
    iterations_used: int = 0
    depth_current: int = 0
    wall_time_used: float = 0.0
    sub_queries_used: int = 0

    def exceeds(self, budget: Budget) -> tuple[bool, str | None]:
        """Return (exceeded, reason) - check if we're 86'd."""

        if budget.max_tokens is not None and self.tokens_used > budget.max_tokens:
            return True, f"86'd: Token budget exceeded: used {self.tokens_used} > max {budget.max_tokens}"

        if budget.max_cost_usd is not None and self.cost_used > budget.max_cost_usd:
            return True, f"86'd: Cost budget exceeded: used ${self.cost_used:.4f} > max ${budget.max_cost_usd:.4f}"

        if budget.max_iterations is not None and self.iterations_used > budget.max_iterations:
            return True, f"86'd: Iteration budget exceeded: used {self.iterations_used} > max {budget.max_iterations}"

        if budget.max_depth is not None and self.depth_current > budget.max_depth:
            return True, f"86'd: Depth budget exceeded: current {self.depth_current} > max {budget.max_depth}"

        if budget.max_wall_time_seconds is not None and self.wall_time_used > budget.max_wall_time_seconds:
            return (
                True,
                f"86'd: Wall-time budget exceeded: used {self.wall_time_used:.2f}s > max {budget.max_wall_time_seconds:.2f}s",
            )

        if budget.max_sub_queries is not None and self.sub_queries_used > budget.max_sub_queries:
            return True, f"86'd: Sub-query budget exceeded: used {self.sub_queries_used} > max {budget.max_sub_queries}"

        return False, None


# -----------------------------------------------------------------------------
# Convenience types
# -----------------------------------------------------------------------------

Message = dict[str, str]
SubQueryFn: TypeAlias = Callable[[str, str | None], str | Awaitable[str]]
SubKytchenFn: TypeAlias = Callable[[str, ContextType | None], KytchenResponse | Awaitable[KytchenResponse]]
