"""Type definitions for LLM cost calculation."""

from typing import NotRequired, TypedDict


class CostBreakdown(TypedDict):
    """Itemized cost breakdown."""

    input_cost: float
    output_cost: float
    cache_read_cost: NotRequired[float]
    cache_creation_cost: NotRequired[float]
    reasoning_cost: NotRequired[float]


class CostResult(TypedDict):
    """Result from calculate_cost()."""

    cost: float
    currency: str
    breakdown: CostBreakdown
    pricing_used: dict[str, float | bool]
