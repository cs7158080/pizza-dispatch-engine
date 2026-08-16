"""Database reachability check.

The check runs a statement rather than inspecting the pool, so its meaning does not
depend on the pool configuration. The SQLAlchemy failure is translated here: nothing
SQLAlchemy-shaped leaves this module.
"""

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


def database_reachable(engine: Engine) -> bool:
    """Return whether a statement can be executed against the database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
