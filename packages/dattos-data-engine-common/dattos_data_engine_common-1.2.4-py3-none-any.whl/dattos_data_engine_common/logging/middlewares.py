from collections.abc import Awaitable, Callable

import logging
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from .context_vars import (
    path_contextvar,
    trace_id_contextvar,
    user_code_contextvar,
    website_contextvar,
)

logger = logging.getLogger()


async def set_context_vars_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    trace_id = request.headers.get("trace-id")
    user_code = request.headers.get("user-code")

    trace_id_contextvar.set(trace_id)
    user_code_contextvar.set(user_code)
    website_contextvar.set(request.url.hostname)
    path_contextvar.set(request.url.path)
    response = await call_next(request)
    return response


async def structlog_bind_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    with structlog.contextvars.bound_contextvars(
        trace_id=trace_id_contextvar.get(),
        website=website_contextvar.get(),
        path=path_contextvar.get(),
        user_code=user_code_contextvar.get(),
    ):
        return await call_next(request)


async def exception_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(exc, exc_info=True)

        raise exc  # Rethrow a exceção para que FastAPI lide com ela


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(BaseHTTPMiddleware, dispatch=exception_logging_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=structlog_bind_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=set_context_vars_middleware)
