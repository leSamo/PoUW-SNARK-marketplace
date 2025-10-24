import { useEffect, useState, Fragment } from "react";
import { DownloadIcon, RedoIcon } from "@patternfly/react-icons";
import { Table, Thead, Tbody, Tr, Th, Td } from '@patternfly/react-table';
import Hash from "../Components/Hash";
import { COMMANDS, sendRpcRequest } from "../Helpers/rpc";
import { AlertVariant, Bullseye, Button, Label, Spinner, Split, SplitItem, Switch, Title } from "@patternfly/react-core";
import ErrorState from "../Components/ErrorState";
import { downloadString } from "../Helpers/download";

const ProofTransactionsTab = ({ addAlert }) => {
    const [arePendingTxsLoading, setPendingTxsLoading] = useState(true);
    const [areConfirmedTxsLoading, setConfirmedTxsLoading] = useState(true);
    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    const [pendingProofTxs, setPendingProofTxs] = useState([]);
    const [confirmedProofTxs, setConfirmedProofTxs] = useState([]);

    const [shouldShowUnconfirmed, setShowUnconfirmed] = useState(true);

    useEffect(() => {
        setPendingTxsLoading(true);
        setConfirmedTxsLoading(true);

        sendRpcRequest(COMMANDS.GET_PENDING_PROOF_TXS, {})
            .then((response) => {
                setPendingProofTxs(response.pending_proof_txs);
                setPendingTxsLoading(false);
            })
            .catch((response) => {
                setError(true);
                setPendingTxsLoading(false);

                addAlert(AlertVariant.danger, "Failed to fetch pending proof transactions");
            })

        sendRpcRequest(COMMANDS.GET_LATEST_BLOCK_ID, {})
            .then((response) => {
                const sequence = Array.from({ length: response.latest_id + 1 }, (_, i) => i);

                Promise.all(sequence.map(block_id => sendRpcRequest(COMMANDS.GET_BLOCK, [block_id])))
                    .then(result => {
                        setConfirmedTxsLoading(false);

                        setConfirmedProofTxs(
                            result.flatMap(({ block }) =>
                                block.body.proof_txs.flatMap((tx) => ({
                                    ...tx,
                                    blockHash: block.header.current_block_hash,
                                    blockTimestamp: block.header.timestamp
                                }))
                            ));
                    })
            })
            .catch((response) => {
                setError(true);
                setConfirmedTxsLoading(false);

                addAlert(AlertVariant.danger, "Failed to fetch blocks");
            })
    }, [refreshCounter]);

    const refresh = () => {
        setRefreshCounter(refreshCounter + 1);
    }

    const proofsTxs = shouldShowUnconfirmed
        ? [...pendingProofTxs, ...confirmedProofTxs]
        : confirmedProofTxs;

    return (arePendingTxsLoading || areConfirmedTxsLoading)
        ? <Bullseye style={{ height: 150 }}><Spinner /></Bullseye>
        : isError
            ? <ErrorState />
            : (
                <Fragment>
                    <Split hasGutter style={{ margin: 16 }}>
                        <SplitItem>
                            <Title headingLevel="h1">
                                Proof Transactions
                            </Title>
                        </SplitItem>
                        <SplitItem isFilled />
                        <SplitItem style={{ margin: 'auto' }}>
                            <Switch
                                label="Show unconfirmed"
                                isChecked={shouldShowUnconfirmed}
                                onChange={(e, newValue) => setShowUnconfirmed(newValue)}
                                isReversed
                            />
                        </SplitItem>
                        <SplitItem>
                            <Button onClick={refresh} icon={<RedoIcon />}>Refresh</Button>
                        </SplitItem>
                    </Split>
                    <Table variant="compact" style={{ border: "1px solid lightgray", borderTop: 0 }}>
                        <Thead>
                            <Tr>
                                <Th>Transaction ID</Th>
                                <Th>Address from</Th>
                                <Th>Circuit hash</Th>
                                <Th>Complexity</Th>
                                <Th>Parameters</Th>
                                <Th>Proof</Th>
                                <Th>Status</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {proofsTxs.length === 0
                                ? (
                                    <Tr>
                                        <Td colSpan={100} style={{ backgroundColor: "#EEE" }}>
                                            <Bullseye>
                                                There are no {shouldShowUnconfirmed || "confirmed"} proof transactions
                                            </Bullseye>
                                        </Td>
                                    </Tr>
                                ) : proofsTxs.map((tx) => (
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
                                            {
                                                tx.blockHash
                                                    ? (
                                                        <Button
                                                            variant="link"
                                                            style={{ padding: 0, width: "fit-content" }}
                                                            icon={<DownloadIcon />}
                                                            onClick={() => downloadString(`proof-${tx.id.slice(0, 12)}.json`, tx.proof)}
                                                        >
                                                            Download
                                                        </Button>
                                                    )
                                                    : (
                                                        <Label isCompact>
                                                            Pending
                                                        </Label>
                                                    )
                                            }
                                        </Td>
                                        <Td dataLabel="Status">
                                            {
                                                tx.blockHash
                                                    ? (
                                                        <Split>
                                                            <SplitItem>
                                                                <Label isCompact color="green" style={{ marginRight: 4 }}>
                                                                    Confirmed
                                                                </Label>
                                                            </SplitItem>
                                                            <SplitItem>
                                                                <Hash>
                                                                    {tx.blockHash}
                                                                </Hash>
                                                            </SplitItem>
                                                        </Split>
                                                    )
                                                    : (
                                                        <Split>
                                                            <SplitItem>
                                                                <Label isCompact color="red">Unconfirmed</Label>
                                                            </SplitItem>
                                                        </Split>
                                                    )
                                            }
                                        </Td>
                                    </Tr>
                                ))}
                        </Tbody>
                    </Table>
                </Fragment >
            )
}


export default ProofTransactionsTab;
