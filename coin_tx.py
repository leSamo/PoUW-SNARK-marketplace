# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✅✅✅❌❌
# ####################################################################################################

from address import Address
import time
import hashlib

class CoinTransaction:
    __id: Address
    __address_from: Address
    __address_to: Address
    __amount: int
    __signature: Signature

    def __init__(self, address_from, address_to, amount):
        if amount <= 0:
            raise Exception("Transaction amount has to be positive")

        timestamp = time.time() * 1000

        self.__address_from = address_from
        self.__address_to = address_to
        self.__amount = amount

        serialized_tx = [timestamp, address_from, address_to, amount].encode()

        self.__id = hashlib.sha256(serialized_tx).hexdigest()
        self.__signature = None

    def sign(self, private_key):
        serialized_tx = [self.__id, self.__address_from, self.__address_to, self.__amount].encode()
        tx_hash = hashlib.sha256(serialized_tx).digest()

        self.__signature = private_key.sign(tx_hash)

    def is_signed(self):
        return self.__signature is not None
