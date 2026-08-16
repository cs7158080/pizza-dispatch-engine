"""Mapping of domain errors to HTTP status codes, over a single body shape.

The table below is the only place a domain failure meets a status code; routes do
not repeat it. Every error body is `{"detail": ...}`, carrying the error's own
message for a domain error.

Pydantic's 422 handler is left in place: its body uses the same key to carry the
list of per-field failures.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pizza.domain.errors import IllegalTransition, OrderNotFound

_STATUS: dict[type[Exception], int] = {OrderNotFound: 404, IllegalTransition: 409}

_Responses = dict[int | str, dict[str, Any]]

# Declared per route, so the generated OpenAPI document names the failures it returns.
NOT_FOUND: _Responses = {404: {"description": "Order not found"}}
CONFLICT: _Responses = {409: {"description": "Illegal transition"}}


def install(app: FastAPI) -> None:
    """Register the error handlers. Called once, by the composition root."""
    for error_type in _STATUS:
        app.add_exception_handler(error_type, _domain_error)
    app.add_exception_handler(Exception, _unexpected_error)


def _domain_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=_STATUS[type(exc)], content={"detail": str(exc)})


def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Answer an unhandled exception with the standard error body.

    Nothing is hidden: Starlette re-raises after this response is sent, so the
    traceback is still logged.
    """
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
