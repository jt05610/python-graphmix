import pytest

from graphmix.location import Location
from graphmix.location import LocationSet
from graphmix.location import WellPlate


def test_location_set_iteration():
    well_plate = LocationSet(n_rows=8, n_columns=12)

    assert len(well_plate) == 96

    for i, location in enumerate(well_plate):
        assert location.row == chr(i // 12 + 65)
        assert location.column == (i % 12) + 1
        assert location in well_plate


def test_location_set_with_occupied_location():
    well_plate = (
        WellPlate[96]
        .with_occupied_location(Location(row="A", column=1))
        .with_occupied_location("A2")
        .with_occupied_locations(("A3", Location(row="A", column=4)))
    )

    assert len(well_plate) == 92
    well_plate_iter = iter(well_plate)

    assert next(well_plate_iter) == Location(row="A", column=5)

    for i in range(1, 5):
        assert Location(row="A", column=i) not in well_plate


def test_location_knows_next_position():
    well_plate = LocationSet(n_rows=8, n_columns=12)
    first_pos = next(well_plate)
    assert first_pos == Location(row="A", column=1)
    assert first_pos.next_location() == Location(row="A", column=2)
    for _ in range(5):
        next(well_plate)
    assert first_pos.next_location() == "A8"


def test_location_set_indexing():
    well_plate = LocationSet(n_rows=8, n_columns=12)

    checks = (
        (0, Location(row="A", column=1)),
        (1, Location(row="A", column=2)),
        ((0, 0), Location(row="A", column=1)),
        ((1, 1), Location(row="B", column=2)),
        ("A1", Location(row="A", column=1)),
        ("B2", Location(row="B", column=2)),
    )
    for check, expected in checks:
        assert well_plate[check] == expected

    # Test out of range
    checks = (
        (8, 12),
        "I11",
        99,
    )
    for check in checks:
        with pytest.raises(IndexError):
            _ = well_plate[check]
