# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import math
import hashlib

from encodeable import Encodeable
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction
import util

class StateTree(Encodeable):
    __state: dict

    def __init__(self):
        self.__state = {}

    def set(self, key : bytes, value : int):
        util.validate_address(key)
        if type(value) != int: raise TypeError("Trying to insert invalid value into the state tree, only int type is permitted as a value")
        if value < 0: raise ValueError("Trying to insert negative value into the state tree")

        self.__state[key] = value

    def get(self, key : bytes) -> int:
        util.validate_address(key)

        try:
            return self.__state[key]
        except KeyError:
            return 0

    def get_hash(self) -> bytes:
        items = str(tuple(sorted(self.__state.items()))).encode()
        return hashlib.sha256(items).digest()

    def encode(self):
        return {key.hex(): value for key, value in self.__state.items()}

    def decode(self, obj):
        # TODO: Validate
        self.__state = {
            bytes.fromhex(key): value for key, value in obj.items()
        }

    def apply_coin_tx(self, coin_tx : CoinTransaction, fee : int, fee_beneficiary : bytes):
        amount = coin_tx.get_amount()

        sender_balance = self.get(coin_tx.get_address_from())
        self.set(coin_tx.get_address_from(), sender_balance - amount - fee)

        receiver_balance = self.get(coin_tx.get_address_to())
        self.set(coin_tx.get_address_to(), receiver_balance + amount)

        miner_balance = self.get(fee_beneficiary)
        self.set(fee_beneficiary, miner_balance + fee)

    def apply_proof_tx(self, proof_tx : ProofTransaction, fee : int, fee_beneficiary : bytes):
        price = math.ceil(proof_tx.get_complexity() / fee)

        sender_balance = self.get(proof_tx.get_address_from())
        self.set(proof_tx.get_address_from(), sender_balance - price)

        miner_balance = self.get(fee_beneficiary)
        self.set(fee_beneficiary, miner_balance + price)
