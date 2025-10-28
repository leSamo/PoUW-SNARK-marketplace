import { Button, Form, FormGroup, Modal, ModalVariant, TextInput } from "@patternfly/react-core";
import { useContext, useState } from "react";
import { AccountContext } from "../App";
import { ECPrivateKey, pemToBuffer } from "../Helpers/key";
import { Buffer } from 'buffer';
const secp256k1 = require('secp256k1');

const CreateCoinTxModal = ({ isOpen, setOpen }) => {
    const [to, setTo] = useState("");
    const [amount, setAmount] = useState("");

    const accounts = useContext(AccountContext);

    const onClose = () => {
        // TODO: Clear all fields
        setOpen(false);
    }

    const activeAccount = accounts?.find(account => account.isActive === true) ?? null;

    let activeAccountHexAddress = null;

    if (activeAccount) {
        const buffer = pemToBuffer(activeAccount.privateKey);
        const decodedKey = ECPrivateKey.decode(buffer, 'der');
        const pubCompressed = secp256k1.publicKeyCreate(decodedKey.privateKey, true);
        activeAccountHexAddress = Buffer.from(pubCompressed).toString('hex');
    }

    return (
        <Modal
            variant={ModalVariant.small}
            title="Create a new coin transaction"
            isOpen={isOpen}
            onClose={onClose}
            actions={[
                <Button
                    key="confirm"
                    variant="primary"
                    onClick={() => {
                        onClose()
                    }}
                >
                    Create
                </Button>,
                <Button key="cancel" variant="link" onClick={onClose}>
                    Cancel
                </Button>
            ]}
        >
            <Form>
                <FormGroup label="Address from">
                    <TextInput
                        isDisabled
                        value={activeAccountHexAddress}
                    />
                </FormGroup>
                <FormGroup label="Address to">
                    <TextInput
                        isRequired
                        value={to}
                        onChange={(e, value) => setTo(value)}
                        placeholder="Enter address"
                    />
                </FormGroup>
                <FormGroup label="Amount">
                    <TextInput
                        isRequired
                        value={amount}
                        onChange={(e, value) => setAmount(value)}
                        placeholder="Enter amount"
                    />
                </FormGroup>
            </Form>
        </Modal>
    );
}

export default CreateCoinTxModal;
