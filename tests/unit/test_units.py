from pydantic import BaseModel

from graphmix.chemistry.units import Q_


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
