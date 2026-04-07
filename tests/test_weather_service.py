from services.weather_service import clothing_advice, weather_description


def test_weather_description_unknown_fallback() -> None:
    assert weather_description(12345) == "погода меняется"


def test_clothing_advice_contains_core_tip() -> None:
    weather = {"temperature": 32, "rain_probability": 70, "wind": 25}
    advice = clothing_advice(weather)
    assert "очень жарко" in advice
    assert "дождевик" in advice
