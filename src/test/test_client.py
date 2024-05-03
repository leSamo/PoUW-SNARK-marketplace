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

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key
    
def test_generate_key():
    file = os.path.join(os.path.dirname(__file__), "./abc")

    process = subprocess.Popen(f'python src/client.py -c "generate-key {file}; exit" -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    stdout, _ = process.communicate()

    assert process.returncode == 0
    assert os.path.exists(file)

    load_ecdsa_private_key(file)

    os.remove(file)
