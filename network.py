# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ❌❌❌❌❌
# ####################################################################################################

peers = []
pending_coin_transactions = []
pending_proof_transactions = []

# called by a client upon joining the network to receive list of pending txs
def get_pending_transactions():
    pass

# answers a client requesting list of pending txs upon the network
def send_pending_transactions():
    pass

# called by a client upon joining the network to get all blocks generated after block id specified in parameter
def get_blockchain(since):
    pass

# broadcast newly generated block to the network
def submit_block():
    pass
