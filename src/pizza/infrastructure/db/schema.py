"""Schema creation from the declarative models.

`create_all` skips tables that already exist, so a repeated run is a no-op. For the
same reason it does not repair a partially created schema; this is acceptable only
because the environment is recreated from empty on every launch.
"""

from sqlalchemy import Engine

from pizza.infrastructure.db.models import Base


def create_schema(engine: Engine) -> None:
    """Create every table that does not already exist."""
    Base.metadata.create_all(engine)
