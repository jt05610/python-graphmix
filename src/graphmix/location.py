from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from graphmix.chemistry.units import Volume


class Location(BaseModel):
    """
    A location within an experiment. Corresponds to a well plate coordinate or
    tube location in a tube rack.
    """

    grid: str | None = None
    row: str
    column: int
    max_volume: Volume | None = None
    dead_volume: Volume | None = None
    _next_location: Callable[[], "Location"] = None

    @classmethod
    def from_str(cls, location: str) -> "Location":
        if ":" in location:
            parent_name, location = location.split(":")
            return cls(
                row=location[0],
                column=int(location[1:]),
                grid=parent_name,
            )
        return cls(row=location[0], column=int(location[1:]))

    def with_grid(self, grid: str) -> "Location":
        return self.model_copy(update={"grid": grid})

    def next_location(self) -> "Location":
        if self._next_location is None:
            raise ValueError("No next location has been set.")
        return self._next_location()

    @property
    def xy(self) -> tuple[int, int]:
        return ord(self.row) - 65, self.column - 1

    def with_next_location(
        self, next_location: Callable[[], "Location"]
    ) -> "Location":
        return self.model_copy(update={"_next_location": next_location})

    def __str__(self):
        return f"{self.row}{self.column}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __ge__(self, other):
        return str(self) >= str(other)


class LocationSet(BaseModel):
    name: str | None = None
    n_rows: int
    n_columns: int
    max_volume: Volume | None = None
    dead_volume: Volume | None = None
    skip_locations: set[Location] = set()
    _iterator: Generator[Location, None, None] | None = None

    def model_post_init(self, __context: Any) -> None:
        self._iterator = self.location_generator()

    def __len__(self):
        return self.n_rows * self.n_columns - len(self.skip_locations)

    def location_generator(self) -> Generator[Location, None, None]:
        for row in range(self.n_rows):
            for column in range(self.n_columns):
                location = Location(
                    row=chr(row + 65),
                    column=column + 1,
                    grid=self.name,
                ).with_next_location(lambda: next(self))
                if location in self.skip_locations:
                    continue
                yield location
                self.skip_locations.add(location)

    def __iter__(self) -> Iterable[Location]:
        return self

    def __next__(self) -> Location:
        return next(self._iterator)

    def __contains__(self, item):
        return item not in self.skip_locations

    def __getitem__(self, item: int | str | tuple) -> Location:
        match item:
            case int():
                row = item // self.n_columns
                column = item % self.n_columns
                if row >= self.n_rows or column >= self.n_columns:
                    raise IndexError("Index out of range.")
                return Location(
                    row=chr(row + 65), column=column + 1, grid=self.name
                )
            case str():
                loc = Location.from_str(item)
                x, y = loc.xy
                if x >= self.n_rows or y >= self.n_columns:
                    raise IndexError("Index out of range.")
                return loc
            case tuple():
                row, column = item
                if row >= self.n_rows or column >= self.n_columns:
                    raise IndexError("Index out of range.")
                return Location(row=chr(row + 65), column=column + 1)

    def reset(self):
        self.skip_locations.clear()
        self._iterator = None

    def with_occupied_location(
        self, location: Location | str
    ) -> "LocationSet":
        if isinstance(location, str):
            location = Location.from_str(location)
        self.skip_locations.add(location)
        return self

    def with_occupied_locations(
        self, locations: Iterable[Location | str]
    ) -> "LocationSet":
        for location in locations:
            self.with_occupied_location(location)
        return self

    def with_max_volume(self, volume: Volume) -> "LocationSet":
        return self.model_copy(update={"max_volume": volume})

    def with_dead_volume(self, volume: Volume) -> "LocationSet":
        return self.model_copy(update={"dead_volume": volume})

    def with_name(self, name: str) -> "LocationSet":
        return self.model_copy(update={"name": name})


class WellPlate(LocationSet):
    def __class_getitem__(cls, item) -> LocationSet:
        match item:
            case 6:
                return LocationSet(n_rows=2, n_columns=3)
            case 12:
                return LocationSet(n_rows=8, n_columns=12)
            case 24:
                return LocationSet(n_rows=4, n_columns=6)
            case 48:
                return LocationSet(n_rows=8, n_columns=6)
            case 96:
                return LocationSet(n_rows=8, n_columns=12)
            case 384:
                return LocationSet(n_rows=16, n_columns=24)
