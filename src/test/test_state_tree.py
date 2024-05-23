# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from state_tree import StateTree
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction

def test_insert():
    st = StateTree()
    st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)

def test_insert_invalid_key_type():
    with pytest.raises(TypeError):
        st = StateTree()
        st.set("123", 123)

def test_insert_invalid_key_length():
    with pytest.raises(ValueError):
        st = StateTree()
        st.set(bytes.fromhex("1234"), 123)

def test_insert_invalid_value_type():
    with pytest.raises(TypeError):
        st = StateTree()
        st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), "invalid")

def test_insert_negative_value():
    with pytest.raises(ValueError):
        st = StateTree()
        st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), -123)

def test_retrieve():
    st = StateTree()
    st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)
    value = st.get(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"))

    assert value == 123

def test_retrieve_missing():
    st = StateTree()
    st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)
    value = st.get(bytes.fromhex("4568b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f123"))

    assert value == 0

def test_retrieve_invalid_key_type():
    with pytest.raises(TypeError):
        st = StateTree()
        st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)
        st.get("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2")

def test_retrieve_invalid_key_length():
    with pytest.raises(ValueError):
        st = StateTree()
        st.get(bytes.fromhex("1234"))

def test_update():
    st = StateTree()
    st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)
    st.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 456)
    value = st.get(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"))

    assert value == 456

def test_hash():
    st1 = StateTree()
    st2 = StateTree()

    assert st1.get_hash() == st2.get_hash()

    st1.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)

    assert st1.get_hash() != st2.get_hash()

    st2.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)

    assert st1.get_hash() == st2.get_hash()

def test_encode_decode():
    st1 = StateTree()
    st1.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 123)
    st1.set(bytes.fromhex("4568b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f123"), 456)

    encoded = st1.encode()

    st2 = StateTree()
    st2.decode(encoded)
    value1 = st2.get(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"))
    value2 = st2.get(bytes.fromhex("4568b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f123"))
    value3 = st2.get(bytes.fromhex("0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000"))

    assert value1 == 123
    assert value2 == 456
    assert value3 == 0

    st2.set(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"), 234)
    st2.set(bytes.fromhex("7778b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f777"), 789)

    value1 = st2.get(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"))
    value2 = st2.get(bytes.fromhex("7778b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f777"))
    value3 = st2.get(bytes.fromhex("0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000"))

    assert value1 == 234
    assert value2 == 789
    assert value3 == 0

def test_coin_tx_application():
    sender = bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2")
    receiver = bytes.fromhex("7778b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f777")
    miner = bytes.fromhex("0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000")

    st = StateTree()
    st.set(sender, 100)

    tx = CoinTransaction()
    tx.setup(sender, receiver, 10)

    st.apply_coin_tx(tx, 1, miner)

    assert st.get(sender) == 89
    assert st.get(receiver) == 10
    assert st.get(miner) == 1


def test_proof_tx_application():
    sender = bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2")
    miner = bytes.fromhex("0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000")

    circuit_hash = bytes.fromhex("7a6e42a3c43b426aad2e6062d33be7cc0650e8ea724c12574d44a740cfd63319")

    st = StateTree()
    st.set(sender, 100)

    tx = ProofTransaction()
    tx.setup(sender, circuit_hash, "1111", 761)

    st.apply_proof_tx(tx, 100, miner)

    assert st.get(sender) == 92
    assert st.get(miner) == 8

# TODO: Validate decoding
