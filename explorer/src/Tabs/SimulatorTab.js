import { Button, ButtonVariant, Form, FormGroup, MenuToggle, NumberInput, Select, SelectList, SelectOption, Sidebar, SidebarContent, SidebarPanel, Slider, Tab, Tabs, TabTitleText, Text, TextInput, TextInputTypes, Title } from '@patternfly/react-core';
import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';

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

    const [selectedNodeId, setSelectedNodeId] = useState(null);

    const onNetworkTypeSelect = (_event, value) => {
        setNetworkTypeSelected(value);
        setNetworkTypeDropdownOpen(false);
    };

    const containerRef = useRef(null);

    const nodes = [...Array(nodeCount)].map((_, id) => ({ id, label: `Node ${id}` }))
    let edges;

    switch (networkTypeSelected) {
        case NETWORK_TYPE.FULLY_CONNECTED: {
            edges = generateFullyConnectedTopologyEdges(nodeCount);
            break;
        }
        case NETWORK_TYPE.LINE: {
            edges = generateLineTopologyEdges(nodeCount);
            break;
        }
        case NETWORK_TYPE.RING: {
            edges = generateRingTopologyEdges(nodeCount);
            break;
        }
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
            zoomView: false
        }
    };

    useEffect(() => {
        const network = new Network(containerRef.current, data, options);

        network.on('click', (params) => {
            if (params.nodes.length > 0) {
                setSelectedNodeId(params.nodes[0]);
            }
        });

        network.on('deselectNode', (params) => {
            setSelectedNodeId(null);
        });

        network.on("hoverNode", function (params) {
            network.canvas.body.container.style.cursor = 'pointer';
        });

        network.on("blurNode", function (params) {
            network.canvas.body.container.style.cursor = 'default';
        });

        return () => network.destroy();
    }, [simulationRefreshCounter]);

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
                            </Tab>
                            <Tab eventKey={2} title={<TabTitleText>Events</TabTitleText>}>
                                There are currently no events logged
                            </Tab>
                            <Tab eventKey={3} title={<TabTitleText>Node detail</TabTitleText>}>
                                {selectedNodeId == null
                                    ? "Select a node to display its details"
                                    : (
                                        <Form>
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
                                }
                            </Tab>
                        </Tabs>
                        <Button
                            variant={ButtonVariant.primary}
                            onClick={() => setSimulationRefreshCounter(simulationRefreshCounter + 1)}
                        >
                            Run simulation
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
