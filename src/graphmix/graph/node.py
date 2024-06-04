from pydantic import BaseModel

from graphmix import Solution
from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Volume
from graphmix.location import Location


class Node(BaseModel):
    solution: Solution
    location: Location
    final_volume: Volume

    def __hash__(self):
        return hash(self.name)

    def __getitem__(self, item: str | Chemical):
        return self.solution.composition.of(item)

    @property
    def name(self) -> str:
        return self.solution.name
