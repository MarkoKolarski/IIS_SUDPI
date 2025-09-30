import React, { useState, useEffect, useCallback } from 'react';
import SideBar from '../components/SideBar';
import '../styles/Reports.css';
import axiosInstance from '../axiosInstance';

const Reports = () => {

    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [reportsData, setReportsData] = useState({
        total_profitability: 0,
        total_cost: 0,
        total_quantity: 0,
        data: [],
        chart_data: {
            profitability: [],
            costs: []
        }
    });
    const [filterOptions, setFilterOptions] = useState({
        periodi: [],
        grupiranje: [],
        statusi: []
    });
    const [filters, setFilters] = useState({
        status: '',
        period: '',
        group_by: 'proizvodu'
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchFilterOptions = async () => {
        try {
            const response = await axiosInstance.get('/reports/filter-options/');
            setFilterOptions(response.data);
        } catch (err) {
            console.error('Error fetching filter options:', err);
        }
    };

    const fetchReportsData = useCallback(async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            
            if (filters.status) params.append('status', filters.status);
            if (filters.period) params.append('period', filters.period);
            if (filters.group_by) params.append('group_by', filters.group_by);

            const response = await axiosInstance.get(`/reports/?${params.toString()}`);
            setReportsData(response.data);
            setError(null);
        } catch (err) {
            console.error('Error fetching reports data:', err);
            setError('Greška pri učitavanju podataka');
        } finally {
            setLoading(false);
        }
    }, [filters]);

    const handleFilterChange = (filterType, value) => {
        setFilters(prevFilters => ({
            ...prevFilters,
            [filterType]: value
        }));
    };

    const formatNumber = (number) => {
        return new Intl.NumberFormat('sr-RS').format(number);
    };

    const formatCurrency = (amount) => {
        return `${formatNumber(amount)} RSD`;
    };

    const formatProfitability = (profit) => {
        const sign = profit >= 0 ? '+' : '';
        return `${sign}${profit.toFixed(1)}%`;
    };

    useEffect(() => {

        fetchFilterOptions();
    }, []);

    useEffect(() => {
        fetchReportsData();
    }, [fetchReportsData]);



    // Emergency fallback if there are critical errors
    if (error === 'CRITICAL_ERROR') {
        return (
            <div style={{ padding: '20px', color: 'red' }}>
                <h1>Greška u učitavanju stranice</h1>
                <p>Molimo proverite konekciju ili kontaktirajte administratora.</p>
            </div>
        );
    }

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
                            <select 
                                id="status-filter"
                                value={filters.status}
                                onChange={(e) => handleFilterChange('status', e.target.value)}
                            >
                                <option value="">Sve</option>
                                {(filterOptions.statusi || []).map(status => (
                                    <option key={status.value} value={status.value}>
                                        {status.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="filter-dropdown">
                            <label htmlFor="period-filter">Period</label>
                            <select 
                                id="period-filter"
                                value={filters.period}
                                onChange={(e) => handleFilterChange('period', e.target.value)}
                            >
                                <option value="">Sve</option>
                                {(filterOptions.periodi || []).map(period => (
                                    <option key={period.value} value={period.value}>
                                        {period.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="filter-dropdown">
                            <label htmlFor="group-by-filter">Grupiši po</label>
                            <select 
                                id="group-by-filter"
                                value={filters.group_by}
                                onChange={(e) => handleFilterChange('group_by', e.target.value)}
                            >
                                {(filterOptions.grupiranje || []).map(group => (
                                    <option key={group.value} value={group.value}>
                                        {group.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <button className="generate-report-btn" onClick={fetchReportsData}>
                        Generiši izveštaj
                    </button>
                </section>

                <section className="chart-section">
                    <div className="chart-card">
                        <div className="chart-card-header">
                            <h2>Profitabilnost po {filters.group_by === 'proizvodu' ? 'proizvodu' : 'dobavljaču'}</h2>
                        </div>
                        <div className="chart-card-body">
                            {loading ? (
                                <div className="loading">Učitava...</div>
                            ) : (
                                <div className="chart-placeholder">
                                    <div className="chart-summary">
                                        <h3>Ukupna profitabilnost: {formatProfitability(reportsData.total_profitability)}</h3>
                                        {(reportsData.chart_data?.profitability || []).slice(0, 5).map((item, index) => (
                                            <div key={index} className="chart-item">
                                                <span>{item.name}: {formatProfitability(item.value)}</span>
                                                <div className="chart-bar" style={{ width: `${Math.abs(item.value)}%` }}></div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="chart-card">
                        <div className="chart-card-header">
                            <h2>Troškovi po {filters.group_by === 'proizvodu' ? 'proizvodu' : 'dobavljaču'}</h2>
                        </div>
                        <div className="chart-card-body">
                            {loading ? (
                                <div className="loading">Učitava...</div>
                            ) : (
                                <div className="chart-placeholder">
                                    <div className="chart-summary">
                                        <h3>Ukupni troškovi: {formatCurrency(reportsData.total_cost)}</h3>
                                        {(reportsData.chart_data?.costs || []).slice(0, 5).map((item, index) => (
                                            <div key={index} className="chart-item">
                                                <span>{item.name}: {formatCurrency(item.value)}</span>
                                                <div className="chart-bar" style={{ width: `${(item.value / reportsData.total_cost) * 100}%` }}></div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                <section className="reports-table-section">
                    <div className="table-container">
                        <div className="table-title-header">
                            <h2>Detaljan prikaz podataka</h2>
                        </div>
                        {error && (
                            <div className="error-message">{error}</div>
                        )}
                        {loading ? (
                            <div className="loading">Učitava podatke...</div>
                        ) : (
                            <div className="table-content">
                                <div className="reports-table-header">
                                    <div className="table-col col-proizvod">
                                        {filters.group_by === 'proizvodu' ? 'Proizvod' : 'Dobavljač'}
                                    </div>
                                    <div className="table-col col-kolicina">Količina</div>
                                    <div className="table-col col-trosak">Ukupan trošak</div>
                                    <div className="table-col col-profit">Profitabilnost</div>
                                </div>
                                <div className="reports-table-body">
                                    {(reportsData.data || []).map((row, index) => (
                                        <div key={row.id || index} className={`table-row ${index % 2 === 0 ? 'row-dark' : 'row-light'}`}>
                                            <div className="table-col col-proizvod">{row.name}</div>
                                            <div className="table-col col-kolicina">{formatNumber(row.quantity)}</div>
                                            <div className="table-col col-trosak">{formatCurrency(row.total_cost)}</div>
                                            <div className={`table-col col-profit ${row.profitability >= 0 ? 'profit-positive' : 'profit-negative'}`}>
                                                <span className="arrow">{row.profitability >= 0 ? '▲' : '▼'}</span> 
                                                {formatProfitability(row.profitability)}
                                            </div>
                                        </div>
                                    ))}
                                    {(reportsData.data || []).length > 0 && (
                                        <div className="table-row summary-row">
                                            <div className="table-col col-proizvod">UKUPNO:</div>
                                            <div className="table-col col-kolicina">{formatNumber(reportsData.total_quantity)} kom</div>
                                            <div className="table-col col-trosak">{formatCurrency(reportsData.total_cost)}</div>
                                            <div className={`table-col col-profit ${reportsData.total_profitability >= 0 ? 'profit-positive' : 'profit-negative'}`}>
                                                <span className="arrow">{reportsData.total_profitability >= 0 ? '▲' : '▼'}</span> 
                                                {formatProfitability(reportsData.total_profitability)}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Reports;
