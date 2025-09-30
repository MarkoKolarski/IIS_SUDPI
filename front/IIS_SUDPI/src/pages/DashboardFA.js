import React, { useState, useEffect } from 'react';
import '../styles/DashboardFA.css';
import SideBar from '../components/SideBar';
import { dashboardAPI } from '../api';

const DashboardFA = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [dashboardData, setDashboardData] = useState({
        pregled_finansija: {
            ukupno_placeno: 0,
            na_cekanju: 0,
            prosecno_vreme_placanja: 0
        },
        profitabilnost_dobavljaca: [],
        nadolazece_isplate: [],
        vizualizacija_troskova: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                const response = await dashboardAPI.getFinansijskiAnalitičarData();
                setDashboardData(response.data);
                setError(null);
            } catch (error) {
                console.error('Greška pri dohvatanju dashboard podataka:', error);
                setError('Greška pri učitavanju podataka. Molimo pokušajte ponovo.');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    return (
        <div className={`dashboard-fa-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <main className="dashboard-fa-main-content">
                <header className="dashboard-header">
                    <h1>Kontrolna tabla - Finansijski analitičar</h1>
                </header>

                {loading && (
                    <div className="loading-message">
                        Učitavanje podataka...
                    </div>
                )}

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                {!loading && !error && (
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
                                        <strong>{dashboardData.pregled_finansija.ukupno_placeno?.toLocaleString('sr-RS', { 
                                            style: 'currency', 
                                            currency: 'EUR',
                                            minimumFractionDigits: 0 
                                        })}</strong>
                                    </div>
                                    <div className="finance-overview-item">
                                        <span>Na čekanju:</span>
                                        <strong>{dashboardData.pregled_finansija.na_cekanju?.toLocaleString('sr-RS', { 
                                            style: 'currency', 
                                            currency: 'EUR',
                                            minimumFractionDigits: 0 
                                        })}</strong>
                                    </div>
                                    <div className="finance-overview-item">
                                        <span>Prosečno vreme plaćanja:</span>
                                        <strong>{dashboardData.pregled_finansija.prosecno_vreme_placanja}d</strong>
                                    </div>
                                </div>
                            </div>

                            {/* Card 2: Profitabilnost dobavljača */}
                            <div className="dashboard-card">
                                <div className="card-header">
                                    <h3>Profitabilnost dobavljača</h3>
                                </div>
                                <div className="card-content">
                                    {dashboardData.profitabilnost_dobavljaca.length > 0 ? (
                                        dashboardData.profitabilnost_dobavljaca.map((supplier, index) => (
                                            <div key={index} className="supplier-item">
                                                <span>{supplier.name}</span>
                                                <span>{supplier.profitability}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="no-data">Nema podataka o dobavljačima</div>
                                    )}
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
                                        {dashboardData.nadolazece_isplate.length > 0 ? (
                                            dashboardData.nadolazece_isplate.map((payment) => (
                                                <div key={payment.id} className="table-row">
                                                    <div className="table-col id-col">{payment.id}</div>
                                                    <div className="table-col supplier-col">{payment.supplier}</div>
                                                    <div className="table-col amount-col">{payment.amount}</div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="no-data">Nema nadolazećih isplata</div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Card 4: Vizualizacija troškova */}
                            <div className="dashboard-card">
                                <div className="card-header">
                                    <h3>Vizualizacija troškova (poslednih 6 meseci)</h3>
                                </div>
                                <div className="card-content">
                                    <div className="chart-placeholder">
                                        {dashboardData.vizualizacija_troskova.length > 0 ? (
                                            <div className="chart-data">
                                                {dashboardData.vizualizacija_troskova.map((item, index) => (
                                                    <div key={index} className="chart-item">
                                                        <div className="chart-month">{item.mesec}</div>
                                                        <div className="chart-bar" 
                                                             style={{
                                                                 height: `${Math.max(10, (item.iznos / Math.max(...dashboardData.vizualizacija_troskova.map(i => i.iznos)) * 100) || 10)}px`,
                                                                 backgroundColor: '#3b82f6'
                                                             }}>
                                                        </div>
                                                        <div className="chart-amount">
                                                            {item.iznos.toLocaleString('sr-RS', { 
                                                                style: 'currency', 
                                                                currency: 'EUR',
                                                                minimumFractionDigits: 0 
                                                            })}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="no-data">Nema podataka o troškovima</div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default DashboardFA;