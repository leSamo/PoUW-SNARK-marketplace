import React, { Fragment, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import IndexRoute from './Routes/IndexRoute';
import Header from './Components/Header';
import { Alert, AlertActionCloseButton, AlertGroup, AlertVariant } from '@patternfly/react-core';

const App = () => {
    const [alerts, setAlerts] = useState([]);

    const addAlert = (variant, title, description) => {
        setAlerts((prevAlerts) => [...prevAlerts, { variant, title, description }]);
    };

    const removeAlert = (index) => {
        setAlerts((prevAlerts) => [...prevAlerts.filter((alert, filterIndex) => filterIndex !== index)]);
    };

    return (
        <Fragment>
            <Header />
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
        </Fragment>
    );
}

export default App;
