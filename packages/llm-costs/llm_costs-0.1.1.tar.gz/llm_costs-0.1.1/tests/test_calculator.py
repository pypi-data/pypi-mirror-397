"""Tests for the main calculator API."""

import pytest

from llm_costs import calculate_cost, get_model_pricing
from llm_costs.calculator import list_models, list_providers


class TestCalculateCost:
    """Tests for calculate_cost function."""

    def test_anthropic_basic(self):
        """Test basic Anthropic cost calculation."""
        result = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
            },
        )

        assert result["currency"] == "USD"
        assert result["cost"] > 0
        # $3/MTok input + $15/MTok output
        # 1000/1M * 3 + 500/1M * 15 = 0.003 + 0.0075 = 0.0105
        assert abs(result["cost"] - 0.0105) < 0.0001
        assert result["breakdown"]["input_cost"] == pytest.approx(0.003, rel=1e-4)
        assert result["breakdown"]["output_cost"] == pytest.approx(0.0075, rel=1e-4)

    def test_anthropic_with_caching(self):
        """Test Anthropic with prompt caching."""
        result = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
                "input_token_details": {
                    "cache_read": 5000,
                    "cache_creation": 0,
                },
            },
        )

        assert result["cost"] > 0
        # Cache read: 5000/1M * 0.30 = 0.0015
        assert "cache_read_cost" in result["breakdown"]
        assert result["breakdown"]["cache_read_cost"] == pytest.approx(0.0015, rel=1e-4)

    def test_anthropic_batch(self):
        """Test Anthropic batch pricing (50% discount)."""
        regular = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
        )

        batch = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
            batch=True,
        )

        assert batch["cost"] == pytest.approx(regular["cost"] * 0.5, rel=1e-4)
        assert batch["pricing_used"]["batch_applied"] is True

    def test_anthropic_long_context_auto(self):
        """Test Anthropic auto-detects long context pricing."""
        result = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            usage={
                "input_tokens": 250000,  # Over 200K threshold
                "output_tokens": 1000,
                "total_tokens": 251000,
            },
        )

        assert result["pricing_used"]["long_context_applied"] is True
        # Long context: input $6/MTok, output $22.50/MTok
        assert result["pricing_used"]["input_per_mtok"] == 6.0
        assert result["pricing_used"]["output_per_mtok"] == 22.5

    def test_anthropic_model_alias(self):
        """Test Anthropic model alias resolution."""
        result = calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4",  # Alias
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
        )

        assert result["cost"] > 0

    def test_openai_basic(self):
        """Test basic OpenAI cost calculation."""
        result = calculate_cost(
            provider="openai",
            model="gpt-4o",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
            },
        )

        assert result["currency"] == "USD"
        assert result["cost"] > 0
        # $2.50/MTok input + $10/MTok output
        # 1000/1M * 2.5 + 500/1M * 10 = 0.0025 + 0.005 = 0.0075
        assert abs(result["cost"] - 0.0075) < 0.0001

    def test_openai_with_cache(self):
        """Test OpenAI with cached input."""
        result = calculate_cost(
            provider="openai",
            model="gpt-4o",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
                "input_token_details": {
                    "cache_read": 2000,
                },
            },
        )

        # Cache read: 2000/1M * 1.25 = 0.0025
        assert "cache_read_cost" in result["breakdown"]
        assert result["breakdown"]["cache_read_cost"] == pytest.approx(0.0025, rel=1e-4)

    def test_openai_reasoning_model(self):
        """Test OpenAI o-series model (reasoning tokens in output)."""
        result = calculate_cost(
            provider="openai",
            model="o3-mini",
            usage={
                "input_tokens": 1000,
                "output_tokens": 2000,  # Includes reasoning tokens
                "total_tokens": 3000,
                "output_token_details": {
                    "reasoning": 1500,  # Part of output_tokens
                },
            },
        )

        assert result["cost"] > 0
        # All output tokens billed at output rate
        # 1000/1M * 1.10 + 2000/1M * 4.40 = 0.0011 + 0.0088 = 0.0099
        assert abs(result["cost"] - 0.0099) < 0.0001

    def test_google_basic(self):
        """Test basic Google Gemini cost calculation."""
        result = calculate_cost(
            provider="google",
            model="gemini-2.5-flash",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
            },
        )

        assert result["currency"] == "USD"
        assert result["cost"] > 0
        # $0.30/MTok input + $2.50/MTok output
        # 1000/1M * 0.30 + 500/1M * 2.50 = 0.0003 + 0.00125 = 0.00155
        assert abs(result["cost"] - 0.00155) < 0.0001

    def test_google_long_context(self):
        """Test Google Gemini long context pricing."""
        result = calculate_cost(
            provider="google",
            model="gemini-2.5-pro",
            usage={
                "input_tokens": 250000,  # Over 200K
                "output_tokens": 1000,
                "total_tokens": 251000,
            },
        )

        assert result["pricing_used"]["long_context_applied"] is True
        # Long context: input $2.50/MTok, output $15/MTok
        assert result["pricing_used"]["input_per_mtok"] == 2.50
        assert result["pricing_used"]["output_per_mtok"] == 15.0

    def test_google_batch(self):
        """Test Google batch pricing."""
        regular = calculate_cost(
            provider="google",
            model="gemini-2.5-flash",
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
        )

        batch = calculate_cost(
            provider="google",
            model="gemini-2.5-flash",
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
            batch=True,
        )

        assert batch["cost"] == pytest.approx(regular["cost"] * 0.5, rel=1e-4)

    def test_unknown_provider(self):
        """Test error on unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            calculate_cost(
                provider="unknown",
                model="some-model",
                usage={"input_tokens": 100, "output_tokens": 100, "total_tokens": 200},
            )

    def test_unknown_model(self):
        """Test error on unknown model."""
        with pytest.raises(ValueError, match="Unknown Anthropic model"):
            calculate_cost(
                provider="anthropic",
                model="unknown-model",
                usage={"input_tokens": 100, "output_tokens": 100, "total_tokens": 200},
            )


class TestGetModelPricing:
    """Tests for get_model_pricing function."""

    def test_direct_model_name(self):
        """Test getting pricing by direct model name."""
        pricing = get_model_pricing("anthropic", "claude-sonnet-4-20250514")
        assert pricing is not None
        assert pricing["input"] == 3.0
        assert pricing["output"] == 15.0

    def test_model_alias(self):
        """Test getting pricing by alias."""
        pricing = get_model_pricing("anthropic", "claude-sonnet-4")
        assert pricing is not None
        assert pricing["input"] == 3.0

    def test_unknown_model(self):
        """Test None returned for unknown model."""
        pricing = get_model_pricing("anthropic", "unknown-model")
        assert pricing is None

    def test_unknown_provider(self):
        """Test None returned for unknown provider."""
        pricing = get_model_pricing("unknown", "some-model")
        assert pricing is None


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = list_providers()
        assert "anthropic" in providers
        assert "openai" in providers
        assert "google" in providers

    def test_list_models(self):
        """Test listing models for a provider."""
        models = list_models("anthropic")
        assert len(models) > 0
        assert "claude-sonnet-4-20250514" in models

    def test_list_models_unknown_provider(self):
        """Test listing models for unknown provider returns empty list."""
        models = list_models("unknown")
        assert models == []
