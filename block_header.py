# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

class BlockHeader:
    __serial_id: int
    __state_root_hash: bytes     # SHA256 hash (32 bytes)
    __timestamp: int
    __difficulty: int
    __previous_block_hash: bytes # SHA256 hash (32 bytes)
    __current_block_hash: bytes  # SHA256 hash (32 bytes)
    __coin_txs_hash: bytes       # SHA256 hash (32 bytes)
    __proof_txs: bytes           # SHA256 hash (32 bytes)

    def __init__(self, serial_id, state_root_hash):
        pass

    def hash(self):
        pass
