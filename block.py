# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import hashlib

from block_header import BlockHeader
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction

class Block:
    __header: BlockHeader
    __coin_txs: list[CoinTransaction]
    __proof_txs: list[ProofTransaction]

    def __init__(self, header, coin_txs, proof_txs):
        self.__header = header
        self.__coin_txs = coin_txs
        self.__proof_txs = proof_txs

    def hash_coin_txs(self):
        tx_hashes = []

        for tx in self.__coin_txs:
            tx_hashes.append(tx.hash())
        
        serialized_txs = tx_hashes.encode()
        return hashlib.sha256(serialized_txs).digest()
    
    def hash_proof_txs(self):
        tx_hashes = []

        for tx in self.__proof_txs:
            tx_hashes.append(tx.hash())
        
        serialized_txs = tx_hashes.encode()
        return hashlib.sha256(serialized_txs).digest()

    def finalize_block(self):
        self.__header.set_txs_hashes(self.hash_coin_txs(), self.hash_proof_txs())
        self.__header.calculate_hash()
