import logging

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources import HTF_L
from pylabrobot.resources import PLT_CAR_L5AC_A00
from pylabrobot.resources import TIP_CAR_480_A00
from pylabrobot.resources import Coordinate
from pylabrobot.resources import Cos_96_DW_500ul
from pylabrobot.resources import Deck
from pylabrobot.resources import Resource

from graphmix.chemistry.units import FlowRate
from graphmix.chemistry.units import Volume
from graphmix.liquid_handling.liquid_handler import DEFAULT_LOGGER
from graphmix.liquid_handling.liquid_handler import AbstractLiquidHandler
from graphmix.liquid_handling.liquid_handler import TransferRequest
from graphmix.location import Location
from graphmix.location import LocationSet


def create_deck(
    grids: dict[str, LocationSet], tips: str | LocationSet
) -> Deck:
    deck = Deck(
        name="deck",
    )
    tip_car = TIP_CAR_480_A00(name="tip carrier")
    tip_car[0] = HTF_L(name="tip_rack")
    deck.assign_child_resource(tip_car, location=Coordinate(0, 0, 0))
    plt_car = PLT_CAR_L5AC_A00(name="plate carrier")
    tip_name = tips if isinstance(tips, str) else tips.name
    for i, g in enumerate(grids.keys()):
        if g == tip_name:
            continue
        plt_car[i] = Cos_96_DW_500ul(name=g)
    deck.assign_child_resource(plt_car, location=Coordinate(5, 10, 15))
    return deck


class Robot(AbstractLiquidHandler):
    handler: LiquidHandler

    def __init__(
        self,
        handler: LiquidHandler,
        tips: LocationSet,
        aspiration_rate: FlowRate = None,
        dispense_rate: FlowRate = None,
        logger: logging.Logger = DEFAULT_LOGGER,
        max_transfer_volume: Volume | None = None,
        min_transfer_volume: Volume | None = None,
    ):
        if max_transfer_volume is None:
            max_transfer_volume = Volume(200, "uL")
        if min_transfer_volume is None:
            min_transfer_volume = Volume(20, "uL")
        self.tips = tips
        self.handler = handler
        self.aspiration_rate = aspiration_rate
        self.dispense_rate = dispense_rate
        self.logger = logger
        self.max_transfer_volume = max_transfer_volume
        self.min_transfer_volume = min_transfer_volume

    async def _setup(self):
        await self.handler.setup()

    @property
    def tip_location(self) -> Resource:
        return self.handler.deck.get_resource("tip_rack")

    async def _pick_up_tip(self, location: Location):
        tip_location = self.tip_location[str(location)]
        await self.handler.pick_up_tips(tip_location)

    async def _drop_tip(self):
        await self.handler.discard_tips()

    async def _aspirate(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        grid = self.handler.deck.get_resource(location.grid)
        loc = grid[str(location)]
        vol = volume.to("uL").magnitude
        if air_cushion is not None:
            air_cushion = air_cushion.to("uL").magnitude
        await self.handler.aspirate(
            loc, vols=vol, blow_out_air_volume=air_cushion
        )

    async def _dispense(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate = None,
    ):
        grid = self.handler.deck.get_resource(location.grid)
        loc = grid[str(location)]
        vol = volume.to("uL").magnitude
        if air_cushion is not None:
            air_cushion = air_cushion.to("uL").magnitude
        await self.handler.dispense(
            loc, vols=vol, blow_out_air_volume=air_cushion
        )

    async def _finish_transfer(self, request: TransferRequest):
        pass

    async def _setup_transfer(self):
        pass
