import { useEffect, useState, Fragment } from "react";
import { RedoIcon } from "@patternfly/react-icons";
import { Table, Thead, Tbody, Tr, Th, Td } from '@patternfly/react-table';
import Hash from "../Components/Hash";
import { COMMANDS, sendRpcRequest } from "../Helpers/rpc";
import { AlertVariant, Bullseye, Button, Label, Spinner, Split, SplitItem, Switch, Title } from "@patternfly/react-core";
import ErrorState from "../Components/ErrorState";

const CircuitsTab = ({ addAlert }) => {
    const [areCircuitsLoading, setCircuitsLoading] = useState(true);

    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    const [circuits, setCircuits] = useState([]);

    useEffect(() => {
        setCircuitsLoading(true);

        sendRpcRequest(COMMANDS.GET_CIRCUITS, {})
            .then((response) => {
                setCircuits(response.circuits);
                setCircuitsLoading(false);
            })
            .catch((response) => {
                setError(true);
                setCircuitsLoading(false);

                addAlert(AlertVariant.danger, "Failed to fetch circuits");
            })
    }, [refreshCounter]);

    const refresh = () => {
        setRefreshCounter(refreshCounter + 1);
    }

    console.log("circuits", circuits)

    return areCircuitsLoading
        ? <Bullseye style={{ height: 150 }}><Spinner /></Bullseye>
        : isError
            ? <ErrorState />
            : (
                <Fragment>
                    <Split hasGutter style={{ margin: 16 }}>
                        <SplitItem>
                            <Title headingLevel="h1">
                                Circuits
                            </Title>
                        </SplitItem>
                        <SplitItem isFilled />
                        <SplitItem>
                            <Button onClick={refresh} icon={<RedoIcon />}>Refresh</Button>
                        </SplitItem>
                    </Split>
                    <Table variant="compact" style={{ border: "1px solid lightgray", borderTop: 0 }}>
                        <Thead>
                            <Tr>
                                <Th>Hash</Th>
                                <Th>Constraint count</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {circuits.length === 0
                                ? (
                                    <Tr>
                                        <Td colSpan={100} style={{ backgroundColor: "#EEE" }}>
                                            <Bullseye>
                                                There are no circuits
                                            </Bullseye>
                                        </Td>
                                    </Tr>
                                ) : circuits.map((circuit) => (
                                    <Tr key={circuit.hash}>
                                        <Td dataLabel="Hash">
                                            <Hash>{circuit.hash}</Hash>
                                        </Td>
                                        <Td dataLabel="Constraint count">
                                            {circuit.constraint_count}
                                        </Td>
                                    </Tr>
                                ))}
                        </Tbody>
                    </Table>
                </Fragment >
            )
};

export default CircuitsTab;
