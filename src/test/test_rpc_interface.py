import subprocess
import os
import sys
import time
import requests
import json

from utils import Client

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

client_program = os.path.join(os.path.dirname(__file__), "..", "client.py")

def test_rpc_interface():
    config = os.path.join(os.path.dirname(__file__), "misc/config/1_peer.json")
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")

    client = Client(f'-v -p 3333 -f {config} -k {private_key} -r 9545 -c "produce-empty"')

    time.sleep(1)

    data = {
        "id": 1,
        "method": "GET_LATEST_BLOCK_ID",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["latest_id"] == 1

    data = {
        "id": 2,
        "method": "GET_BLOCK",
        "params": [0],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["block"]["header"]["serial_id"] == 0

    data = {
        "id": 2,
        "method": "GET_PENDING_COIN_TXS",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["pending_coin_txs"] == []

    data = {
        "id": 2,
        "method": "GET_PENDING_PROOF_TXS",
        "params": [],
    }

    response = requests.post('http://localhost:9545', data=json.dumps(data))

    assert response.status_code == 200
    assert response.json()["result"]["pending_proof_txs"] == []

