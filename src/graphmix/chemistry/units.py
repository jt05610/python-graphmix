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

        def validate(value: str) -> ureg.Quantity:
            return ureg.Quantity(value)

        from_number_schema = core_schema.chain_schema(
            [
                core_schema.union_schema(
                    [
                        core_schema.int_schema(),
                        core_schema.float_schema(),
                        core_schema.str_schema(),
                    ]
                ),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_number_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ureg.Quantity),
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


Quantity = Annotated[ureg.Quantity, _QuantityPydanticAnnotation]

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
