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
import time
import json

import util
import network
from block import Block
from block_body import BlockBody
from block_header import BlockHeader

USAGE = 'Usage: python client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help] [-p|--port <port number>]'

server_running = True
private_key = None
port = 12346

def receive_incoming(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Process received data (you can modify this part based on your requirements)
        print("Received:", data.decode())

        new_block = Block()
        new_block.decode(json.loads(data.decode()))

        network.blockchain.append(new_block)

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
            client_socket, _ = server_socket.accept()

            if server_running:
                util.vprint("Connection established.")

            # Start a new thread to handle the client connection
            client_thread = threading.Thread(target=receive_incoming, args=(client_socket,))
            client_thread.start()
    except:
        print("Socket terminated")

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
        opts, args = getopt.getopt(argv, "hvk:p:", ["help", "verbose", "key=", "port="])
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(-1)

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

    if private_key is None:
        util.iprint("Private key file was not provided, running in anonymous mode -- transactions cannot be created")
    else:
        util.iprint("Private key file loaded succefully")
        util.iprint(f"Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")

    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.start()
    
    while True:
        try:
            command = input()
        except:
            command = "exit"

        if command == "exit":
            server_running = False

            terminating_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            terminating_socket.connect(("localhost", port))
            
            break

        elif command == "help":
            print()
            print(f"{util.Colors.YELLOW}{util.Colors.BOLD}Available commands:{util.Colors.RESET}")
            print(f"  {util.Colors.YELLOW}verbose <on|off>{util.Colors.RESET} -- toggles verbose logging")
            print(f"  {util.Colors.YELLOW}exit{util.Colors.RESET} -- terminates client")
            print(f"  {util.Colors.YELLOW}send <receiver address> <amount>{util.Colors.RESET} -- create a coin transaction and submit it to the network")
            print(f"  {util.Colors.YELLOW}generate-key <output file>{util.Colors.RESET} -- generate SECP256k1 private key and save it in <output file> in PEM format")
            print(f"  {util.Colors.YELLOW}inspect <block id>{util.Colors.RESET} -- print information about block with <block id>")
            print(f"  {util.Colors.YELLOW}status{util.Colors.RESET} -- print current status of the network")
            print(f"  {util.Colors.YELLOW}produce-empty{util.Colors.RESET} -- produces an empty dummy block and broadcasts it to the network")
            print(f"  {util.Colors.YELLOW}auth <private key file>{util.Colors.RESET} -- switches from anonymous mode to authenticated mode")
            print()

        elif command == "verbose on":
            util.verbose_logging = True
            util.iprint("Enabled verbose logging")

        elif command == "verbose off":
            util.verbose_logging(False)
            util.iprint("Disabled verbose logging")

        elif command.split(" ")[0] == "send":
            pass

        elif command.split(" ")[0] == 'generate-key':
            if len(command.split(" ")) != 2:
                util.eprint("Usage: generate-key <output file>")
                continue

            generate_key(command.split(" ")[1])
            
        elif command.split(" ")[0] == 'send':
            if len(command.split(" ")) != 3:
                util.eprint("Usage: send <receiver address> <amount>")
                continue

            if private_key is None:
                util.eprint("This command requires authentication, you can use the 'auth' command to authenticate")
                continue              
            
            # TODO:
            # check if funds are sufficient
            # create transaction object
            # sign transaction
            # broadcast transactions

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
            print(f"{util.Colors.YELLOW}{util.Colors.BOLD}Block {current_block_id}:{util.Colors.RESET}")
            print(f"  {util.Colors.YELLOW}Timestamp:{util.Colors.RESET}", block.get_timestamp())
            print(f"  {util.Colors.YELLOW}Difficulty:{util.Colors.RESET}", block.get_difficulty())
            print(f"  {util.Colors.YELLOW}Current block hash:{util.Colors.RESET}", block.get_current_block_hash().hex())
            print()

        elif command == 'status':
            print()
            print(f"{util.Colors.YELLOW}{util.Colors.BOLD}Network status:{util.Colors.RESET}")
            print(f"  {util.Colors.YELLOW}Connected peers ({len(network.peers)}):{util.Colors.RESET}", network.peers)
            print(f"  {util.Colors.YELLOW}Pending coin transactions ({len(network.pending_coin_transactions)}):{util.Colors.RESET}", network.pending_coin_transactions)
            print(f"  {util.Colors.YELLOW}Pending proof transactions ({len(network.pending_proof_transactions)}):{util.Colors.RESET}", network.pending_proof_transactions)
            print(f"  {util.Colors.YELLOW}Latest block id:{util.Colors.RESET}", network.blockchain[-1].get_id())
            print()

        elif command == 'produce-empty':
            previous_block = network.blockchain[-1]

            new_block_body = BlockBody()
            new_block_body.setup([], [], previous_block.get_state_tree())

            coin_txs_hash = new_block_body.hash_coin_txs()
            proof_txs_hash = new_block_body.hash_proof_txs()
            state_root_hash = new_block_body.hash_state_tree()

            current_timestamp = round(time.time() * 1000)

            new_block_header = BlockHeader()
            new_block_header.setup(previous_block.get_id() + 1, current_timestamp, 0, previous_block.get_current_block_hash(), coin_txs_hash, proof_txs_hash, state_root_hash)

            new_block = Block()
            new_block.setup(new_block_header, new_block_body)

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
            util.eprint("Unknown command. Type 'help' to see a list of commands.")

    server_thread.join()
    util.vprint("Successfully terminated server thread")

if __name__ == "__main__":
    main(sys.argv[1:])
