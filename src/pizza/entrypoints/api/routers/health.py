"""Health route.

It reports on the database only: status updates still succeed while the broker is
unreachable, so a broker fault must not fail the check.
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
