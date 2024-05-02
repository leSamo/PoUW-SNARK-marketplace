# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️✔️
# ####################################################################################################

from abc import ABC, abstractmethod

class Encodeable(ABC):

    @abstractmethod
    def encode(self) -> dict:
        pass

    @abstractmethod
    def decode(self) -> None:
        pass
