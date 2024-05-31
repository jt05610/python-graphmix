import itertools
from collections.abc import Iterable

import pytest
from pydantic import BaseModel
from pydantic import ValidationError

from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import Volume


def test_quantity_works_with_pydantic():
    class FakeModel(BaseModel):
        volume: Q_

    def assert_model(instance: FakeModel, value: Q_):
        assert instance.volume == value
        assert instance.model_dump() == {"volume": f"{value:#~}"}

    checks_to_run = (
        (FakeModel(volume=Q_("100 uL")), Q_("100 uL")),
        (FakeModel(volume=Q_(100, "uL")), Q_("100 uL")),
        (FakeModel(volume=100), Q_("100")),
        (FakeModel(volume="100 uL"), Q_("100 uL")),
    )

    for m, v in checks_to_run:
        assert_model(m, v)


def iter_tuple_with_arguments(t: Iterable[tuple], length: int) -> tuple:
    """Iterates through an iterable of tuples. If there are less than `length`
    elements in the tuple, it will fill the rest with `None` values.
    """

    for args in t:
        yield tuple(
            itertools.chain(args, itertools.repeat(None, length - len(args)))
        )


def test_quantity_with_enforced_dimensionality():
    class FakeModel(BaseModel):
        volume: Volume

    def assert_model(
        passed_value: Q_ | str | float,
        value: Q_,
        expected_error: Exception | None = None,
    ):
        def assertions(inst: FakeModel):
            assert inst.volume == value
            assert inst.model_dump() == {"volume": f"{value:#~}"}

        if expected_error is not None:
            with pytest.raises(expected_error):
                assertions(FakeModel(volume=passed_value))
            return
        instance = FakeModel(volume=passed_value)
        assertions(instance)

    checks_to_run = (
        (Q_("100 uL"), Q_("100 uL")),
        (Q_(100, "uL"), Q_("100 uL")),
        (100, Q_("100 mL")),
        ("100 uL", Q_("100 uL")),
        ("100 s", Q_("100 uL"), ValidationError),
        (Q_(100, "s"), Q_("100 uL"), ValidationError),
    )

    for m, v, e in iter_tuple_with_arguments(checks_to_run, 3):
        assert_model(m, v, e)
