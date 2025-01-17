SIMULATOR_NODE_STATE = {
    INACTIVE: "INACTIVE",
    EAVESDROP: "EAVESDROP",
    GOSSIP: "GOSSIP",
    MINE: "MINE"
}

const SimulatorNode = {
    peers: [],
    pendingCoinTxs: [],
    pendingProofTxs: [],
    knownBlocks: [],
    state: SIMULATOR_NODE_STATE.INACTIVE,
    performance: 0
};
