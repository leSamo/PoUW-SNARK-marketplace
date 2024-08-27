import { Fragment, React, useEffect, useState } from "react";
import { COMMANDS, sendMessage } from "../Helpers/network";
import { Bullseye, Button, EmptyState, EmptyStateHeader, EmptyStateIcon, Label, Spinner, Split, SplitItem, Title } from "@patternfly/react-core";
import { ExclamationCircleIcon, RedoIcon } from "@patternfly/react-icons";
import { Table, Thead, Tbody, Tr, Th, Td } from '@patternfly/react-table';
import Hash from "../Hash";
import { formatTimestamp } from "../Helpers/date";

const Index = () => {
    const [isLoading, setLoading] = useState(true);
    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    const [latestBlockId, setLatestBlockId] = useState(null);
    const [blocks, setBlocks] = useState([]);

    const [isExpanded, setExpanded] = useState(new Set());

    useEffect(() => {
        setLoading(true);

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
        }, [refreshCounter]);

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

    const refresh = () => {
        setRefreshCounter(refreshCounter + 1);
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
                        <Fragment>
                            <Split hasGutter style={{ margin: 16 }}>
                                <SplitItem>
                                    <Title headingLevel="h1">
                                        Confirmed Blocks
                                    </Title>
                                </SplitItem>
                                <SplitItem isFilled />
                                <SplitItem>
                                    <Button onClick={refresh} icon={<RedoIcon />}>Refresh</Button>
                                </SplitItem>
                            </Split>
                            <Table variant="compact">
                                <Thead>
                                    <Tr>
                                        <Th>Serial ID</Th>
                                        <Th>Block hash</Th>
                                        <Th>Mined by</Th>
                                        <Th>Produced at</Th>
                                        <Th>Coin transaction count</Th>
                                        <Th>Proof transaction count</Th>
                                    </Tr>
                                </Thead>
                                <Tbody>
                                    {blocks.map(({ block }, index) => (
                                        <Tr key={index}>
                                            <Td dataLabel="Serial ID">
                                                <Split>
                                                    <SplitItem>
                                                        {block.header.serial_id}
                                                    </SplitItem>
                                                    <SplitItem>
                                                        {block.header.serial_id === 0 && <Label isCompact color="green" style={{ marginLeft: 8 }}>Genesis</Label>}
                                                    </SplitItem>
                                                </Split>
                                            </Td>
                                            <Td dataLabel="Block hash">
                                                <Hash>{block.header.current_block_hash}</Hash>
                                            </Td>
                                            <Td dataLabel="Mined by">
                                                <Hash>{block.header.miner}</Hash>
                                            </Td>
                                            <Td dataLabel="Produced at">
                                                {formatTimestamp(block.header.timestamp)}
                                            </Td>
                                            <Td dataLabel="Coin transaction count">
                                                {block.body.coin_txs.length}
                                            </Td>
                                            <Td dataLabel="Proof transaction count">
                                                {block.body.proof_txs.length}
                                            </Td>
                                        </Tr>
                                    ))}
                                </Tbody>
                            </Table>
                            {/*
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
                            */}
                        </Fragment>
                    )
            }
        </Fragment>
    );
}

export default Index;
