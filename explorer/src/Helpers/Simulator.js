export const EVENT_TYPE = {
    // called on connected nodes
    RECEIVE_PEER: "RECEIVE_PEER",
    RECEIVE_BLOCK: "RECEIVE_BLOCK",
    RECEIVE_PENDING_COIN_TX: "RECEIVE_PENDING_COIN_TX",
    RECEIVE_PENDING_PROOF_TX: "RECEIVE_PENDING_PROOF_TX",

    // called by nodes on themselves
    CONFIRM_COIN_TX: "CONFIRM_COIN_TX",
    CONFIRM_PROOF_TX: "CONFIRM_PROOF_TX",
}

const Event = {
    scheduledTime: 0,
    type: null,
    recipient: null,
    payload: null
}

const Simulator = {
    randomSeed: 0,
    stopTime: 1000,
    currentTime: 0,
    initialState: {
        nodes: [],
        edges: [],
        pendingEvents: []
    },
    currentState: {
        nodes: [],
        edges: [],
        pendingEvents: []
    }
};
