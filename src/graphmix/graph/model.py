from typing import Annotated
from typing import Any

import networkx as nx
from pydantic import GetCoreSchemaHandler
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core import core_schema

from graphmix.chemistry.units import Q_


def serialize(G: nx.DiGraph) -> dict:
    data = nx.node_link_data(G)
    for edge in data["links"]:
        edge["concentration"] = str(edge["concentration"])
    return data


class _DiGraphPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Returns a CoreSchema with the following behavior:
        """

        def validate(value: dict) -> nx.DiGraph:
            for edge in value["links"]:
                edge["concentration"] = Q_(edge["concentration"])
            return nx.node_link_graph(value, directed=True)

        from_dict_schema = core_schema.chain_schema(
            [
                core_schema.dict_schema(),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_dict_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(nx.DiGraph),
                    from_dict_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: serialize(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.dict_schema())


DiGraph = Annotated[nx.DiGraph, _DiGraphPydanticAnnotation]
