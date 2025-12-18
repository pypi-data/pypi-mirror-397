"""Main cost calculation API."""

from pathlib import Path

import yaml

from llm_costs.models import CostResult
from llm_costs.providers.anthropic import calculate_anthropic_cost
from llm_costs.providers.google import calculate_google_cost
from llm_costs.providers.openai import calculate_openai_cost

# Cache for loaded pricing configs
_pricing_cache: dict[str, dict] = {}

# Provider to calculator function mapping
_PROVIDER_CALCULATORS = {
    "anthropic": calculate_anthropic_cost,
    "openai": calculate_openai_cost,
    "google": calculate_google_cost,
}


def _get_pricing_dir() -> Path:
    """Get the directory containing pricing YAML files."""
    return Path(__file__).parent / "pricing"


def _load_pricing(provider: str) -> dict:
    """Load pricing config for a provider, with caching."""
    if provider in _pricing_cache:
        return _pricing_cache[provider]

    pricing_file = _get_pricing_dir() / f"{provider}.yaml"
    if not pricing_file.exists():
        raise ValueError(f"No pricing data for provider: {provider}")

    with open(pricing_file) as f:
        pricing = yaml.safe_load(f)

    _pricing_cache[provider] = pricing
    return pricing


def calculate_cost(
    provider: str,
    model: str,
    usage: dict,
    batch: bool = False,
    long_context: bool | None = None,
) -> CostResult:
    """
    Calculate cost for an LLM API call.

    Args:
        provider: Provider name ("anthropic", "openai", "google")
        model: Model name (e.g., "claude-sonnet-4-20250514", "gpt-4o")
        usage: Token usage in LangChain UsageMetadata format:
            {
                "input_tokens": int,
                "output_tokens": int,
                "total_tokens": int,
                "input_token_details": {
                    "cache_read": int,      # Cached input tokens read
                    "cache_creation": int,  # Tokens written to cache
                },
                "output_token_details": {
                    "reasoning": int,       # Reasoning tokens (o1/thinking models)
                },
            }
        batch: Whether batch API pricing applies (typically 50% discount)
        long_context: Force long context pricing. Auto-detected if None based on
            total input tokens exceeding provider threshold (typically 200K).

    Returns:
        CostResult with total cost, breakdown, and pricing info used.

    Raises:
        ValueError: If provider or model is unknown.

    Example:
        >>> result = calculate_cost(
        ...     provider="anthropic",
        ...     model="claude-sonnet-4-20250514",
        ...     usage={
        ...         "input_tokens": 1000,
        ...         "output_tokens": 500,
        ...         "total_tokens": 1500,
        ...     },
        ... )
        >>> print(f"Cost: ${result['cost']:.6f}")
        Cost: $0.010500
    """
    provider = provider.lower()

    if provider not in _PROVIDER_CALCULATORS:
        raise ValueError(f"Unknown provider: {provider}. Supported: {list(_PROVIDER_CALCULATORS)}")

    pricing = _load_pricing(provider)
    calculator = _PROVIDER_CALCULATORS[provider]

    # Build kwargs - not all providers support all options
    kwargs: dict = {
        "model": model,
        "usage": usage,
        "pricing": pricing,
        "batch": batch,
    }

    # Only pass long_context to providers that support it
    if provider in ("anthropic", "google"):
        kwargs["long_context"] = long_context

    return calculator(**kwargs)


def get_model_pricing(provider: str, model: str) -> dict | None:
    """
    Get pricing info for a specific model.

    Args:
        provider: Provider name ("anthropic", "openai", "google")
        model: Model name or alias

    Returns:
        Model pricing config dict, or None if not found.

    Example:
        >>> pricing = get_model_pricing("anthropic", "claude-sonnet-4-20250514")
        >>> print(f"Input: ${pricing['input']}/MTok")
        Input: $3.0/MTok
    """
    provider = provider.lower()

    try:
        pricing = _load_pricing(provider)
    except ValueError:
        return None

    models = pricing.get("models", {})

    # Direct match
    if model in models:
        return models[model]

    # Check aliases
    for model_config in models.values():
        aliases = model_config.get("aliases", [])
        if model in aliases:
            return model_config

    return None


def list_models(provider: str) -> list[str]:
    """
    List all known models for a provider.

    Args:
        provider: Provider name

    Returns:
        List of model names (primary names, not aliases)
    """
    provider = provider.lower()

    try:
        pricing = _load_pricing(provider)
    except ValueError:
        return []

    return list(pricing.get("models", {}).keys())


def list_providers() -> list[str]:
    """List all supported providers."""
    return list(_PROVIDER_CALCULATORS.keys())
