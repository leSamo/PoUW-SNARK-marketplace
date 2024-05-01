# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import os
import sys
import pytest
import ecdsa

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from coin_tx import CoinTransaction

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key

def test_valid():
    private_key = load_ecdsa_private_key(os.path.join(os.path.dirname(__file__), './misc/private_key'))

    tx = CoinTransaction()
    tx.setup(
        "0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2".encode(),
        "222222222222222222222222222222222222222222222222222222222222222222".encode(),
        50
    )

    assert not tx.is_signed()

    tx.sign(private_key)

    assert tx.is_signed()

def test_same_addreses():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            "0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2".encode(),
            "0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2".encode(),
            50
        )

def test_invalid_addresses():
    pass

def test_negative_amount():
    pass

def test_invalid_signature():
    pass

def test_encode_decode():
    pass

# TODO: Validate decoding
