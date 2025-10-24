import { Button, ButtonVariant, Form, FormGroup, List, ListItem, MenuToggle, NumberInput, Select, SelectList, SelectOption, Sidebar, SidebarContent, SidebarPanel, Slider, Tab, Tabs, TabTitleText, Text, TextContent, TextInput, TextInputTypes, Title } from '@patternfly/react-core';
import React, { Fragment, useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';

const NODE = 0;
const EDGE = 1;

const NETWORK_TYPE = {
    FULLY_CONNECTED: "Fully connected",
    LINE: "Line",
    RING: "Ring"
}

const generateFullyConnectedTopologyEdges = (n) => {
    const edges = [];

    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            edges.push({ from: i, to: j });
        }
    }

    return edges;
}

const generateLineTopologyEdges = (n) => {
    const edges = [];

    for (let i = 0; i < n; i++) {
        edges.push({ from: i, to: i + 1 });
    }

    return edges;
}

const generateRingTopologyEdges = (n) => {
    const edges = [];

    for (let i = 0; i < n; i++) {
        edges.push({ from: i, to: i + 1 });
    }

    edges.push({ from: n - 1, to: 0 });

    return edges;
}

const SimulatorTab = ({ addAlert }) => {
    const [pageSelectedTab, setPageSelectedTab] = useState(0);

    const [randomSeed, setRandomSeed] = useState(0);
    const [stopTime, setStopTime] = useState(1000);
    const [nodeCount, setNodeCount] = useState(4);

    const [isNetworkTypeDropwdownOpen, setNetworkTypeDropdownOpen] = useState(false);
    const [networkTypeSelected, setNetworkTypeSelected] = useState(NETWORK_TYPE.FULLY_CONNECTED);

    const [simulationRefreshCounter, setSimulationRefreshCounter] = useState(0);

    const [currentTimeValue, setCurrentTimeValue] = useState(0);
    const [inputCurrentTimeValue, setInputCurrentTimeValue] = useState(0);

    const [selectedObjectId, setSelectedObjectId] = useState(null);
    const [selectedObjectType, setSelectedObjectType] = useState(null);

    const [isEditingTopology, setEditingTopology] = useState(false);

    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);

    const onNetworkTypeSelect = (_event, value) => {
        setNetworkTypeSelected(value);
        setNetworkTypeDropdownOpen(false);
    };

    const containerRef = useRef(null);

    const generateNetwork = () => {
        const _nodes = [...Array(nodeCount)].map((_, id) => ({ id, label: `Node ${id}` }))
        let _edges;

        switch (networkTypeSelected) {
            case NETWORK_TYPE.FULLY_CONNECTED: {
                _edges = generateFullyConnectedTopologyEdges(nodeCount);
                break;
            }
            case NETWORK_TYPE.LINE: {
                _edges = generateLineTopologyEdges(nodeCount);
                break;
            }
            case NETWORK_TYPE.RING: {
                _edges = generateRingTopologyEdges(nodeCount);
                break;
            }
        }

        setNodes(_nodes);
        setEdges(_edges);
    }

    const data = { nodes, edges };
    const options = {
        nodes: {
            shape: 'dot',
            size: 16,
            font: { color: '#000' },
            color: { background: '#0074D9' }
        },
        edges: {
            color: '#ccc',
        },
        interaction: {
            hover: true,
            dragView: false,
            zoomView: false,
            selectConnectedEdges: false,
            hoverConnectedEdges: false
        }
    };

    useEffect(() => {
        const network = new Network(containerRef.current, data, options);

        network.on('click', (params) => {
            if (params.nodes.length > 0) {
                setSelectedObjectId(params.nodes[0]);
                setSelectedObjectType(NODE);
                setPageSelectedTab(3);
            }

            if (params.edges.length > 0) {
                setSelectedObjectId(params.edges[0]);
                setSelectedObjectType(EDGE);
                setPageSelectedTab(3);
            }
        });

        network.on("oncontext", (params) => {
            params.event.preventDefault();

            setSelectedObjectId(null);
            setSelectedObjectType(null);

            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const nodeIndex = nodes.findIndex(node => node.id === nodeId);

                setNodes([...nodes.slice(0, nodeIndex), ...nodes.slice(nodeIndex + 1)]);

            } else if (params.edges.length > 0) {
                const edgeId = params.edges[0];
                const edgeIndex = edges.findIndex(edge => edge.id === edgeId);

                setEdges([...edges.slice(0, edgeIndex), ...edges.slice(edgeIndex + 1)]);
            }
        });

        network.on('deselectNode', (params) => {
            setSelectedObjectId(null);
            setSelectedObjectType(null);
        });

        network.on('deselectEdge', (params) => {
            setSelectedObjectId(null);
            setSelectedObjectType(null);
        });

        network.on("hoverNode", function (params) {
            network.canvas.body.container.style.cursor = 'pointer';
        });

        network.on("blurNode", function (params) {
            network.canvas.body.container.style.cursor = 'default';
        });

        return () => network.destroy();
    }, [nodes, edges]);

    return (
        <div style={{ margin: 16 }}>
            <Title headingLevel="h1">
                Simulator
            </Title>
            <Sidebar hasGutter hasBorder>
                <SidebarPanel width={{
                    default: "width_25"
                }}>
                    <Form>
                        <Tabs activeKey={pageSelectedTab} onSelect={(e, index) => setPageSelectedTab(index)}>
                            <Tab eventKey={0} title={<TabTitleText>Simulation</TabTitleText>}>
                                <FormGroup label="Random seed">
                                    <TextInput
                                        value={randomSeed}
                                        type={TextInputTypes.number}
                                        onChange={(_event, value) => setRandomSeed(value)}
                                    />
                                </FormGroup>
                                <FormGroup label="Stop time">
                                    <TextInput
                                        value={stopTime}
                                        type={TextInputTypes.number}
                                        onChange={(_event, value) => setStopTime(value)}
                                    />
                                </FormGroup>
                            </Tab>
                            <Tab eventKey={1} title={<TabTitleText>Network</TabTitleText>}>
                                <FormGroup label="Node count">
                                    <NumberInput
                                        value={nodeCount}
                                        onChange={(event) => setNodeCount(+event.target.value)}
                                        onPlus={() => setNodeCount(nodeCount + 1)}
                                        onMinus={() => setNodeCount(nodeCount - 1)}
                                    />
                                </FormGroup>
                                <FormGroup label="Connection type">
                                    <Select
                                        isOpen={isNetworkTypeDropwdownOpen}
                                        selected={networkTypeSelected}
                                        onSelect={onNetworkTypeSelect}
                                        onOpenChange={(isOpen) => setNetworkTypeDropdownOpen(isOpen)}
                                        toggle={(toggleRef) => (
                                            <MenuToggle
                                                ref={toggleRef}
                                                onClick={() => setNetworkTypeDropdownOpen(!isNetworkTypeDropwdownOpen)}
                                                isExpanded={isNetworkTypeDropwdownOpen}
                                                style={{ width: "100%" }}
                                            >
                                                {networkTypeSelected}
                                            </MenuToggle>
                                        )}
                                        shouldFocusToggleOnSelect
                                    >
                                        <SelectList>
                                            {Object.entries(NETWORK_TYPE).map(([k, v]) => (
                                                <SelectOption value={v} key={k}>
                                                    {v}
                                                </SelectOption>
                                            ))}
                                        </SelectList>
                                    </Select>
                                </FormGroup>
                                <Button variant="secondary" style={{ width: "100%", marginTop: 16 }} onClick={() => generateNetwork()}>
                                    Generate network
                                </Button>
                                {isEditingTopology
                                    ? (
                                        <Button variant="warning" style={{ width: "100%", marginTop: 16 }} onClick={() => setEditingTopology(false)}>
                                            Edit topology
                                        </Button>
                                    )
                                    : (
                                        <div style={{ marginTop: 16 }}>
                                            <List>
                                                <ListItem>
                                                    Select and right click to remove a node or a connection
                                                </ListItem>
                                                <ListItem>
                                                    Hover over a node and scroll to change its consensual power
                                                </ListItem>
                                                <ListItem>
                                                    Hover over a connection and scroll to change its latency
                                                </ListItem>
                                            </List>
                                            <Button variant="warning" style={{ width: "100%", marginTop: 16 }} onClick={() => setEditingTopology(true)}>
                                                Stop editing topology
                                            </Button>
                                        </div>
                                    )
                                }
                            </Tab>
                            <Tab eventKey={2} title={<TabTitleText>Events</TabTitleText>}>
                                There are currently no events logged
                            </Tab>
                            <Tab eventKey={3} title={<TabTitleText>Inspect</TabTitleText>}>
                                {selectedObjectId === null
                                    ? "Select a node to display its details"
                                    : selectedObjectType === NODE
                                        ? (
                                            <Form>
                                                <TextContent>
                                                    <Text component="h5">{nodes.find(node => node.id === selectedObjectId).label}</Text>
                                                </TextContent>
                                                <FormGroup label="Peers">
                                                    <Text>
                                                        TODO: Peer count
                                                    </Text>
                                                </FormGroup>
                                                <FormGroup label="Pending coin txs">
                                                    <Text>
                                                        TODO: Pending coin txs
                                                    </Text>
                                                </FormGroup>
                                                <FormGroup label="Pending proof txs">
                                                    <Text>
                                                        TODO: Pending proof txs
                                                    </Text>
                                                </FormGroup>
                                                <FormGroup label="Known blocks">
                                                    <Text>
                                                        TODO: Known blocks
                                                    </Text>
                                                </FormGroup>
                                                <FormGroup label="Mining">
                                                    <Text>
                                                        TODO: Mining
                                                    </Text>
                                                </FormGroup>
                                            </Form>
                                        )
                                        : (
                                            <Form>
                                                <TextContent>
                                                    <Text component="h5">
                                                        Edge between&nbsp;
                                                        {edges.find(edge => edge.id === selectedObjectId).from} and&nbsp;
                                                        {edges.find(edge => edge.id === selectedObjectId).to}</Text>
                                                </TextContent>
                                                <FormGroup label="Latency (TODO)">
                                                    <Text>
                                                        <TextInput
                                                            isDisabled
                                                            value={0}
                                                            type={TextInputTypes.number}
                                                            onChange={(_event, value) => setStopTime(value)}
                                                        />
                                                    </Text>
                                                </FormGroup>
                                                <FormGroup label="Throughput (TODO)">
                                                    <Text>
                                                        <TextInput
                                                            isDisabled
                                                            value="∞"
                                                            onChange={(_event, value) => setStopTime(value)}
                                                        />
                                                    </Text>
                                                </FormGroup>
                                            </Form>
                                        )
                                }
                            </Tab>
                        </Tabs>
                        <Button
                            variant={ButtonVariant.primary}
                            onClick={() => setSimulationRefreshCounter(simulationRefreshCounter + 1)}
                        >
                            Run simulation
                        </Button>
                        <Button
                            variant={ButtonVariant.secondary}
                            onClick={() => { }}
                        >
                            Save configuration
                        </Button>
                    </Form>
                </SidebarPanel>
                <SidebarContent>
                    <div style={{ marginBottom: 8, padding: 16, border: "solid 1px black" }}>
                        <Slider
                            hasTooltipOverThumb
                            isInputVisible
                            value={currentTimeValue}
                            inputValue={inputCurrentTimeValue}
                            onChange={(_event, value) => {
                                setCurrentTimeValue(value);
                                setInputCurrentTimeValue(value);
                            }}
                        />
                    </div>
                    <div ref={containerRef} style={{ width: '600px', height: '400px', border: '1px solid black' }} />
                </SidebarContent>
            </Sidebar>
        </div>
    );
};

export default SimulatorTab;
