import pytest
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.service_layer.registry import ChemicalRegistry
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork
from graphmix.chemistry.units import Q_
from graphmix.graph.protocol import Protocol
from graphmix.graph.solution import Solution
from graphmix.location import WellPlate


@pytest.fixture
def sqlite_session_factory():
    engine = create_engine("sqlite://", echo=False)

    def _mock_session_factory():
        SQLModel.metadata.create_all(engine)
        return Session(engine)

    return _mock_session_factory


@pytest.fixture
def registry(sqlite_session_factory):
    uow = ChemicalUnitOfWork(sqlite_session_factory)
    return ChemicalRegistry(uow)


@pytest.fixture
def nacl() -> Chemical:
    return Chemical(name="NaCl", formula="NaCl", molar_mass="58.44 g/mol")


@pytest.fixture
def h2o() -> Chemical:
    return Chemical(name="H2O", formula="H2O", molar_mass="18.015 g/mol")


@pytest.fixture
def saline(nacl, h2o) -> Solution:
    return (
        Solution(name="saline")
        .with_component(nacl, Q_(1, "mg/mL"))
        .with_component(h2o, Q_(100, "%"))
    )


@pytest.fixture
def water(h2o) -> Solution:
    return Solution(name="water").with_component(h2o, Q_(100, "%"))


@pytest.fixture
def diluted_solution_name():
    return "saline_diluted_with_water"


@pytest.fixture
def dilution_protocol(saline, water, diluted_solution_name) -> Protocol:
    return (
        Protocol(grids={"0": WellPlate[96]})
        .with_node(
            entity=saline,
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_node(
            entity=water,
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_dilution(
            name=diluted_solution_name,
            species=saline.components["NaCl"],
            source=saline,
            diluent=water,
            final_volume=Q_(100, "uL"),
            final_concentration=Q_(0.5, "mg/mL"),
            into="0",
        )
    )
