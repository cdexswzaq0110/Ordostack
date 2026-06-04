from __future__ import annotations

from datetime import UTC, datetime, timedelta
import base64
import hashlib
import hmac
import json
from typing import Any

from fastapi import HTTPException, status

from app.config import load_runtime_config
from app.repositories.store import get_store
from app.schemas.auth import AuthToken, UserCreate, UserLogin, UserRead
from app.security import hash_password, verify_password

DEMO_AUTH_EMAIL = "demo@ordostack.local"
DEMO_AUTH_PASSWORD = "ordostack-demo"
TOKEN_LIFETIME = timedelta(days=7)


def register_user(payload: UserCreate) -> AuthToken:
    store = get_store()
    email = normalize_email(payload.email)
    if store.get_user_by_email(email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = store.create_user(
        {
            "email": email,
            "display_name": payload.display_name.strip(),
            "password_hash": hash_password(payload.password),
        }
    )
    return build_auth_token(user)


def login_user(payload: UserLogin) -> AuthToken:
    store = get_store()
    user = store.get_user_by_email(normalize_email(payload.email))
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return build_auth_token(user)


def get_user_from_token(token: str) -> UserRead:
    payload = decode_token(token)
    user = get_store().get_user(int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return UserRead.model_validate(user)


def build_auth_token(user: dict[str, Any]) -> AuthToken:
    user_read = UserRead.model_validate(user)
    return AuthToken(access_token=encode_token(user_read), user=user_read)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def encode_token(user: UserRead) -> str:
    expires_at = datetime.now(UTC) + TOKEN_LIFETIME
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": int(expires_at.timestamp()),
    }
    payload_segment = base64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = sign(payload_segment)
    return f"{payload_segment}.{signature}"


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload_segment, signature = token.split(".", 1)
    except ValueError as error:
        raise invalid_token_error() from error

    if not hmac.compare_digest(sign(payload_segment), signature):
        raise invalid_token_error()

    try:
        payload = json.loads(base64_url_decode(payload_segment))
    except (json.JSONDecodeError, ValueError) as error:
        raise invalid_token_error() from error

    expires_at = int(payload.get("exp", 0))
    if expires_at < int(datetime.now(UTC).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token expired")
    if "sub" not in payload:
        raise invalid_token_error()
    return payload


def sign(payload_segment: str) -> str:
    secret = load_runtime_config().auth_token_secret.encode("utf-8")
    digest = hmac.new(secret, payload_segment.encode("utf-8"), hashlib.sha256).digest()
    return base64_url_encode(digest)


def base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def invalid_token_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
