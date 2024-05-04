# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️❌❌❌❌
# ####################################################################################################

import socket
import json

import util
from coin_tx import CoinTransaction
from block import Block
from state_tree import StateTree
from peer import Peer

port = 12346

peers = []
pending_coin_transactions = []
pending_proof_transactions = []

config = None

blockchain = None
self_ip_address = None

def setup_config(filepath : str):
    global config, blockchain, self_ip_address

    with open(filepath, 'r') as file:
        json_data = json.load(file)

    config = json_data

    genesis_block = Block()
    genesis_block.decode(config['genesis_block'])

    blockchain = [genesis_block]
    self_ip_address = config['self_ip_address']

    assert len(blockchain) > 0, "Missing genesis block in 'blockchain' variable"

def setup_peers():
    global port, peers

    for peer_str in config['seed_nodes']:
        if peer_str == f"{config['self_ip_address']}:{port}":
            continue

        peerObj = Peer()
        peerObj.setup_from_string(peer_str)

        if peer_str not in [p.to_string() for p in peers]:
            peers.append(peerObj)

        if len(peers) >= config['max_peer_count']:
            break

        send_message(peerObj.to_tuple(), util.Command.GET_PEERS)

def accept_peers(received_peers : list[Peer]):
    global port, peers

    if len(peers) >= config['max_peer_count']:
        return

    for peer_str in received_peers:
        if peer_str == f"{config['self_ip_address']}:{port}":
            continue

        peerObj = Peer()
        peerObj.setup_from_string(peer_str)

        if peer_str not in [p.to_string() for p in peers]:
            util.vprint(f"Accepting peer {peer_str}")
            peers.append(peerObj)

            if len(peers) >= config['max_peer_count']:
                return

            send_message(peerObj.to_tuple(), util.Command.GET_PEERS)      

def send_message(receiver, command, message = {}):
    global port

    try:
        sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sending_socket.connect(receiver)

        sending_socket.send(json.dumps({
            'command': command,
            'port': port,
            **message
        }).encode())

        util.vprint(f"Successfully sent message {command} to peer {receiver}")
    except Exception as error:
        util.vprint(f"Failed to send message {command} to peer {receiver} - {error}")
        # TODO: consider removing stale peers after N unsuccessful connections

# called by a client upon joining the network to receive list of pending txs
def get_pending_transactions():
    pass

# answers a client requesting list of pending txs upon the network

# broadcast newly created coin transaction to the network
def broadcast_pending_coin_transaction(tx : CoinTransaction):
    global peers

    assert tx.is_signed(), "Unsigned coin transactions cannot be broadcast"

    pending_coin_transactions.append(tx)

    message = { 'tx': tx.encode() }

    for peer in peers:
        send_message(peer.to_tuple(), util.Command.BROADCAST_PENDING_COIN_TX, message)

# called by a client upon joining the network to get all blocks generated after block id specified in parameter
def get_blockchain(since):
    pass

# broadcast newly generated block to the network
def broadcast_block(block : Block) -> None:
    global peers

    blockchain.append(block)

    # TODO: Verify block before broadcasting

    message = { 'block': block.encode() }

    for peer in peers:
        send_message(peer.to_tuple(), util.Command.BROADCAST_BLOCK, message)

def verify_coin_transaction(tx : CoinTransaction, st : StateTree) -> bool:
    try:
        # TODO: assert sender funds are sufficient

        # TODO: update state tree

        return True, st
    except Exception:
        return False, st

def verify_block(previous_block : Block, block : Block) -> bool:
    try:
        # header verification
        #   serial id verification
        assert(block.get_id() == previous_block.get_id() + 1)
        #   time verification
        assert(block.get_timestamp() <= util.get_current_time() + config['time_difference_tolerance'])
        assert(previous_block.get_timestamp() <= block.get_timestamp())

        #   TODO: difficulty verification

        #   previous hash link
        assert(previous_block.get_current_block_hash() == block.get_previous_block_hash())
        #   current hash calculation
        assert(block.verify_hash())

        # TODO: body verification
            # individual coin transaction verification
            # individual proof transaction verification
                # proof verification
                # proof complexity verification
                # difficulty threshold verification
            # state tree verification
                # check if state tree hash matches
                   
        return True
    except Exception:
        return False
