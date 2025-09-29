import React, { useState } from 'react';
import SideBar from '../components/SideBar';
import '../styles/Penalties.css';

const Penalties = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const penaltiesData = [
        { id: 1, dobavljac: 'A', ugovor: 'Ugovor1', datum_krsenja: '15.09.2025', iznos: '450 RSD', status: 'Rešen' },
        { id: 2, dobavljac: 'B', ugovor: 'Ugovor2', datum_krsenja: '12.09.2025', iznos: '350 RSD', status: 'Obavešten' },
        { id: 3, dobavljac: 'C', ugovor: 'Ugovor3', datum_krsenja: '08.09.2025', iznos: '1500 RSD', status: 'Obavešten' },
        { id: 4, dobavljac: 'D', ugovor: 'Ugovor4', datum_krsenja: '05.09.2025', iznos: '700 RSD', status: 'Rešen' },
    ];

    const getStatusBadge = (status) => {
        switch (status.toLowerCase()) {
            case 'rešen':
                return <span className="status-badge status-resolved">{status}</span>;
            case 'obavešten':
                return <span className="status-badge status-notified">{status}</span>;
            default:
                return <span className="status-badge">{status}</span>;
        }
    };

    return (
        <div className={`penalties-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <div className="penalties-main-content">
                <header className="penalties-header">
                    <h1>Penali</h1>
                </header>

                <section className="penalties-filter-section">
                    <div className="filter-dropdown">
                        <label htmlFor="dobavljac-filter">Dobavljač</label>
                        <button id="dobavljac-filter">Svi dobavljači <span className="chevron">▼</span></button>
                    </div>
                </section>

                <section className="penalties-table-section">
                    <div className="table-container">
                        <div className="table-title-header">
                            <h2>Pregled penala</h2>
                        </div>
                        <div className="table-content">
                            <div className="penalties-table-header">
                                <div className="table-col col-id">ID</div>
                                <div className="table-col col-dobavljac">Dobavljač</div>
                                <div className="table-col col-ugovor">Ugovor</div>
                                <div className="table-col col-datum">Datum kršenja</div>
                                <div className="table-col col-iznos">Iznos</div>
                                <div className="table-col col-status">Status</div>
                            </div>
                            <div className="penalties-table-body">
                                {penaltiesData.map((row, index) => (
                                    <div key={row.id} className={`table-row ${index % 2 === 0 ? 'row-dark' : 'row-light'}`}>
                                        <div className="table-col col-id">{row.id}</div>
                                        <div className="table-col col-dobavljac">{row.dobavljac}</div>
                                        <div className="table-col col-ugovor">{row.ugovor}</div>
                                        <div className="table-col col-datum">{row.datum_krsenja}</div>
                                        <div className="table-col col-iznos">{row.iznos}</div>
                                        <div className="table-col col-status">{getStatusBadge(row.status)}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                <section className="analysis-section">
                    <div className="analysis-container">
                        <div className="analysis-title-header">
                            <h2>Automatska analiza saradnje</h2>
                        </div>
                        <div className="analysis-cards-wrapper">
                            <div className="analysis-card">
                                <h3>TechCorp Solutions d.o.o.</h3>
                                <p><strong>Broj penala:</strong> 4</p>
                                <p><strong>Ukupan iznos:</strong> 1.250 RSD</p>
                                <p className="critical-metric"><strong>Stopa kršenja:</strong> 75% ugovora</p>
                                <p className="recommendation-negative"><strong>Preporuka:</strong> Razmotriti prekid saradnje</p>
                            </div>
                            <div className="analysis-card">
                                <h3>Global Trade Ltd.</h3>
                                <p><strong>Broj penala:</strong> 1</p>
                                <p><strong>Ukupan iznos:</strong> 320 RSD</p>
                                <p className="positive-metric"><strong>Stopa kršenja:</strong> 15% ugovora</p>
                                <p className="recommendation-positive"><strong>Preporuka:</strong> Pouzdana saradnja</p>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Penalties;
