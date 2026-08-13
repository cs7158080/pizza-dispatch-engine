"""What the healthcheck asks, and the one dependency it reports on.

The database only: a status update succeeds while the broker is unreachable, so
a service that could not reach the broker would be failing a check it passes.
"""

from fastapi import APIRouter, HTTPException

from pizza.entrypoints.api.deps import WiringDep
from pizza.entrypoints.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health")
def health(wiring: WiringDep) -> HealthResponse:
    """Report whether the service can reach its database."""
    if not wiring.database_reachable():
        raise HTTPException(status_code=503, detail="Database unreachable")
    return HealthResponse()
