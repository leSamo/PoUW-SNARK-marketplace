# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️✔️❌
# ####################################################################################################

import sys

verbose_logging = False

class Colors:
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
        print(f"{Colors.PURPLE}VERBOSE:{Colors.RESET}", *args, file=sys.stdout, **kwargs)

def iprint(*args, **kwargs):
    """ Print with info priority """
    print(f"{Colors.BLUE}INFO:{Colors.RESET}", *args, file=sys.stdout, **kwargs)

def eprint(*args, **kwargs):
    """ Print with error priority """
    print(f"{Colors.RED}ERROR:{Colors.RESET}", *args, file=sys.stdout, **kwargs)
