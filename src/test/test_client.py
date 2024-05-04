# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import os
import sys
import ecdsa
import subprocess
import socket
import time
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key

def test_help():
    process = subprocess.Popen(f'python src/client.py -h', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert "Usage:" in stdout.decode()
    assert process.returncode == 0

def test_generate_key():
    file = os.path.join(os.path.dirname(__file__), "./abc")

    process = subprocess.Popen(f'python src/client.py -c "generate-key {file}; exit" -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()

    assert process.returncode == 0
    assert os.path.exists(file)

    load_ecdsa_private_key(file)

    os.remove(file)

def test_available_commands():
    process = subprocess.Popen(f'python src/client.py -c "help; exit" -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'Available commands:' in stdout.decode()

def test_verbose():
    process = subprocess.Popen(f'python src/client.py -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'VERBOSE:' in stdout.decode()

    process = subprocess.Popen(f'python src/client.py', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert 'VERBOSE:' not in stdout.decode()    

def test_port():
    process = subprocess.Popen(f'python src/client.py -v -p 6464', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.stdin.write("status\n".encode())
    process.stdin.flush()

    time.sleep(0.1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', 6464))
        assert result == 0

    process.stdin.write("exit\n".encode())
    process.stdin.flush()
    stdout, _ = process.communicate()
    process.stdin.close()
    process.wait()

    assert process.returncode == 0


def test_initial_peer_discovery():
    process3333 = subprocess.Popen(f'python src/client.py -v -p 3333 -f {os.path.join(os.path.dirname(__file__), "misc/config/2_peers.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(0.3)
    process1111 = subprocess.Popen(f'python src/client.py -v -p 1111 -f {os.path.join(os.path.dirname(__file__), "misc/config/1_peer.json")}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(0.3)
    process1111.stdin.write("status\n".encode())
    process1111.stdin.flush()

    process3333.stdin.write("exit\n".encode())
    process3333.stdin.flush()

    process1111.stdin.write("exit\n".encode())
    process1111.stdin.flush()

    stdout1111, _ = process1111.communicate()

    pattern = r"Connected peers \((\d+)\):"

    # Search for the pattern in the text
    match = re.search(pattern, stdout1111.decode())
    peer_count = int(match.group(1))

    print(stdout1111.decode())

    assert peer_count == 2
    assert "localhost:2222" in stdout1111.decode()
    assert "localhost:3333" in stdout1111.decode()
