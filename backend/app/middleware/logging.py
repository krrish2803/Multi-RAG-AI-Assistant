"""Logging middleware - structured request logging."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("request")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        start = time.perf_counter()

        try:
            response = await call_next(request)
            latency_ms = int((time.perf_counter() - start) * 1000)

            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                client_ip=request.client.host if request.client else "unknown",
            )

            return response

        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                latency_ms=latency_ms,
            )
            raise
