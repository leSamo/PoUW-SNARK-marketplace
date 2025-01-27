# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ####################################################################################################

import socket
import json
import hashlib

import util
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction
from block import Block
from state_tree import StateTree
from peer import Peer
from bind_zokrates import Zokrates

port = 12346

peers = []
circuits = None

pending_coin_transactions : list[CoinTransaction] = []
pending_proof_transactions : list[ProofTransaction] = []

partial_block_coin_transactions : list[CoinTransaction] = []
partial_block_proof_transactions : list[ProofTransaction] = []

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
    global peers

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

def setup_circuits():
    global circuits

    circuits = Zokrates.prepare_circuits()
    print(circuits)

def accept_peers(received_peers : list[Peer]):
    global peers

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

def receive_pending_coin_transactions(pending_txs_obj):
    for tx in pending_txs_obj:
        new_tx = CoinTransaction()
        new_tx.decode(tx)

        if new_tx.get_id() not in [t.get_id() for t in pending_coin_transactions]:
            pending_coin_transactions.append(new_tx)
            util.vprint(f"Accepted pending coin tx with id {new_tx.get_id()}")

def receive_pending_proof_transactions(pending_txs_obj):
    for tx in pending_txs_obj:
        new_tx = ProofTransaction()
        new_tx.decode(tx)

        if new_tx.get_id() not in [t.get_id() for t in pending_proof_transactions]:
            pending_proof_transactions.append(new_tx)
            util.vprint(f"Accepted pending proof tx with id {new_tx.get_id()}")

# broadcast newly created coin transaction to the network
def broadcast_pending_coin_transaction(tx : CoinTransaction, sender : str = ''):
    assert tx.is_signed(), "Unsigned coin transactions cannot be broadcast"

    pending_coin_transactions.append(tx)

    message = { 'tx': tx.encode() }

    for peer in peers:
        if peer.to_string() != sender:
            send_message(peer.to_tuple(), util.Command.BROADCAST_PENDING_COIN_TX, message)

# broadcast newly created coin transaction to the network
def broadcast_pending_proof_transaction(tx : CoinTransaction, sender : str = ''):
    assert tx.is_signed(), "Unsigned proof transactions cannot be broadcast"

    pending_proof_transactions.append(tx)

    message = { 'tx': tx.encode() }

    for peer in peers:
        if peer.to_string() != sender:
            send_message(peer.to_tuple(), util.Command.BROADCAST_PENDING_PROOF_TX, message)

# broadcast newly generated block to the network
def broadcast_block(block : Block, sender : str = '') -> None:
    blockchain.append(block)

    message = { 'block': block.encode() }

    for peer in peers:
        if peer.to_string() != sender:
            send_message(peer.to_tuple(), util.Command.BROADCAST_BLOCK, message)

def get_pending_block_integrity(state_tree : StateTree) -> str:
    integrity = state_tree.get_hash()

    for tx in partial_block_coin_transactions:
        integrity += tx.get_integrity()

    for tx in partial_block_proof_transactions:
        integrity += tx.get_integrity()

    return str(int(hashlib.sha256(integrity).digest().hex()[4:], 16))

def get_block_integrity(block : Block) -> str:
    integrity = block.get_body().hash_state_tree()

    for tx in block.get_body().get_coin_txs():
        integrity += tx.get_integrity()

    for tx in block.get_body().get_proof_txs():
        integrity += tx.get_integrity()

    return str(int(hashlib.sha256(integrity).digest().hex()[4:], 16))
