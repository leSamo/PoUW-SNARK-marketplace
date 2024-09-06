import { Masthead, MastheadContent, MastheadMain, Split, SplitItem, SearchInput, Button } from "@patternfly/react-core";
import { useState } from "react";

const Header = () => {
    const [searchValue, setSearchValue] = useState("");

    return (
        <Masthead>
            <MastheadMain>
                PoUW SNARK Marketplace Blockchain Explorer
            </MastheadMain>
            <MastheadContent>
                <Split hasGutter style={{ width: '100%' }}>
                    <SplitItem isFilled />
                    <SplitItem>
                        <SearchInput
                            placeholder="Search by address or hash"
                            value={searchValue}
                            onChange={(_event, value) => setSearchValue(value)}
                            onClear={() => setSearchValue('')}
                        />
                    </SplitItem>
                    <SplitItem>
                        <Button>Search</Button>
                    </SplitItem>
                </Split>
            </MastheadContent>
        </Masthead>
    );
}

export default Header;
