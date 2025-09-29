import React, { useState } from 'react';
import '../styles/DashboardFA.css';
import SideBar from '../components/SideBar';

const DashboardFA = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const suppliers = [
        { name: 'Dobavljač A', profitability: '92%' },
        { name: 'Dobavljač B', profitability: '87%' },
        { name: 'Dobavljač C', profitability: '75%' },
        { name: 'Dobavljač D', profitability: '60%' },
        { name: 'Dobavljač E', profitability: '95%' },
    ];

    const upcomingPayments = [
        { id: '12345', supplier: 'Dobavljač A', amount: '500€' },
        { id: '12346', supplier: 'Dobavljač B', amount: '700€' },
        { id: '12347', supplier: 'Dobavljač C', amount: '350€' },
        { id: '12348', supplier: 'Dobavljač D', amount: '900€' },
        { id: '12349', supplier: 'Dobavljač E', amount: '450€' },
    ];

    return (
        <div className={`dashboard-fa-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <main className="dashboard-fa-main-content">
                <header className="dashboard-header">
                    <h1>Kontrolna tabla - Finansijski analitičar</h1>
                </header>

                <div className="dashboard-content">
                    <div className="dashboard-grid">
                        {/* Card 1: Pregled finansija */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Pregled finansija</h3>
                            </div>
                            <div className="card-content">
                                <div className="finance-overview-item">
                                    <span>Ukupno plaćeno:</span>
                                    <strong>12,450€</strong>
                                </div>
                                <div className="finance-overview-item">
                                    <span>Na čekanju:</span>
                                    <strong>3,200€</strong>
                                </div>
                                <div className="finance-overview-item">
                                    <span>Prosečno vreme plaćanja:</span>
                                    <strong>7d</strong>
                                </div>
                            </div>
                        </div>

                        {/* Card 2: Profitabilnost dobavljača */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Profitabilnost dobavljača</h3>
                            </div>
                            <div className="card-content">
                                {suppliers.map((supplier, index) => (
                                    <div key={index} className="supplier-item">
                                        <span>{supplier.name}</span>
                                        <span>{supplier.profitability}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Card 3: Nadolazeće isplate */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Nadolazeće isplate</h3>
                            </div>
                            <div className="card-content">
                                <div className="upcoming-payments-table">
                                    <div className="table-header-row">
                                        <div className="table-col id-col">ID</div>
                                        <div className="table-col supplier-col">Dobavljač</div>
                                        <div className="table-col amount-col">Iznos</div>
                                    </div>
                                    {upcomingPayments.map((payment) => (
                                        <div key={payment.id} className="table-row">
                                            <div className="table-col id-col">{payment.id}</div>
                                            <div className="table-col supplier-col">{payment.supplier}</div>
                                            <div className="table-col amount-col">{payment.amount}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Card 4: Vizualizacija troškova */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Vizualizacija troškova</h3>
                            </div>
                            <div className="card-content">
                                <div className="chart-placeholder">
                                    {/* Placeholder for chart */}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardFA;