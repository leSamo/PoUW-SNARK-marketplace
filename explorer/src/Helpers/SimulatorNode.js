import { EVENT_TYPE } from "./Simulator";

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
    performance: 0,
    executeEvent: (eventType) => { // returns array of event to be scheduled
        switch (eventType) {
            case EVENT_TYPE.RECEIVE_PEER:
                break;
        }
    }
};
