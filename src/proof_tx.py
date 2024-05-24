# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import hashlib
import ecdsa

from encodeable import Encodeable
from bind_zokrates import Zokrates
import util

class ProofTransaction(Encodeable):
    __id: bytes             # SHA256 hash (32 bytes)
    __address_from: bytes   # SECP256k1 public key in SEC1 format (33 bytes)
    __proof: str            # encoded JSON
    __circuit_hash: bytes   # SHA256 hash (32 bytes)
    __parameters: str
    __complexity: int       # number of constraints
    __signature: bytes      # SECP256k1 signature (64 bytes)

    def __init__(self) -> None:
        pass

    def setup(self, address_from, circuit_hash, parameters, complexity) -> None:
        timestamp = util.get_current_time()
        serialized_tx = "|".join([str(timestamp), address_from.hex(), circuit_hash.hex(), parameters]).encode()

        self.__id = hashlib.sha256(serialized_tx).digest()
        self.__address_from = address_from
        self.__proof = None
        self.__circuit_hash = circuit_hash
        self.__parameters = parameters
        self.__complexity = complexity
        self.__signature = None

        self.check_validity()

    def check_validity(self) -> None:
        util.validate_address(self.__address_from)
        util.validate_hash(self.__circuit_hash)

        if type(self.__complexity) != int:
            raise TypeError("Complexity has to be an integer")

        if self.__complexity <= 0:
            raise ValueError("Complexity has to be a positive integer")

    def hash(self) -> bytes:
        serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__circuit_hash.hex(), self.__parameters, str(self.__complexity)]).encode()

        return hashlib.sha256(serialized_tx).digest()

    def get_integrity(self) -> bytes:
        serialized_tx = "|".join([self.__id.hex(), self.__address_from.hex(), self.__circuit_hash.hex(), self.__parameters, str(self.__complexity), self.__signature.hex()]).encode()
        return hashlib.sha256(serialized_tx).digest()

    def sign(self, private_key) -> None:
        corresponding_public_key = bytes.fromhex(private_key.get_verifying_key().to_string('compressed').hex())

        if corresponding_public_key != self.__address_from: raise ValueError("Incorrect private key used to signed transaction")

        self.__signature = private_key.sign(self.hash())

    def verify_transaction(self) -> bool:
        if not ecdsa.VerifyingKey.from_string(self.__address_from, curve=ecdsa.SECP256k1).verify(self.__signature, self.hash()):
            return False

        return True

    def is_signed(self) -> bool:
        return self.__signature is not None

    # TODO: Check signature

    def get_id(self) -> int:
        return self.__id

    def get_circuit_hash(self) -> bytes:
        return self.__circuit_hash

    def get_parameters(self) -> str:
        return self.__parameters

    def get_complexity(self) -> int:
        return self.__complexity

    def get_address_from(self) -> bytes:
        return self.__address_from

    def get_proof(self) -> str:
        return self.__proof

    def encode(self) -> dict:
        return {
            'id': self.__id.hex(),
            'address_from': self.__address_from.hex(),
            'proof': self.__proof if self.__proof is not None else '',
            'circuit_hash': self.__circuit_hash.hex(),
            'parameters': self.__parameters,
            'complexity': self.__complexity,
            'signature': self.__signature.hex()
        }

    def decode(self, obj : dict) -> None:
        self.__id = bytes.fromhex(obj['id'])
        self.__address_from = bytes.fromhex(obj['address_from'])
        self.__proof = None if obj['proof'] == '' else obj['proof']
        self.__circuit_hash = bytes.fromhex(obj['circuit_hash'])
        self.__parameters = obj['parameters']
        self.__complexity = obj['complexity']
        self.__signature = bytes.fromhex(obj['signature'])

    def __str__(self) -> str:
        if self.__proof is None:
            return f"{self.__id.hex()[0:6]}…: {self.__address_from.hex()[0:6]}… --({self.__parameters})--> {self.__circuit_hash.hex()[0:6]}… @ {self.__complexity} constraints ({util.Color.RED()}unproven{util.Color.RESET()})"
        else:
            return f"{self.__id.hex()[0:6]}…: {self.__address_from.hex()[0:6]}… --({self.__parameters})--> {self.__circuit_hash.hex()[0:6]}… @ {self.__complexity} constraints ({util.Color.GREEN()}proven{util.Color.RESET()})"

    def prove(self, block_metadata, circuit_folder) -> None:
        self.__proof = Zokrates.generate_proof(block_metadata, circuit_folder, self.__parameters)

    def validate(self, block_metadata, circuit_folder) -> bool:
        Zokrates.verify_proof(block_metadata, circuit_folder, self.__proof, self.__parameters)
        pass
