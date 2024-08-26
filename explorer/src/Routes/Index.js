import { Fragment, React, useEffect, useState } from "react";
import { COMMANDS, sendMessage } from "../Helpers/network";
import { Accordion, AccordionContent, AccordionItem, AccordionToggle, Bullseye, EmptyState, EmptyStateHeader, EmptyStateIcon, Spinner } from "@patternfly/react-core";
import { ExclamationCircleIcon } from "@patternfly/react-icons";

const Index = () => {
    const [isLoading, setLoading] = useState(true);
    const [isError, setError] = useState(false);

    const [latestBlockId, setLatestBlockId] = useState(null);
    const [blocks, setBlocks] = useState([]);

    const [isExpanded, setExpanded] = useState(new Set());

    useEffect(() => {
        sendMessage(COMMANDS.GET_LATEST_BLOCK_ID, {})
            .then((response) => {
                setLatestBlockId(response.latest_id);

                console.log(response.latest_id);

                const sequence = Array.from({ length: response.latest_id + 1 }, (_, i) => i);

                Promise.all(sequence.map(block_id => sendMessage(COMMANDS.GET_BLOCK, [block_id])))
                    .then(result => {
                        setBlocks(result);
                        setLoading(false);
                    })
                })
            .catch((response) => {
                setError(true);
                setLoading(false);
            })
        }, []);

    const onToggle = (id) => {
        const newSet = new Set(isExpanded);

        if (isExpanded.has(id)) {
            newSet.delete(id)
            setExpanded(newSet);
        }
        else {
            newSet.add(id)
            setExpanded(newSet);
        }
    }

    console.log(">>>>>", blocks);

    return (
        <Fragment>
            {isError
                ? (
                    <EmptyState>
                        <EmptyStateHeader
                            titleText="An error occured"
                            icon={<EmptyStateIcon icon={ExclamationCircleIcon} />}
                        />
                    </EmptyState>
                ) : isLoading
                    ? <Bullseye><Spinner /></Bullseye>
                    : (
                        <Accordion isBordered togglePosition="start">
                            {blocks.map((block, index) => (
                                <AccordionItem key={index}>
                                    <AccordionToggle
                                        onClick={() => {
                                            onToggle(index);
                                        }}
                                        isExpanded={isExpanded.has(index)}
                                    >
                                        {index}: {block.block.header.current_block_hash}
                                    </AccordionToggle>
                                    <AccordionContent isHidden={!isExpanded.has(index)}>
                                        Miner: {block.block.header.miner}
                                    </AccordionContent>
                                </AccordionItem>
                            ))}
                        </Accordion>
                    )
            }
        </Fragment>
    );
}

export default Index;
