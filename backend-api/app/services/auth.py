from __future__ import annotations

from datetime import UTC, datetime, timedelta
import base64
import hashlib
import hmac
import json
from threading import RLock
from typing import Any

from fastapi import HTTPException, status

from app.config import load_runtime_config
from app.repositories.store import get_store
from app.schemas.auth import AuthToken, UserCreate, UserLogin, UserRead
from app.security import hash_password, validate_password_policy, verify_password

DEMO_AUTH_EMAIL = "demo@ordostack.local"
DEMO_AUTH_PASSWORD = "ordostack-demo"

_login_rate_limit_lock = RLock()
_login_rate_limit_state: dict[str, dict[str, Any]] = {}


def register_user(payload: UserCreate) -> AuthToken:
    store = get_store()
    email = normalize_email(payload.email)
    if store.get_user_by_email(email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    validate_register_password(password=payload.password, email=email)
    user = store.create_user(
        {
            "email": email,
            "display_name": payload.display_name.strip(),
            "password_hash": hash_password(payload.password),
        }
    )
    return build_auth_token(user)


def login_user(payload: UserLogin, client_identifier: str = "unknown") -> AuthToken:
    store = get_store()
    email = normalize_email(payload.email)
    rate_limit_key = build_rate_limit_key(email=email, client_identifier=client_identifier)
    enforce_login_rate_limit(rate_limit_key)

    user = store.get_user_by_email(email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        record_failed_login(rate_limit_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    clear_login_rate_limit(rate_limit_key)
    return build_auth_token(user)


def get_user_from_token(token: str) -> UserRead:
    payload = decode_token(token)
    user = get_store().get_user(int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return UserRead.model_validate(user)


def build_auth_token(user: dict[str, Any]) -> AuthToken:
    user_read = UserRead.model_validate(user)
    access_token, expires_at = encode_token(user_read)
    return AuthToken(access_token=access_token, expires_at=expires_at, user=user_read)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def encode_token(user: UserRead) -> tuple[str, datetime]:
    config = load_runtime_config()
    expires_at = datetime.now(UTC) + timedelta(minutes=config.auth_token_ttl_minutes)
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": int(expires_at.timestamp()),
    }
    payload_segment = base64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = sign(payload_segment)
    return f"{payload_segment}.{signature}", expires_at


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


def validate_register_password(*, password: str, email: str) -> None:
    config = load_runtime_config()
    violations = validate_password_policy(password, email=email, min_length=config.auth_password_min_length)
    if not violations:
        return

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Password must include " + ", ".join(violations),
    )


def build_rate_limit_key(*, email: str, client_identifier: str) -> str:
    return f"{email}:{client_identifier.strip() or 'unknown'}"


def enforce_login_rate_limit(rate_limit_key: str) -> None:
    config = load_runtime_config()
    now = datetime.now(UTC)
    with _login_rate_limit_lock:
        state = _login_rate_limit_state.get(rate_limit_key)
        if state is None:
            return

        locked_until = state.get("locked_until")
        if isinstance(locked_until, datetime) and locked_until > now:
            raise login_rate_limit_error(locked_until)

        window_started_at = now - timedelta(seconds=config.auth_login_window_seconds)
        attempts = [attempt for attempt in state.get("attempts", []) if attempt >= window_started_at]
        if attempts:
            state["attempts"] = attempts
            state["locked_until"] = None
            return

        _login_rate_limit_state.pop(rate_limit_key, None)


def record_failed_login(rate_limit_key: str) -> None:
    config = load_runtime_config()
    now = datetime.now(UTC)
    window_started_at = now - timedelta(seconds=config.auth_login_window_seconds)

    with _login_rate_limit_lock:
        state = _login_rate_limit_state.setdefault(rate_limit_key, {"attempts": [], "locked_until": None})
        attempts = [attempt for attempt in state["attempts"] if attempt >= window_started_at]
        attempts.append(now)
        state["attempts"] = attempts

        if len(attempts) < config.auth_login_max_failures:
            return

        locked_until = now + timedelta(seconds=config.auth_login_lockout_seconds)
        state["locked_until"] = locked_until
        raise login_rate_limit_error(locked_until)


def clear_login_rate_limit(rate_limit_key: str | None = None) -> None:
    with _login_rate_limit_lock:
        if rate_limit_key is None:
            _login_rate_limit_state.clear()
            return
        _login_rate_limit_state.pop(rate_limit_key, None)


def login_rate_limit_error(locked_until: datetime) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": "Too many failed login attempts",
            "locked_until": locked_until.isoformat(),
        },
    )
