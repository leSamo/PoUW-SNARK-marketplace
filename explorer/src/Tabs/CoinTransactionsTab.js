import { useEffect, useState, Fragment } from "react";
import { RedoIcon } from "@patternfly/react-icons";
import { Table, Thead, Tbody, Tr, Th, Td } from '@patternfly/react-table';
import Hash from "../Components/Hash";
import { COMMANDS, sendRpcRequest } from "../Helpers/rpc";
import { AlertVariant, Bullseye, Button, Label, Spinner, Split, SplitItem, Switch, Title } from "@patternfly/react-core";
import ErrorState from "../Components/ErrorState";

const CoinTransactionsTab = ({ addAlert }) => {
    const [arePendingTxsLoading, setPendingTxsLoading] = useState(true);
    const [areConfirmedTxsLoading, setConfirmedTxsLoading] = useState(true);
    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    const [pendingCoinTxs, setPendingCoinTxs] = useState([]);
    const [confirmedCoinTxs, setConfirmedCoinTxs] = useState([]);

    const [shouldShowUnconfirmed, setShowUnconfirmed] = useState(true);

    useEffect(() => {
        setPendingTxsLoading(true);
        setConfirmedTxsLoading(true);

        sendRpcRequest(COMMANDS.GET_PENDING_COIN_TXS, {})
            .then((response) => {
                setPendingCoinTxs(response.pending_coin_txs);
                setPendingTxsLoading(false);
            })
            .catch((response) => {
                setError(true);
                setPendingTxsLoading(false);

                addAlert(AlertVariant.danger, "Failed to fetch pending coin transactions");
            })

        sendRpcRequest(COMMANDS.GET_LATEST_BLOCK_ID, {})
            .then((response) => {
                const sequence = Array.from({ length: response.latest_id + 1 }, (_, i) => i);

                Promise.all(sequence.map(block_id => sendRpcRequest(COMMANDS.GET_BLOCK, [block_id])))
                    .then(result => {
                        setConfirmedTxsLoading(false);

                        setConfirmedCoinTxs(
                            result.flatMap(({ block }) =>
                                block.body.coin_txs.flatMap((tx) => ({
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

    const coinsTxs = shouldShowUnconfirmed
        ? [...pendingCoinTxs, ...confirmedCoinTxs]
        : confirmedCoinTxs;

    return (arePendingTxsLoading || areConfirmedTxsLoading)
        ? <Bullseye style={{ height: 150 }}><Spinner /></Bullseye>
        : isError
            ? <ErrorState />
            : (
                <Fragment>
                    <Split hasGutter style={{ margin: 16 }}>
                        <SplitItem>
                            <Title headingLevel="h1">
                                Coin Transactions
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
                                <Th>Address to</Th>
                                <Th>Amount</Th>
                                <Th>Status</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {coinsTxs.length === 0
                                ? (
                                    <Tr>
                                        <Td colSpan={100} style={{ backgroundColor: "#EEE" }}>
                                            <Bullseye>
                                                There are no {shouldShowUnconfirmed || "confirmed"} coin transactions
                                            </Bullseye>
                                        </Td>
                                    </Tr>
                                ) : coinsTxs.map((tx) => (
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


export default CoinTransactionsTab;
