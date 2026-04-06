import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        client = request.client.host if request.client else "-"
        logger.info(
            "%s %s %s -> %s %.2fms",
            client,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
