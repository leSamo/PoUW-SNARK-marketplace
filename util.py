# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️❌
# ####################################################################################################

import sys

verbose_logging = False

class Color:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def vprint(*args, **kwargs):    
    """ Print with verbose priority """
    global verbose_logging
    if verbose_logging:
        print(f"{Color.PURPLE}VERBOSE:{Color.RESET}", *args, file=sys.stdout, **kwargs)

def iprint(*args, **kwargs):
    """ Print with info priority """
    print(f"{Color.BLUE}INFO:{Color.RESET}", *args, file=sys.stdout, **kwargs)

def eprint(*args, **kwargs):
    """ Print with error priority """
    print(f"{Color.RED}ERROR:{Color.RESET}", *args, file=sys.stdout, **kwargs)

class Command:
    # request-response commands
    GET_PEERS = 'GET_PEERS'
    PEERS = 'PEERS'
    GET_LATEST_BLOCK_ID = 'GET_LATEST_BLOCK_ID'
    LATEST_BLOCK_ID = 'LATEST_BLOCK_ID'
    GET_BLOCK = 'GET_BLOCK'
    BLOCK = 'BLOCK'
    GET_PENDING_COIN_TXS = 'GET_PENDING_COIN_TXS'
    GET_PENDING_PROOF_TXS = 'GET_PENDING_PROOF_TXS'

    # broadcast commands
    BROADCAST_BLOCK = 'BROADCAST_BLOCK'
    BROADCAST_PENDING_COIN_TX = 'BROADCAST_PENDING_COIN_TX'
    BROADCAST_PENDING_PROOF_TX = 'BROADCAST_PENDING_PROOF_TX'
