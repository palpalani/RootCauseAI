"""Cost tracking and monitoring for OpenAI API usage."""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

# OpenAI pricing (as of 2024, update as needed)
# GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens
PRICING = {
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,  # per token
        "output": 0.60 / 1_000_000,  # per token
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,
        "output": 10.00 / 1_000_000,
    },
    "gpt-3.5-turbo": {
        "input": 0.50 / 1_000_000,
        "output": 1.50 / 1_000_000,
    },
}


class CostTracker:
    """Track OpenAI API costs and usage."""

    def __init__(self, storage_path: Path | str = "cost_data.json") -> None:
        """Initialize cost tracker.

        Args:
            storage_path: Path to store cost data.
        """
        self.storage_path = Path(storage_path)
        self.daily_costs: dict[str, float] = defaultdict(float)
        self.daily_usage: dict[str, int] = defaultdict(int)
        self._load_data()

    def _load_data(self) -> None:
        """Load historical cost data."""
        if self.storage_path.exists():
            try:
                with self.storage_path.open() as f:
                    data = json.load(f)
                    self.daily_costs = defaultdict(float, data.get("daily_costs", {}))
                    self.daily_usage = defaultdict(int, data.get("daily_usage", {}))
            except Exception as e:
                logger.warning(f"Failed to load cost data: {e}")

    def _save_data(self) -> None:
        """Save cost data to disk."""
        try:
            data = {
                "daily_costs": dict(self.daily_costs),
                "daily_usage": dict(self.daily_usage),
                "last_updated": datetime.now().isoformat(),
            }
            with self.storage_path.open("w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cost data: {e}")

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Record API usage and calculate cost.

        Args:
            model: Model name used.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Cost in USD.
        """
        if model not in PRICING:
            logger.warning(f"Unknown model pricing: {model}, using gpt-4o-mini")
            model = "gpt-4o-mini"

        pricing = PRICING[model]
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])

        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_costs[today] += cost
        self.daily_usage[today] += 1

        self._save_data()

        logger.info(
            f"API usage: {input_tokens} input + {output_tokens} output tokens = ${cost:.4f}",
        )

        return cost

    def get_daily_cost(self, date: str | None = None) -> float:
        """Get cost for a specific date.

        Args:
            date: Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            Cost in USD.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.daily_costs.get(date, 0.0)

    def get_monthly_cost(self) -> float:
        """Get cost for current month.

        Returns:
            Total cost in USD for current month.
        """
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")

        total = 0.0
        for date, cost in self.daily_costs.items():
            if date >= month_start:
                total += cost

        return total

    def get_usage_stats(self, days: int = 7) -> dict[str, float | int]:
        """Get usage statistics for the last N days.

        Args:
            days: Number of days to analyze.

        Returns:
            Dictionary with usage statistics.
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        total_cost = 0.0
        total_requests = 0
        daily_averages: list[float] = []

        for date, cost in self.daily_costs.items():
            if date >= cutoff_date:
                total_cost += cost
                total_requests += self.daily_usage.get(date, 0)
                daily_averages.append(cost)

        avg_daily_cost = sum(daily_averages) / len(daily_averages) if daily_averages else 0.0

        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "average_daily_cost": avg_daily_cost,
            "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0.0,
            "days_analyzed": days,
        }

    def check_budget_alert(self, daily_budget: float, monthly_budget: float) -> dict[str, bool]:
        """Check if budgets are exceeded.

        Args:
            daily_budget: Daily budget limit in USD.
            monthly_budget: Monthly budget limit in USD.

        Returns:
            Dictionary with alert status.
        """
        daily_cost = self.get_daily_cost()
        monthly_cost = self.get_monthly_cost()

        return {
            "daily_exceeded": daily_cost > daily_budget,
            "monthly_exceeded": monthly_cost > monthly_budget,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "daily_budget": daily_budget,
            "monthly_budget": monthly_budget,
        }


# Global cost tracker instance
_cost_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get or create global cost tracker instance.

    Returns:
        CostTracker instance.
    """
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
