import { React, useEffect } from "react";
import { sendMessage } from "../Helpers/network";

const Index = () => {
    // fetch all blocks

    useEffect(() => {
        sendMessage();
    }, []);

    return (
        <span>ahoj</span>
        // list of blocks
    );
}

export default Index;