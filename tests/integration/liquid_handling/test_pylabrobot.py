import unittest

from pylabrobot.liquid_handling import ChatterBoxBackend
from pylabrobot.liquid_handling import LiquidHandler

from graphmix import Q_
from graphmix import Solution
from graphmix.chemistry.chemical import Chemical
from graphmix.graph.node import Node
from graphmix.liquid_handling.liquid_handler import SingleTransferRequest
from graphmix.liquid_handling.robot import Robot
from graphmix.liquid_handling.robot import create_deck
from graphmix.location import LocationSet


class PyLabRobotTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.grids = {
            "tip_rack": LocationSet(name="tip_rack", n_rows=12, n_columns=8),
            "plate": LocationSet(name="plate", n_rows=8, n_columns=12),
        }
        deck = create_deck(self.grids, "tip_rack")
        self.lh = LiquidHandler(
            backend=ChatterBoxBackend(num_channels=1), deck=deck
        )
        self.handler = Robot(handler=self.lh, tips=self.grids["tip_rack"])

    async def test_pylabrobot_single_transfer(self):
        await self.handler.setup()
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
        saline_node = Node(
            solution=_saline,
            location=next(self.grids["plate"]),
            final_volume=Q_(100, "uL"),
        )
        destination_node = Node(
            solution=diluted_saline,
            location=next(self.grids["plate"]),
            final_volume=Q_(100, "uL"),
        )

        transfers = (
            SingleTransferRequest(
                source=saline_node,
                volume=Q_(50, "uL"),
                destination=destination_node,
            ),
        )

        await self.handler.transfer(transfers[0])
