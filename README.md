# SNARK Marketplace Blockchain

## Requirements
- Python 3.11 with pip
- Zokrates 0.8.8

## First Time Setup
1. Make sure you run `pip install -r requirements.txt` to install dependencies
2. (Optional) Configure network parameters in `src/config.json`

## Testing Accounts
**PeerA**
- Address: 0318b58b73bbfd6ec26f599649ecc624863c775e034c2afea0c94a1c0641d8f6f2
- Genesis blocks includes 1000 coins on account

## Automated Tests
Automated tests are located in the `src/test` directory and can be run with `pytest src/test/test_*.py -v`. Make sure your client is not running during the tests execution as it might interfere with the tests.

## Usage
    Usage: python client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help] [-p|--port <port number>] [-c|--command <command>] [-f|--config <config file>]

    -k, --key <private key file>   Authenticate using an existing private key file
    -v, --verbose                  Show more detailed log messages
    -h, --help                     Print this message
    -p, --port <port number>       Open the listening socket on a specific port number
    -c, --command <command>        Run semicolon separated list of commands just after client initialization
    -f, --config <config file>     Provide a non-default configuration file
    -n, --no-color                 Don't print colored text into the terminal

## Available Client Commands
    verbose <on|off> -- toggles verbose logging
    exit -- terminates client
    send <receiver address> <amount> -- create a coin transaction and submit it to the network
    request-proof <circuit hash> <parameters> -- request a proof to be generated
    select-proof-tx <proof index> -- manually produce a proof and include it in partial block
    select-coin-tx <coin tx index> -- manually confirm a coin transaction and include it in partial block
    partial -- print information about currently produced partial block
    produce-block -- finish and broadcast current block
    generate-key <output file> -- generate SECP256k1 private key and save it in <output file> in PEM format
    inspect <block id> -- print information about block with <block id>
    status -- print current status of the network
    display-proof <block id> <proof transaction index> -- prints a proof from a block in JSON format.
    auth <private key file> -- switches from anonymous mode to authenticated mode
    balance [<address>] -- prints current (latest known block) balance of <address> or self if authenticated and <address> is not provided
    logout -- switches to non-authenticated mode

## Limitations and Future Work

- **Transaction prefix splitting** -- As mentioned in the thesis, there are conflicts possible where two nodes work on the same transactions, which leads to wasted work on the part of the node which fails to publish first. This could be mitigated by allowing miners to only include transactions which match with their address in the prefix.
- **Blockchain explorer** -- Having a web app that could interact with the network and display data in user-friendly format would make debugging and exploring the network easier.
- **Statically defined circuits** - implement circuit mgmt
- **Testing utilities class** -- Writing unit tests involves a lot of boilerplate code for process spawning and communication pipelining. Some test setup code could be abstracted into a class to make writing tests easier.
- **Improved reputation system** -- Implemented reputation system is very rudimentary and could be abused with manually crafted messages.
- **Better interactive console** -- User experience when using the client could be improved by implementing support for tab-completion and command history accessible with arrow keys similarly to Shell.
- **Difficulty calculation** -- For debugging purposes, the difficulty parameter of the network is not calculated, nor enforced. Difficulty mechanism would exist to keep block time approximately the same by changing the amount of work required to produce a block depending on the total computational power of the network.
- **Merkle-Patricia trie instead of Python dict** -- For simplicity, the blockchain uses plain Python dictionary to store the mapping from accounts to balances. It would be more performant to use Merkle-Patricia tries in production level environment.

## Adding a New Circuit

This implementation does not include the circuit subnetwork which uses proof-of-stake-like circuit retrieval and registration using ZoKrates and SMPC. Its function is mocked by statically providing circuits in their source code and circuit form with ABI, proving key and verifying key.

To add a new circuit, just create a new folder under `src/circuits` such as `src/circuits/d` and add the ZoKrates source code file with `.zok` extension into it. Navigate to the directory and run the following commands:

1. `zokrates compile -i <zokrates source code file>`
2. `zokrates setup`

The circuit will be automatically registered when client is started the next time. To learn the hash of the circuit, start the app with `-v` switch and inspect first few logged messages.

## Example Commands

Here are some example commands to demonstrate the network:

Open two terminals, A and B and run the following commands:

A: `python src/client.py -p 2222 -k src/test/misc/private_key`
B: `python src/client.py -p 3333 -k src/test/misc/private_key_2`

Create a coin and a proof transaction with the client A (who has been given 1000 coins in the genesis block):

A: `send 02d56856ae307c2ff4843366284061f6e68aceb1e217c946d83812c52bdfecd2fc 50`
A: `request-proof 00845b36c160d19764a21fc5fcadd5e6a28c29d5fa6fd307026e0ecb8305e1ee 2 3 6`

By entering `status` command into either of the terminals, the transactions will now be listed as pending. Select the transactions with client B and produce a block:

B: `select-coin-tx 0`
B: `select-proof-tx 0`

Running the command `partial` will display the transactions we have selected for mining.

B: `produce-block`

Block has now been generated along with the proof generation and coin transaction confirmation. Running `status` in either of the terminals will list this block as the latest block and running `inspect 1` will list the information about the new block. Client A can now print the generate proof for future use with `display-proof 1 0`. By running the `balance` the A's terminal we will be able to see that the balance has decreased from the original 1000 to 948 due to coin transfer and fees.

Open a third terminal C and run:
C: `python src/client.py -p 4444`

Client C will synchronize with the network on initialization. This can be checked with the `status` command. Since we have not provided the `-k` switch, the client will be in anonymous mode, which is read-only. Authenticated mode can be entered with `auth` client command.

## Generating a New Account

TODO

## Network Configuration

TODO
