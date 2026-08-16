"""SQLAlchemy unit of work: one transaction and the repositories bound to it.

Each entry opens its own `Session` and each exit closes it, so one instance can be
re-entered after a commit to run a second transaction.

Leaving the block without calling `commit()` rolls back.
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
        # A no-op once commit() has been called; the rollback guarantee otherwise.
        self._session.rollback()
        self._session.close()
        self._session = None

    def commit(self) -> None:
        """Commit the transaction.

        Raises:
            TransactionFailed: The transaction could not be committed.
        """
        if self._session is None:
            raise RuntimeError("commit() outside the unit of work")
        try:
            self._session.commit()
        except SQLAlchemyError as error:
            raise TransactionFailed("could not commit the transaction") from error
