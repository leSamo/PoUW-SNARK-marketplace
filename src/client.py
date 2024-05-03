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

import util
import network
from block import Block
from block_body import BlockBody
from block_header import BlockHeader
from coin_tx import CoinTransaction
from proof_tx import ProofTransaction

USAGE = 'Usage: python client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help] [-p|--port <port number>] [-c|--command <command>]'

server_running = True
private_key = None
port = 12346

def receive_incoming(client_socket, client_address):
    # TODO: Consider adding client_address to PEERS if not already

    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            break
        
        message = json.loads(data.decode())

        # Process received data (you can modify this part based on your requirements)
        util.vprint(f"Received from {client_address}:", json.dumps(message, indent=2))

        if message['command'] == util.Command.BROADCAST_BLOCK:
            new_block = Block()
            new_block.decode(message['block'])

            # TODO: verify block
            # TODO: reject out of order block

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
            network.send_message(client_address, util.Command.LATEST_BLOCK_ID, { 'latest_id': network.blockchain[-1].get_id() })

        elif message['command'] == util.Command.LATEST_BLOCK_ID:
            # TODO: sync
            pass


    # Close the connection when done
    client_socket.close()

def start_server(port):
    global server_running, verbose_logging

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(5)
    util.vprint(f"Server listening on port {port}")

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
    global server_running, verbose_logging, private_key, port

    try:
        opts, args = getopt.getopt(argv, "hvk:p:c:", ["help", "verbose", "key=", "port=", "command="])
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(-1)

    cli_commands = []

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(USAGE)
            sys.exit()
        elif opt in ['-v', '--verbose']:
            util.iprint("Enabled verbose logging")
            util.verbose_logging = True
        elif opt in ['-k', '--key']:
            private_key = load_ecdsa_private_key(arg)
        elif opt in ['-p', '--port']:
            port = int(arg)
        elif opt in ['-c', '--command']:
            cli_commands = arg.split(";")

    if private_key is None:
        util.iprint("Private key file was not provided, running in anonymous mode -- transactions cannot be created")
    else:
        util.iprint("Private key file loaded succefully")
        util.iprint(f"Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")

    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.start()

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
                terminating_socket.connect(("localhost", port))
            except:
                util.eprint("Failed to open terminating socket")
            
            break

        elif command == "help":
            print()
            print(f"{util.Color.YELLOW}{util.Color.BOLD}Available commands:{util.Color.RESET}")
            print(f"  {util.Color.YELLOW}verbose <on|off>{util.Color.RESET} -- toggles verbose logging")
            print(f"  {util.Color.YELLOW}exit{util.Color.RESET} -- terminates client")
            print(f"  {util.Color.YELLOW}send <receiver address> <amount>{util.Color.RESET} -- create a coin transaction and submit it to the network")
            print(f"  {util.Color.YELLOW}generate-key <output file>{util.Color.RESET} -- generate SECP256k1 private key and save it in <output file> in PEM format")
            print(f"  {util.Color.YELLOW}inspect <block id>{util.Color.RESET} -- print information about block with <block id>")
            print(f"  {util.Color.YELLOW}status{util.Color.RESET} -- print current status of the network")
            print(f"  {util.Color.YELLOW}produce-empty{util.Color.RESET} -- produces an empty dummy block and broadcasts it to the network")
            print(f"  {util.Color.YELLOW}auth <private key file>{util.Color.RESET} -- switches from anonymous mode to authenticated mode")
            print(f"  {util.Color.YELLOW}balance [<address>]{util.Color.RESET} -- prints current (latest known block) balance of <address> or self if authenticated and <address> is not provided")
            print()

        elif command == "verbose on":
            util.iprint("Enabled verbose logging")
            util.verbose_logging = True

        elif command == "verbose off":
            util.iprint("Disabled verbose logging")
            util.verbose_logging(False)

        elif command.split(" ")[0] == 'balance':
            latest_block = network.blockchain[-1]
        
            if len(command.split(" ")) == 1:
                if private_key is None:
                    util.eprint("Either authenticate to list current self balance, or use 'balance <address>'")
                    continue

                sender_address = private_key.get_verifying_key().to_string('compressed').hex()
                current_sender_balance = latest_block.get_state_tree().get(sender_address)

                print(f"Current balance (block {latest_block.get_id()}): {current_sender_balance}")
            
            elif len(command.split(" ")) == 2:
                current_sender_balance = latest_block.get_state_tree().get(command.split(" ")[1])

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

            # TODO:
            # check if funds are sufficient
            latest_block = network.blockchain[-1]
            sender_address = private_key.get_verifying_key().to_string('compressed').hex()
            current_sender_balance = latest_block.get_state_tree().get(sender_address) or 0

            # TODO: Check if valid address
            try:
                receiver_address = command.split(" ")[1]
                amount = int(command.split(" ")[2])

                assert current_sender_balance >= amount, "Insufficient sender balance"

                new_tx = CoinTransaction()
                new_tx.setup(sender_address.encode(), receiver_address.encode(), amount)

                new_tx.sign(private_key)

                network.broadcast_pending_coin_transaction(new_tx)
                
            except Exception as e:
                util.eprint("Failed to create coin transaction:", e)
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
            print(f"{util.Color.YELLOW}{util.Color.BOLD}Block {current_block_id}:{util.Color.RESET}")
            print(f"  {util.Color.YELLOW}Timestamp:{util.Color.RESET}", block.get_timestamp())
            print(f"  {util.Color.YELLOW}Difficulty:{util.Color.RESET}", block.get_difficulty())
            print(f"  {util.Color.YELLOW}Current block hash:{util.Color.RESET}", block.get_current_block_hash().hex())
            print()

        elif command == 'status':
            print()
            print(f"{util.Color.YELLOW}{util.Color.BOLD}Network status:{util.Color.RESET}")
            print(f"  {util.Color.YELLOW}Connected peers ({len(network.peers)}):{util.Color.RESET}", network.peers)
            print(f"  {util.Color.YELLOW}Pending coin transactions ({len(network.pending_coin_transactions)}):{util.Color.RESET}", network.pending_coin_transactions)
            print(f"  {util.Color.YELLOW}Pending proof transactions ({len(network.pending_proof_transactions)}):{util.Color.RESET}", network.pending_proof_transactions)
            print(f"  {util.Color.YELLOW}Latest block id:{util.Color.RESET}", network.blockchain[-1].get_id())
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
            new_block_header.setup(previous_block.get_id() + 1, current_timestamp, 0, previous_block.get_current_block_hash(), coin_txs_hash, proof_txs_hash, state_root_hash)

            new_block = Block()
            new_block.setup(new_block_header, new_block_body)
            new_block.finish_block()

            util.iprint("Sucessfully produced an empty block with id", previous_block.get_id() + 1)

            network.broadcast_block(new_block)

        elif command.split(" ")[0] == 'auth':
            if len(command.split(" ")) != 2:
                util.eprint("Usage: auth <private key file>")
                continue

            private_key = load_ecdsa_private_key(command.split(" ")[1])

            util.iprint("Private key file loaded succefully")
            util.iprint(f"Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")

        else:
            util.eprint(f"Unknown command '{command}'. Type 'help' to see a list of commands.")

    server_thread.join()
    util.vprint("Successfully terminated main thread")

if __name__ == "__main__":
    main(sys.argv[1:])
