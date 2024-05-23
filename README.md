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
Automated tests are located in the `src/test` directory and can be run with `pytest src/test/test_*.py -v`.

## Usage
    Usage: python client.py [-k|--key <private key file>] [-v|--verbose] [-h|--help] [-p|--port <port number>] [-c|--command <command>] [-f|--config <config file>]

    -k, --key <private key file>   Authenticate using an existing private key file
    -v, --verbose                  Show more detailed log messages
    -h, --help                     Print this message
    -p, --port <port number>       Open the listening socket on a specific port number
    -c, --command <command>        Run semicolon separated list of commands just after client initialization
    -f, --config <config file>     Provide a non-default configuration file
    -n, --no-color                 Don't print colored text into the terminal

## Limitations and Future Work
TODO

- Sycomore - prefix splitting
- Blockchain explorer
- statically defined circuits - implement circuit mgmt
- test util class - process inicialisation and communication
- improved reputation system
- better interactive console - tabbing and command history accessible with arrow keys
- hash generation
- difficulty calculation

## Adding a New Circuit
TODO
