# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️❌
# ####################################################################################################

import hashlib

from coin_tx import CoinTransaction
from proof_tx import ProofTransaction
from encodeable import Encodeable

class BlockBody(Encodeable):
    __coin_txs: list[CoinTransaction]
    __proof_txs: list[ProofTransaction]
    __state_tree: dict

    def __init__(self, coin_txs, proof_txs, state_tree):
        self.__coin_txs = coin_txs
        self.__proof_txs = proof_txs
        self.__state_tree = state_tree

    def __init__(self, obj):
        self.__decode(obj)

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

    def encode(self):
        return {
            'coin_txs': [tx.encode() for tx in self.__coin_txs],
            'proof_txs': [tx.encode() for tx in self.__coin_txs],
            'state_tree': tuple(sorted(self.__state_tree.items()))
        }
    
    def __decode(self, obj):
        self.__coin_txs = [CoinTransaction(tx) for tx in obj['coin_txs']]
        self.__proof_txs = [CoinTransaction(tx) for tx in obj['proof_txs']]
        self.__state_tree = dict(obj['state_tree'])
