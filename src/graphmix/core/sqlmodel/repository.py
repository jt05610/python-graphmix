from collections.abc import Iterator
from typing import Any
from typing import Generic

from sqlmodel import Session
from sqlmodel import select

from graphmix.core.repository import AbstractRepository
from graphmix.core.repository import T


class SqlModelRepository(Generic[T], AbstractRepository[T]):
    model: type[T]
    session: Session

    def __init__(self, model: type[T], session: Session):
        self.session = session
        self.model = model

    def add(self, item: T) -> None:
        self.session.add(item)

    def get(self, id: int) -> T:
        statement = select(self.model).where(self.model.id == id)

        return self.session.exec(statement).first()

    def get_by(self, field: str, value: Any) -> T:
        statement = select(self.model).where(
            getattr(self.model, field) == value
        )
        return self.session.exec(statement).first()

    def list(self) -> list[T]:
        statement = select(self.model)
        return self.session.exec(statement).all()

    def delete(self, id: int) -> None:
        self.session.delete(self.get(id))

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self.session)
