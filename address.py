# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✅✅✅✅✅
# ####################################################################################################

import hashlib

class Address:
    def __init__(self, raw_bytes=None, public_key=None):
        if raw_bytes is not None:
            if len(raw_bytes) != 32:
                raise ValueError("Address must be a list of 32 bytes")
            self.address_bytes = raw_bytes
        elif public_key is not None:
            self.address_bytes = self.hash_public_key(public_key)
        else:
            raise ValueError("Either raw_bytes or public_key has to be provided")

    def hash_public_key(self, public_key):
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

        return ripemd160_hash

    def __str__(self):
        return self.address_bytes.hex()
