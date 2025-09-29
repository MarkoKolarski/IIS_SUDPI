import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/Register.js';
import Login from './pages/Login.js';
import DashboardFA from './pages/DashboardFA.js';
import NavBar from './components/NavBar';

const App = () => {
    return (
        <Router>
            <NavBar />
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard-fa" element={<DashboardFA />} />
            </Routes>
        </Router>
    );
};

export default App;
