"""The one driver route: registering one. There is no driver read anywhere."""

from fastapi import APIRouter

from pizza.entrypoints.api.deps import RegisterDriverDep
from pizza.entrypoints.api.schemas import Created, RegisterDriverRequest

router = APIRouter()


@router.post("/drivers", status_code=201)
def register_driver(
    body: RegisterDriverRequest, register: RegisterDriverDep
) -> Created:
    """Register a driver, available from the start, and answer with their identifier."""
    return Created(id=register(body.name))
