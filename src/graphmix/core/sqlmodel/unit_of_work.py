from sqlalchemy import Engine
from sqlmodel import Session

from graphmix.core.sqlmodel.repository import SqlModelRepository
from graphmix.core.unit_of_work import AbstractUnitOfWork


class SqlModelUnitOfWork(AbstractUnitOfWork):
    engine: Engine
    session: Session

    def __init__(self, engine: Engine):
        self.engine = engine

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = Session(self.engine)
        self.repo = SqlModelRepository(self.session)
        return self.session

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
