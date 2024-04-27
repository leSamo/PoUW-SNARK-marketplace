# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

from block_header import BlockHeader
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction

class Block:
    __header: BlockHeader
    __coin_txs: list[CoinTransaction]
    __proof_txs: list[ProofTransaction]

    def __init__(self, serial_id, state_root_hash):
        pass

    def hash_coin_txs(self):
        pass
    
    def hash_proof_txs(self):
        pass
