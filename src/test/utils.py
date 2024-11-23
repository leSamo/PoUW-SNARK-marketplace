import subprocess
import sys
import os
import ecdsa
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

client_program = os.path.join(os.path.dirname(__file__), "..", "client.py")

class MockClient:
    __process = None

    def __init__(self, arguments = ""):
        self.__process = subprocess.Popen(
            f'python {client_program} {arguments}',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True, # text mode instead of binary mode for input/output
            bufsize=1  # line buffering
        )

    def __del__(self):
        self.close_stdin()

    def return_code(self):
        self.__process.wait()
        return self.__process.returncode

    def stdout_blocking(self):
        os.set_blocking(self.__process.stdout.fileno(), True)

        return self.__process.stdout.read()

    def stdout(self):
        time.sleep(0.2)

        os.set_blocking(self.__process.stdout.fileno(), False)

        return self.__process.stdout.read()

    def stdin(self, string):
        self.__process.stdin.write(string)
        self.__process.stdin.flush()

    def close_stdin(self):
        self.__process.stdin.close()

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)

        return private_key
