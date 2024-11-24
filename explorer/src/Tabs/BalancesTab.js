import React, { Fragment, useEffect, useMemo, useState } from 'react';
import { Chart, ChartAxis, ChartGroup, ChartLine, ChartThemeColor, ChartLegendTooltip, createContainer } from '@patternfly/react-charts/victory';
import { AlertVariant, Button, Split, SplitItem, Title } from '@patternfly/react-core';
import { COMMANDS, sendRpcRequest } from "../Helpers/rpc";
import { RedoIcon } from '@patternfly/react-icons';

const BalancesTab = ({ addAlert }) => {
    const [blocks, setBlocks] = useState([]);
    const [areBlocksLoading, setBlocksLoading] = useState(true);
    const [isError, setError] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    useEffect(() => {
        setBlocksLoading(true);

        sendRpcRequest(COMMANDS.GET_LATEST_BLOCK_ID, {})
            .then((response) => {
                const sequence = Array.from({ length: response.latest_id + 1 }, (_, i) => i);

                Promise.all(sequence.map(block_id => sendRpcRequest(COMMANDS.GET_BLOCK, [block_id])))
                    .then(result => {
                        setBlocksLoading(false);

                        setBlocks(result.map(block => block.block.body.state_tree));
                    })
            })
            .catch((response) => {
                setError(true);
                setBlocksLoading(false);

                addAlert(AlertVariant.danger, "Failed to fetch blocks");
            })
    }, [refreshCounter]);

    console.log("blocks", blocks)

    const allAccounts = useMemo(() => {
        const accounts = new Set();

        blocks.forEach(block => Object.keys(block).forEach(account => accounts.add(account)));

        return accounts;
    }, [refreshCounter, blocks]);

    console.log("allAccounts", allAccounts)

    const refresh = () => {
        setRefreshCounter(refreshCounter + 1);
    }

    const CursorVoronoiContainer = createContainer("voronoi", "cursor");
    const legendData = [...allAccounts].map(account => ({ childName: account, name: account + "   " }));

    return (
        <Fragment>
            <Split hasGutter style={{ margin: 16 }}>
                <SplitItem>
                    <Title headingLevel="h1">
                        Balances
                    </Title>
                </SplitItem>
                <SplitItem isFilled />
                <SplitItem>
                    <Button onClick={refresh} icon={<RedoIcon />}>Refresh</Button>
                </SplitItem>
            </Split>
            <div style={{ height: '500px', width: '100%' }}>
                <Chart
                    ariaDesc="Balances of accounts across blocks"
                    ariaTitle="Balances of accounts across blocks"
                    containerComponent={
                        <CursorVoronoiContainer
                            cursorDimension="x"
                            labels={({ datum }) => `${datum.y}`}
                            labelComponent={<ChartLegendTooltip legendData={legendData} title={(datum) => `Block with serial ID ${datum.x}`} />}
                            mouseFollowTooltips
                            voronoiDimension="x"
                            voronoiPadding={50}
                        />
                    }
                    legendData={legendData}
                    legendPosition="bottom"
                    height={500}
                    width={1500}
                    maxDomain={{ y: 1000 }}
                    minDomain={{ y: 0 }}
                    padding={{
                        bottom: 75, // Adjusted to accommodate legend
                        left: 50,
                        right: 50,
                        top: 50
                    }}
                    themeColor={ChartThemeColor.blue}
                >
                    <ChartAxis tickValues={[...Array(blocks.length).keys()]} />
                    <ChartAxis dependentAxis showGrid />
                    <ChartGroup>
                        {
                            [...allAccounts].map(account => (
                                <ChartLine
                                    data={
                                        blocks.map((block, index) => (
                                            {
                                                x: index.toString(),
                                                y: block[account] ?? 0
                                            }
                                        ))
                                    }
                                    name={account}
                                />
                            ))
                        }
                    </ChartGroup>
                </Chart>
            </div>
        </Fragment>
    );
};

export default BalancesTab;
