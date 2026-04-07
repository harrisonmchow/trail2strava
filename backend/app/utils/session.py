from __future__ import annotations

from starlette.requests import Request
from starlette.responses import Response

from app.utils.crypto import decrypt_tokens, encrypt_tokens

COOKIE_NAME = "at2s_session"


def set_session(response: Response, data: dict) -> None:
    encrypted = encrypt_tokens(data)
    response.set_cookie(
        key=COOKIE_NAME,
        value=encrypted,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400,  # 24 hours
        path="/",
    )


def get_session(request: Request) -> dict | None:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return None
    try:
        return decrypt_tokens(cookie)
    except Exception:
        return None


def clear_session(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")
