import React, { useState } from 'react';
import SideBar from '../components/SideBar';
import '../styles/Reports.css';

const Reports = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const data = [
        { id: 1, proizvod: 'Proizvod A', kolicina: '1,250', ukupan_trosak: '520.315,25 RSD', profitabilnost: '+28%' },
        { id: 2, proizvod: 'Proizvod B', kolicina: '2,180', ukupan_trosak: '398.742,50 RSD', profitabilnost: '+22%' },
        { id: 3, proizvod: 'Proizvod C', kolicina: '1,890', ukupan_trosak: '234.127,75 RSD', profitabilnost: '+15%' },
    ];

    const total = {
        proizvod: 'UKUPNO:',
        kolicina: '5,320 kom',
        ukupan_trosak: '1.153.185,50 RSD',
        profitabilnost: '+65%',
    };

    return (
        <div className={`reports-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <div className="reports-main-content">
                <header className="reports-header">
                    <h1>Izveštaji</h1>
                </header>

                <section className="reports-filter-section">
                    <div className="filter-controls">
                        <div className="filter-dropdown">
                            <label htmlFor="status-filter">Status</label>
                            <button id="status-filter">Sve <span className="chevron">▼</span></button>
                        </div>
                        <div className="filter-dropdown">
                            <label htmlFor="period-filter">Period</label>
                            <button id="period-filter">Ovaj mesec <span className="chevron">▼</span></button>
                        </div>
                        <div className="filter-dropdown">
                            <label htmlFor="group-by-filter">Grupiši po</label>
                            <button id="group-by-filter">Proizvodu <span className="chevron">▼</span></button>
                        </div>
                    </div>
                    <button className="generate-report-btn">Generiši izveštaj</button>
                </section>

                <section className="chart-section">
                    <div className="chart-card">
                        <div className="chart-card-header">
                            <h2>Profitabilnost po proizvodu</h2>
                        </div>
                        <div className="chart-card-body">
                            <div className="chart-placeholder"></div>
                        </div>
                    </div>
                    <div className="chart-card">
                        <div className="chart-card-header">
                            <h2>Troškovi po proizvodu</h2>
                        </div>
                        <div className="chart-card-body">
                            <div className="chart-placeholder"></div>
                        </div>
                    </div>
                </section>

                <section className="reports-table-section">
                    <div className="table-container">
                        <div className="table-title-header">
                            <h2>Detaljan prikaz podataka</h2>
                        </div>
                        <div className="table-content">
                            <div className="reports-table-header">
                                <div className="table-col col-proizvod">Proizvod</div>
                                <div className="table-col col-kolicina">Količina</div>
                                <div className="table-col col-trosak">Ukupan trošak</div>
                                <div className="table-col col-profit">Profitabilnost</div>
                            </div>
                            <div className="reports-table-body">
                                {data.map((row, index) => (
                                    <div key={row.id} className={`table-row ${index % 2 === 0 ? 'row-dark' : 'row-light'}`}>
                                        <div className="table-col col-proizvod">{row.proizvod}</div>
                                        <div className="table-col col-kolicina">{row.kolicina}</div>
                                        <div className="table-col col-trosak">{row.ukupan_trosak}</div>
                                        <div className="table-col col-profit profit-positive">
                                            <span className="arrow">▲</span> {row.profitabilnost}
                                        </div>
                                    </div>
                                ))}
                                <div className="table-row summary-row">
                                    <div className="table-col col-proizvod">{total.proizvod}</div>
                                    <div className="table-col col-kolicina">{total.kolicina}</div>
                                    <div className="table-col col-trosak">{total.ukupan_trosak}</div>
                                    <div className="table-col col-profit profit-positive">
                                        <span className="arrow">▲</span> {total.profitabilnost}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Reports;
