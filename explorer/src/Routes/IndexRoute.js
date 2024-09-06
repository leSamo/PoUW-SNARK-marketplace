import { Fragment, useState } from "react";
import { Tab, Tabs, TabTitleText } from "@patternfly/react-core";
import ConfirmedBlocksTab from "../Tabs/ConfirmedBlocksTab";
import TransactionsTab from "../Tabs/TransactionsTab";

// TODO: 1 route per tab
const IndexRoute = ({ addAlert }) => {
    const [pageSelectedTab, setPageSelectedTab] = useState(0);

    return (
        <Fragment>
            <Tabs activeKey={pageSelectedTab} onSelect={(e, index) => setPageSelectedTab(index)}>
                <Tab eventKey={0} title={<TabTitleText>Confirmed Blocks</TabTitleText>}>
                    <ConfirmedBlocksTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={1} title={<TabTitleText>Transactions</TabTitleText>}>
                    <TransactionsTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={2} title={<TabTitleText>Circuits</TabTitleText>}>
                    Circuits
                </Tab>
            </Tabs>
        </Fragment>
    );
}

export default IndexRoute;
