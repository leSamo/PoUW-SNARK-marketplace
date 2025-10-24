import React, { createContext, Fragment, useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import IndexRoute from './Routes/IndexRoute';
import Header from './Components/Header';
import { Alert, AlertActionCloseButton, AlertGroup, AlertVariant } from '@patternfly/react-core';

export const AccountContext = createContext(null);
export const ACCOUNTS_LOCAL_STORAGE_KEY = "accounts";

const loadAccounts = () => {
    const string = localStorage.getItem(ACCOUNTS_LOCAL_STORAGE_KEY);

    try {
        return JSON.parse(string) ?? [];
    }
    catch {
        return [];
    }
}

const App = () => {
    const [alerts, setAlerts] = useState([]);
    const [accounts, setAccounts] = useState(null);
    const [accountsRefreshCounter, setAccountsRefreshCounter] = useState(0);

    useEffect(() => {
        setAccounts(loadAccounts());
    }, [accountsRefreshCounter]);

    const addAlert = (variant, title, description) => {
        setAlerts((prevAlerts) => [...prevAlerts, { variant, title, description }]);
    };

    const removeAlert = (index) => {
        setAlerts((prevAlerts) => [...prevAlerts.filter((alert, filterIndex) => filterIndex !== index)]);
    };

    return (
        <AccountContext.Provider value={accounts}>
            <Header refreshAccounts={() => setAccountsRefreshCounter(accountsRefreshCounter + 1)}/>
            <Router>
                <Routes>
                    <Route path="/" element={<IndexRoute addAlert={addAlert}/>} />
                </Routes>
            </Router>
            <AlertGroup isToast>
                {alerts.map(({ variant, title, description }, index) => (
                    <Alert
                        variant={AlertVariant[variant]}
                        timeout
                        title={title}
                        actionClose={
                            <AlertActionCloseButton
                                title={title}
                                onClose={() => removeAlert(index)}
                            />
                        }
                        key={index}
                    >
                        {description}
                    </Alert>
                )
                )}
            </AlertGroup>
        </AccountContext.Provider>
    );
}

export default App;
