import { Button, Form, FormGroup, Modal, ModalVariant, TextInput, TextInputTypes } from "@patternfly/react-core";
import { useContext, useState } from "react";
import { AccountContext } from "../App";
import { ECPrivateKey, pemToBuffer } from "../Helpers/key";
import { Buffer } from 'buffer';
import { COMMANDS, sendRpcRequest } from "../Helpers/rpc";
const secp256k1 = require('secp256k1');
const crypto = require('crypto');
const EC = require('elliptic').ec;
const ec = new EC('secp256k1');

const CreateCoinTxModal = ({ isOpen, setOpen }) => {
    const [addressTo, setAddressTo] = useState("");
    const [amount, setAmount] = useState("");

    const accounts = useContext(AccountContext);

    const onClose = () => {
        // TODO: Clear all fields
        setOpen(false);

        setAddressTo("");
        setAmount("");
    }

    const activeAccount = accounts?.find(account => account.isActive === true) ?? null;

    let activeAccountHexAddress = null;

    if (activeAccount) {
        const buffer = pemToBuffer(activeAccount.privateKey);
        const decodedKey = ECPrivateKey.decode(buffer, 'der');
        const pubCompressed = secp256k1.publicKeyCreate(decodedKey.privateKey, true);
        activeAccountHexAddress = Buffer.from(pubCompressed).toString('hex');
    }

    const onSubmit = () => {
        const transactionObject = {
            address_from: activeAccountHexAddress,
            address_to: Buffer.from(addressTo).toString('hex'),
            amount: Number(amount)
        }

        const timestamp = Math.round(Date.now() / 1000) * 1000
        const serialized_tx = [
            timestamp.toString(),
            transactionObject.address_from,
            transactionObject.address_to,
            amount.toString()
        ].join("|")

        console.log(">>>", serialized_tx)

        const tx_hash = crypto.createHash('sha256')
            .update(serialized_tx)
            .digest('hex');
        
        transactionObject.id = tx_hash;

        const key = ec.keyFromPrivate(activeAccount.privateKey, 'hex');

        const signature = key.sign(tx_hash, { canonical: true });

        transactionObject.signature = signature;

        sendRpcRequest(COMMANDS.BROADCAST_PENDING_COIN_TX, transactionObject);

        onClose();
    }

    const validateAmount = () => {
        const num = Number(amount);

        if (isNaN(num) || !Number.isInteger(num) || num <= 0) {
            return "error";
        }
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
                    onClick={onSubmit}
                    isDisabled={validateAmount() === 'error'}
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
                        value={addressTo}
                        onChange={(e, value) => setAddressTo(value)}
                        placeholder="Enter address"
                    />
                </FormGroup>
                <FormGroup label="Amount">
                    <TextInput
                        isRequired
                        value={amount}
                        onChange={(e, value) => setAmount(value)}
                        placeholder="Enter amount"
                        validated={amount !== "" && validateAmount()}
                    />
                </FormGroup>
            </Form>
        </Modal>
    );
}

export default CreateCoinTxModal;
