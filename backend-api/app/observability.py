from __future__ import annotations

import json
import logging
import re
import time
import uuid
from collections.abc import Callable, Awaitable

from fastapi import FastAPI, Request, Response

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

logger = logging.getLogger("ordostack.requests")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def configure_request_observability(app: FastAPI, service_name: str) -> None:
    @app.middleware("http")
    async def request_observability_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = get_request_id(request)
        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            log_request(
                service_name=service_name,
                request_id=request_id,
                request=request,
                status_code=500,
                duration_ms=elapsed_ms(started_at),
                level="exception",
            )
            raise

        response.headers[REQUEST_ID_HEADER] = request_id
        log_request(
            service_name=service_name,
            request_id=request_id,
            request=request,
            status_code=response.status_code,
            duration_ms=elapsed_ms(started_at),
            level="info",
        )
        return response


def get_request_id(request: Request) -> str:
    candidate = request.headers.get(REQUEST_ID_HEADER)
    if candidate is not None and REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid.uuid4())


def elapsed_ms(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)


def log_request(
    *,
    service_name: str,
    request_id: str,
    request: Request,
    status_code: int,
    duration_ms: int,
    level: str,
) -> None:
    payload = {
        "event": "http_request",
        "service": service_name,
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    message = json.dumps(payload, separators=(",", ":"))
    if level == "exception":
        logger.exception(message)
        return
    logger.info(message)
