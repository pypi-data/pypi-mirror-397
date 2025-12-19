import time
from typing import Optional, Callable, Awaitable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, FileResponse

from wmain.common.logging import HttpLogRecord


def make_logging_middleware(
        max_body_size: int = 1024,
        before_request: Optional[Callable[[HttpLogRecord], Awaitable[None]]] = None,
        after_request: Optional[Callable[[HttpLogRecord], Awaitable[None]]] = None,
):
    class LoggingMiddleware(BaseHTTPMiddleware):

        async def dispatch(self, request: Request, call_next):

            body_bytes: Optional[bytes] = await request.body()
            if body_bytes and len(body_bytes) > max_body_size:
                body_bytes = None

            # 支持 FastAPI 后续读取
            async def receive():
                return {
                    "type": "http.request",
                    "body": body_bytes or b"",
                    "more_body": False
                }

            info = HttpLogRecord(
                client_host=request.client.host,
                client_port=request.client.port,
                method=request.method,
                url=str(request.url),
                scheme=request.url.scheme,
                host=request.url.hostname or "",
                port=request.url.port or 0,
                path=request.url.path,
                query_string=request.url.query or "",
                http_version=request.scope.get("http_version", ""),

                request_headers=dict(request.headers),
                request_body=body_bytes,
            )
            info.set_request_time()
            request._receive = receive

            if before_request is not None:
                await before_request(info)

            response = await call_next(request)

            response_bytes = None
            if not isinstance(response, (StreamingResponse, FileResponse)):
                collected = b""
                async for chunk in response.body_iterator:
                    collected += chunk
                if len(collected) <= max_body_size:
                    response_bytes = collected

                async def new_iter():
                    yield collected

                response.body_iterator = new_iter()

            info.set_response_time()
            info.set_response(response)
            info.cal_duration()
            info.response_body = response_bytes

            if after_request is not None:
                await after_request(info)
            return response

    return LoggingMiddleware
