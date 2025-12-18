"""Google Gemini cost calculator."""

from llm_costs.models import CostBreakdown, CostResult


def calculate_google_cost(
    model: str,
    usage: dict,
    pricing: dict,
    batch: bool = False,
    long_context: bool | None = None,
) -> CostResult:
    """
    Calculate cost for Google Gemini models.

    Args:
        model: Model name (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
        usage: LangChain UsageMetadata structure
        pricing: Loaded pricing config
        batch: Whether batch API pricing applies
        long_context: Whether long context pricing applies. Auto-detected if None.

    Returns:
        CostResult with cost breakdown

    Note:
        Gemini's "thinking tokens" are included in output_tokens and billed at output rate.
    """
    model_pricing = _get_model_pricing(model, pricing)
    if not model_pricing:
        raise ValueError(f"Unknown Google model: {model}")

    # Extract from LangChain UsageMetadata structure
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    input_details = usage.get("input_token_details", {}) or {}

    cache_read = input_details.get("cache_read", 0)

    # Determine if long context applies
    total_input = input_tokens + cache_read
    lc_config = model_pricing.get("long_context")
    if long_context is None and lc_config:
        long_context = total_input > lc_config["threshold"]

    # Get base prices - Google uses different pricing structure for long context
    if long_context and lc_config:
        input_price = lc_config["input"]
        output_price = lc_config["output"]
        cache_read_price = lc_config.get("cache_read", 0)
    else:
        input_price = model_pricing["input"]
        output_price = model_pricing["output"]
        cache_read_price = model_pricing.get("cache_read", 0)

    # Apply batch discount
    if batch:
        discount = model_pricing.get("batch_discount", 0.5)
        input_price *= discount
        output_price *= discount
        cache_read_price *= discount

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
