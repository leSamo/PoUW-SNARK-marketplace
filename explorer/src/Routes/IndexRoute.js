import { Fragment, useState } from "react";
import { Tab, Tabs, TabTitleText } from "@patternfly/react-core";
import ConfirmedBlocksTab from "../Tabs/ConfirmedBlocksTab";
import CoinTransactionsTab from "../Tabs/CoinTransactionsTab";
import CircuitsTab from "../Tabs/CircuitsTab";
import BalancesTab from "../Tabs/BalancesTab";
import ProofTransactionsTab from "../Tabs/ProofTransactionsTab";

// TODO: 1 route per tab
const IndexRoute = ({ addAlert }) => {
    const [pageSelectedTab, setPageSelectedTab] = useState(0);

    return (
        <Fragment>
            <Tabs activeKey={pageSelectedTab} onSelect={(e, index) => setPageSelectedTab(index)}>
                <Tab eventKey={0} title={<TabTitleText>Confirmed Blocks</TabTitleText>}>
                    <ConfirmedBlocksTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={1} title={<TabTitleText>Coin Transactions</TabTitleText>}>
                    <CoinTransactionsTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={2} title={<TabTitleText>Proof Transactions</TabTitleText>}>
                    <ProofTransactionsTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={3} title={<TabTitleText>Circuits</TabTitleText>}>
                    <CircuitsTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={4} title={<TabTitleText>Balances</TabTitleText>}>
                    <BalancesTab addAlert={addAlert} />
                </Tab>
            </Tabs>
        </Fragment>
    );
}

export default IndexRoute;
