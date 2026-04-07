from __future__ import annotations

from pydantic import BaseModel


class AllTrailsPhoto(BaseModel):
    url: str
    caption: str | None = None


class AllTrailsActivity(BaseModel):
    url: str
    title: str
    activity_type: str
    distance_meters: float
    elevation_gain_meters: float
    duration_seconds: int
    moving_time_seconds: int = 0
    avg_pace: str = ""
    calories: int = 0
    date: str  # ISO 8601
    has_gps_data: bool
    coordinates: list[tuple[float, float, float | None]] = []  # lat, lon, ele
    photos: list[AllTrailsPhoto] = []
