# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

import socket
import json

import util
import config

peers = config.SEED_NODES # list of tuples (IP address, port)
pending_coin_transactions = []
pending_proof_transactions = []

blockchain = [config.genesis_block]

assert len(blockchain) > 0, "Missing genesis block in 'blockchain' variable"

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
def broadcast_block(block):
    # blockchain.append(block)

    for peer in peers:
        try:
            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sending_socket.connect(peer)
            sending_socket.send(json.dumps(block.encode()).encode())

            util.vprint("Successfully sent newly produced block to peer", peer)
        except Exception as e:
            util.vprint("Failed to send newly produced block to peer", peer, '-', e)
            continue
