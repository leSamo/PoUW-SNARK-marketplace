# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️✔️❌❌
# ####################################################################################################

import socket
import threading
import getopt
import sys
import ecdsa
import json
import traceback
import time
import os

import util
import network
from block import Block
from block_body import BlockBody
from block_header import BlockHeader
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction
from bind_zokrates import Zokrates

USAGE = 'Usage: python client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help] [-p|--port <port number>] [-c|--command <command>] [-f|--config <config file>] [-n|--no-color]'
USAGE_ARGUMENTS = """
    -k, --key <private key file>   Authenticate using an existing private key file
    -v, --verbose                  Show more detailed log messages
    -h, --help                     Print this message
    -p, --port <port number>       Open the listening socket on a specific port number
    -c, --command <command>        Run semicolon separated list of commands just after client initialization
    -f, --config <config file>     Provide a non-default configuration file
    -n, --no-color                 Don't print colored text into the terminal
"""

server_running = True
private_key = None

def start_blockchain_sync():
    util.vprint("Synchronization: Looking for peers")

    time.sleep(0.3)

    util.vprint("Synchronization: Searching for longest chain")

    for peer in network.peers:
        network.send_message(peer.to_tuple(), util.Command.GET_LATEST_BLOCK_ID)

    time.sleep(0.3)

    best_peer = None
    best_peer_latest_block_id = 0

    for peer in network.peers:
        if peer.get_latest_block_id() > network.blockchain[-1].get_id():
            best_peer = peer
            best_peer_latest_block_id = peer.get_latest_block_id()

    if best_peer is None:
        util.vprint("Synchronization: Did not find a fresher peer")
    else:
        util.vprint(f"Synchronization: Determined freshest peer: {best_peer.to_string()}")
        util.vprint("Synchronization: Downloading blocks")

        for block_id in range(network.blockchain[-1].get_id() + 1, best_peer_latest_block_id + 1):
            network.send_message(best_peer.to_tuple(), util.Command.GET_BLOCK, { 'block_id': block_id })
            time.sleep(0.2)

def start_pending_tx_sync():
    util.vprint("Synchronization: Retrieving pending transactions")

    time.sleep(0.3)

    for peer in network.peers:
        network.send_message(peer.to_tuple(), util.Command.GET_PENDING_COIN_TXS)
        network.send_message(peer.to_tuple(), util.Command.GET_PENDING_PROOF_TXS)

def receive_incoming(client_socket, client_address):
    # TODO: Consider adding client_address to PEERS if not already
    # TODO: Reputation check

    data = []

    while True:
        received = client_socket.recv(1024)
        if not received:
            break

        data.append(received)

    data =  b''.join(data)

    message = None

    try:
        message = json.loads(data.decode())
    except:
        util.vprint(f"Received a message not in JSON format")
        return

    # Process received data (you can modify this part based on your requirements)
    util.vprint(f"Received from {client_address[0]}:{message['port']}:", json.dumps(message, indent=2))

    # Disregard messages which don't have command and peer fields
    if 'command' not in message or 'port' not in message:
        util.vprint(f"Received a message missing 'command' or 'port' fields")
        return

    # Disregard reply messages if coming from non-peers
    if message['command'] in [util.Command.PEERS, util.Command.LATEST_BLOCK_ID, util.Command.BLOCK, util.Command.PENDING_COIN_TXS, util.Command.PENDING_PROOF_TXS] and f"{client_address[0]}:{message['port']}" not in [peer.to_string() for peer in network.peers]:
        util.vprint(f"Received reply message from {client_address[0]}:{message['port']} which is not a peer")
        return

    if message['command'] == util.Command.GET_PEERS:
        util.vprint("Sending peers")
        network.send_message((client_address[0], message['port']), util.Command.PEERS, { 'peers': [peer.to_string() for peer in network.peers] + [f'{network.self_ip_address}:{network.port}'] })

    elif message['command'] == util.Command.PEERS:
        network.accept_peers(message['peers'])

    elif message['command'] == util.Command.GET_BLOCK:
        if type(message['block_id']) != int:
            util.vprint("Received request for non-int block id")
            return

        if message['block_id'] >= len(network.blockchain):
            util.vprint("Received request for block id which is too high")
            return

        util.vprint(f"Sending block {message['block_id']}")

        network.send_message((client_address[0], message['port']), util.Command.BLOCK, { 'block': network.blockchain[message['block_id']].encode() })

    elif message['command'] == util.Command.PENDING_COIN_TXS:
        network.receive_pending_coin_transactions(message['pending_txs'])

    elif message['command'] == util.Command.GET_PENDING_COIN_TXS:
        util.vprint(f"Sending pending coin txs")

        network.send_message((client_address[0], message['port']), util.Command.PENDING_COIN_TXS, { 'pending_txs': [tx.encode() for tx in network.pending_coin_transactions] })

    elif message['command'] == util.Command.PENDING_PROOF_TXS:
        network.receive_pending_proof_transactions(message['pending_txs'])

    elif message['command'] == util.Command.GET_PENDING_PROOF_TXS:
        util.vprint(f"Sending pending proof txs")

        network.send_message((client_address[0], message['port']), util.Command.PENDING_PROOF_TXS, { 'pending_txs': [tx.encode() for tx in network.pending_proof_transactions] })

    elif message['command'] == util.Command.BLOCK:
        # TODO: verify block
        received_block = Block()
        received_block.decode(message['block'])

        if network.verify_block(network.blockchain[-1], received_block):
            network.blockchain.append(received_block)
            util.vprint("Received valid block")
        else:
            util.vprint("Received invalid block")
            return

    elif message['command'] == util.Command.BROADCAST_BLOCK:
        new_block = Block()
        new_block.decode(message['block'])

        # TODO: verify block

        if new_block.get_id() != network.blockchain[-1].get_id() + 1:
            util.vprint(f"Received out of order block with id {new_block.get_id()}, expected {network.blockchain[-1].get_id() + 1}")
            return

        network.blockchain.append(new_block)

        # TODO: propagate block to all peers except self and sender

    elif message['command'] == util.Command.BROADCAST_PENDING_COIN_TX:
        new_tx = CoinTransaction()
        new_tx.decode(message['tx'])

        # TODO: verify tx

        network.pending_coin_transactions.append(new_tx)

        # TODO: propagate tx to all peers except self and sender

    elif message['command'] == util.Command.BROADCAST_PENDING_PROOF_TX:
        new_tx = ProofTransaction()
        new_tx.decode(message['tx'])

        # TODO: verify tx

        network.pending_pending_transactions.append(new_tx)

        # TODO: propagate tx to all peers except self and sender

    elif message['command'] == util.Command.GET_LATEST_BLOCK_ID:
        util.vprint(f"Peer {client_address[0]}:{message['port']} is requesting latest block id")
        network.send_message((client_address[0], message['port']), util.Command.LATEST_BLOCK_ID, { 'latest_id': network.blockchain[-1].get_id() })

    elif message['command'] == util.Command.LATEST_BLOCK_ID:
        util.vprint(f"Received latest block id from peer {client_address[0]}:{message['port']}: {message['latest_id']}")

        for peer in network.peers:
            if peer.to_string() == f"{client_address[0]}:{message['port']}":
                peer.set_latest_block_id(message['latest_id'])

    else:
        util.vprint(f"Received unknown message command '{message['command']}' from {client_address[0]}:{message['port']}")

    # Close the connection when done
    client_socket.close()

def start_listener_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((network.self_ip_address, network.port))
    server_socket.listen(5)
    util.vprint(f"Server listening on port {network.port}")

    try:
        while server_running:
            client_socket, client_address = server_socket.accept()

            if server_running:
                util.vprint("Connection established.")

            # Start a new thread to handle the client connection
            client_thread = threading.Thread(target=receive_incoming, args=(client_socket, client_address))
            client_thread.start()
    except:
        util.eprint("Server socket failed")

def load_ecdsa_private_key(filename):
    with open(filename, "r") as key_file:
        key_str = key_file.read()
        private_key = ecdsa.SigningKey.from_pem(key_str)
        return private_key

def generate_key(filename):
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

    private_key_pem = private_key.to_pem()

    with open(filename, "wb") as f:
        f.write(private_key_pem)

    util.iprint("Generated address", private_key.get_verifying_key().to_string('compressed').hex())
    util.iprint(f"Private key saved to the file '{filename}'")

def main(argv):
    global server_running, verbose_logging, private_key

    try:
        opts, args = getopt.getopt(argv, "hvk:p:c:f:n", ["help", "verbose", "key=", "port=", "command=", "config=", "no-color"])
    except getopt.GetoptError:
        print(USAGE)
        print(USAGE_ARGUMENTS)
        sys.exit(-1)

    cli_commands = []
    config_file = os.path.join(os.path.dirname(__file__), "config.json")

    if ('-n', '') in opts or ('--no-color', '') in opts:
        util.vprint("Disabled colors in the terminal")
        util.enable_colors = False

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(USAGE)
            print(USAGE_ARGUMENTS)
            sys.exit()
        elif opt in ['-v', '--verbose']:
            util.iprint("Enabled verbose logging")
            util.verbose_logging = True
        elif opt in ['-k', '--key']:
            try:
                private_key = load_ecdsa_private_key(arg)
            except e:
                util.eprint("Failed to load private key file:", e)
                sys.exit(-1)
        elif opt in ['-p', '--port']:
            network.port = int(arg)
        elif opt in ['-c', '--command']:
            cli_commands = arg.split(";")
        elif opt in ['-f', '--config']:
            config_file = arg

    Zokrates.check_version()

    network.setup_config(config_file)

    if private_key is None:
        util.iprint("Private key file was not provided, running in anonymous mode -- transactions cannot be created")
    else:
        util.iprint("Private key file loaded successfully")
        util.iprint(f"Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")

    server_thread = threading.Thread(target=start_listener_socket)
    server_thread.start()

    time.sleep(0.1)

    network.setup_peers()

    block_sync_thread = threading.Thread(target=start_blockchain_sync)
    block_sync_thread.start()

    pending_tx_sync_thread = threading.Thread(target=start_pending_tx_sync)
    pending_tx_sync_thread.start()

    circuits = Zokrates.prepare_circuits()

    # prevent 'terminating' (exit) socket being open before 'server' socket
    if len(cli_commands) > 0:
        time.sleep(0.1)

    while True:
        try:
            if len(cli_commands) > 0:
                command = cli_commands.pop(0).strip()
            else:
                command = input().strip()
        except:
            command = "exit"

        if command == "exit":
            server_running = False

            try:
                terminating_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                terminating_socket.connect((network.self_ip_address, network.port))
            except:
                util.eprint("Failed to open terminating socket")

            break

        elif command == "help":
            # TODO: Autoproduce block
            print()
            print(f"{util.Color.YELLOW()}{util.Color.BOLD()}Available commands:{util.Color.RESET()}")
            print(f"  {util.Color.YELLOW()}verbose <on|off>{util.Color.RESET()} -- toggles verbose logging")
            print(f"  {util.Color.YELLOW()}exit{util.Color.RESET()} -- terminates client")
            print(f"  {util.Color.YELLOW()}send <receiver address> <amount>{util.Color.RESET()} -- create a coin transaction and submit it to the network")
            print(f"  {util.Color.YELLOW()}request-proof <circuit hash> <parameters>{util.Color.RESET()} -- request a proof to be generated")
            print(f"  {util.Color.YELLOW()}📝 produce-proof <proof index>{util.Color.RESET()} -- manually produce a proof and include it in partial block")
            print(f"  {util.Color.YELLOW()}confirm-coin-tx <coin tx index>{util.Color.RESET()} -- manually confirm a coin transaction and include it in partial block")
            print(f"  {util.Color.YELLOW()}partial{util.Color.RESET()} -- print information about currently produced partial block")
            print(f"  {util.Color.YELLOW()}📝 produce-block{util.Color.RESET()} -- finish and broadcast current block")
            print(f"  {util.Color.YELLOW()}generate-key <output file>{util.Color.RESET()} -- generate SECP256k1 private key and save it in <output file> in PEM format")
            print(f"  {util.Color.YELLOW()}inspect <block id>{util.Color.RESET()} -- print information about block with <block id>")
            print(f"  {util.Color.YELLOW()}status{util.Color.RESET()} -- print current status of the network")
            print(f"  {util.Color.YELLOW()}produce-empty{util.Color.RESET()} -- produces an empty dummy block and broadcasts it to the network")
            print(f"  {util.Color.YELLOW()}auth <private key file>{util.Color.RESET()} -- switches from anonymous mode to authenticated mode")
            print(f"  {util.Color.YELLOW()}balance [<address>]{util.Color.RESET()} -- prints current (latest known block) balance of <address> or self if authenticated and <address> is not provided")
            print(f"  {util.Color.YELLOW()}logout{util.Color.RESET()} -- switches to non-authenticated mode")
            print()

        elif command == "verbose on":
            util.iprint("Enabled verbose logging")
            util.verbose_logging = True

        elif command == "verbose off":
            util.iprint("Disabled verbose logging")
            util.verbose_logging(False)

        elif command.split(" ")[0] == "confirm-coin-tx":
            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue

            if len(command.split(" ")) != 2:
                if private_key is None:
                    util.eprint("Usage: confirm-coin-tx <coin tx index>")
                    continue

            try:
                proof_index = int(command.split(" ")[1])
            except ValueError:
                util.eprint("Usage: confirm-coin-tx <coin tx index>")
                continue

            if proof_index >= len(network.pending_coin_transactions):
                util.eprint("Coin transaction index out of bounds")
                continue

            tx = network.pending_coin_transactions[proof_index]

            if tx.get_id() in [t.get_id() for t in network.partial_block_coin_transactions]:
                util.eprint("The coin transaction is already confirmed in the current partial block")
                continue
            else:
                if tx.verify_transaction():
                    network.partial_block_coin_transactions.append(tx)
                    util.iprint("Successfully included the coin transaction")
                else:
                    util.eprint("The coin transaction is invalid")
                    continue

        elif command == "partial":
            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue

            print()
            print(f"{util.Color.YELLOW()}{util.Color.BOLD()}Currently produced partial block status:{util.Color.RESET()}")

            if len(network.partial_block_coin_transactions) == 0 and len(network.partial_block_proof_transactions):
                print(f"  {util.Color.YELLOW()}There is no partical block being produced -- use the 'produce-proof' command to start producing block{util.Color.RESET()}")
            else:
                if len(network.partial_block_proof_transactions) == 0:
                    print(f"  {util.Color.YELLOW()}No confirmed proof transactions{util.Color.RESET()}")
                else:
                    print(f"  {util.Color.YELLOW()}Generated proofs ({len(network.partial_block_proof_transactions)}):{util.Color.RESET()}")
                    for tx in network.partial_block_proof_transactions:
                        # TODO: Highlight stale proofs
                        print(f"    - {tx}")

                if len(network.partial_block_coin_transactions) == 0:
                    print(f"  {util.Color.YELLOW()}No confirmed coin transactions{util.Color.RESET()}")
                else:
                    print(f"  {util.Color.YELLOW()}Confirmed coin transactions ({len(network.partial_block_coin_transactions)}):{util.Color.RESET()}")
                    for tx in network.partial_block_coin_transactions:
                        # TODO: Highlight stale proofs
                        print(f"    - {tx}")

        elif command.split(" ")[0] == "produce-proof":
            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue

            if len(command.split(" ")) != 2:
                if private_key is None:
                    util.eprint("Usage: produce-proof <proof index>")
                    continue

            try:
                proof_index = int(command.split(" ")[1])
            except ValueError:
                util.eprint("Usage: produce-proof <proof index>")
                continue

            if proof_index >= len(network.pending_proof_transactions):
                util.eprint("Proof transaction index out of bounds")
                continue

            tx = network.pending_proof_transactions[proof_index]

            if tx.get_id() in [t.get_id() for t in network.partial_block_proof_transactions]:
                util.eprint("The proof transaction is already confirmed in the current partial block")
                continue
            else:
                if tx.verify_transaction():
                    # TODO: Check if exists in circuits dict
                    proof = Zokrates.generate_proof(circuits[tx.get_circuit_hash()], tx.get_parameters())
                    # TODO: tx.set_proof() ???
                    # TODO: Recalc hash???
                    network.partial_block_proof_transactions.append(tx)
                    util.iprint("Successfully included the proof transaction")
                else:
                    util.eprint("The proof transaction is invalid")
                    continue


            # Zokrates.produce_proof and remember it in current partial block

        elif command.split(" ")[0] == 'balance':
            latest_block = network.blockchain[-1]

            if len(command.split(" ")) == 1:
                if private_key is None:
                    util.eprint("Either authenticate to list current self balance, or use 'balance <address>'")
                    continue

                sender_address = bytes.fromhex(private_key.get_verifying_key().to_string('compressed').hex())
                current_sender_balance = latest_block.get_state_tree().get(sender_address)

                print(f"Current balance (block {latest_block.get_id()}): {current_sender_balance}")

            elif len(command.split(" ")) == 2:
                current_sender_balance = latest_block.get_state_tree().get(bytes.fromhex(command.split(" ")[1]))

                print(f"Current balance (block {latest_block.get_id()}): {current_sender_balance}")

            else:
                util.eprint("Usage: balance [<address>]")

        elif command.split(" ")[0] == 'generate-key':
            if len(command.split(" ")) != 2:
                util.eprint("Usage: generate-key <output file>")
                continue

            generate_key(command.split(" ")[1])

        elif command.split(" ")[0] == 'send':
            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue

            if len(command.split(" ")) != 3:
                util.eprint("Usage: send <receiver address> <amount>")
                continue

            # TODO: check if funds are sufficient
            latest_block = network.blockchain[-1]
            sender_address = bytes.fromhex(private_key.get_verifying_key().to_string('compressed').hex())
            current_sender_balance = latest_block.get_state_tree().get(sender_address) or 0

            util.validate_address(sender_address)

            try:
                receiver_address = bytes.fromhex(command.split(" ")[1])
                amount = int(command.split(" ")[2])

                assert current_sender_balance >= amount, "Insufficient sender balance"

                new_tx = CoinTransaction()
                new_tx.setup(sender_address, receiver_address, amount)

                new_tx.sign(private_key)

                network.broadcast_pending_coin_transaction(new_tx)

                util.iprint("Successfully created and broadcasted coin transaction")

            except Exception as e:
                util.eprint("Failed to create pending coin transaction:", e)
                continue

        elif command.split(" ")[0] == 'request-proof':
            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue

            if len(command.split(" ")) != 3:
                # TODO: Quote parameters?
                util.eprint("Usage: request-proof <circuit hash> <parameters>")
                continue

            # TODO: check if funds are sufficient
            try:
                sender_address = bytes.fromhex(private_key.get_verifying_key().to_string('compressed').hex())
                new_tx = ProofTransaction()
                new_tx.setup(sender_address, bytes.fromhex(command.split(" ")[1]), command.split(" ")[2])

                new_tx.sign(private_key)

                network.broadcast_pending_proof_transaction(new_tx)

                util.iprint("Successfully created and broadcasted proof transaction")
            except Exception as e:
                util.eprint("Failed to create pending proof transaction:", e)
                traceback.print_exc()
                continue

        elif command.split(" ")[0] == 'inspect':
            if len(command.split(" ")) != 2:
                util.eprint("Usage: inspect <block id>")
                continue

            try:
                current_block_id = int(command.split(" ")[1])
            except:
                util.eprint("Usage: inspect <block id>")
                continue

            block = network.blockchain[current_block_id]

            assert block.get_id() == current_block_id, "Blocks out of order in 'blockchain' variable"

            print()
            print(f"{util.Color.YELLOW()}{util.Color.BOLD()}Block {current_block_id}:{util.Color.RESET()}")
            print(f"  {util.Color.YELLOW()}Timestamp:{util.Color.RESET()}", block.get_timestamp())
            print(f"  {util.Color.YELLOW()}Difficulty:{util.Color.RESET()}", block.get_difficulty())
            print(f"  {util.Color.YELLOW()}Current block hash:{util.Color.RESET()}", block.get_current_block_hash().hex())
            print()

        elif command == 'status':
            print()
            print(f"{util.Color.YELLOW()}{util.Color.BOLD()}Network status:{util.Color.RESET()}")

            if len(network.peers) == 0:
                print(f"  {util.Color.YELLOW()}No connected peers{util.Color.RESET()}")
            else:
                print(f"  {util.Color.YELLOW()}Connected peers ({len(network.peers)}):{util.Color.RESET()}")

                for peer in network.peers:
                    print(f"    - {peer.to_string()} (reputation {peer.get_reputation()})")

            if len(network.pending_coin_transactions) == 0:
                print(f"  {util.Color.YELLOW()}No pending coin transactions{util.Color.RESET()}")
            else:
                print(f"  {util.Color.YELLOW()}Pending coin transactions ({len(network.pending_coin_transactions)}):{util.Color.RESET()}")

                for tx in network.pending_coin_transactions:
                    print(f"    - {tx}")

            if len(network.pending_proof_transactions) == 0:
                print(f"  {util.Color.YELLOW()}No pending proof transactions{util.Color.RESET()}")
            else:
                print(f"  {util.Color.YELLOW()}Pending proof transactions ({len(network.pending_proof_transactions)}):{util.Color.RESET()}")

                for tx in network.pending_proof_transactions:
                    print(f"    - {tx}")

            print(f"  {util.Color.YELLOW()}Latest block:{util.Color.RESET()} {network.blockchain[-1].get_current_block_hash().hex()[0:6]}… (id {network.blockchain[-1].get_id()})")
            print()

        elif command == 'produce-empty':
            previous_block = network.blockchain[-1]

            new_block_body = BlockBody()
            new_block_body.setup([], [], previous_block.get_state_tree())

            coin_txs_hash = new_block_body.hash_coin_txs()
            proof_txs_hash = new_block_body.hash_proof_txs()
            state_root_hash = new_block_body.hash_state_tree()

            current_timestamp = util.get_current_time()

            new_block_header = BlockHeader()
            new_block_header.setup(previous_block.get_id() + 1, current_timestamp, 1, previous_block.get_current_block_hash(), coin_txs_hash, proof_txs_hash, state_root_hash)

            new_block = Block()
            new_block.setup(new_block_header, new_block_body)
            new_block.finish_block()

            util.iprint("Sucessfully produced an empty block with id", previous_block.get_id() + 1)

            network.broadcast_block(new_block)

        elif command.split(" ")[0] == 'auth':
            if len(command.split(" ")) != 2:
                util.eprint("Usage: auth <private key file>")
                continue

            try:
                private_key = load_ecdsa_private_key(command.split(" ")[1])

                util.iprint("Private key file loaded successfully")
                util.iprint(f"Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")
            except e:
                util.eprint("Failed to load private key file:", e)

        elif command == 'logout':
            if private_key is None:
                util.eprint("You are not currently authenticated, therefore you cannot log out")
                continue
            else:
                util.iprint("Successfully logged out")

            private_key = None

        else:
            util.eprint(f"Unknown command '{command}'. Type 'help' to see a list of commands.")

    server_thread.join()
    block_sync_thread.join()
    pending_tx_sync_thread.join()

    util.vprint("Successfully terminated main thread")

if __name__ == "__main__":
    main(sys.argv[1:])
