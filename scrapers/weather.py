"""Weather scraper using the wttr.in JSON API."""

import requests

BASE_URL = "https://wttr.in"


def get_weather(location: str) -> dict:
    """Return current weather and a 3-day forecast for a location.

    Args:
        location: City name, airport code, or coordinates (e.g. "London",
                  "JFK", "48.8566,2.3522").

    Returns:
        Dict with keys:
          - location: resolved location name
          - current: dict with temp_c, temp_f, feels_like_c, feels_like_f,
                     description, humidity, wind_kmph, wind_mph
          - forecast: list of up to 3 dicts with date, max_temp_c, min_temp_c,
                      max_temp_f, min_temp_f, description
    """
    resp = requests.get(
        f"{BASE_URL}/{location}",
        params={"format": "j1"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    nearest = data.get("nearest_area", [{}])[0]
    area_name = nearest.get("areaName", [{}])[0].get("value", location)
    country = nearest.get("country", [{}])[0].get("value", "")
    resolved_location = f"{area_name}, {country}" if country else area_name

    current_cond = data.get("current_condition", [{}])[0]
    current = {
        "temp_c": int(current_cond.get("temp_C", 0)),
        "temp_f": int(current_cond.get("temp_F", 0)),
        "feels_like_c": int(current_cond.get("FeelsLikeC", 0)),
        "feels_like_f": int(current_cond.get("FeelsLikeF", 0)),
        "description": current_cond.get("weatherDesc", [{}])[0].get("value", ""),
        "humidity": int(current_cond.get("humidity", 0)),
        "wind_kmph": int(current_cond.get("windspeedKmph", 0)),
        "wind_mph": int(current_cond.get("windspeedMiles", 0)),
    }

    forecast = []
    for day in data.get("weather", []):
        hourly = day.get("hourly", [{}])
        descriptions = [h.get("weatherDesc", [{}])[0].get("value", "") for h in hourly if h.get("weatherDesc")]
        description = descriptions[len(descriptions) // 2] if descriptions else ""
        forecast.append(
            {
                "date": day.get("date", ""),
                "max_temp_c": int(day.get("maxtempC", 0)),
                "min_temp_c": int(day.get("mintempC", 0)),
                "max_temp_f": int(day.get("maxtempF", 0)),
                "min_temp_f": int(day.get("mintempF", 0)),
                "description": description,
            }
        )

    return {
        "location": resolved_location,
        "current": current,
        "forecast": forecast,
    }


if __name__ == "__main__":
    city = "London"
    data = get_weather(city)
    print(f"Weather for {data['location']}:")
    c = data["current"]
    print(f"  Now: {c['temp_c']}°C / {c['temp_f']}°F  — {c['description']}")
    print(f"  Feels like: {c['feels_like_c']}°C, Humidity: {c['humidity']}%, Wind: {c['wind_kmph']} km/h")
    print("\n  3-Day Forecast:")
    for day in data["forecast"]:
        print(f"  {day['date']}: {day['min_temp_c']}–{day['max_temp_c']}°C  {day['description']}")
