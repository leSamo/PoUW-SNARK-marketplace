# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import os
import sys
import subprocess
import socket
import time
import re

# TODO: Kill all ports from previous test runs

from utils import Client, load_ecdsa_private_key

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def test_help():
    client = Client('-h')

    assert "Usage:" in client.stdout()
    assert client.return_code() == 0

def test_generate_key():
    file = os.path.join(os.path.dirname(__file__), "./abc")

    client = Client(f'-c "generate-key {file}; exit"')

    assert client.return_code() == 0
    assert os.path.exists(file)

    load_ecdsa_private_key(file)

    os.remove(file)

def test_available_commands():
    client = Client('-c "help; exit"')

    assert client.return_code() == 0
    assert 'Available commands:' in client.stdout()

def test_verbose():
    client = Client('-v -c "exit"')

    assert client.return_code() == 0
    assert 'VERBOSE:' in client.stdout()

    client = Client()

    client.stdin("verbose on\n")

    assert 'Enabled verbose logging' in client.stdout()

    client.stdin("verbose off\n")
    client.stdin("exit\n")

    assert 'Disabled verbose logging' in client.stdout()
    assert client.return_code() == 0

def test_port():
    client = Client(f'-p 6464 -c "status"')

    time.sleep(0.1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', 6464))
        assert result == 0

    client.stdin("exit\n")
    assert client.return_code() == 0

def test_initial_peer_discovery():
    config3333 = os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")
    config1111 = os.path.join(os.path.dirname(__file__), "misc/config/1_peer.json")

    client3333 = Client(f'-p 3333 -f {config3333}')
    time.sleep(0.3)
    client1111 = Client(f'-p 1111 -f {config1111}')
    time.sleep(0.3)

    client1111.stdin("status\n")
    client3333.stdin("exit\n")
    client1111.stdin("exit\n")

    pattern = r"Peers \((\d+)\):"

    output = client1111.stdout()

    assert "127.0.0.1:2222" in output
    assert "127.0.0.1:3333" in output

    match = re.search(pattern, output)
    peer_count = int(match.group(1))

    assert peer_count == 2

def test_initial_block_discovery():
    config = os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")

    client2222 = Client(f'-p 2222 -f {config} -k {private_key} -c "produce-empty"')

    time.sleep(0.3)

    client3333 = Client(f'-p 3333 -f {config}')

    time.sleep(1)

    client3333.stdin("status\n")

    time.sleep(0.3)

    pattern = r"Latest block:\033\[0m [0-9a-f]{6}… \(id (\d+)\)"

    match = re.search(pattern, client3333.stdout())
    latest_block_id = int(match.group(1))

    assert latest_block_id == 1

def test_initial_tx_discovery():
    config = os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")
    send_command = "send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50"

    client2222 = Client(f'-p 2222 -k {private_key} -f {config} -c "{send_command}; status"')

    time.sleep(0.3)

    client3333 = Client(f'-p 3333 -f {config}')

    time.sleep(0.5)

    assert "Pending coin transactions (1)" in client2222.stdout()

    client3333.stdin("status\n")

    assert "Pending coin transactions (1)" in client3333.stdout()

def test_balance():
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")
    balance1_command = "balance 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2"
    balance2_command = "balance 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000"

    client = Client(f'-p 2222 -k {private_key} -c "balance; {balance1_command}; {balance2_command}; exit"')

    pattern = r"Current balance \(block \d+\): (\d+)"

    balances = re.findall(pattern, client.stdout_blocking())

    assert int(balances[0]) == 1000
    assert int(balances[1]) == 1000
    assert int(balances[2]) == 0

def test_inspect():
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")
    client = Client(f'-p 2222 -k {private_key} -c "inspect 0; exit"')

    output = client.stdout_blocking()

    block_id = int(re.findall(r'Block (\d+):', output)[0])
    timestamp = int(re.findall(r'Timestamp:\033\[0m (\d+)', output)[0])
    difficulty = int(re.findall(r'Difficulty:\033\[0m (\d+)', output)[0])
    block_hash = re.findall(r'Current block hash:\033\[0m ([0-9a-z]+)', output)[0]

    assert block_id == 0
    assert timestamp == 1714436126662
    assert difficulty == 1
    assert block_hash == '6936414ccf1b1df9937d3a6ca1980c8f6571b10603a9e4d2ffde506a6fb8fc1f'

def test_not_auth():
    client = Client(f'-p 2222')

    client.stdin("send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50\n")

    client.stdin(f"auth {os.path.join(os.path.dirname(__file__), 'misc/private_key')}\n")

    client.stdin("send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50\nexit\n")

    output = client.stdout_blocking()

    assert "This command requires authentication" in output
    assert "Private key file loaded successfully" in output
    assert "Successfully created and broadcasted coin transaction" in output

def test_auth():
    client = Client(f'-p 2222')

    assert "Private key file was not provided, running in anonymous mode" in client.stdout()

    client.stdin(f"auth {os.path.join(os.path.dirname(__file__), 'misc/private_key')}\n")

    output = client.stdout()

    assert "Private key file loaded successfully" in output
    assert "Your address: 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2" in output

def test_partial_block():
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")
    send_command = "send 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f0 50"

    client = Client(f'-p 2222 -k {private_key} -c "{send_command}; select-coin-tx 0; partial; exit"')

    assert "Selected coin transactions (1)" in client.stdout_blocking()

# test coin tx creation, proof tx creation from client A; confirmation and block generation by client B

def test_block_construction():
    private_key = os.path.join(os.path.dirname(__file__), "misc/private_key")
    coin_tx_command = "send 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f0 50"
    proof_tx_command = "request-proof 00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee 2 3 6"

    requesting_process = Client(f'-p 2222 -k {private_key} -v -c "{coin_tx_command}; {proof_tx_command}"')

    miner_process = Client(f'-p 3333 -v -k {private_key}')

    time.sleep(1) # wait for miner to sync up

    miner_process.stdin(f"select-coin-tx 0\n")
    miner_process.stdin(f"select-proof-tx 0\n")
    miner_process.stdin(f"produce-block\n")

    time.sleep(1) # wait for requester to sync up

    requesting_process.stdin(f"status\nexit\n")

    miner_process.stdin("exit\n")

    assert "(id 1)" in requesting_process.stdout() # check if latest block has id of 1
