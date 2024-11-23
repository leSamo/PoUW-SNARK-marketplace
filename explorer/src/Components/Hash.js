import React from 'react';
import { Button, Popover, Split, SplitItem } from '@patternfly/react-core';
import { CopyIcon } from '@patternfly/react-icons';

const Hash = ({ children }) => (
    <Split>
        <SplitItem>
        <Popover bodyContent={children}>
            <Button
                isInline
                variant="plain"
                style={{ textDecoration: "underline", textDecorationStyle: "dotted", padding: 0, width: "fit-content", fontFamily: 'monospace' }}
            >
                {children?.slice(0, 12)}
            </Button>
        </Popover>
        </SplitItem>
        <SplitItem>
        <Button
            variant="plain"
            aria-label="Copy"
            onClick={() => navigator.clipboard.writeText(children)} style={{ padding: 0, paddingLeft: 8 }}
        >
            <CopyIcon />
        </Button>
        </SplitItem>
    </Split>
)

export default Hash;
