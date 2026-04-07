from __future__ import annotations

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    url: str


class UploadRequest(BaseModel):
    url: str
    custom_title: str | None = None


class ConversionResult(BaseModel):
    strava_activity_id: int
    strava_activity_url: str
    upload_method: str  # "gpx" or "manual"


class ErrorResponse(BaseModel):
    error: str
    message: str
    retryable: bool = False
