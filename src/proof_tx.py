# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import hashlib

from encodeable import Encodeable
import util

class ProofTransaction(Encodeable):
    __id: bytes             # SHA256 hash (32 bytes)
    __address_from: bytes   # SECP256k1 public key in SEC1 format (33 bytes)
    __proof: bytes          # encoded JSON
    __circuit_hash: bytes   # SHA256 hash (32 bytes)
    __parameters: str
    __signature: bytes      # SECP256k1 signature (64 bytes)

    def __init__(self) -> None:
        pass

    def setup(self, address_from, circuit_hash, parameters) -> None:
        util.validate_address(address_from)
        util.validate_hash(circuit_hash)

        timestamp = util.get_current_time()
        serialized_tx = "|".join([str(timestamp), address_from.hex(), circuit_hash.hex(), parameters]).encode()

        self.__id = hashlib.sha256(serialized_tx).digest()
        self.__address_from = address_from
        self.__proof = None
        self.__circuit_hash = circuit_hash
        self.__parameters = parameters
        self.__signature = None

        self.check_validity()

    def check_validity(self):
        # TODO: check if proof is valid JSON
        pass

    def hash(self) -> bytes:
        if self.__proof is None:
            serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__circuit_hash.hex(), self.__parameters]).encode()
        else:
            serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__proof.hex(), self.__circuit_hash.hex(), self.__parameters]).encode()

        return hashlib.sha256(serialized_tx).digest()

    def sign(self, private_key) -> None:
        self.__signature = private_key.sign(self.hash())

    def verify_transaction(self, public_key) -> bool:
        self.check_validity()

        if not public_key.verify(self.__signature, self.hash()):
            return False

        return True

    def is_signed(self) -> bool:
        return self.__signature is not None

    # TODO: Check signature

    def get_id(self) -> int:
        return self.__amount

    def get_circuit_hash(self) -> bytes:
        return self.__circuit_hash

    def get_parameters(self) -> str:
        return self.__parameters

    def encode(self) -> dict:
        return {
            'id': self.__id.hex(),
            'address_from': self.__address_from.hex(),
            'proof': self.__proof.hex() if self.__proof is not None else '',
            'circuit_hash': self.__circuit_hash.hex(),
            'parameters': self.__parameters,
            'signature': self.__signature.hex()
        }

    def decode(self, obj : dict) -> None:
        self.__id = bytes.fromhex(obj['id'])
        self.__address_from = bytes.fromhex(obj['address_from'])
        self.__proof =  bytes.fromhex(obj['proof'])
        self.__circuit_hash = bytes.fromhex(obj['circuit_hash'])
        self.__parameters = obj['parameters']
        self.__signature = bytes.fromhex(obj['signature'])

    def __str__(self) -> str:
        if self.__proof is None:
            return f"{self.__id.hex()[0:6]}…: {self.__address_from.hex()[0:6]}…: {self.__circuit_hash.hex()[0:6]}… --({self.__parameters})--> {util.Color.RED}unproven{util.Color.RESET}"
        else:
            return f"{self.__id.hex()[0:6]}…: {self.__address_from.hex()[0:6]}…: {self.__circuit_hash.hex()[0:6]}… --({self.__parameters})--> {self.__proof.hex()[0:6]}…"
