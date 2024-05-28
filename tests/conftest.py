import pytest
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from graphmix.chemistry.service_layer.registry import ChemicalRegistry
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork


@pytest.fixture
def sqlite_session_factory():
    engine = create_engine("sqlite://", echo=True)

    def _mock_session_factory():
        SQLModel.metadata.create_all(engine)
        return Session(engine)

    return _mock_session_factory


@pytest.fixture
def registry(sqlite_session_factory):
    uow = ChemicalUnitOfWork(sqlite_session_factory)
    return ChemicalRegistry(uow)
