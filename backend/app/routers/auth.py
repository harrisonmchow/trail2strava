from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.strava import (
    exchange_token,
    generate_oauth_state,
    get_authorization_url,
    verify_oauth_state,
)
from app.utils.session import clear_session, get_session, set_session

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/login")
@limiter.limit("30/minute")
async def login(request: Request):
    state = generate_oauth_state()
    url = get_authorization_url(state)
    return {"url": url, "state": state}


@router.post("/token")
@limiter.limit("30/minute")
async def token(request: Request):
    body = await request.json()
    code = body.get("code")
    state = body.get("state")

    if not code or not state:
        return JSONResponse(
            status_code=400,
            content={"error": "missing_params", "message": "Missing code or state"},
        )

    if not verify_oauth_state(state):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_state", "message": "Invalid OAuth state"},
        )

    try:
        token_data = await exchange_token(code)
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "error": "token_exchange_failed",
                "message": f"Failed to exchange token with Strava: {str(e)}",
            },
        )

    athlete = token_data.get("athlete", {})
    session_data = {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_at": token_data["expires_at"],
        "athlete_id": athlete.get("id"),
        "first_name": athlete.get("firstname", ""),
    }

    response = JSONResponse(
        content={
            "athlete_id": athlete.get("id"),
            "first_name": athlete.get("firstname", ""),
        }
    )
    set_session(response, session_data)
    return response


@router.get("/status")
async def status(request: Request):
    session = get_session(request)
    if not session:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "athlete_id": session.get("athlete_id"),
        "first_name": session.get("first_name", ""),
    }


@router.post("/logout")
async def logout(request: Request):
    response = JSONResponse(content={"ok": True})
    clear_session(response)
    return response
