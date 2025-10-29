import { EmptyState, EmptyStateBody, EmptyStateHeader, EmptyStateIcon } from "@patternfly/react-core";
import { ExclamationCircleIcon } from "@patternfly/react-icons";
import { RPC_PORT } from "../Helpers/rpc";

const ErrorState = () => (
    <EmptyState>
        <EmptyStateHeader
            titleText="An error occured"
            icon={<EmptyStateIcon icon={ExclamationCircleIcon} color="var(--pf-v5-global--danger-color--100)" />}
        />
        <EmptyStateBody>
            Is your client running with RPC interface on port {RPC_PORT}?
        </EmptyStateBody>
    </EmptyState>
);

export default ErrorState;
