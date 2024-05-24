from typing import Any
from typing import Optional

from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlmodel import Field
from sqlmodel import SQLModel

from graphmix.chemistry.units import Q_


class Quantity(TypeDecorator):
    impl = String

    @staticmethod
    def get_col_spec(**kw):
        return "VARCHAR(255)"

    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                return str(value)
            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                return Q_(value)
            return value

        return process


class Entity(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Chemical(Entity, table=True):
    formula: str
    smiles: Optional[str] = None
    molar_mass: Q_ | str = Field(sa_type=Quantity)

    def count(self, element: str) -> int:
        if self.smiles is None:
            return 0
        return self.smiles.count(element)

    def model_post_init(self, __context: Any) -> None:
        if isinstance(self.molar_mass, str):
            self.molar_mass = Q_(self.molar_mass)
            if self.molar_mass.units == "":
                self.molar_mass = Q_(self.molar_mass.magnitude, "g/mol")
            return
        if isinstance(self.molar_mass, float):
            self.molar_mass = Q_(self.molar_mass, "g/mol")


class NucleicAcid(Entity, table=True):
    molar_mass: Q_ = Field(sa_type=Quantity)
    number_of_phosphates: Optional[int] = None
