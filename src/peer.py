# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

from encodeable import Encodeable

class Peer(Encodeable):
    __reputation: int
    __is_blacklisted: bool
    __ip_address: str
    __port: int

    def __init__(self):
        pass

    def setup(self, address_from, address_to, amount):
        self.__reputation = 0

    def increase_reputation(self):
        if self.__reputation < 10:
            self.__reputation += 1

    def decrease_reputation(self):
        if self.__reputation > -10:
            self.__reputation -= 1
        else:
            self.__is_blacklisted = True

    def to_tuple(self):
        return (self.__ip_address, self.__port)

    def encode(self):
        return {
            'ip_address': self.__ip_address,
            'port': self.__port,
            'reputation': self.__reputation,
            'is_blacklisted': self.__is_blacklisted
        }
    
    def decode(self, obj):
        self.__ip_address = obj['ip_address']
        self.__port = obj['port']
        self.__reputation = obj['reputation']
        self.__is_blacklisted = obj['is_blacklisted']
