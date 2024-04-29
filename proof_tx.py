# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import time
import hashlib

class ProofTransaction:
    __id: bytes             # SHA256 hash (32 bytes)
    __address_from: bytes   # SECP256k1 public key in SEC1 format (33 bytes)
    __proof: bytes          # encoded JSON
    __circuit_hash: bytes   # SHA256 hash (32 bytes)
    __key_randomness: bytes # raw 32 bytes
    __signature: bytes      # SECP256k1 signature (64 bytes)

    def __init__(self, address_from, proof, circuit_hash, key_randomness):
        timestamp = time.time() * 1000
        serialized_tx = [timestamp, address_from, proof, circuit_hash, key_randomness].encode()

        self.__id = hashlib.sha256(serialized_tx).hexdigest()
        self.__address_from = address_from
        self.__proof = proof
        self.__circuit_hash = circuit_hash
        self.__key_randomness = key_randomness
        self.__signature = None

        self.check_validity()

    def check_validity(self):
        # TODO: check if proof is valid JSON
        pass

    def hash(self):
        serialized_tx = [self.__id, self.__address_from, self.__proof, self.__circuit_hash, self.__key_randomness].encode()
        return hashlib.sha256(serialized_tx).digest()
    
    def sign(self, private_key):
        self.__signature = private_key.sign(self.hash())
    
    def verify_transaction(self, public_key):
        self.check_validity()
        
        if not public_key.verify(self.__signature, self.hash()):
            return False
        
        return True

    def is_signed(self):
        return self.__signature is not None