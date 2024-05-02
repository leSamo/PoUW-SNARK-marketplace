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
        bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
        bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
        50
    )

    assert not tx.is_signed()

    tx.sign(private_key)

    assert tx.is_signed()

def test_same_addreses():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            50
        )

def test_invalid_addresses():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("25"),
            50
        )

    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("25"),
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            50
        )

    with pytest.raises(TypeError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            "222222222222222222222222222222222222222222222222222222222222222222",
            50
        )
    
    with pytest.raises(TypeError):
        tx = CoinTransaction()
        tx.setup(
            "0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2",
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            50
        )

def test_zero_amount():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            0
        )

def test_negative_amount():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            -50
        )

def test_invalid_signature():
    private_key = load_ecdsa_private_key(os.path.join(os.path.dirname(__file__), './misc/private_key'))

    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            50
        )

        tx.sign(private_key)

def test_encode_decode():
    private_key = load_ecdsa_private_key(os.path.join(os.path.dirname(__file__), './misc/private_key'))

    tx1 = CoinTransaction()
    tx1.setup(
        bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
        bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
        50
    )

    tx1.sign(private_key)

    encoded = tx1.encode()
    tx2 = CoinTransaction()
    tx2.decode(encoded)

    assert tx2.is_signed()
    assert tx2.verify_transaction(bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"))
    assert tx2.__address_from == bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2")
    assert tx2.__address_to == bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222")
    assert tx2.__amount == 50

def test_encode_decode_unsigned():
    with pytest.raises(ValueError):
        tx = CoinTransaction()
        tx.setup(
            bytes.fromhex("0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"),
            bytes.fromhex("222222222222222222222222222222222222222222222222222222222222222222"),
            50
        )

        # Cannot encode unsigned transactions
        tx.encode()

# TODO: Validate decoding, especially signature
