from services.budget_service import BudgetService


def test_register_usage_increases_spent() -> None:
    service = BudgetService(
        daily_budget_usd=2.0,
        timezone_name="UTC",
        input_cost_per_1m=1.0,
        output_cost_per_1m=2.0,
    )

    cost = service.register_usage(input_tokens=1_000_000, output_tokens=500_000)
    assert round(cost, 3) == 2.0
    assert round(service.spent_today(), 3) == 2.0


def test_can_spend_false_when_limit_hit() -> None:
    service = BudgetService(
        daily_budget_usd=0.5,
        timezone_name="UTC",
        input_cost_per_1m=1.0,
        output_cost_per_1m=1.0,
    )
    service.register_usage(input_tokens=500_000, output_tokens=0)
    assert not service.can_spend()
