import { Masthead, MastheadContent, MastheadMain, Split, SplitItem, Dropdown, MenuToggle, DropdownList, DropdownItem, Modal, Button, ModalVariant, FileUpload, Tile, Form, FormGroup, TextArea } from "@patternfly/react-core";
import { PlusCircleIcon } from "@patternfly/react-icons";
import { useEffect, useState } from "react";
import { ECPrivateKey, pemToBuffer } from "../Helpers/key";
const secp256k1 = require('secp256k1');
var asn1 = require('asn1.js');

const PRIVATE_KEY_METHOD = {
    enterText: "enterText",
    uploadFile: "uploadFile"
}

const Header = () => {
    // const [searchValue, setSearchValue] = useState("");
    const [isUserDropdownOpen, setUserDropdownOpen] = useState(false);
    const [isUserModalOpen, setUserModalOpen] = useState(false);

    // This is not a good practice in production applications, this explorer exists just for demonstration purposes
    const [privateKey, setPrivateKey] = useState(null);

    const [modalInputField, setModalInputField] = useState("");
    const [modalFilename, setModalFilename] = useState("");
    const [modalPrivateKeyMethodSelected, setModalPrivateKeyMethodSelected] = useState(PRIVATE_KEY_METHOD.enterText);
    const [modalEnterText, setModalEnterText] = useState("");

    useEffect(() => {
        // TODO: Validate if private key is valid
        const privateKeyLoaded = localStorage.getItem("privateKey")

        if (privateKeyLoaded !== null) {
            setPrivateKey(privateKeyLoaded);
        }
    }, [])

    const isKeyValid = (value) => {
        try {
            const buffer = pemToBuffer(value);

            const decodedKey = ECPrivateKey.decode(buffer, 'der');

            const isValid = secp256k1.privateKeyVerify(decodedKey.privateKey);
        }
        catch {
            return false;
        }

        return true;
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
                                <MenuToggle ref={toggleRef} onClick={() => setUserDropdownOpen(!isUserDropdownOpen)} isExpanded={isUserDropdownOpen}>
                                    No account
                                </MenuToggle>
                            )}
                            shouldFocusToggleOnSelect
                        >
                            <DropdownList>
                                <DropdownItem value={0} onClick={() => setUserModalOpen(true)}>
                                    <PlusCircleIcon style={{ marginRight: 4 }} />
                                    Add account
                                </DropdownItem>
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
                onClose={() => setUserModalOpen(!isUserModalOpen)}
                actions={[
                    <Button key="confirm" variant="primary" onClick={() => setUserModalOpen(!isUserModalOpen)}>
                        {/* TODO: Disable when key invalid */}
                        Confirm
                    </Button>,
                    <Button key="cancel" variant="link" onClick={() => setUserModalOpen(!isUserModalOpen)}>
                        Cancel
                    </Button>
                ]}
            >
                <Form>
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
                        />
                    </FormGroup>

                    {modalPrivateKeyMethodSelected === PRIVATE_KEY_METHOD.enterText && (
                        <FormGroup label="Enter private key string">
                            <TextArea
                                aria-label="Enter private key string"
                                resizeOrientation="vertical"
                                placeholder={"Enter private key in PEM or base64 format"}
                                autoResize
                                value={modalEnterText}
                                onChange={(e, value) => {
                                    setModalEnterText(value);
                                }}
                                validated={(isKeyValid(modalEnterText) || modalEnterText.length === 0) || "error"}
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
