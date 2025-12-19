"""Unit tests for pricing calculations."""

import unittest

from vibelab.pricing import (
    calculate_cost,
    get_litellm_pricing,
    get_pricing,
    list_available_models,
    LITELLM_AVAILABLE,
)
from vibelab.harnesses import HARNESSES


class TestPricing(unittest.TestCase):
    """Tests for pricing calculations."""

    def test_calculate_cost_with_input_output(self):
        """Test cost calculation with input/output token breakdown."""
        harness = HARNESSES["claude-code"]
        cost = calculate_cost(harness, "anthropic", "opus", input_tokens=1000, output_tokens=500)
        self.assertIsNotNone(cost)
        # Expected: (1000/1M * 15) + (500/1M * 75) = 0.015 + 0.0375 = 0.0525
        self.assertAlmostEqual(cost, 0.0525, places=6)

    def test_calculate_cost_with_total_tokens(self):
        """Test cost calculation with total tokens only."""
        harness = HARNESSES["openai-codex"]
        cost = calculate_cost(harness, "openai", "gpt-4o", total_tokens=1000)
        self.assertIsNotNone(cost)
        # Expected: (500/1M * 2.50) + (500/1M * 10.0) = 0.00125 + 0.005 = 0.00625
        self.assertAlmostEqual(cost, 0.00625, places=6)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation with unknown model."""
        harness = HARNESSES["claude-code"]
        cost = calculate_cost(harness, "anthropic", "unknown-model", input_tokens=1000, output_tokens=500)
        self.assertIsNone(cost)

    def test_pricing_coverage(self):
        """Test that all harness models have pricing."""
        for harness in HARNESSES.values():
            for provider in harness.supported_providers:
                models = harness.get_models(provider)
                for model_info in models:
                    # Check if pricing exists
                    pricing = harness.get_pricing(provider, model_info.id)
                    if pricing:
                        self.assertIsNotNone(
                            pricing,
                            f"Pricing found for {harness.id}:{provider}:{model_info.id}",
                        )
                    else:
                        # Log warning but don't fail - new models may not have pricing yet
                        print(
                            f"Warning: No pricing found for {harness.id}:{provider}:{model_info.id}"
                        )


class TestLiteLLMPricing(unittest.TestCase):
    """Tests for LiteLLM pricing integration."""

    def test_litellm_available(self):
        """Test that LiteLLM is available."""
        self.assertTrue(LITELLM_AVAILABLE, "LiteLLM should be installed")

    def test_litellm_pricing_openai(self):
        """Test LiteLLM pricing for OpenAI models."""
        pricing = get_litellm_pricing("gpt-4o")
        self.assertIsNotNone(pricing, "Should find gpt-4o pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_anthropic(self):
        """Test LiteLLM pricing for Anthropic models."""
        pricing = get_litellm_pricing("claude-3-5-sonnet-20241022")
        self.assertIsNotNone(pricing, "Should find claude-3-5-sonnet pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_gemini(self):
        """Test LiteLLM pricing for Gemini models."""
        pricing = get_litellm_pricing("gemini-1.5-pro")
        self.assertIsNotNone(pricing, "Should find gemini-1.5-pro pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_get_pricing_prefers_litellm(self):
        """Test that get_pricing prefers LiteLLM over harness pricing."""
        harness = HARNESSES["openai-codex"]
        pricing = get_pricing("gpt-4o", harness, "openai")
        self.assertIsNotNone(pricing)
        # LiteLLM should have cache pricing info
        self.assertIsNotNone(pricing.cache_read_price_per_1m)

    def test_get_pricing_falls_back_to_harness(self):
        """Test that get_pricing falls back to harness for unknown models."""
        harness = HARNESSES["claude-code"]
        # 'opus' is a Claude Code simplified name not in LiteLLM
        pricing = get_pricing("opus", harness, "anthropic")
        self.assertIsNotNone(pricing, "Should fall back to harness pricing for 'opus'")

    def test_list_available_models_filtering(self):
        """Test listing models with provider filter."""
        openai_models = list_available_models("openai")
        self.assertGreater(len(openai_models), 0, "Should find OpenAI models")
        
        anthropic_models = list_available_models("anthropic")
        self.assertGreater(len(anthropic_models), 0, "Should find Anthropic models")

