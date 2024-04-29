# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import time
import hashlib

class CoinTransaction:
    __id: bytes           # SHA256 hash (32 bytes)
    __address_from: bytes # SECP256k1 public key in SEC1 format (33 bytes)
    __address_to: bytes   # SECP256k1 public key in SEC1 format (33 bytes) 
    __amount: int
    __signature: bytes    # SECP256k1 signature (64 bytes)

    def __init__(self, id, address_from, address_to, amount, signature):
        self.__id = id
        self.__address_from = address_from
        self.__address_to = address_to
        self.__amount = amount
        self.__signature = signature

        self.check_validity()

    def __init__(self, address_from, address_to, amount):
        timestamp = time.time() * 1000
        serialized_tx = [timestamp, address_from, address_to, amount].encode()

        self.__id = hashlib.sha256(serialized_tx).hexdigest()
        self.__address_from = address_from
        self.__address_to = address_to
        self.__amount = amount
        self.__signature = None

        self.check_validity()

    def check_validity(self):
        if self.__amount <= 0:
            raise Exception("Transaction amount has to be positive")
        
        if self.__address_from == self.__address_to:
            raise Exception("Sender and receiver addresses cannot be the same")

    def hash(self):
        serialized_tx = [self.__id, self.__address_from, self.__address_to, self.__amount].encode()
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
    
    def encode(self):
        return {
            'id': self.__id,
            'address_from': self.__address_from.hex(),
            'address_to': self.__address_to.hex(),
            'amount': self.__amount,
            'signature': self.__signature.hex()
        }
    
def decode(obj):
    return CoinTransaction(
        bytes.fromhex(obj['id']),
        bytes.fromhex(obj['address_from']),
        bytes.fromhex(obj['address_to']),
        obj['amount'],
        bytes.fromhex(obj['signature']),
    )
