from collections.abc import Callable
from pathlib import Path
from typing import Generic

from sqlmodel import Session

from graphmix.core.repository import T
from graphmix.core.sqlmodel.repository import SqlModelRepository
from graphmix.core.unit_of_work import AbstractUnitOfWork


class SessionFactory:
    f: Callable[[], Session]
    path: Path | None = None

    def __init__(
        self, f: Callable[[], Session], path: str | Path | None = None
    ):
        if path is not None and not isinstance(path, Path):
            path = Path(path)
        self.f = f
        self.path = path

    def __call__(self) -> Session:
        return self.f()


class SqlModelUnitOfWork(Generic[T], AbstractUnitOfWork):
    session_factory: SessionFactory
    session: Session
    model: type[T]

    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.repo = SqlModelRepository(self.model, self.session)
        return self.session

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @property
    def path(self) -> Path:
        return self.session_factory.path
