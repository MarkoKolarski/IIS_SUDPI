import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/Register.js';
import Login from './pages/Login.js';
import DashboardFA from './pages/DashboardFA.js';
import Invoice from './pages/Invoice.js';


const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard-fa" element={<DashboardFA />} />
                <Route path="/invoice" element={<Invoice />} />
            </Routes>
        </Router>
    );
};

export default App;
