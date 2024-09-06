import { EmptyState, EmptyStateBody, EmptyStateHeader, EmptyStateIcon } from "@patternfly/react-core";
import { ExclamationCircleIcon } from "@patternfly/react-icons";


const ErrorState = () => (
    <EmptyState>
        <EmptyStateHeader
            titleText="An error occured"
            icon={<EmptyStateIcon icon={ExclamationCircleIcon} color="var(--pf-v5-global--danger-color--100)" />}
        />
        <EmptyStateBody>
            Is your client running with RPC interface on port 9545?
        </EmptyStateBody>
    </EmptyState>
);

export default ErrorState;
