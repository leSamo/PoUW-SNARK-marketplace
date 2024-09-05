import { Fragment, React, useEffect, useState } from "react";
import { COMMANDS, sendMessage } from "../Helpers/network";
import { Bullseye, Button, EmptyState, EmptyStateBody, EmptyStateHeader, EmptyStateIcon, Label, Spinner, Split, SplitItem, Tab, TabTitleText, Tabs, Title } from "@patternfly/react-core";
import { DownloadIcon, ExclamationCircleIcon, RedoIcon } from "@patternfly/react-icons";
import { Table, Thead, Tbody, Tr, Th, Td, ExpandableRowContent } from '@patternfly/react-table';
import Hash from "../Hash";
import { formatTimestamp } from "../Helpers/date";

const Index = () => {
    const [isLoading, setLoading] = useState(true);
    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    const [latestBlockId, setLatestBlockId] = useState(null);
    const [blocks, setBlocks] = useState([]);

    const [isExpanded, setExpanded] = useState(new Set());
    const [selectedTab, setSelectedTab] = useState({});

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

    const onToggle = (e, id) => {
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

    const downloadString = (filename, string) => {
        const element = document.createElement("a");
        const file = new Blob([string], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = filename;
        document.body.appendChild(element);
        element.click();
    }

    console.log(">>>>>", blocks);

    return (
        <Fragment>
            {isError
                ? (
                    <EmptyState>
                        <EmptyStateHeader
                            titleText="An error occured"
                            icon={<EmptyStateIcon icon={ExclamationCircleIcon} color="var(--pf-v5-global--danger-color--100)"/>}
                        />
                        <EmptyStateBody>
                            Is your client running with RPC interface on port 9545?
                        </EmptyStateBody>
                    </EmptyState>
                ) : isLoading
                    ? <Bullseye style={{ height: 150 }}><Spinner /></Bullseye>
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
                                        <Th screenReaderText="Expand row"/>
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
                                        <Fragment key={index}>
                                            <Tr>
                                                <Td
                                                    expand={{
                                                        rowIndex: index,
                                                        isExpanded: isExpanded.has(index),
                                                        onToggle,
                                                        expandId: index
                                                    }}
                                                    />
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
                                            <Tr isExpanded={isExpanded.has(index)}>
                                                <Td colSpan={100}>
                                                    <ExpandableRowContent>
                                                        <Tabs
                                                            activeKey={selectedTab[index] ?? 0}
                                                            onSelect={(e, v) => setSelectedTab({ ...selectedTab, [index]: v})}
                                                            isBox
                                                        >
                                                            <Tab eventKey={0} title={<TabTitleText>Coin transactions</TabTitleText>}>
                                                                <Table style={{ border: "1px solid lightgray", borderTop: 0 }}>
                                                                    <Thead>
                                                                        <Tr>
                                                                            <Th>Transaction ID</Th>
                                                                            <Th>Address from</Th>
                                                                            <Th>Address to</Th>
                                                                            <Th>Amount</Th>
                                                                        </Tr>
                                                                    </Thead>
                                                                    <Tbody>
                                                                        {block.body.coin_txs.length === 0 
                                                                            ? (
                                                                                <Tr>
                                                                                    <Td colSpan={100} style={{ backgroundColor: "#EEE"}}>
                                                                                        <Bullseye>
                                                                                            This block does not contain any coin transactions
                                                                                        </Bullseye>
                                                                                    </Td>
                                                                                </Tr>
                                                                            ) : block.body.coin_txs.map((tx) => (
                                                                            <Tr key={tx.id}>
                                                                                <Td dataLabel="Transaction ID">
                                                                                    <Hash>{tx.id}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Address from">
                                                                                    <Hash>{tx.address_from}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Address to">
                                                                                    <Hash>{tx.address_to}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Amount">
                                                                                    {tx.amount}
                                                                                </Td>
                                                                            </Tr>
                                                                        ))}
                                                                    </Tbody>
                                                                </Table>
                                                            </Tab>
                                                            <Tab eventKey={1} title={<TabTitleText>Proof transactions</TabTitleText>}>
                                                                <Table style={{ border: "1px solid lightgray", borderTop: 0 }}>
                                                                    <Thead>
                                                                        <Tr>
                                                                            <Th>Transaction ID</Th>
                                                                            <Th>Address from</Th>
                                                                            <Th>Circuit hash</Th>
                                                                            <Th>Complexity</Th>
                                                                            <Th>Parameters</Th>
                                                                            <Th>Proof</Th>
                                                                        </Tr>
                                                                    </Thead>
                                                                    <Tbody>
                                                                        {block.body.proof_txs.length === 0 
                                                                        ? (
                                                                            <Tr>
                                                                                <Td colSpan={100} style={{ backgroundColor: "#EEE"}}>
                                                                                    <Bullseye>
                                                                                        This block does not contain any proof transactions
                                                                                    </Bullseye>
                                                                                </Td>
                                                                            </Tr>
                                                                        ) : block.body.proof_txs.map((tx) => (
                                                                            <Tr key={tx.id}>
                                                                                <Td dataLabel="Transaction ID">
                                                                                    <Hash>{tx.id}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Address from">
                                                                                    <Hash>{tx.address_from}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Circuit hash">
                                                                                    <Hash>{tx.circuit_hash}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Complexity">
                                                                                    {tx.complexity}
                                                                                </Td>
                                                                                <Td dataLabel="Parameters">
                                                                                    {tx.parameters.split(" ").join(", ")}
                                                                                </Td>
                                                                                <Td dataLabel="Proof">
                                                                                    <Button
                                                                                        variant="link"
                                                                                        style={{ padding: 0, width: "fit-content" }}
                                                                                        icon={<DownloadIcon />}
                                                                                        onClick={() => downloadString(`proof-${tx.id.slice(0, 12)}.json`, tx.proof)}
                                                                                    >
                                                                                        Download
                                                                                    </Button>
                                                                                </Td>
                                                                            </Tr>
                                                                        ))}
                                                                    </Tbody>
                                                                </Table>
                                                            </Tab>
                                                            <Tab eventKey={2} title={<TabTitleText>Account state</TabTitleText>}>
                                                                <Table style={{ border: "1px solid lightgray", borderTop: 0 }}>
                                                                    <Thead>
                                                                        <Tr>
                                                                            <Th>Account address</Th>
                                                                            <Th>Balance</Th>
                                                                        </Tr>
                                                                    </Thead>
                                                                    <Tbody>
                                                                        {Object.entries(block.body.state_tree).length === 0
                                                                        ? (
                                                                            <Tr>
                                                                                <Td colSpan={100} style={{ backgroundColor: "#EEE"}}>
                                                                                    <Bullseye>
                                                                                        This block does not contain any account state data
                                                                                    </Bullseye>
                                                                                </Td>
                                                                            </Tr>
                                                                        ) : Object.entries(block.body.state_tree).map(([key, value]) => (
                                                                            <Tr key={key}>
                                                                                <Td dataLabel="Account address">
                                                                                    <Hash>{key}</Hash>
                                                                                </Td>
                                                                                <Td dataLabel="Balance">
                                                                                    {value}
                                                                                </Td>
                                                                            </Tr>
                                                                        ))}
                                                                    </Tbody>
                                                                </Table>
                                                            </Tab>
                                                        </Tabs>
                                                    </ExpandableRowContent>
                                                </Td>
                                            </Tr>
                                        </Fragment>
                                    ))}
                                </Tbody>
                            </Table>
                        </Fragment>
                    )
            }
        </Fragment>
    );
}

export default Index;
