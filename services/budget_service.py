from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class BudgetUsage:
    day: str
    spent_usd: float = 0.0


class BudgetService:
    def __init__(
        self,
        daily_budget_usd: float,
        timezone_name: str,
        input_cost_per_1m: float,
        output_cost_per_1m: float,
    ) -> None:
        self.daily_budget_usd = daily_budget_usd
        self.tz = ZoneInfo(timezone_name)
        self.input_cost_per_1m = input_cost_per_1m
        self.output_cost_per_1m = output_cost_per_1m
        self._usage = BudgetUsage(day=self._today_key())

    def _today_key(self) -> str:
        return datetime.now(self.tz).strftime("%Y-%m-%d")

    def _ensure_today(self) -> None:
        today = self._today_key()
        if today != self._usage.day:
            self._usage = BudgetUsage(day=today)

    def can_spend(self) -> bool:
        self._ensure_today()
        return self._usage.spent_usd < self.daily_budget_usd

    def register_usage(self, input_tokens: int, output_tokens: int) -> float:
        self._ensure_today()
        cost = (
            (input_tokens / 1_000_000) * self.input_cost_per_1m
            + (output_tokens / 1_000_000) * self.output_cost_per_1m
        )
        self._usage.spent_usd += cost
        return cost

    def spent_today(self) -> float:
        self._ensure_today()
        return self._usage.spent_usd
