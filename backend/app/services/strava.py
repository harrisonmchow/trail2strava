from __future__ import annotations

import hashlib
import hmac
import io
import secrets
import time

import httpx

from app.config import settings

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"


def generate_oauth_state() -> str:
    nonce = secrets.token_urlsafe(32)
    sig = hmac.new(
        settings.SESSION_SECRET.encode(), nonce.encode(), hashlib.sha256
    ).hexdigest()[:16]
    return f"{nonce}.{sig}"


def verify_oauth_state(state: str) -> bool:
    parts = state.split(".")
    if len(parts) != 2:
        return False
    nonce, sig = parts
    expected = hmac.new(
        settings.SESSION_SECRET.encode(), nonce.encode(), hashlib.sha256
    ).hexdigest()[:16]
    return hmac.compare_digest(sig, expected)


def get_authorization_url(state: str) -> str:
    redirect_uri = f"{settings.FRONTEND_URL}/callback"
    return (
        f"{STRAVA_AUTH_URL}?"
        f"client_id={settings.STRAVA_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=activity:write&"
        f"state={state}&"
        f"approval_prompt=auto"
    )


async def exchange_token(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def ensure_valid_token(session_data: dict) -> tuple[str, dict | None]:
    """Returns (access_token, updated_session_data_or_None)."""
    expires_at = session_data.get("expires_at", 0)
    if time.time() < expires_at - 300:
        return session_data["access_token"], None

    token_data = await refresh_access_token(session_data["refresh_token"])
    updated = {
        **session_data,
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_at": token_data["expires_at"],
    }
    return updated["access_token"], updated


async def upload_gpx(access_token: str, gpx_content: str, name: str, description: str, sport_type: str, external_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        files = {"file": ("activity.gpx", io.BytesIO(gpx_content.encode()), "application/gpx+xml")}
        data = {
            "data_type": "gpx",
            "name": name,
            "description": description,
            "sport_type": sport_type,
            "external_id": external_id,
        }
        resp = await client.post(
            f"{STRAVA_API_BASE}/uploads",
            headers={"Authorization": f"Bearer {access_token}"},
            files=files,
            data=data,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


async def poll_upload(access_token: str, upload_id: int, max_attempts: int = 10) -> dict:
    async with httpx.AsyncClient() as client:
        import asyncio
        for _ in range(max_attempts):
            resp = await client.get(
                f"{STRAVA_API_BASE}/uploads/{upload_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("activity_id"):
                return data
            if data.get("error"):
                raise Exception(f"Strava upload error: {data['error']}")

            await asyncio.sleep(2)

    raise Exception("Upload processing timed out")


async def create_manual_activity(
    access_token: str,
    name: str,
    sport_type: str,
    start_date_local: str,
    elapsed_time: int,
    description: str,
    distance: float,
) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{STRAVA_API_BASE}/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": name,
                "sport_type": sport_type,
                "start_date_local": start_date_local,
                "elapsed_time": elapsed_time,
                "description": description,
                "distance": distance,
            },
        )
        resp.raise_for_status()
        return resp.json()
