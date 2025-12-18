"""Anthropic Claude cost calculator."""

from llm_costs.models import CostBreakdown, CostResult


def calculate_anthropic_cost(
    model: str,
    usage: dict,
    pricing: dict,
    batch: bool = False,
    long_context: bool | None = None,
) -> CostResult:
    """
    Calculate cost for Anthropic models.

    Args:
        model: Model name (e.g., "claude-sonnet-4-20250514")
        usage: LangChain UsageMetadata structure
        pricing: Loaded pricing config
        batch: Whether batch API pricing applies (50% discount)
        long_context: Whether long context pricing applies. Auto-detected if None.

    Returns:
        CostResult with cost breakdown
    """
    model_pricing = _get_model_pricing(model, pricing)
    if not model_pricing:
        raise ValueError(f"Unknown Anthropic model: {model}")

    # Extract from LangChain UsageMetadata structure
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    input_details = usage.get("input_token_details", {}) or {}

    cache_read = input_details.get("cache_read", 0)
    cache_creation = input_details.get("cache_creation", 0)

    # Determine if long context applies
    total_input = input_tokens + cache_read + cache_creation
    lc_config = model_pricing.get("long_context")
    if long_context is None and lc_config:
        long_context = total_input > lc_config["threshold"]

    # Get base prices
    input_price = model_pricing["input"]
    output_price = model_pricing["output"]

    # Apply long context multiplier
    if long_context and lc_config:
        input_price *= lc_config["input_multiplier"]
        output_price *= lc_config["output_multiplier"]

    # Apply batch discount
    if batch:
        discount = model_pricing.get("batch_discount", 0.5)
        input_price *= discount
        output_price *= discount

    # Calculate costs (prices are per million tokens)
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price

    # Cache costs (cache pricing doesn't get long context multiplier in Anthropic)
    cache_read_price = model_pricing.get("cache_read", 0)
    cache_creation_price = model_pricing.get("cache_creation", 0)
    if batch:
        cache_read_price *= model_pricing.get("batch_discount", 0.5)
        cache_creation_price *= model_pricing.get("batch_discount", 0.5)

    cache_read_cost = (cache_read / 1_000_000) * cache_read_price
    cache_creation_cost = (cache_creation / 1_000_000) * cache_creation_price

    total_cost = input_cost + output_cost + cache_read_cost + cache_creation_cost

    breakdown = CostBreakdown(
        input_cost=round(input_cost, 8),
        output_cost=round(output_cost, 8),
    )
    if cache_read:
        breakdown["cache_read_cost"] = round(cache_read_cost, 8)
    if cache_creation:
        breakdown["cache_creation_cost"] = round(cache_creation_cost, 8)

    return CostResult(
        cost=round(total_cost, 8),
        currency=pricing["currency"],
        breakdown=breakdown,
        pricing_used={
            "input_per_mtok": input_price,
            "output_per_mtok": output_price,
            "batch_applied": batch,
            "long_context_applied": long_context or False,
        },
    )


def _get_model_pricing(model: str, pricing: dict) -> dict | None:
    """Get pricing for a model, checking aliases."""
    models = pricing.get("models", {})

    # Direct match
    if model in models:
        return models[model]

    # Check aliases
    for model_name, model_config in models.items():
        aliases = model_config.get("aliases", [])
        if model in aliases:
            return model_config

    return None
