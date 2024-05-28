from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from typing import Any

import pint
from pydantic import GetCoreSchemaHandler
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core import core_schema

ureg = pint.UnitRegistry()
ureg.setup_matplotlib()
ureg.default_format = "P~"


def dimensionality_validator(
    dimensionality: str | None = None, default_unit: str | None = None
):

    if dimensionality is None:

        def validator_func(value: ureg.Quantity) -> ureg.Quantity:
            return value

    else:

        def validator_func(value: ureg.Quantity) -> ureg.Quantity:
            if value.dimensionality != dimensionality:
                raise ValueError(
                    f"Expected a quantity with dimensionality {dimensionality}, but got {value.dimensionality}."
                )
            return value

    if default_unit is None:

        def convert_func(value: int | float | str | Decimal) -> ureg.Quantity:
            return ureg.Quantity(value)

    else:

        def convert_func(value: int | float | str | Decimal) -> ureg.Quantity:
            return ureg.Quantity(value, default_unit)

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
    Substance = "[substance]"
    MolarMass = "[mass] / [substance]"
    MolarConcentration = "[substance] / [length] ** 3"
    MassConcentration = "[mass] / [length] ** 3"
    Volume = "[length] ** 3"
    Percent = "dimensionless"


class DimQuantity:

    def __class_getitem__(
        cls, item: str | Dimensionality, default_unit: str | None = None
    ):
        return Annotated[
            ureg.Quantity, dimensionality_validator(item, default_unit)
        ]


Mass = DimQuantity[Dimensionality.Mass]
Substance = DimQuantity[Dimensionality.Substance]
MolarMass = DimQuantity[Dimensionality.MolarMass]
MolarConcentration = DimQuantity[Dimensionality.MolarConcentration]
MassConcentration = DimQuantity[Dimensionality.MassConcentration]
Volume = DimQuantity[Dimensionality.Volume]
Percent = DimQuantity[Dimensionality.Percent]
