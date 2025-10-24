import { Masthead, MastheadContent, MastheadMain, Split, SplitItem, Dropdown, MenuToggle, DropdownList, DropdownItem, Modal, Button, ModalVariant, FileUpload, Tile, Form, FormGroup, TextArea, TextInput, Divider, Bullseye, Spinner, spinnerSize, ButtonSize, Tooltip } from "@patternfly/react-core";
import { PlusCircleIcon, TrashIcon, WalletIcon } from "@patternfly/react-icons";
import { useContext, useEffect, useState } from "react";
import { ECPrivateKey, pemToBuffer } from "../Helpers/key";
import { AccountContext, ACCOUNTS_LOCAL_STORAGE_KEY } from "../App";
const secp256k1 = require('secp256k1');
var asn1 = require('asn1.js');

const PRIVATE_KEY_METHOD = {
    enterText: "enterText",
    uploadFile: "uploadFile"
}

const Header = ({ refreshAccounts }) => {
    // const [searchValue, setSearchValue] = useState("");
    const [isUserDropdownOpen, setUserDropdownOpen] = useState(false);
    const [isUserModalOpen, setUserModalOpen] = useState(false);

    // This is not a good practice in production applications, this explorer exists just for demonstration purposes
    const [privateKey, setPrivateKey] = useState(null);

    const [modalAccountName, setModalAccountName] = useState("");
    const [modalInputField, setModalInputField] = useState("");
    const [modalFilename, setModalFilename] = useState("");
    const [modalPrivateKeyMethodSelected, setModalPrivateKeyMethodSelected] = useState(PRIVATE_KEY_METHOD.enterText);
    const [modalPrivateKeyString, setModalPrivateKeyString] = useState("");

    const accounts = useContext(AccountContext);

    const isKeyValid = (value) => {
        try {
            const buffer = pemToBuffer(value);
            const decodedKey = ECPrivateKey.decode(buffer, 'der');
            const isValid = secp256k1.privateKeyVerify(decodedKey.privateKey);

            return isValid;
        }
        catch {
            return false;
        }
    }

    const onUserModalClose = () => {
        setUserModalOpen(!isUserModalOpen);
        setModalPrivateKeyString("");
        setModalPrivateKeyMethodSelected(PRIVATE_KEY_METHOD.enterText);
        // TODO: Clear uploaded file
    }

    const addNewAccount = () => {
        // TODO: Forbid duplicate names
        onUserModalClose();

        const newAccount = {
            name: modalAccountName,
            privateKey: modalPrivateKeyString
        };

        localStorage.setItem(ACCOUNTS_LOCAL_STORAGE_KEY, JSON.stringify([...accounts, newAccount]));
        refreshAccounts();
    }

    const removeAccount = (name) => {
        const filteredAccounts = accounts.filter(acc => acc.name !== name);

        localStorage.setItem(ACCOUNTS_LOCAL_STORAGE_KEY, JSON.stringify(filteredAccounts));
        refreshAccounts();
    }

    return (
        <Masthead>
            <MastheadMain>
                PoUW SNARK Marketplace Blockchain Explorer
            </MastheadMain>
            <MastheadContent>
                <Split hasGutter style={{ width: '100%' }}>
                    <SplitItem isFilled />
                    <SplitItem>
                        <Dropdown
                            isOpen={isUserDropdownOpen}
                            onSelect={() => setUserDropdownOpen(false)}
                            onOpenChange={(isOpen) => setUserDropdownOpen(isOpen)}
                            toggle={(toggleRef) => (
                                <MenuToggle style={{ minWidth: 250 }} ref={toggleRef} onClick={() => setUserDropdownOpen(!isUserDropdownOpen)} isExpanded={isUserDropdownOpen}>
                                    Select account
                                </MenuToggle>
                            )}
                            shouldFocusToggleOnSelect
                        >
                            <DropdownList>
                                {accounts === null ?
                                    (
                                        <Bullseye>
                                            <Spinner size={spinnerSize.lg} />
                                        </Bullseye>
                                    ) : accounts.length === 0 ? (
                                        <Bullseye>
                                            <span style={{ padding: 4, fontSize: 12, color: 'gray' }}>
                                                No accounts set up yet
                                            </span>
                                        </Bullseye>
                                    ) : (
                                        accounts.map(account => (
                                            <div key={account.name} style={{ paddingLeft: 12, paddingRight: 12, paddingTop: 4, paddingBottom: 4 }}>
                                                <Split hasGutter>
                                                    <SplitItem>
                                                        <WalletIcon />
                                                    </SplitItem>
                                                    <SplitItem>
                                                        {account.name}
                                                    </SplitItem>
                                                    <SplitItem isFilled />
                                                    <SplitItem>
                                                        <Tooltip content="Delete account">
                                                            <Button variant="danger" size={ButtonSize.sm} onClick={() => window.confirm(`Are you sure you want to delete account '${account.name}'?`) && removeAccount(account.name)}>
                                                                <TrashIcon />
                                                            </Button>
                                                        </Tooltip>
                                                    </SplitItem>
                                                </Split>
                                            </div>
                                        ))
                                    )
                                }
                                <Divider />
                                <Bullseye>
                                    <Button onClick={() => setUserModalOpen(true)}>
                                        <PlusCircleIcon style={{ marginRight: 4 }} />
                                        Add account
                                    </Button>
                                </Bullseye>
                            </DropdownList>
                        </Dropdown>
                    </SplitItem>
                    {/*
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
                    */}
                </Split>
            </MastheadContent>
            <Modal
                variant={ModalVariant.small}
                title="Add account"
                isOpen={isUserModalOpen}
                onClose={onUserModalClose}
                actions={[
                    <Button
                        key="confirm"
                        variant="primary"
                        onClick={addNewAccount}
                        isDisabled={
                            !isKeyValid(modalPrivateKeyString) || modalAccountName.trim() == ""
                        }
                    >
                        Confirm
                    </Button>,
                    <Button key="cancel" variant="link" onClick={onUserModalClose}>
                        Cancel
                    </Button>
                ]}
            >
                <Form>
                    <FormGroup label="Account name">
                        <TextInput
                            value={modalAccountName}
                            onChange={(e, value) => setModalAccountName(value)}
                            placeholder="Enter custom account name"
                        />
                    </FormGroup>
                    <FormGroup label="Supply private key">
                        <Tile
                            title="Enter text"
                            isSelected={modalPrivateKeyMethodSelected === PRIVATE_KEY_METHOD.enterText}
                            onClick={() => setModalPrivateKeyMethodSelected(PRIVATE_KEY_METHOD.enterText)}
                        />
                        <Tile
                            title="Upload from file"
                            isSelected={modalPrivateKeyMethodSelected === PRIVATE_KEY_METHOD.uploadFile}
                            onClick={() => setModalPrivateKeyMethodSelected(PRIVATE_KEY_METHOD.uploadFile)}
                            isDisabled
                        >
                            To be implemented
                        </Tile>
                    </FormGroup>

                    {modalPrivateKeyMethodSelected === PRIVATE_KEY_METHOD.enterText && (
                        <FormGroup label="Enter private key string">
                            <TextArea
                                aria-label="Enter private key string"
                                resizeOrientation="vertical"
                                placeholder={"Enter private key in PEM or base64 format"}
                                autoResize
                                value={modalPrivateKeyString}
                                onChange={(e, value) => {
                                    setModalPrivateKeyString(value);
                                }}
                                validated={(isKeyValid(modalPrivateKeyString) || modalPrivateKeyString.length === 0) || "error"}
                            />
                        </FormGroup>
                    )}

                    {modalPrivateKeyMethodSelected === PRIVATE_KEY_METHOD.uploadFile && (
                        <FormGroup label="File upload">
                            <FileUpload
                                value={modalInputField}
                                filename={modalFilename}
                                filenamePlaceholder="Drag and drop a private key file or click 'Upload'"
                                onFileInputChange={() => console.log("file input change")}
                                onDataChange={() => console.log("data change")}
                                onTextChange={() => console.log("text change")}
                                onReadStarted={() => console.log("read started")}
                                onReadFinished={() => console.log("read finished")}
                                onClearClick={() => console.log("clear")}
                                isLoading={false}
                                allowEditingUploadedText={false}
                                browseButtonText="Upload"
                            />
                        </FormGroup>
                    )}
                </Form>
            </Modal>
        </Masthead>
    );
}

export default Header;
