"""Recent + upcoming weather from Open-Meteo (free, no API key).

We only need a few facts for trimming advice:
  - Is frost coming in the next 14 days?  (fresh cuts and new shoots get damaged)
  - Was it hot and dry in the last 7 days? (wilting is probably thirst)
"""
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

FROST_C = 0.0
HOT_C = 30.0
DRY_MM = 5.0  # total rain over 7 days below this counts as "dry"


@dataclass
class Weather:
    place: str
    latitude: float
    frost_soon: bool  # min temp <= 0°C in the next 14 days
    first_frost_in_days: int | None
    hot_dry_recently: bool  # a 30°C+ day and < 5 mm rain in the last 7 days
    max_temp_7d: float
    rain_7d_mm: float

    @property
    def hemisphere(self) -> str:
        return "south" if self.latitude < 0 else "north"

    def summary(self) -> str:
        frost = (f"frost expected in {self.first_frost_in_days} day(s)" if self.frost_soon
                 else "no frost in the next 14 days")
        return (f"{self.place}: last 7 days max {self.max_temp_7d:.0f}°C, "
                f"{self.rain_7d_mm:.0f} mm rain; {frost}.")


def _get(url: str, params: dict) -> dict:
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=10) as r:
        return json.load(r)


def geocode(place: str) -> tuple[float, float, str]:
    res = _get("https://geocoding-api.open-meteo.com/v1/search", {"name": place, "count": 1})
    if not res.get("results"):
        raise ValueError(f"Couldn't find a place called {place!r}")
    r = res["results"][0]
    return r["latitude"], r["longitude"], f"{r['name']}, {r.get('country', '')}".strip(", ")


def summarize(daily: dict, place: str, latitude: float, past_days: int = 7) -> Weather:
    tmin, tmax, rain = daily["temperature_2m_min"], daily["temperature_2m_max"], daily["precipitation_sum"]
    past = slice(0, past_days)
    future_min = tmin[past_days:]
    frost_days = [i for i, t in enumerate(future_min) if t is not None and t <= FROST_C]
    max_7d = max(t for t in tmax[past] if t is not None)
    rain_7d = sum(r or 0 for r in rain[past])
    return Weather(place=place, latitude=latitude,
                   frost_soon=bool(frost_days), first_frost_in_days=frost_days[0] if frost_days else None,
                   hot_dry_recently=max_7d >= HOT_C and rain_7d < DRY_MM,
                   max_temp_7d=max_7d, rain_7d_mm=rain_7d)


def fetch(place: str) -> Weather:
    lat, lon, name = geocode(place)
    res = _get("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon, "timezone": "auto",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": 7, "forecast_days": 14,
    })
    return summarize(res["daily"], name, lat)
