# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import sys
import os
import time
import hashlib

verbose_logging = False
enable_colors = True

class Color:
    def RED():
        return '\033[31m' if enable_colors else ''

    def GREEN():
        return '\033[32m' if enable_colors else ''

    def YELLOW():
        return '\033[33m' if enable_colors else ''

    def BLUE():
        return '\033[34m' if enable_colors else ''

    def PURPLE():
        return '\033[35m' if enable_colors else ''

    def BOLD():
        return '\033[1m' if enable_colors else ''

    def RESET():
        return '\033[0m' if enable_colors else ''

def vprint(*args, **kwargs):
    """ Print with verbose priority """
    if verbose_logging:
        print(f"{Color.PURPLE()}VERBOSE:{Color.RESET()}", *args, file=sys.stdout, **kwargs)

def iprint(*args, **kwargs):
    """ Print with info priority """
    print(f"{Color.BLUE()}INFO:{Color.RESET()}", *args, file=sys.stdout, **kwargs)

def eprint(*args, **kwargs):
    """ Print with error priority """
    print(f"{Color.RED()}ERROR:{Color.RESET()}", *args, file=sys.stdout, **kwargs)

def wprint(*args, **kwargs):
    """ Print with warning priority """
    print(f"{Color.YELLOW()}WARN:{Color.RESET()}", *args, file=sys.stdout, **kwargs)

class Command:
    # request-response commands
    GET_PEERS = 'GET_PEERS'
    PEERS = 'PEERS'
    GET_LATEST_BLOCK_ID = 'GET_LATEST_BLOCK_ID'
    LATEST_BLOCK_ID = 'LATEST_BLOCK_ID'
    GET_BLOCK = 'GET_BLOCK'
    BLOCK = 'BLOCK'
    GET_PENDING_COIN_TXS = 'GET_PENDING_COIN_TXS'
    PENDING_COIN_TXS = 'PENDING_COIN_TXS'
    GET_PENDING_PROOF_TXS = 'GET_PENDING_PROOF_TXS'
    PENDING_PROOF_TXS = 'PENDING_PROOF_TXS'

    # broadcast commands
    BROADCAST_BLOCK = 'BROADCAST_BLOCK'
    BROADCAST_PENDING_COIN_TX = 'BROADCAST_PENDING_COIN_TX'
    BROADCAST_PENDING_PROOF_TX = 'BROADCAST_PENDING_PROOF_TX'

def get_current_time():
    return round(time.time() * 1000)

def validate_address(address):
    if type(address) != bytes: raise TypeError("Invalid address type, only address of bytes type is permitted")
    if len(address) != 33: raise ValueError("Invalid address size, expected length of 33 bytes")

def validate_hash(hash):
    if type(hash) != bytes: raise TypeError("Invalid hash type, only hash of bytes type is permitted")
    if len(hash) != 32: raise ValueError("Invalid hash size, expected length of 32 bytes")

def find_files_with_extension(folder, extension):
    result = []
    for file in os.listdir(folder):
        if file.endswith(extension):
            result.append(file)

    return result

def get_file_hash(filename : str) -> str:
    hasher = hashlib.new('sha256')

    with open(filename, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hasher.update(chunk)

    return hasher.hexdigest()
