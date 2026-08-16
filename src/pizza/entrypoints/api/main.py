"""Composition root of the api service: the only module that builds the adapters.

Settings are loaded at import time, so an invalid environment exits non-zero with
one message instead of starting a service that fails every request.

Startup opens no connection: `create_engine` and the publisher both perform their
I/O on first use, so the service starts whether or not the database and the broker
are up.
"""

import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pizza.config import ConfigurationError, load_service_settings
from pizza.entrypoints.api import errors
from pizza.entrypoints.api.deps import Wiring
from pizza.entrypoints.api.routers import drivers, health, orders
from pizza.infrastructure.broker.publisher import PikaEventPublisher
from pizza.infrastructure.clock import SystemClock
from pizza.infrastructure.db.probe import database_reachable
from pizza.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from pizza.log import configure_logging

try:
    settings = load_service_settings(os.environ)
except ConfigurationError as error:
    print(error, file=sys.stderr)
    raise SystemExit(1) from error

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Build the resources that outlive a request, and close them on shutdown."""
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    publisher = PikaEventPublisher(
        settings.broker_url,
        settings.broker_publish_timeout_seconds,
        settings.dispatch_retry_delay_seconds,
    )

    app.state.wiring = Wiring(
        new_unit_of_work=partial(SqlAlchemyUnitOfWork, session_factory),
        clock=SystemClock(),
        publisher=publisher,
        database_reachable=partial(database_reachable, engine),
    )

    yield

    publisher.close()
    engine.dispose()


app = FastAPI(title="Pizza Dispatch", lifespan=lifespan)
errors.install(app)
app.include_router(orders.router)
app.include_router(drivers.router)
app.include_router(health.router)
