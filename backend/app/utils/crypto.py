import base64
import hashlib
import json

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    key = hashlib.sha256(settings.SESSION_SECRET.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_tokens(data: dict) -> str:
    f = _get_fernet()
    return f.encrypt(json.dumps(data).encode()).decode()


def decrypt_tokens(token: str) -> dict:
    f = _get_fernet()
    return json.loads(f.decrypt(token.encode()).decode())
