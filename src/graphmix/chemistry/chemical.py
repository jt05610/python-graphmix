import decimal
from typing import Any

from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlmodel import Field
from sqlmodel import SQLModel

from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import MolarMass


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


class Chemical(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, repr=False)
    name: str
    formula: str
    smiles: str | None = None
    molar_mass: MolarMass | str = Field(sa_type=Quantity)

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
        if isinstance(self.molar_mass, float | int | decimal.Decimal):
            self.molar_mass = Q_(self.molar_mass, "g/mol")

    def __hash__(self):
        return hash(self.name)
