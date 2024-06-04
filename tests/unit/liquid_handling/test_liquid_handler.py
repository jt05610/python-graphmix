import logging
import unittest

from graphmix import Q_
from graphmix import Solution
from graphmix.chemistry.chemical import Chemical
from graphmix.graph.node import Node
from graphmix.liquid_handling.liquid_handler import MockLiquidHandler
from graphmix.liquid_handling.liquid_handler import SingleTransferRequest
from graphmix.location import LocationSet

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()


class TestLiquidHandler(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        tips = LocationSet(name="tip_rack", n_rows=12, n_columns=8)
        self.handler = MockLiquidHandler(
            tips=tips,
            max_transfer_volume=Q_(200, "uL"),
            min_transfer_volume=Q_(20, "uL"),
            logger=logger,
        )

    async def test_single_transfer(self):
        _water = Solution(name="water").with_component(
            Chemical(
                name="h2o",
                formula="H2O",
                molar_mass=Q_(18.01528, "g/mol"),
            ),
            Q_(100, "%"),
        )
        _saline = Solution(name="saline").with_component(
            Chemical(
                name="nacl",
                formula="NaCl",
                molar_mass=Q_(58.44, "g/mol"),
            ),
            Q_(1, "mg/mL"),
        )
        diluted_saline = _saline.dilute_with(_water, 0.5)
        plate = LocationSet(name="plate", n_rows=8, n_columns=12)
        saline_node = Node(
            solution=_saline,
            location=next(plate),
            final_volume=Q_(100, "uL"),
        )
        water_node = Node(
            solution=_water,
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

        await self.handler.transfer(transfers[0])
        first_called = [
            "_setup_transfer",
            "_pick_up_tip",
            "_aspirate",
            "_dispense",
            "_finish_transfer",
        ]
        assert self.handler.called == first_called
        await self.handler.transfer(transfers[1])

        second_called = [
            *first_called,
            "_setup_transfer",
            "_drop_tip",
            "_pick_up_tip",
            "_aspirate",
            "_dispense",
            "_finish_transfer",
        ]

        assert self.handler.called == second_called

        assert len(self.handler.transfers) == 2
