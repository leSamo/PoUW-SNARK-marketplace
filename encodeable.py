from abc import ABC, abstractmethod

class Encodeable(ABC):

    @abstractmethod
    def encode(self):
        pass

    @abstractmethod
    def __decode(self):
        pass
