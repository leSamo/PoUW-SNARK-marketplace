import { Fragment } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Index from './Routes/Index';
import Header from './Header';

const App = () => {
    return (
        <Fragment>
            <Header />
            <Router>
                <Routes>
                    <Route path="/" element={<Index />} />
                </Routes>
            </Router>
        </Fragment>
    );
}

export default App;
