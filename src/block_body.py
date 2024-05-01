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
from state_tree import StateTree

class BlockBody(Encodeable):
    __coin_txs: list[CoinTransaction]
    __proof_txs: list[ProofTransaction]
    __state_tree: StateTree

    def __init__(self):
        pass

    def setup(self, coin_txs, proof_txs, state_tree):
        self.__coin_txs = coin_txs
        self.__proof_txs = proof_txs
        self.__state_tree = state_tree

    def hash_coin_txs(self):
        tx_hashes = []

        for tx in self.__coin_txs:
            tx_hashes.append(tx.hash().decode())
        
        serialized_txs = ("|").join(tx_hashes).encode()
        return hashlib.sha256(serialized_txs).digest()
    
    def hash_proof_txs(self):
        tx_hashes = []

        for tx in self.__proof_txs:
            tx_hashes.append(tx.hash().decode())
        
        serialized_txs = ("|").join(tx_hashes).encode()
        return hashlib.sha256(serialized_txs).digest()

    def hash_state_tree(self):
        return self.__state_tree.get_hash()

    def encode(self):
        return {
            'coin_txs': [tx.encode() for tx in self.__coin_txs],
            'proof_txs': [tx.encode() for tx in self.__coin_txs],
            'state_tree': self.__state_tree.encode()
        }
    
    def decode(self, obj):
        coin_transactions = []
        proof_transactions = []

        for tx in obj['coin_txs']:
            ct = CoinTransaction()
            ct.setup(tx)
            coin_transactions.append(ct)

        for tx in obj['proof_txs']:
            pt = ProofTransaction()
            pt.setup(tx)
            proof_transactions.append(pt)

        state_tree = StateTree()
        state_tree.decode(obj['state_tree'])

        self.__coin_txs = coin_transactions
        self.__proof_txs = proof_transactions
        self.__state_tree = state_tree

    def get_state_tree(self):
        return self.__state_tree