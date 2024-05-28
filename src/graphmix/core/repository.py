from abc import abstractmethod
from collections.abc import Iterator
from typing import Any
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class AbstractRepository(Generic[T]):

    @abstractmethod
    def add(self, item: T) -> None:
        """
        Adds an item to the repository
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> T:
        """
        Gets an item from the repository by id
        """
        raise NotImplementedError

    @abstractmethod
    def get_by(self, field: str, value: Any) -> T:
        """
        Gets an item from the repository by a field
        """
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[T]:
        """
        Lists all items in the repository
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> None:
        """
        Deletes an item from the repository by id
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """
        Returns an iterator for the repository
        """
        raise NotImplementedError

    @abstractmethod
    def __next__(self) -> T:
        """
        Returns the next item in the repository
        """
        raise NotImplementedError
