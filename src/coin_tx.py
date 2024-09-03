# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import hashlib

import util
from encodeable import Encodeable
import ecdsa

# TODO: Add timestamp
class CoinTransaction(Encodeable):
    __id: bytes           # SHA256 hash (32 bytes)
    __address_from: bytes # SECP256k1 public key in SEC1 format (33 bytes)
    __address_to: bytes   # SECP256k1 public key in SEC1 format (33 bytes)
    __amount: int
    __signature: bytes    # SECP256k1 signature (64 bytes)

    def __init__(self):
        pass

    def setup(self, address_from : bytes, address_to : bytes, amount : int) -> None:
        util.validate_address(address_from)
        util.validate_address(address_to)

        timestamp = util.get_current_time()
        serialized_tx = "|".join([str(timestamp), address_from.hex(), address_to.hex(), str(amount)]).encode()

        self.__id = hashlib.sha256(serialized_tx).digest()
        self.__address_from = address_from
        self.__address_to = address_to
        self.__amount = amount
        self.__signature = None

        self.check_validity()

    def check_validity(self) -> None:
        if self.__amount <= 0:
            raise ValueError("Transaction amount must be positive")

        if self.__address_from == self.__address_to:
            raise ValueError("Sender and receiver addresses cannot be the same")

    def hash(self) -> bytes:
        serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__address_to.hex(), str(self.__amount)]).encode()
        return hashlib.sha256(serialized_tx).digest()

    def get_integrity(self) -> bytes:
        serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__address_to.hex(), str(self.__amount), self.__signature.hex()]).encode()
        return hashlib.sha256(serialized_tx).digest()

    def sign(self, private_key) -> None:
        corresponding_public_key = bytes.fromhex(private_key.get_verifying_key().to_string('compressed').hex())

        if corresponding_public_key != self.__address_from: raise ValueError("Incorrect private key used to signed transaction")

        self.__signature = private_key.sign(self.hash())

    def verify_transaction(self) -> bool:
        self.check_validity()

        if not ecdsa.VerifyingKey.from_string(self.__address_from, curve=ecdsa.SECP256k1).verify(self.__signature, self.hash()):
            return False

        return True

    def is_signed(self) -> bool:
        return self.__signature is not None

    def get_id(self) -> int:
        return self.__amount

    def get_address_from(self) -> bytes:
        return self.__address_from

    def get_address_to(self) -> bytes:
        return self.__address_to

    def get_amount(self) -> int:
        return self.__amount

    def encode(self) -> dict:
        if not self.is_signed(): raise ValueError("Cannot encode an unsigned transaction");

        return {
            'id': self.__id.hex(),
            'address_from': self.__address_from.hex(),
            'address_to': self.__address_to.hex(),
            'amount': self.__amount,
            'signature': self.__signature.hex()
        }

    def decode(self, obj : dict) -> None:
        self.__id = bytes.fromhex(obj['id'])
        self.__address_from =  bytes.fromhex(obj['address_from'])
        self.__address_to = bytes.fromhex(obj['address_to'])
        self.__amount = obj['amount']
        self.__signature = bytes.fromhex(obj['signature'])

    def __str__(self) -> str:
        return f"{self.__id.hex()[0:6]}…: {self.__address_from.hex()[0:6]}… --({self.__amount})--> {self.__address_to.hex()[0:6]}…"
