import axios from 'axios'

export const COMMANDS = {
    GET_LATEST_BLOCK_ID: 'GET_LATEST_BLOCK_ID',
    GET_BLOCK: 'GET_BLOCK',
    GET_PENDING_COIN_TXS: 'GET_PENDING_COIN_TXS',
    GET_PENDING_PROOF_TXS: 'GET_PENDING_PROOF_TXS',

    BROADCAST_PENDING_COIN_TX: 'BROADCAST_PENDING_COIN_TX',
    BROADCAST_PENDING_PROOF_TX: 'BROADCAST_PENDING_PROOF_TX',
}

export const sendRpcRequest = async (command, params = {}) => {
    if (!command in COMMANDS) {
        throw Error("Invalid RPC command");
    }

    return axios.post(`http://localhost:9545/`, {
        jsonrpc: "2.0",
        id: 0,
        method: command,
        params
      })
      .then(function (response) {
        return response.data.result;
      })
      .catch(function (error) {
        throw error;
      });
};
