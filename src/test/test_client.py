# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import os
import sys
import ecdsa
import subprocess
import socket
import time
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

client_program = os.path.join(os.path.dirname(__file__), "..", "client.py")

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key

def test_help():
    process = subprocess.Popen(f'python {client_program} -h', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert "Usage:" in stdout.decode()
    assert process.returncode == 0

def test_generate_key():
    file = os.path.join(os.path.dirname(__file__), "./abc")

    process = subprocess.Popen(f'python {client_program} -c "generate-key {file}; exit" -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()

    assert process.returncode == 0
    assert os.path.exists(file)

    load_ecdsa_private_key(file)

    os.remove(file)

def test_available_commands():
    process = subprocess.Popen(f'python {client_program} -c "help; exit" -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'Available commands:' in stdout.decode()

def test_verbose():
    process = subprocess.Popen(f'python {client_program} -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'VERBOSE:' in stdout.decode()

    process = subprocess.Popen(f'python {client_program}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'VERBOSE:' not in stdout.decode()

def test_port():
    process = subprocess.Popen(f'python {client_program} -v -p 6464', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.stdin.write("status\n".encode())
    process.stdin.flush()

    time.sleep(0.1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', 6464))
        assert result == 0

    process.stdin.write("exit\n".encode())
    process.stdin.flush()
    stdout, _ = process.communicate()
    process.stdin.close()
    process.wait()

    assert process.returncode == 0

def test_initial_peer_discovery():
    process3333 = subprocess.Popen(f'python {client_program} -v -p 3333 -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(0.3)
    process1111 = subprocess.Popen(f'python {client_program} -v -p 1111 -f {os.path.join(os.path.dirname(__file__), "misc/config/1_peer.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(0.3)
    process1111.stdin.write("status\n".encode())
    process1111.stdin.flush()

    process3333.stdin.write("exit\n".encode())
    process3333.stdin.flush()

    process1111.stdin.write("exit\n".encode())
    process1111.stdin.flush()

    stdout1111, _ = process1111.communicate()

    pattern = r"Peers \((\d+)\):"

    match = re.search(pattern, stdout1111.decode())
    peer_count = int(match.group(1))

    assert peer_count == 2
    assert "127.0.0.1:2222" in stdout1111.decode()
    assert "127.0.0.1:3333" in stdout1111.decode()

def test_initial_block_discovery():
    process2222 = subprocess.Popen(f'python {client_program} -v -p 2222 -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")} -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -c "produce-empty"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(0.3)

    process3333 = subprocess.Popen(f'python {client_program} -v -p 3333 -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(1)

    process3333.stdin.write("status\n".encode())
    process3333.stdin.flush()

    time.sleep(0.3)

    stdout3333, _ = process3333.communicate()

    pattern = r"Latest block:\033\[0m [0-9a-f]{6}… \(id (\d+)\)"

    match = re.search(pattern, stdout3333.decode())
    latest_block_id = int(match.group(1))

    assert latest_block_id == 1

    process2222.stdin.close()
    process3333.stdin.close()

def test_initial_tx_discovery():
    process2222 = subprocess.Popen(f'python {client_program} -v -p 2222 -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")} -c "send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50; status"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(0.3)

    process3333 = subprocess.Popen(f'python {client_program} -v -p 3333 -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(1)

    stdout2222, _ = process2222.communicate()

    assert "Pending coin transactions (1)" in stdout2222.decode()

    process3333.stdin.write("status\n".encode())
    process3333.stdin.flush()

    stdout3333, _ = process3333.communicate()

    assert "Pending coin transactions (1)" in stdout3333.decode()

def test_balance():
    process = subprocess.Popen(f'python {client_program} -p 2222 -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -c "balance; balance 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2; balance 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000; exit"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    stdout, _ = process.communicate()

    pattern = r"Current balance \(block \d+\): (\d+)"

    balances = re.findall(pattern, stdout.decode())

    assert int(balances[0]) == 1000
    assert int(balances[1]) == 1000
    assert int(balances[2]) == 0

def test_inspect():
    process = subprocess.Popen(f'python {client_program} -p 2222 -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -c "inspect 0; exit"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    stdout, _ = process.communicate()

    block_id = int(re.findall(r'Block (\d+):', stdout.decode())[0])
    timestamp = int(re.findall(r'Timestamp:\033\[0m (\d+)', stdout.decode())[0])
    difficulty = int(re.findall(r'Difficulty:\033\[0m (\d+)', stdout.decode())[0])
    block_hash = re.findall(r'Current block hash:\033\[0m ([0-9a-z]+)', stdout.decode())[0]

    assert block_id == 0
    assert timestamp == 1714436126662
    assert difficulty == 1
    assert block_hash == '6936414ccf1b1df9937d3a6ca1980c8f6571b10603a9e4d2ffde506a6fb8fc1f'

def test_not_auth():
    process = subprocess.Popen(f'python {client_program} -p 2222 -v', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    process.stdin.write("send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50\n".encode())
    process.stdin.flush()

    process.stdin.write(f"auth {os.path.join(os.path.dirname(__file__), 'misc/private_key')}\n".encode())
    process.stdin.flush()

    process.stdin.write("send 0008b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f000 50\nexit\n".encode())
    process.stdin.flush()

    time.sleep(0.5)

    process.wait()
    stdout, _ = process.communicate()

    assert "This command requires authentication" in stdout.decode()
    assert "Private key file loaded successfully" in stdout.decode()
    assert "Successfully created and broadcasted coin transaction" in stdout.decode()

def test_auth():
    process = subprocess.Popen(f'python {client_program} -p 2222', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    process.stdin.write(f"auth {os.path.join(os.path.dirname(__file__), 'misc/private_key')}\n".encode())
    process.stdin.flush()

    stdout, _ = process.communicate()

    assert "Private key file was not provided, running in anonymous mode" in stdout.decode()

    assert "Private key file loaded successfully" in stdout.decode()
    assert "Your address: 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2" in stdout.decode()

def test_partial_block():
    process = subprocess.Popen(f'python {client_program} -p 2222 -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -c "send 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f0 50; select-coin-tx 0; partial; exit"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    process.wait()
    stdout, _ = process.communicate()

    assert "Selected coin transactions (1)" in stdout.decode()

# test coin tx creation, proof tx creation from client A; confirmation and block generation by client B
def test_block_construction():
    CREATE_COIN_TX = "send 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f0 50"
    CREATE_PROOF_TX = "request-proof 00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee 2 3 6"

    requesting_process = subprocess.Popen(f'python {client_program} -p 2222 -k {os.path.join(os.path.dirname(__file__), "misc/private_key")} -v -c "{CREATE_COIN_TX}; {CREATE_PROOF_TX}"', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    miner_process = subprocess.Popen(f'python {client_program} -p 3333 -v -k {os.path.join(os.path.dirname(__file__), "misc/private_key")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # wait for miner to sync up
    time.sleep(1)

    miner_process.stdin.write(f"select-coin-tx 0\n".encode())
    miner_process.stdin.flush()

    miner_process.stdin.write(f"select-proof-tx 0\n".encode())
    miner_process.stdin.flush()

    miner_process.stdin.write(f"produce-block\n".encode())
    miner_process.stdin.flush()

    # wait for requester to sync up
    time.sleep(1)

    requesting_process.stdin.write(f"status\nexit\n".encode())
    requesting_process.stdin.flush()

    requesting_process.wait()
    stdout, _ = requesting_process.communicate()

    print(stdout.decode())

    miner_process.stdin.write("exit\n".encode())
    miner_process.stdin.flush()

    # check if latest block has id of 1
    assert "(id 1)" in stdout.decode()
