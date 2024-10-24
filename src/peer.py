# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

from encodeable import Encodeable

# TODO: Add boolean whether active
class Peer(Encodeable):
    __ip_address: str
    __port: int
    __latest_block_id: int

    def __init__(self):
        pass

    def setup_from_string(self, ip_address_with_port: str) -> None:
        ip_address, port = ip_address_with_port.split(":")

        self.__ip_address = ip_address
        self.__port = int(port)
        self.__latest_block_id = 0

    def setup_from_tuple(self, tuple) -> None:
        self.__ip_address = tuple[0]
        self.__port = tuple[1]

    def set_latest_block_id(self, block_id):
        self.__latest_block_id = block_id

    def get_latest_block_id(self):
        return self.__latest_block_id

    def to_tuple(self):
        return (self.__ip_address, self.__port)

    def to_string(self):
        return f"{self.__ip_address}:{str(self.__port)}"

    def encode(self):
        return {
            'ip_address': self.__ip_address,
            'port': self.__port,
        }

    def decode(self, obj):
        self.__ip_address = obj['ip_address']
        self.__port = obj['port']
