"""Every domain error to its status code, over one body shape.

The table is the only place a domain failure meets a status number, so no route
carries the mapping and no route repeats it. The body is always `{"detail": …}`;
for a domain error the sentence is the error's own, so it exists once.

Pydantic's `422` handler is left alone: its body is a list of per-field failures,
which is the same key carrying the shape that class of failure needs.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pizza.domain.errors import IllegalTransition, OrderNotFound

_STATUS: dict[type[Exception], int] = {OrderNotFound: 404, IllegalTransition: 409}

_Responses = dict[int | str, dict[str, Any]]

# Declared per route, so the generated document names the failures it answers with.
NOT_FOUND: _Responses = {404: {"description": "Order not found"}}
CONFLICT: _Responses = {409: {"description": "Illegal transition"}}


def install(app: FastAPI) -> None:
    """Register the handlers. Called once, by the composition root."""
    for error_type in _STATUS:
        app.add_exception_handler(error_type, _domain_error)
    app.add_exception_handler(Exception, _unexpected_error)


def _domain_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=_STATUS[type(exc)], content={"detail": str(exc)})


def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Give an unhandled exception the one key every error response carries.

    It hides nothing: Starlette re-raises after this response is sent, so the
    server still logs the traceback.
    """
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
