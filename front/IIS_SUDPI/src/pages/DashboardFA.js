import React, { useState } from 'react';
import '../styles/DashboardFA.css';
import SideBar from '../components/SideBar';

const DashboardFA = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    return (
        <div className={`dashboard-fa-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <main className="dashboard-fa-main-content">
                <div className="dashboard-fa-container">
                    <header className="dashboard-header">
                        <h1>Dashboard - Finansijski Analitičar</h1>
                        <p>Dobrodošli na dashboard za finansijske analitičare</p>
                    </header>

                    <div className="dashboard-content">
                        <div className="dashboard-grid">
                            <div className="dashboard-card">
                                <h3>Finansijski Izveštaji</h3>
                                <p>Pregled i kreiranje finansijskih izveštaja</p>
                                <button className="card-button">Otvori</button>
                            </div>

                            <div className="dashboard-card">
                                <h3>Analiza Troškova</h3>
                                <p>Analiza troškova nabavke i održavanja zaliha</p>
                                <button className="card-button">Analiziraj</button>
                            </div>

                            <div className="dashboard-card">
                                <h3>Fakture</h3>
                                <p>Pregled i verifikacija faktura</p>
                                <button className="card-button">Pregledaj</button>
                            </div>

                            <div className="dashboard-card">
                                <h3>Transakcije</h3>
                                <p>Praćenje finansijskih transakcija</p>
                                <button className="card-button">Prikaži</button>
                            </div>

                            <div className="dashboard-card">
                                <h3>Budžet</h3>
                                <p>Planiranje i kontrola budžeta</p>
                                <button className="card-button">Upravljaj</button>
                            </div>

                            <div className="dashboard-card">
                                <h3>Statistike</h3>
                                <p>Finansijske statistike i KPI-jevi</p>
                                <button className="card-button">Pogledaj</button>
                            </div>
                        </div>
                    </div>

                    <footer className="dashboard-footer">
                        <p>© 2024 IIS SUDPI - Finansijski Dashboard</p>
                    </footer>
                </div>
            </main>
        </div>
    );
};

export default DashboardFA;