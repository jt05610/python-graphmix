import logging

import pytest

from graphmix import Q_
from graphmix.graph.node import Node
from graphmix.liquid_handling.liquid_handler import MockLiquidHandler
from graphmix.liquid_handling.liquid_handler import SingleTransferRequest
from graphmix.location import LocationSet

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()


@pytest.mark.asyncio
async def test_single_transfer(saline, water):
    tips = LocationSet(name="tip_rack", n_rows=12, n_columns=8)
    handler = MockLiquidHandler(
        tips=tips,
        max_transfer_volume=Q_(200, "uL"),
        min_transfer_volume=Q_(20, "uL"),
        logger=logger,
    )

    diluted_saline = saline.dilute_with(water, 0.5)
    plate = LocationSet(name="plate", n_rows=8, n_columns=12)
    saline_node = Node(
        solution=saline,
        location=next(plate),
        final_volume=Q_(100, "uL"),
    )
    water_node = Node(
        solution=water,
        location=next(plate),
        final_volume=Q_(100, "uL"),
    )
    destination_node = Node(
        solution=diluted_saline,
        location=next(plate),
        final_volume=Q_(100, "uL"),
    )

    transfers = (
        SingleTransferRequest(
            source=saline_node,
            volume=Q_(50, "uL"),
            destination=destination_node,
        ),
        SingleTransferRequest(
            source=water_node,
            volume=Q_(50, "uL"),
            destination=destination_node,
        ),
    )

    await handler.transfer(transfers[0])
    first_called = [
        "_setup_transfer",
        "_pick_up_tip",
        "_aspirate",
        "_dispense",
        "_finish_transfer",
    ]
    assert handler.called == first_called
    await handler.transfer(transfers[1])

    second_called = [
        *first_called,
        "_setup_transfer",
        "_drop_tip",
        "_pick_up_tip",
        "_aspirate",
        "_dispense",
        "_finish_transfer",
    ]

    assert handler.called == second_called

    assert len(handler.transfers) == 2
