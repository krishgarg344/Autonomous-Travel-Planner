import requests
from langchain_core.tools import tool


def _geocode(city: str):
    """Turn a city name into lat/lon using Open-Meteo's free geocoding endpoint."""
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        raise ValueError(f"Could not find coordinates for '{city}'")
    return results[0]["latitude"], results[0]["longitude"]


@tool
def get_weather(city: str, start_date: str, end_date: str) -> dict:
    """Get the daily weather forecast for a city between two dates (YYYY-MM-DD).
    Use this before planning outdoor activities so you can avoid rainy days.
    """
    try:
        lat, lon = _geocode(city)
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "start_date": start_date,
                "end_date": end_date,
            },
            timeout=10,
        )
        resp.raise_for_status()
        daily = resp.json().get("daily", {})

        forecast = []
        for i, date in enumerate(daily.get("time", [])):
            forecast.append({
                "date": date,
                "max_temp_c": daily["temperature_2m_max"][i],
                "min_temp_c": daily["temperature_2m_min"][i],
                "rain_chance_pct": daily["precipitation_probability_max"][i],
            })
        return {"city": city, "forecast": forecast}

    except Exception as e:
        # Open-Meteo only forecasts ~16 days out, so far-future trips will fail here.
        # Agent should treat this as "no weather data available" and continue planning.
        return {"city": city, "forecast": [], "error": str(e)}
