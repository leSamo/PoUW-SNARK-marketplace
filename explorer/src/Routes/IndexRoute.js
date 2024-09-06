import { Fragment, useState } from "react";
import ConfirmedBlocksTab from "../Tabs/ConfirmedBlocksTab";
import { Tab, Tabs, TabTitleText } from "@patternfly/react-core";

const IndexRoute = ({ addAlert }) => {
    const [pageSelectedTab, setPageSelectedTab] = useState(0);

    return (
        <Fragment>
            <Tabs activeKey={pageSelectedTab} onSelect={(e, index) => setPageSelectedTab(index)}>
                <Tab eventKey={0} title={<TabTitleText>Confirmed Blocks</TabTitleText>}>
                    <ConfirmedBlocksTab addAlert={addAlert} />
                </Tab>
                <Tab eventKey={1} title={<TabTitleText>Unconfirmed transactions</TabTitleText>}>
                    Unconfirmed transactions
                </Tab>
                <Tab eventKey={2} title={<TabTitleText>Circuits</TabTitleText>}>
                    Circuits
                </Tab>
            </Tabs>
        </Fragment>
    );
}

export default IndexRoute;
