import React, { useState, useEffect, useCallback } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DashboardSO.css';

const DashboardSO = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [skladista, setSkladista] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchSkladista = useCallback(async () => {
        try {
            setLoading(true);
            setError('');
            const response = await axiosInstance.get('/skladista/');
            setSkladista(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju skladišta:', error);
            setError('Greška pri učitavanju skladišta');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSkladista();
        
        // Auto-refresh svakih 30 sekundi da povuče najnovije podatke
        const interval = setInterval(() => {
            fetchSkladista();
        }, 30000);
        
        // Cleanup interval kada se komponenta unmount-uje
        return () => clearInterval(interval);
    }, [fetchSkladista]);

    const getTemperatureDisplayColor = (temperatura) => {
        if (temperatura === null) return '#6b7280'; // siva za N/A
        if (temperatura <= 2) return '#3b82f6'; // plava za nisku
        if (temperatura <= 5) return '#16a34a'; // zelena za umereenu
        return '#dc2626'; // crvena za visoku
    };

    const getRizikDisplayText = (statusRizika) => {
        const map = {
            'nizak': 'ne',
            'umeren': 'umereno', 
            'visok': 'da'
        };
        return map[statusRizika] || statusRizika;
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
                        {/* Stanje u skladištima */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Stanje u skladištima</h3>
                            </div>
                            <div className="card-content">
                                {loading && <div className="loading">Učitavanje skladišta...</div>}
                                {error && <div className="error">{error}</div>}
                                
                                {!loading && !error && (
                                    <div className="skladista-table-container">
                                        <table className="skladista-table">
                                            <thead>
                                                <tr>
                                                    <th>Mesto</th>
                                                    <th>Temperatura</th>
                                                    <th>Rizik</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {skladista.length > 0 ? (
                                                    skladista.map((skladiste) => (
                                                        <tr key={skladiste.sifra_s}>
                                                            <td>{skladiste.mesto_s}</td>
                                                            <td style={{
                                                                color: getTemperatureDisplayColor(skladiste.poslednja_temperatura),
                                                                fontWeight: 'bold'
                                                            }}>
                                                                {skladiste.poslednja_temperatura !== null ? skladiste.poslednja_temperatura : 'N/A'}
                                                            </td>
                                                            <td>{getRizikDisplayText(skladiste.status_rizika_s)}</td>
                                                        </tr>
                                                    ))
                                                ) : (
                                                    <tr>
                                                        <td colSpan="3" className="no-data">
                                                            Nema skladišta za prikaz
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
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