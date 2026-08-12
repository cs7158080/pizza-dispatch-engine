"""Creating the schema from the models that describe it.

`create_all` skips a table it finds, so running it twice is a no-op; by the same
mechanism it does not repair a partially created schema, which is safe only because
the environment is recreated from empty on every launch.
"""

from sqlalchemy import Engine

from pizza.infrastructure.db.models import Base


def create_schema(engine: Engine) -> None:
    Base.metadata.create_all(engine)
