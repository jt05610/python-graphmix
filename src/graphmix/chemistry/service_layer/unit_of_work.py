from pathlib import Path

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from graphmix import config
from graphmix.chemistry.chemical import Chemical
from graphmix.core.sqlmodel.unit_of_work import SessionFactory
from graphmix.core.sqlmodel.unit_of_work import SqlModelUnitOfWork
from graphmix.core.util import get_app_dir


def db_path(db_name: str) -> Path:
    db_dir = get_app_dir(config.APP_NAME)
    return Path(db_dir) / db_name


def session_factory(db_name: str = config.DB_NAME) -> SessionFactory:
    path = db_path(db_name)
    sqlite_path = f"sqlite:///{path}"
    needs_metadata = False
    if not Path.exists(path):
        needs_metadata = True
        path.mkdir(parents=True)

    engine = create_engine(sqlite_path, echo=False)
    # if the file does not exist, create the metadata
    if needs_metadata:
        SQLModel.metadata.create_all(engine)

    def _factory():
        return Session(engine)

    return _factory


class ChemicalUnitOfWork(SqlModelUnitOfWork):
    model = Chemical
