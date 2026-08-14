"""Whether the database can be reached, answered by running a statement.

A statement rather than a pool setting: the check must mean the same thing
whatever the pool is configured to do. Translating the failure here is the same
duty the repositories have — nothing SQLAlchemy-shaped leaves this module.
"""

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


def database_reachable(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
