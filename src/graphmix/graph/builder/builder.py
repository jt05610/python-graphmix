from abc import ABC
from abc import abstractmethod

from graphmix.graph.protocol import Protocol


class ProtocolBuilder(ABC):

    @abstractmethod
    def build(self) -> Protocol:
        raise NotImplementedError
