from decimal import Decimal
from typing import Annotated
from typing import Any

import pint
from pydantic import GetCoreSchemaHandler
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core import core_schema

from graphmix.core.util import StrEnum

ureg = pint.UnitRegistry()
ureg.default_format = "P~"


def dimensionality_validator(
    dimensionality: str | None = None, default_unit: str | None = None
):

    if dimensionality is None:

        def validator_func(value: ureg.Quantity) -> ureg.Quantity:
            return value

    else:

        def validator_func(value: ureg.Quantity) -> ureg.Quantity:
            if (
                value.units.dimensionality != dimensionality
                and value.units != "percent"
            ):
                raise ValueError(
                    f"Expected a quantity with dimensionality {dimensionality}, but got {value.dimensionality}."
                )
            return value

    if default_unit is None:

        def convert_func(value: int | float | str | Decimal) -> ureg.Quantity:
            return ureg.Quantity(value)

    else:

        def convert_func(value: int | float | str | Decimal) -> ureg.Quantity:
            q = ureg.Quantity(value)
            if q.units == "":
                q = Quantity(q.magnitude, default_unit)
            return q

    class _QuantityPydanticAnnotation:

        @classmethod
        def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: GetCoreSchemaHandler
        ) -> CoreSchema:
            """
            Returns a CoreSchema with the following behavior:
            * ints or floats will be converted to ureg.Quantity with no unit.
            * strings will be converted to ureg.Quantity with a unit if specified in the string.
            * ureg.Quantity instances will be parsed as is.
            * Nothing else will pass validation.
            * Serialization will always return a string.
            """

            from_number_schema = core_schema.chain_schema(
                [
                    core_schema.union_schema(
                        [
                            core_schema.int_schema(),
                            core_schema.float_schema(),
                            core_schema.str_schema(),
                        ]
                    ),
                    core_schema.no_info_plain_validator_function(convert_func),
                    core_schema.no_info_plain_validator_function(
                        validator_func
                    ),
                ]
            )

            return core_schema.json_or_python_schema(
                json_schema=from_number_schema,
                python_schema=core_schema.union_schema(
                    [
                        core_schema.chain_schema(
                            [
                                core_schema.is_instance_schema(ureg.Quantity),
                                core_schema.no_info_plain_validator_function(
                                    validator_func
                                ),
                            ]
                        ),
                        from_number_schema,
                    ]
                ),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    lambda instance: str(instance)
                ),
            )

        @classmethod
        def __get_pydantic_json_schema(
            cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
        ) -> JsonSchemaValue:
            return handler(
                core_schema.union_schema(
                    core_schema.int_schema(),
                    core_schema.float_schema(),
                    core_schema.str_schema(),
                )
            )

    return _QuantityPydanticAnnotation


Quantity = Annotated[ureg.Quantity, dimensionality_validator()]

Q_ = Quantity

uL = ureg.uL
mL = ureg.mL
L = ureg.L
mg = ureg.mg
ug = ureg.ug
mol = ureg.mol
molar_mass = ureg.g / ureg.mol
molar = ureg.molar
mmol = ureg.mmol
mM = ureg.mM
percent = ureg.percent
g = ureg.g


class Dimensionality(StrEnum):
    Mass = "[mass]"
    Mole = "[substance]"
    MolarMass = "[mass] / [substance]"
    MolarConcentration = "[substance] / [length] ** 3"
    MassConcentration = "[mass] / [length] ** 3"
    Volume = "[length] ** 3"
    Percent = "dimensionless"
    FlowRate = "[length] ** 3 / [time]"


class DimQuantity(Quantity):
    def __class_getitem__(
        cls, item: str | Dimensionality | tuple[Dimensionality, str]
    ):
        if isinstance(item, tuple):
            validator = dimensionality_validator(item[0], item[1])
        else:
            validator = dimensionality_validator(item)

        return Annotated[ureg.Quantity, validator]


Mass = DimQuantity[Dimensionality.Mass, "g"]
"""A Quantity that must have a mass unit."""

Mole = DimQuantity[Dimensionality.Mole, "mol"]
"""A Quantity that must have a mole unit."""

MolarMass = DimQuantity[Dimensionality.MolarMass, "g/mol"]
"""A Quantity that must have a molar mass unit."""

MolarConcentration = DimQuantity[Dimensionality.MolarConcentration, "mol/mL"]
"""A Quantity that must have a molar concentration unit."""

MassConcentration = DimQuantity[Dimensionality.MassConcentration, "mg/mL"]
"""A Quantity that must have a mass concentration unit."""

Volume = DimQuantity[Dimensionality.Volume, "mL"]
"""A Quantity that must have a volume unit."""

Percent = DimQuantity[Dimensionality.Percent, "%"]
"""A Quantity that must be dimensionless."""

Concentration = MolarConcentration | MassConcentration
"""A Quantity that must have a concentration unit, either molar or MassConcentration."""

FlowRate = DimQuantity[Dimensionality.FlowRate, "mL/min"]
"""A Quantity that must have a flow rate unit."""
