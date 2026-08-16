"""One-shot service that creates the database schema, then exits.

It runs alone, before the api and the worker start, so that no two processes create
the same table at once. Nothing downstream starts unless this exits zero.
"""

import os
import sys

from sqlalchemy import create_engine

from pizza.config import ConfigurationError, load_service_settings
from pizza.infrastructure.db.schema import create_schema


def main() -> None:
    """Create the schema and exit, or exit non-zero on an invalid environment."""
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
