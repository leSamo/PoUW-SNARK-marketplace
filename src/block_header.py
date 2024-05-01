# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import hashlib

from encodeable import Encodeable

class BlockHeader(Encodeable):
    __serial_id: int
    __timestamp: int
    __difficulty: int
    __previous_block_hash: bytes # SHA256 hash (32 bytes)
    __current_block_hash: bytes  # SHA256 hash (32 bytes)
    __coin_txs_hash: bytes       # SHA256 hash (32 bytes)
    __proof_txs_hash: bytes      # SHA256 hash (32 bytes)
    __state_root_hash: bytes     # SHA256 hash (32 bytes)

    def __init__(self):
        pass

    def setup(self, serial_id, timestamp, difficulty, previous_block_hash, coin_txs_hash, proof_txs_hash, state_root_hash):
        self.__serial_id = serial_id
        self.__timestamp = timestamp
        self.__difficulty = difficulty
        self.__previous_block_hash = previous_block_hash
        self.__coin_txs_hash = coin_txs_hash
        self.__proof_txs_hash = proof_txs_hash
        self.__state_root_hash = state_root_hash

    def calculate_hash(self):
        serialized_block = "|".join([
            str(self.__serial_id),
            str(self.__timestamp),
            str(self.__difficulty),
            self.__previous_block_hash.hex(),
            self.__coin_txs_hash.hex(),
            self.__proof_txs_hash.hex(),
            self.__state_root_hash.hex()
        ]).encode()
        block_hash = hashlib.sha256(serialized_block).digest()

        return block_hash

    def encode(self):
        self.calculate_hash()

        return {
            'serial_id': self.__serial_id,
            'timestamp': self.__timestamp,
            'difficulty': self.__difficulty,
            'previous_block_hash': self.__previous_block_hash.hex(),
            'current_block_hash': self.__current_block_hash.hex(),
            'coin_txs_hash': self.__coin_txs_hash.hex(),
            'proof_txs_hash': self.__proof_txs_hash.hex(),
            'state_root_hash': self.__state_root_hash.hex()
        }
    
    def decode(self, obj):
        self.__serial_id = obj['serial_id']
        self.__timestamp = obj['timestamp']
        self.__difficulty = obj['difficulty']
        self.__previous_block_hash = bytes.fromhex(obj['previous_block_hash'])
        self.__current_block_hash = bytes.fromhex(obj['current_block_hash'])
        self.__coin_txs_hash = bytes.fromhex(obj['coin_txs_hash'])
        self.__proof_txs_hash = bytes.fromhex(obj['proof_txs_hash'])
        self.__state_root_hash = bytes.fromhex(obj['state_root_hash'])

    def get_id(self):
        return self.__serial_id
    
    def get_timestamp(self):
        return self.__timestamp
    
    def get_difficulty(self):
        return self.__difficulty
    
    def get_previous_block_hash(self):
        return self.get_previous_block_hash()
    
    def verify_hash(self) -> bool:
        block_hash = self.calculate_hash()
        return self.__current_block_hash == block_hash
    
    def get_current_block_hash(self):
        return self.__current_block_hash
    
    def finish_block(self):
        block_hash = self.calculate_hash()
        self.__current_block_hash = block_hash
