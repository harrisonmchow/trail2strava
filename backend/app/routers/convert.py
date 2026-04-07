from __future__ import annotations

import hashlib
from datetime import datetime

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.alltrails import AllTrailsActivity
from app.models.conversion import ConversionResult, UploadRequest
from app.services.gpx import generate_gpx
from app.services.gpx_parser import parse_gpx
from app.services.mapper import map_activity_type
from app.services.strava import (
    create_manual_activity,
    ensure_valid_token,
    poll_upload,
    upload_gpx,
)
from app.utils.session import get_session, set_session

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _require_session(request: Request) -> dict | None:
    session = get_session(request)
    if not session:
        return None
    return session


def _build_description(activity: AllTrailsActivity) -> str:
    """Build a rich description for the Strava activity."""
    desc_parts = [
        "Originally recorded on AllTrails",
    ]
    if activity.url:
        desc_parts.append(activity.url)
    desc_parts.extend([
        "",
        f"Activity: {activity.title}",
        f"Type: {activity.activity_type}",
    ])
    if activity.calories:
        desc_parts.append(f"Calories: {activity.calories:,}")
    if activity.avg_pace:
        desc_parts.append(f"Avg Pace: {activity.avg_pace}")
    if activity.photos:
        desc_parts.append("")
        desc_parts.append(f"Photos ({len(activity.photos)}):")
        for i, photo in enumerate(activity.photos[:5], 1):
            caption = f" - {photo.caption}" if photo.caption else ""
            desc_parts.append(f"  {i}. {photo.url}{caption}")
    desc_parts.append("")
    desc_parts.append("Synced via Trail2Strava")
    return "\n".join(desc_parts)


async def _upload_to_strava(
    access_token: str,
    activity: AllTrailsActivity,
    custom_title: str | None,
    gpx_content: str | None,
) -> ConversionResult:
    """Upload an activity to Strava via GPX or manual creation."""
    title = custom_title or activity.title
    sport_type = map_activity_type(activity.activity_type)
    description = _build_description(activity)

    if gpx_content:
        # Upload the GPX file directly (preserves GPS track + timestamps)
        external_id = hashlib.md5(
            (activity.url or activity.title).encode()
        ).hexdigest()[:16]

        upload_resp = await upload_gpx(
            access_token=access_token,
            gpx_content=gpx_content,
            name=title,
            description=description,
            sport_type=sport_type,
            external_id=external_id,
        )

        upload_id = upload_resp["id"]
        final = await poll_upload(access_token, upload_id)
        activity_id = final["activity_id"]

        return ConversionResult(
            strava_activity_id=activity_id,
            strava_activity_url=f"https://www.strava.com/activities/{activity_id}",
            upload_method="gpx",
        )

    elif activity.has_gps_data and activity.coordinates:
        # Generate GPX from coordinates
        start_time = (
            datetime.fromisoformat(activity.date.replace("Z", "+00:00"))
            if activity.date
            else datetime.now()
        )

        generated_gpx = generate_gpx(
            coordinates=activity.coordinates,
            activity_name=title,
            start_time=start_time,
            duration_seconds=activity.duration_seconds or 3600,
        )

        external_id = hashlib.md5(
            (activity.url or activity.title).encode()
        ).hexdigest()[:16]

        upload_resp = await upload_gpx(
            access_token=access_token,
            gpx_content=generated_gpx,
            name=title,
            description=description,
            sport_type=sport_type,
            external_id=external_id,
        )

        upload_id = upload_resp["id"]
        final = await poll_upload(access_token, upload_id)
        activity_id = final["activity_id"]

        return ConversionResult(
            strava_activity_id=activity_id,
            strava_activity_url=f"https://www.strava.com/activities/{activity_id}",
            upload_method="gpx",
        )

    else:
        # Manual activity creation (no GPS data)
        resp = await create_manual_activity(
            access_token=access_token,
            name=title,
            sport_type=sport_type,
            start_date_local=activity.date or datetime.now().isoformat(),
            elapsed_time=activity.duration_seconds or 3600,
            description=description,
            distance=activity.distance_meters,
        )
        activity_id = resp["id"]

        return ConversionResult(
            strava_activity_id=activity_id,
            strava_activity_url=f"https://www.strava.com/activities/{activity_id}",
            upload_method="manual",
        )


@router.post("/analyze-gpx")
@limiter.limit("10/minute")
async def analyze_gpx(
    request: Request,
    file: UploadFile = File(...),
    source_url: str = Form(""),
):
    """Parse an uploaded GPX file and return activity data."""
    session = _require_session(request)
    if not session:
        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "Please connect your Strava account first",
            },
        )

    if not file.filename or not file.filename.lower().endswith(".gpx"):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_file",
                "message": "Please upload a .gpx file",
            },
        )

    try:
        content = await file.read()
        gpx_text = content.decode("utf-8")
        activity = parse_gpx(gpx_text, source_url=source_url)
        return activity.model_dump()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "parse_failed",
                "message": f"Could not parse GPX file: {str(e)}",
            },
        )


@router.post("/upload-gpx")
@limiter.limit("10/minute")
async def upload_gpx_file(
    request: Request,
    file: UploadFile = File(...),
    custom_title: str = Form(""),
    source_url: str = Form(""),
):
    """Upload a GPX file directly to Strava."""
    session = _require_session(request)
    if not session:
        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "Please connect your Strava account first",
            },
        )

    # Get valid access token
    try:
        access_token, updated_session = await ensure_valid_token(session)
    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "error": "auth_expired",
                "message": "Strava authorization expired. Please reconnect.",
            },
        )

    try:
        content = await file.read()
        gpx_text = content.decode("utf-8")
        activity = parse_gpx(gpx_text, source_url=source_url)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "parse_failed",
                "message": f"Could not parse GPX file: {str(e)}",
            },
        )

    try:
        result = await _upload_to_strava(
            access_token=access_token,
            activity=activity,
            custom_title=custom_title or None,
            gpx_content=gpx_text,
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "error": "upload_failed",
                "message": f"Failed to create Strava activity: {str(e)}",
                "retryable": True,
            },
        )

    response = JSONResponse(content=result.model_dump())
    if updated_session:
        set_session(response, updated_session)
    return response


@router.post("/upload")
@limiter.limit("10/minute")
async def upload(request: Request, body: UploadRequest):
    """Upload using previously analyzed activity data (URL-based flow)."""
    session = _require_session(request)
    if not session:
        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "Please connect your Strava account first",
            },
        )

    try:
        access_token, updated_session = await ensure_valid_token(session)
    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "error": "auth_expired",
                "message": "Strava authorization expired. Please reconnect.",
            },
        )

    # For URL-based flow, re-scrape to get the data
    from app.services.alltrails import scrape_alltrails, validate_alltrails_url

    if not validate_alltrails_url(body.url):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_url",
                "message": "Please provide a valid AllTrails activity URL",
            },
        )

    try:
        activity = await scrape_alltrails(body.url)
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "error": "scraping_failed",
                "message": str(e),
                "retryable": True,
            },
        )

    try:
        result = await _upload_to_strava(
            access_token=access_token,
            activity=activity,
            custom_title=body.custom_title,
            gpx_content=None,
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "error": "upload_failed",
                "message": f"Failed to create Strava activity: {str(e)}",
                "retryable": True,
            },
        )

    response = JSONResponse(content=result.model_dump())
    if updated_session:
        set_session(response, updated_session)
    return response
