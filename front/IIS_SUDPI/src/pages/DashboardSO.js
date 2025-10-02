import React, { useState } from 'react';
import MainSideBar from '../components/MainSideBar';
import '../styles/DashboardSO.css';

const DashboardSO = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    return (
        <div className={`dashboard-so-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="dashboard-so-main-content">
                <header className="dashboard-header">
                    <h1>Kontrolna tabla - Skladišni operater</h1>
                </header>

                <div className="dashboard-content">
                    <div className="dashboard-grid">
                        {/* Placeholder za buduci sadrzaj */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Centralni deo - prazan</h3>
                            </div>
                            <div className="card-content">
                                <div className="placeholder-content">
                                    <p>Ovde će biti dodati sadržaji kasnije</p>
                                </div>
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Drugo mesto - prazno</h3>
                            </div>
                            <div className="card-content">
                                <div className="placeholder-content">
                                    <p>Rezervisano za buduće funkcionalnosti</p>
                                </div>
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Treće mesto - prazno</h3>
                            </div>
                            <div className="card-content">
                                <div className="placeholder-content">
                                    <p>Mesto za dodatne komponente</p>
                                </div>
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Četvrto mesto - prazno</h3>
                            </div>
                            <div className="card-content">
                                <div className="placeholder-content">
                                    <p>Prostor za nova svojstva</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardSO;