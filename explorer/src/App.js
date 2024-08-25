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
                    {/*
                    <Route path="/block/:blockId" element={<BlockDetail />} />
                    <Route path="*" element={<NotFound />} />
                     */}
                </Routes>
            </Router>
        </Fragment>
    );
}

export default App;
