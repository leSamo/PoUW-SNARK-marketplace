import subprocess
import os
import sys
import time
import requests
import json
import pytest

from utils import MockClient
from util import Command

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

client_program = os.path.join(os.path.dirname(__file__), "..", "client.py")

@pytest.fixture
def client():
    config = os.path.join(os.path.dirname(__file__), "misc/config/1_peer.json")
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")

    client = MockClient(f'-v -p 3333 -f {config} -k {private_key} -r 9545 -c "produce-empty"')

    time.sleep(1)

    yield client

    client.close_stdin()

    time.sleep(0.5)

def test_get_latest_block(client):
    data = {
        "id": 0,
        "method": Command.GET_LATEST_BLOCK_ID,
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["latest_id"] == 1

    client.stdin("produce-empty\n")

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["latest_id"] == 2

def test_get_block(client):
    data = {
        "id": 0,
        "method": "GET_BLOCK",
        "params": [0],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["block"]["header"]["serial_id"] == 0

def test_get_pending_coin_txs(client):
    data = {
        "id": 0,
        "method": "GET_PENDING_COIN_TXS",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["pending_coin_txs"] == []

    client.stdin("send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50\n")

    time.sleep(0.1)

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert len(response.json()["result"]["pending_coin_txs"]) == 1

def test_get_pending_proof_txs(client):
    data = {
        "id": 0,
        "method": "GET_PENDING_PROOF_TXS",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["pending_proof_txs"] == []

    client.stdin("request-proof 00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee 2 3 6\n")

    time.sleep(0.1)

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    print(response.json())

    assert response.status_code == 200
    assert len(response.json()["result"]["pending_proof_txs"]) == 1

def test_get_circuits(client):
    data = {
        "id": 0,
        "method": "GET_CIRCUITS",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert len(response.json()["result"]["circuits"]) == 3
