"""
core/usage_tracker.py
---------------------
Track token usage and costs across all API calls.
"""

from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path

class UsageTracker:
    """
    Global singleton to track token usage and costs.
    
    ⚠️ WARNING: Pricing is hardcoded and based on OpenAI's rates as of December 2024.
    ⚠️ These prices may change over time. Always verify current pricing at:
    ⚠️ https://openai.com/api/pricing/
    
    Pricing as of December 2024 (per 1M tokens):
    - GPT-4o: $2.50 input, $10.00 output
    - GPT-4o-mini: $0.15 input, $0.60 output
    - text-embedding-3-small: $0.02
    - text-embedding-3-large: $0.13
    
    Note: Cost estimates are approximations. Actual costs may vary based on:
    - OpenAI pricing changes
    - Token counting variations
    - Special pricing tiers or agreements
    """
    
    # Current OpenAI pricing (per 1M tokens)
    # ⚠️ IMPORTANT: Update these values if OpenAI changes their pricing
    # Last updated: December 2024
    # Source: https://openai.com/api/pricing/
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
        "text-embedding-3-large": {"input": 0.13, "output": 0.0},
        "text-embedding-ada-002": {"input": 0.10, "output": 0.0},
    }
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all usage statistics."""
        self.stats = {
            "session_start": datetime.now().isoformat(),
            "total_calls": 0,
            "llm_calls": 0,
            "embedding_calls": 0,
            "vision_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "by_model": {}
        }
    
    def track_llm_call(self, model: str, input_tokens: int, output_tokens: int):
        """
        Track a language model API call.
        
        Parameters
        ----------
        model : str
            Model name (e.g., 'gpt-4o-mini')
        input_tokens : int
            Number of input/prompt tokens
        output_tokens : int
            Number of output/completion tokens
        """
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        model_key = self._normalize_model_name(model)
        if model_key in self.PRICING:
            pricing = self.PRICING[model_key]
            cost = (input_tokens / 1_000_000 * pricing["input"] + 
                   output_tokens / 1_000_000 * pricing["output"])
        else:
            cost = 0.0  # Unknown model
        
        # Update totals
        self.stats["total_calls"] += 1
        self.stats["llm_calls"] += 1
        self.stats["total_input_tokens"] += input_tokens
        self.stats["total_output_tokens"] += output_tokens
        self.stats["total_tokens"] += total_tokens
        self.stats["total_cost_usd"] += cost
        
        # Update per-model stats
        if model not in self.stats["by_model"]:
            self.stats["by_model"][model] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0
            }
        
        model_stats = self.stats["by_model"][model]
        model_stats["calls"] += 1
        model_stats["input_tokens"] += input_tokens
        model_stats["output_tokens"] += output_tokens
        model_stats["total_tokens"] += total_tokens
        model_stats["cost_usd"] += cost
    
    def track_embedding_call(self, model: str, tokens: int):
        """
        Track an embedding API call.
        
        Parameters
        ----------
        model : str
            Model name (e.g., 'text-embedding-3-small')
        tokens : int
            Number of tokens processed
        """
        # Calculate cost
        model_key = self._normalize_model_name(model)
        if model_key in self.PRICING:
            cost = tokens / 1_000_000 * self.PRICING[model_key]["input"]
        else:
            cost = 0.0
        
        # Update totals
        self.stats["total_calls"] += 1
        self.stats["embedding_calls"] += 1
        self.stats["total_input_tokens"] += tokens
        self.stats["total_tokens"] += tokens
        self.stats["total_cost_usd"] += cost
        
        # Update per-model stats
        if model not in self.stats["by_model"]:
            self.stats["by_model"][model] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0
            }
        
        model_stats = self.stats["by_model"][model]
        model_stats["calls"] += 1
        model_stats["input_tokens"] += tokens
        model_stats["total_tokens"] += tokens
        model_stats["cost_usd"] += cost
    
    def track_vision_call(self, model: str, input_tokens: int, output_tokens: int):
        """Track a vision model call (same as LLM but with vision flag)."""
        self.stats["vision_calls"] += 1
        self.track_llm_call(model, input_tokens, output_tokens)
    
    def get_stats(self) -> Dict:
        """
        Get current usage statistics.
        
        Returns
        -------
        dict
            Usage statistics including tokens, costs, and breakdown by model
        """
        return self.stats.copy()
    
    def print_summary(self):
        """Print a human-readable summary of usage statistics."""
        print("\n" + "="*70)
        print("Token Usage & Cost Summary")
        print("="*70)
        print(f"Session Start: {self.stats['session_start']}")
        print(f"\nAPI Calls:")
        print(f"  Total Calls:      {self.stats['total_calls']}")
        print(f"  LLM Calls:        {self.stats['llm_calls']}")
        print(f"  Embedding Calls:  {self.stats['embedding_calls']}")
        print(f"  Vision Calls:     {self.stats['vision_calls']}")
        print(f"\nToken Usage:")
        print(f"  Input Tokens:     {self.stats['total_input_tokens']:,}")
        print(f"  Output Tokens:    {self.stats['total_output_tokens']:,}")
        print(f"  Total Tokens:     {self.stats['total_tokens']:,}")
        print(f"\nEstimated Cost:")
        print(f"  Total Cost (USD): ${self.stats['total_cost_usd']:.4f}")
        print(f"  ⚠️  Note: Estimates based on Dec 2024 pricing")
        
        if self.stats['by_model']:
            print(f"\nBreakdown by Model:")
            for model, stats in self.stats['by_model'].items():
                print(f"  {model}:")
                print(f"    Calls:        {stats['calls']}")
                print(f"    Total Tokens: {stats['total_tokens']:,}")
                print(f"    Cost (USD):   ${stats['cost_usd']:.4f}")
        
        print("="*70 + "\n")
    
    def save_to_file(self, filepath: str):
        """Save usage statistics to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"✅ Usage statistics saved to {filepath}")
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name to match pricing keys."""
        model_lower = model.lower()
        # Handle versioned models
        if "gpt-4o-mini" in model_lower:
            return "gpt-4o-mini"
        elif "gpt-4o" in model_lower:
            return "gpt-4o"
        elif "gpt-4" in model_lower:
            return "gpt-4"
        elif "gpt-3.5-turbo" in model_lower:
            return "gpt-3.5-turbo"
        elif "text-embedding-3-small" in model_lower:
            return "text-embedding-3-small"
        elif "text-embedding-3-large" in model_lower:
            return "text-embedding-3-large"
        elif "text-embedding-ada-002" in model_lower:
            return "text-embedding-ada-002"
        else:
            return model


# Global singleton instance
_tracker = UsageTracker()

def get_tracker() -> UsageTracker:
    """Get the global usage tracker instance."""
    return _tracker
