import logging
from abc import ABC
from abc import abstractmethod

from pydantic import BaseModel

from graphmix import Solution
from graphmix.chemistry.units import FlowRate
from graphmix.chemistry.units import Volume
from graphmix.graph.node import Node
from graphmix.location import Location
from graphmix.location import LocationSet

DEFAULT_LOGGER = logging.getLogger(__name__)


class MixRequest(BaseModel):
    volume: Volume
    rate: FlowRate
    rounds: int
    location: Location


class TransferRequest(BaseModel):
    source: Node
    reuse_tip: bool = False
    air_cushion: Volume = Volume(0, "uL")
    aspirate_rate: FlowRate = None
    dispense_rate: FlowRate = None
    aspirate_mix: MixRequest = None


class SingleTransferRequest(TransferRequest):
    volume: Volume
    destination: Node
    dispense_mix: MixRequest = None


class MultiTransferRequest(TransferRequest):
    aspirate_volume: Volume
    dispense_volume: Volume
    destinations: tuple[Node, ...]


class AbstractLiquidHandler(ABC):
    tips: LocationSet
    max_transfer_volume: Volume
    min_transfer_volume: Volume
    last_solution: Solution = None
    has_tip: bool = False
    aspiration_rate: FlowRate = None
    dispense_rate: FlowRate = None
    logger: logging.Logger = DEFAULT_LOGGER

    @abstractmethod
    async def _setup(self):
        raise NotImplementedError

    async def setup(self):
        self.logger.info("Setting up liquid handler")
        await self._setup()

    @abstractmethod
    async def _pick_up_tip(self, location: Location):
        raise NotImplementedError

    async def pick_up_tip(self, location: Location):
        self.logger.info(f"Picking up tip at {location}")
        await self._pick_up_tip(location)
        self.has_tip = True

    @abstractmethod
    async def _drop_tip(self):
        raise NotImplementedError

    async def drop_tip(self):
        if not self.has_tip:
            return
        self.logger.info("Dropping tip")
        await self._drop_tip()
        self.last_solution = None
        self.has_tip = False

    @abstractmethod
    async def _aspirate(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        raise NotImplementedError

    async def aspirate(
        self,
        volume: Volume,
        node: Node,
        air_cushion: Volume | None = None,
        rate: FlowRate = None,
    ):
        self.logger.info(f"Aspirating {volume} from {node.location}")
        await self._aspirate(
            volume, node.location, air_cushion=air_cushion, rate=rate
        )
        self.last_solution = node.solution

    @abstractmethod
    async def _dispense(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        raise NotImplementedError

    async def dispense(
        self,
        volume: Volume,
        node: Node,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        self.logger.info(f"Dispensing {volume} to {node.location}")
        await self._dispense(
            volume, node.location, air_cushion=air_cushion, rate=rate
        )
        self.last_solution = node.solution

    def _can_reuse_tip(self, request: TransferRequest) -> bool:
        if not request.reuse_tip:
            return False
        last_solutes = tuple(
            sorted(
                k.name for k in self.last_solution.composition.solutes.keys()
            )
        )
        current_solutes = tuple(
            sorted(
                k.name
                for k in request.source.solution.composition.solutes.keys()
            )
        )
        return last_solutes == current_solutes

    async def mix(self, mix_request: MixRequest):
        self.logger.info(
            f"Mixing {mix_request.volume} at {mix_request.location}"
        )
        for _ in range(mix_request.rounds):
            await self._aspirate(
                mix_request.volume, mix_request.location, rate=mix_request.rate
            )
            await self._dispense(
                mix_request.volume, mix_request.location, rate=mix_request.rate
            )

    async def change_tip(self):
        self.logger.info("Changing tip")
        await self.drop_tip()
        await self.pick_up_tip(next(self.tips))

    @abstractmethod
    async def _finish_transfer(self, request: TransferRequest):
        raise NotImplementedError

    async def finish_transfer(self, request: TransferRequest):
        self.logger.info("Finishing transfer")
        await self._finish_transfer(request)

    @abstractmethod
    async def _setup_transfer(self):
        raise NotImplementedError

    async def setup_transfer(
        self, request: TransferRequest
    ) -> tuple[FlowRate, FlowRate]:
        self.logger.info(f"Setting up transfer from {request.source.location}")
        await self._setup_transfer()

        if not self._can_reuse_tip(request):
            await self.change_tip()

        aspiration_rate = (
            request.aspirate_rate
            if request.aspirate_rate is not None
            else self.aspiration_rate
        )

        dispense_rate = (
            request.dispense_rate
            if request.dispense_rate is not None
            else self.dispense_rate
        )

        return aspiration_rate, dispense_rate

    def _check_single_request(self, request: SingleTransferRequest):
        if request.volume > self.max_transfer_volume:
            raise ValueError(
                f"Transfer volume {request.volume} exceeds max transfer volume "
                f"{self.max_transfer_volume}"
            )

        if request.volume < self.min_transfer_volume:
            raise ValueError(
                f"Transfer volume {request.volume} is less than min transfer volume "
                f"{self.min_transfer_volume}"
            )

    async def transfer(self, request: SingleTransferRequest):
        try:
            self._check_single_request(request)
        except ValueError as e:
            self.logger.error(e)
            raise
        self.logger.info(
            f"Transferring {request.volume} from {request.source.location} to "
            f"{request.destination.location}"
        )
        aspiration_rate, dispense_rate = await self.setup_transfer(request)

        if request.aspirate_mix:
            await self.mix(request.aspirate_mix)

        await self.aspirate(
            request.volume, request.source, rate=aspiration_rate
        )

        await self.dispense(
            request.volume, request.destination, rate=dispense_rate
        )

        if request.dispense_mix:
            await self.mix(request.dispense_mix)

        await self.finish_transfer(request)

    def _check_multi_request(self, request: MultiTransferRequest):
        if request.aspirate_volume > self.max_transfer_volume:
            raise ValueError(
                f"Aspirate volume {request.aspirate_volume} exceeds max transfer volume "
                f"{self.max_transfer_volume}"
            )

        if request.aspirate_volume < self.min_transfer_volume:
            raise ValueError(
                f"Aspirate volume {request.aspirate_volume} is less than min transfer volume "
                f"{self.min_transfer_volume}"
            )

        if request.dispense_volume > self.max_transfer_volume:
            raise ValueError(
                f"Dispense volume {request.dispense_volume} exceeds max transfer volume "
                f"{self.max_transfer_volume}"
            )

        if request.dispense_volume < self.min_transfer_volume:
            raise ValueError(
                f"Dispense volume {request.dispense_volume} is less than min transfer volume "
                f"{self.min_transfer_volume}"
            )

    async def multi_transfer(self, request: MultiTransferRequest):
        try:
            self._check_multi_request()
        except ValueError as e:
            self.logger.error(e)
            raise
        self.logger.info(
            f"Transferring {request.aspirate_volume} from "
            f"{request.source.location} to {len(request.destinations)} "
            f"destinations ({request.dispense_volume} each)"
        )
        aspiration_rate, dispense_rate = await self.setup_transfer(request)

        if request.aspirate_mix:
            await self.mix(request.aspirate_mix)

        await self.aspirate(
            request.aspirate_volume, request.source, rate=aspiration_rate
        )

        for destination in request.destinations:
            await self.dispense(
                request.dispense_volume, destination, rate=dispense_rate
            )

        await self.finish_transfer(request)


class MockLiquidHandler(AbstractLiquidHandler):
    transfers: list[TransferRequest]
    called: list[str]

    def __init__(
        self,
        tips: LocationSet,
        max_transfer_volume: Volume,
        min_transfer_volume: Volume,
        aspiration_rate: FlowRate = None,
        dispense_rate: FlowRate = None,
        logger: logging.Logger = DEFAULT_LOGGER,
    ):
        self.tips = tips
        self.max_transfer_volume = max_transfer_volume
        self.min_transfer_volume = min_transfer_volume
        self.aspiration_rate = aspiration_rate
        self.dispense_rate = dispense_rate
        self.logger = logger
        self.transfers = []
        self.called = []

    async def _setup(self):
        self.transfers = []
        self.called.append("_setup")

    async def _pick_up_tip(self, location: Location):
        self.called.append("_pick_up_tip")

    async def _drop_tip(self):
        self.called.append("_drop_tip")

    async def _aspirate(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        self.called.append("_aspirate")

    async def _dispense(
        self,
        volume: Volume,
        location: Location,
        air_cushion: Volume | None = None,
        rate: FlowRate | None = None,
    ):
        self.called.append("_dispense")

    async def _finish_transfer(self, request: TransferRequest):
        self.called.append("_finish_transfer")
        self.transfers.append(request)

    async def _setup_transfer(self):
        self.called.append("_setup_transfer")
