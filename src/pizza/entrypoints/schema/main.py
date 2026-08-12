"""The one-shot service that creates the schema, then exits.

It runs alone, before the api and the worker start, so that two processes never
inspect the catalogue and create the same table at once. Nothing downstream starts
unless this exits zero.

It is an entry point because it composes — it builds the engine and reaches into
infrastructure. It drives no use case.
"""

import os
import sys

from sqlalchemy import create_engine

from pizza.config import ConfigurationError, load_service_settings
from pizza.infrastructure.db.schema import create_schema


def main() -> None:
    try:
        settings = load_service_settings(os.environ)
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    engine = create_engine(settings.database_url)
    try:
        create_schema(engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
