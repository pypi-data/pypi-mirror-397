"""Type definitions for Kytchen SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


@dataclass
class Dataset:
    """A dataset stored in Kytchen."""

    id: str
    name: str
    size_bytes: int
    content_hash: str
    status: Literal["uploaded", "processing", "ready", "failed"]
    created_at: float
    format: str | None = None
    processing_error: str | None = None


@dataclass
class Budget:
    """Resource budget for a query."""

    max_tokens: int | None = None
    max_cost_usd: float | None = None
    max_iterations: int | None = None
    max_wall_time_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in {
            "max_tokens": self.max_tokens,
            "max_cost_usd": self.max_cost_usd,
            "max_iterations": self.max_iterations,
            "max_wall_time_seconds": self.max_wall_time_seconds,
        }.items() if v is not None}


@dataclass
class Evidence:
    """Evidence from a tool execution."""

    tool_name: str
    snippet: str
    params: dict[str, Any] = field(default_factory=dict)
    line_start: int | None = None
    line_end: int | None = None
    note: str | None = None


@dataclass
class QueryResult:
    """Result of a query execution."""

    run_id: str
    answer: str | None
    success: bool
    error: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunEvent:
    """Event from a streaming query."""

    type: Literal["started", "thinking", "tool_call", "tool_result", "completed", "error"]
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
