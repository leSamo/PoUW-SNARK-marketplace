# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import os
import ecdsa
import pytest

from proof_tx import ProofTransaction

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key

def test_valid():
    private_key = load_ecdsa_private_key(os.path.join(os.path.dirname(__file__), './misc/private_key'))

    tx = ProofTransaction()

    tx.setup(
        bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
        bytes.fromhex("00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee"),
        "2 3 6",
        3
    )

    assert not tx.is_signed()

    tx.sign(private_key)

    assert tx.is_signed()

def test_negative_complexity():
    with pytest.raises(ValueError):
        tx = ProofTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee"),
            "2 3 6",
            -3
        )


def test_invalid_address():
    with pytest.raises(ValueError):
        tx = ProofTransaction()
        tx.setup(
            bytes.fromhex("123"),
            bytes.fromhex("00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee"),
            "2 3 6",
            3
        )

def test_invalid_hash():
    with pytest.raises(ValueError):
        tx = ProofTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("123"),
            "2 3 6",
            3
        )

def test_invalid_signature():
    private_key = load_ecdsa_private_key(os.path.join(os.path.dirname(__file__), './misc/private_key'))

    with pytest.raises(ValueError):
        tx = ProofTransaction()
        tx.setup(
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            bytes.fromhex("00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee"),
            "2 3 6",
            3
        )

        tx.sign(private_key)
