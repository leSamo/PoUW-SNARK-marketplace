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
    __state_root_hash: bytes     # SHA256 hash (32 bytes)
    __timestamp: int
    __difficulty: int
    __previous_block_hash: bytes # SHA256 hash (32 bytes)
    __current_block_hash: bytes  # SHA256 hash (32 bytes)
    __coin_txs_hash: bytes       # SHA256 hash (32 bytes)
    __proof_txs_hash: bytes      # SHA256 hash (32 bytes)

    def __init__(self, serial_id, state_root_hash, timestamp, difficulty, previous_block_hash, coin_txs_hash, proof_txs_hash):
        self.__serial_id = serial_id
        self.__state_root_hash = state_root_hash
        self.__timestamp = timestamp
        self.__difficulty = difficulty
        self.__previous_block_hash = previous_block_hash
        self.__coin_txs_hash = coin_txs_hash
        self.__proof_txs_hash = proof_txs_hash

    def __init__(self, obj):
        self.__decode(obj)

    def calculate_hash(self):
        serialized_block = [self.__serial_id, self.__state_root_hash, self.__timestamp, self.__difficulty, self.__previous_block_hash, self.__coin_txs_hash, self.__proof_txs_hash].encode()
        block_hash = hashlib.sha256(serialized_block).digest()

        self.__current_block_hash = block_hash

    def encode(self):
        return {
            'serial_id': self.__serial_id,
            'state_root_hash': self.__state_root_hash,
            'timestamp': self.__timestamp,
            'difficulty': self.__difficulty,
            'previous_block_hash': self.__previous_block_hash,
            'current_block_hash': self.__current_block_hash,
            'coin_txs_hash': self.__coin_txs_hash,
            'proof_txs_hash': self.__proof_txs_hash
        }
    
    def __decode(self, obj):
        self.__serial_id: obj['serial_id']
        self.__state_root_hash: obj['state_root_hash']
        self.__timestamp: obj['timestamp']
        self.__difficulty: obj['difficulty']
        self.__previous_block_hash: obj['previous_block_hash']
        self.__current_block_hash: obj['current_block_hash']
        self.__coin_txs_hash: obj['coin_txs_hash']
        self.__proof_txs_hash: obj['proof_txs_hash']
