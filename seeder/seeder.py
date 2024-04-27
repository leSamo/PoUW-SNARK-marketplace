# ####################################################################################################
# The analysis of cryptographic techniques for offloading computations and storage in blockchains
# Master thesis 2023/24
# Samuel Olekšák
# ❌❌❌❌❌
# ####################################################################################################

# this is a simulation of a seeder node, which upon request sends a whole blockchain

import socket

from config import *

COMMAND_ALL = 'ALL'

GENESIS_BLOCK = []

BLOCKCHAIN = []

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
  print("Socket creation failed with error:", err)
  exit(-1)

SERVER_ADDRESS = (SEEDER_HOST, SEEDER_PORT)
sock.bind(SERVER_ADDRESS)

sock.listen()
print("Server listening on port", SEEDER_PORT)

conn, addr = sock.accept()
print('Connected by', addr)

data = conn.recv(1024) 
print("Received data:", data.decode())

if data.decode() == COMMAND_ALL:
  conn.sendall("test hi".encode())

conn.close()
sock.close()