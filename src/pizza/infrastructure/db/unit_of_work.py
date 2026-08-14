"""One transaction, and the repositories bound to it.

Each entry opens its own `Session` and each exit closes it, so the same instance can
be used again after a commit — which is what the publish-then-mark sequence needs:
the mark is a second transaction, taken after the first one has ended.

Leaving the block without `commit()` rolls back.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from pizza.application.ports import TransactionFailed, UnitOfWork
from pizza.infrastructure.db.outbox import SqlAlchemyOutboxStore
from pizza.infrastructure.db.repositories import (
    SqlAlchemyDriverRepository,
    SqlAlchemyOrderRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        session = self._session_factory()
        self._session = session
        self.orders = SqlAlchemyOrderRepository(session)
        self.drivers = SqlAlchemyDriverRepository(session)
        self.outbox = SqlAlchemyOutboxStore(session)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._session is None:
            return
        # A no-op once commit() has been called, and the whole of the guarantee
        # otherwise.
        self._session.rollback()
        self._session.close()
        self._session = None

    def commit(self) -> None:
        """Raises TransactionFailed."""
        if self._session is None:
            raise RuntimeError("commit() outside the unit of work")
        try:
            self._session.commit()
        except SQLAlchemyError as error:
            raise TransactionFailed("could not commit the transaction") from error
