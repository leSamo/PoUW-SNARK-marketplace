import net from "node:net"
import PromiseSocket from "promise-socket"

const HOST = "127.0.0.1"
const PORT = 12346

const COMMANDS = {
    GET_PEERS: 'GET_PEERS',
    PEERS: 'PEERS',
    GET_LATEST_BLOCK_ID: 'GET_LATEST_BLOCK_ID',
    LATEST_BLOCK_ID: 'LATEST_BLOCK_ID',
    GET_BLOCK: 'GET_BLOCK',
    BLOCK: 'BLOCK',
    GET_PENDING_COIN_TXS: 'GET_PENDING_COIN_TXS',
    PENDING_COIN_TXS: 'PENDING_COIN_TXS',
    GET_PENDING_PROOF_TXS: 'GET_PENDING_PROOF_TXS',
    PENDING_PROOF_TXS: 'PENDING_PROOF_TXS',

    BROADCAST_BLOCK: 'BROADCAST_BLOCK',
    BROADCAST_PENDING_COIN_TX: 'BROADCAST_PENDING_COIN_TX',
    BROADCAST_PENDING_PROOF_TX: 'BROADCAST_PENDING_PROOF_TX',
}

export const sendMessage = async (receiver, command, message = {}) => {
    const socket = new net.Socket();
    const promiseSocket = new PromiseSocket(socket);

    await promiseSocket.connect({port: 2222, host: "localhost"});

    promiseSocket.setTimeout(1000)
    const chunk = await promiseSocket.readAll()

    console.log(chunk);
}

/*
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
*/