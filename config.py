# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

from block import Block
from block_body import BlockBody
from block_header import BlockHeader

SEED_NODES = ['localhost:2222']

#################### GENESIS BLOCK CONFIGURATION ####################
genesis_state_tree = {
    '0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2': 1000
}

genesis_block_body = BlockBody()
genesis_block_body.setup([], [], genesis_state_tree)

coin_txs_hash = genesis_block_body.hash_coin_txs()
proof_txs_hash = genesis_block_body.hash_proof_txs()
state_root_hash = genesis_block_body.hash_state_tree()

genesis_block_header = BlockHeader()
genesis_block_header.setup(0, 1714436126662, 0, '00000000000000000000000000000000'.encode(), coin_txs_hash, proof_txs_hash, state_root_hash)

genesis_block = Block()
genesis_block.setup(genesis_block_header, genesis_block_body)
