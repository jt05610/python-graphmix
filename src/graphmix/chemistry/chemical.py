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


class Chemical(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    formula: str
    molar_mass: Q_ = Field(sa_type=Quantity)
