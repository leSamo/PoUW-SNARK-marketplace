# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import hashlib

from encodeable import Encodeable

class StateTree(Encodeable):
    __state: dict

    def __init__(self):
        self.__state = {}

    def set(self, key : bytes, value : int):
        if type(key) != bytes: raise TypeError("Invalid address type during state tree inserting, only address of bytes type is permitted")
        if len(key) != 33: raise ValueError("Invalid address size during state tree inserting, expected length of 33 bytes")
        if type(value) != int: raise TypeError("Trying to insert invalid value into the state tree, only int type is permitted as a value")
        if value < 0: raise ValueError("Trying to insert negative value into the state tree")

        self.__state[key] = value

    def get(self, key : bytes) -> int:
        if type(key) != bytes: raise TypeError("Invalid address type during state tree inserting, only address of bytes type is permitted")
        if len(key) != 33: raise ValueError("Invalid address size during state tree inserting, expected length of 33 bytes")

        try:
            return self.__state[key]
        except KeyError:
            return 0
        
    def get_hash(self):
        items = str(tuple(sorted(self.__state.items()))).encode()
        return hashlib.sha256(items).digest()

    def encode(self):
        return {key.hex(): value for key, value in self.__state.items()}
    
    def decode(self, obj):
        # TODO: Validate
        self.__state = {bytes.fromhex(key): value for key, value in obj.items()}
