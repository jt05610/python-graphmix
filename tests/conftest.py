from typing import Type

import pytest
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine


@pytest.fixture
def sqlite_session_factory():
    engine = create_engine("sqlite://", echo=True)

    def _mock_session_factory(model: Type[SQLModel]):
        SQLModel.metadata.create_all(engine)
        return Session(engine)

    return _mock_session_factory
