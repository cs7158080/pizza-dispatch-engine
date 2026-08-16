"""Driver routes. Registration only: drivers are never read through the API."""

from fastapi import APIRouter

from pizza.entrypoints.api.deps import RegisterDriverDep
from pizza.entrypoints.api.schemas import Created, RegisterDriverRequest

router = APIRouter()


@router.post("/drivers", status_code=201)
def register_driver(
    body: RegisterDriverRequest, register: RegisterDriverDep
) -> Created:
    """Register a driver, available from the start, and return their identifier."""
    return Created(id=register(body.name))
