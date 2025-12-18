"""OpenAI cost calculator."""

from llm_costs.models import CostBreakdown, CostResult


def calculate_openai_cost(
    model: str,
    usage: dict,
    pricing: dict,
    batch: bool = False,
) -> CostResult:
    """
    Calculate cost for OpenAI models.

    Args:
        model: Model name (e.g., "gpt-4o", "o3-mini")
        usage: LangChain UsageMetadata structure
        pricing: Loaded pricing config
        batch: Whether batch API pricing applies

    Returns:
        CostResult with cost breakdown

    Note:
        For o-series reasoning models, reasoning tokens are included in output_tokens
        and billed at the output rate. LangChain's UsageMetadata captures this in
        output_token_details.reasoning but we don't need special handling since
        the total is already in output_tokens.
    """
    model_pricing = _get_model_pricing(model, pricing)
    if not model_pricing:
        raise ValueError(f"Unknown OpenAI model: {model}")

    # Extract from LangChain UsageMetadata structure
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    input_details = usage.get("input_token_details", {}) or {}

    cache_read = input_details.get("cache_read", 0)

    # Get base prices
    input_price = model_pricing["input"]
    output_price = model_pricing["output"]
    cache_read_price = model_pricing.get("cache_read", 0)

    # OpenAI batch has different pricing per model - for now assume 50% discount
    # (OpenAI's batch pricing varies by model but is roughly 50% for most)
    if batch:
        input_price *= 0.5
        output_price *= 0.5
        cache_read_price *= 0.5

    # Calculate costs (prices are per million tokens)
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    cache_read_cost = (cache_read / 1_000_000) * cache_read_price

    total_cost = input_cost + output_cost + cache_read_cost

    breakdown = CostBreakdown(
        input_cost=round(input_cost, 8),
        output_cost=round(output_cost, 8),
    )
    if cache_read:
        breakdown["cache_read_cost"] = round(cache_read_cost, 8)

    return CostResult(
        cost=round(total_cost, 8),
        currency=pricing["currency"],
        breakdown=breakdown,
        pricing_used={
            "input_per_mtok": input_price,
            "output_per_mtok": output_price,
            "batch_applied": batch,
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
