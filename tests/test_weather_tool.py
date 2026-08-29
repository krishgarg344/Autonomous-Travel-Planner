from tools.get_weather import get_weather

def test_get_weather():
    result = get_weather.invoke({
        "city": "Jaipur",
        "start_date": "2026-08-30",
        "end_date": "2026-09-02"
    })

    print(result)

    assert result["city"] == "Jaipur"
    assert "error" not in result
    assert "forecast" in result
    assert len(result["forecast"]) > 0

    for day in result["forecast"]:
        assert "date" in day
        assert "max_temp_c" in day
        assert "min_temp_c" in day
        assert "rain_chance_pct" in day