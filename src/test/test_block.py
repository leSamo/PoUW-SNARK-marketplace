# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import os
import sys
import pytest
import util
import hashlib

from block import Block
from block_header import BlockHeader
from block_body import BlockBody
from state_tree import StateTree

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

ADDRESS = bytes.fromhex("0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000")

def test_valid():
    current_time = util.get_current_time()

    st = StateTree()

    body = BlockBody()
    body.setup([], [], st)

    header = BlockHeader()
    header.setup(1, current_time, 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    block = Block()
    block.setup(header, body)

    assert block.get_id() == 1
    assert block.get_timestamp() == current_time
    assert block.get_previous_block_hash() == hashlib.sha256("abc".encode()).digest()

def test_hashes():
    current_time = util.get_current_time()

    st = StateTree()

    body = BlockBody()
    body.setup([], [], st)

    header1 = BlockHeader()
    header1.setup(1, current_time, 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    header2 = BlockHeader()
    header2.setup(2, current_time, 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    header3 = BlockHeader()
    header3.setup(2, current_time, 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    block1 = Block()
    block1.setup(header1, body)
    block1.finish_block()

    block2 = Block()
    block2.setup(header2, body)
    block2.finish_block()

    block3 = Block()
    block3.setup(header2, body)
    block3.finish_block()

    assert block1.get_current_block_hash() != block2.get_current_block_hash()
    assert block2.get_current_block_hash() == block3.get_current_block_hash()

def test_invalid_id():
    st = StateTree()

    body = BlockBody()
    body.setup([], [], st)

    with pytest.raises(ValueError):
        header = BlockHeader()
        header.setup(-1, util.get_current_time(), 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

def test_invalid_difficulty():
    st = StateTree()

    body = BlockBody()
    body.setup([], [], st)

    with pytest.raises(ValueError):
        header = BlockHeader()
        header.setup(1, util.get_current_time(), 0, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    with pytest.raises(ValueError):
        header = BlockHeader()
        header.setup(1, util.get_current_time(), -1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

def test_encode_decode():
    current_time = util.get_current_time()

    st = StateTree()

    body = BlockBody()
    body.setup([], [], st)

    header = BlockHeader()
    header.setup(1, current_time, 1, hashlib.sha256("abc".encode()).digest(), body.hash_coin_txs(), body.hash_proof_txs(), st.get_hash())

    block = Block()
    block.setup(header, body)

    with pytest.raises(ValueError):
        block.encode()

    block.finish_block()

    encoded = block.encode()

    new_block = Block()
    new_block.decode(encoded)

    assert new_block.get_id() == 1
    assert new_block.get_timestamp() == current_time
    assert new_block.get_previous_block_hash() == hashlib.sha256("abc".encode()).digest()
