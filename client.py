# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ✔️✔️❌❌❌
# ####################################################################################################

import socket
import threading
import getopt
import sys
import ecdsa

USAGE = 'Usage: client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help]'

server_running = True
verbose_logging = False
private_key = None

def vprint(*args, **kwargs):    
    """ Print with verbose priority """
    global verbose_logging
    if verbose_logging:
        print("VERBOSE: ", *args, file=sys.stdout, **kwargs)

def receive_incoming(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Process received data (you can modify this part based on your requirements)
        print("Received:", data.decode())

    # Close the connection when done
    client_socket.close()

def start_server(port):
    global server_running, verbose_logging

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(5)
    vprint(f"Server listening on port {port}")

    try:
        while server_running:
            client_socket, _ = server_socket.accept()

            if server_running:
                vprint("Connection established.")

            # Start a new thread to handle the client connection
            client_thread = threading.Thread(target=receive_incoming, args=(client_socket,))
            client_thread.start()
    except Exception:
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

    print("Private key saved to", filename)

def main(argv):
    global server_running, verbose_logging, private_key

    try:
        opts, args = getopt.getopt(argv, "hvk:", ["help", "verbose", "key="])
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(-1)

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(USAGE)
            sys.exit()
        elif opt in ['-v', '--verbose']:
            print("Enabled verbose logging")
            verbose_logging = True
        elif opt in ['-k', '--key']:
            private_key = load_ecdsa_private_key(arg)

    if private_key is None:
        print("INFO: Private key file was not provided, running in anonymous mode -- transactions cannot be created")
    else:
        print("INFO: Private key file loaded succefully")
        print(f"INFO: Your address: {private_key.get_verifying_key().to_string('compressed').hex()}")

    server_port = 12346
    server_thread = threading.Thread(target=start_server, args=(server_port,))
    server_thread.start()
    
    while True:
        command = input()
        if command == "exit":
            server_running = False

            terminating_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            terminating_socket.connect(("localhost", server_port))
            
            break
        elif command == "help":
            print()
            print("Available commands:")
            print("\tverbose <on|off> -- toggles verbose logging")
            print("\texit -- terminates client")
            print("\tsend <receiver address> <amount> -- create a coin transaction and submit it to the network")
            print("\tgenerate-key <output file> -- generate SECP256k1 private key and save it in <output file> in PEM format")
            #print("\trequest-proof <> <>")
            print()
        elif command == "verbose on":
            verbose_logging = True
            print("Enabled verbose logging")
        elif command == "vebose off":
            verbose_logging = False
            print("Disabled verbose logging")
        elif command.split(" ")[0] == "send":
            pass
        elif command.split(" ")[0] == 'generate-key':
            if len(command.split(" ")) != 2:
                print("ERROR: Usage: generate-key <output file>")
                continue

            generate_key(command.split(" ")[1])
        elif command.split(" ")[0] == 'send':
            if len(command.split(" ")) != 3:
                print("ERROR: Usage: send <receiver address> <amount>")
                continue
            
            # TODO:
            # check if funds are sufficient
            # create transaction object
            # sign transaction
            # broadcast transactions
        else:
            print("Unknown command. Type 'help' to see a list of commands.")

    server_thread.join()
    vprint("Successfully terminated server thread")

if __name__ == "__main__":
    main(sys.argv[1:])
