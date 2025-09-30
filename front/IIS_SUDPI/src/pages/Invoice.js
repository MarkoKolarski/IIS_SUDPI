import React, { useState, useEffect } from 'react';
import SideBar from '../components/SideBar';
import '../styles/Invoice.css';
import { FaChevronDown, FaTimes, FaSearch } from 'react-icons/fa';
import axiosInstance from '../axiosInstance';

const Invoice = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [invoices, setInvoices] = useState([]);
    const [filterOptions, setFilterOptions] = useState({
        statusi: [],
        dobavljaci: [],
        datumi: []
    });
    const [filters, setFilters] = useState({
        status: 'svi',
        dobavljac: 'svi',
        datum: 'svi'
    });
    const [searchQuery, setSearchQuery] = useState('');
    const [activeSearch, setActiveSearch] = useState('');
    const [pagination, setPagination] = useState({
        count: 0,
        num_pages: 0,
        current_page: 1,
        has_next: false,
        has_previous: false
    });
    const [loading, setLoading] = useState(true);
    const [dropdownOpen, setDropdownOpen] = useState({
        status: false,
        dobavljac: false,
        datum: false
    });

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    // Učitavanje filter opcija prilikom mount-a
    useEffect(() => {
        loadFilterOptions();
    }, []);

    // Učitavanje faktura kada se promene filteri
    useEffect(() => {
        loadInvoices();
    }, [filters, activeSearch, pagination.current_page]);

    const loadFilterOptions = async () => {
        try {
            const response = await axiosInstance.get('/invoices/filter-options/');
            setFilterOptions(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju filter opcija:', error);
        }
    };

    const loadInvoices = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({
                status: filters.status,
                dobavljac: filters.dobavljac,
                datum: filters.datum,
                page: pagination.current_page,
                page_size: 10
            });

            if (activeSearch) {
                params.append('search', activeSearch);
            }

            const response = await axiosInstance.get(`/invoices/?${params}`);
            setInvoices(response.data.results);
            setPagination({
                count: response.data.count,
                num_pages: response.data.num_pages,
                current_page: response.data.current_page,
                has_next: response.data.has_next,
                has_previous: response.data.has_previous
            });
        } catch (error) {
            console.error('Greška pri učitavanju faktura:', error);
            setInvoices([]);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (filterType, value) => {
        setFilters(prev => ({
            ...prev,
            [filterType]: value
        }));
        setPagination(prev => ({ ...prev, current_page: 1 }));
        setDropdownOpen(prev => ({ ...prev, [filterType]: false }));
    };

    const handleSearch = () => {
        setActiveSearch(searchQuery);
        setPagination(prev => ({ ...prev, current_page: 1 }));
    };

    const clearSearch = () => {
        setSearchQuery('');
        setActiveSearch('');
        setPagination(prev => ({ ...prev, current_page: 1 }));
    };

    const toggleDropdown = (dropdownType) => {
        setDropdownOpen(prev => ({
            ...prev,
            [dropdownType]: !prev[dropdownType]
        }));
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('sr-RS');
    };

    const formatAmount = (amount) => {
        return `${parseFloat(amount).toFixed(0)}€`;
    };

    const getStatusClassName = (status) => {
        switch (status) {
            case 'Čeka verifikaciju':
                return 'status-waiting';
            case 'Plaćeno':
                return 'status-paid';
            case 'Primljeno':
                return 'status-received';
            case 'Odbačeno':
                return 'status-rejected';
            default:
                return '';
        }
    };

    const getSelectedLabel = (filterType, value) => {
        const options = filterOptions[filterType] || [];
        const selected = options.find(option => option.value === value);
        return selected ? selected.label : 'Svi';
    };

    return (
        <div className={`invoice-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <main className="invoice-main-content">
                <header className="invoice-header">
                    <h1>Fakture</h1>
                </header>

                <section className="filter-section">
                    <div className="filter-controls">
                        <div className="filter-dropdown">
                            <label>Status</label>
                            <button onClick={() => toggleDropdown('status')}>
                                <span>{getSelectedLabel('statusi', filters.status)}</span>
                                <FaChevronDown />
                            </button>
                            {dropdownOpen.status && (
                                <div className="dropdown-menu">
                                    {filterOptions.statusi.map(option => (
                                        <div 
                                            key={option.value}
                                            className="dropdown-item"
                                            onClick={() => handleFilterChange('status', option.value)}
                                        >
                                            {option.label}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="filter-dropdown">
                            <label>Dobavljač</label>
                            <button onClick={() => toggleDropdown('dobavljac')}>
                                <span>{getSelectedLabel('dobavljaci', filters.dobavljac)}</span>
                                <FaChevronDown />
                            </button>
                            {dropdownOpen.dobavljac && (
                                <div className="dropdown-menu">
                                    {filterOptions.dobavljaci.map(option => (
                                        <div 
                                            key={option.value}
                                            className="dropdown-item"
                                            onClick={() => handleFilterChange('dobavljac', option.value)}
                                        >
                                            {option.label}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="filter-dropdown">
                            <label>Datum</label>
                            <button onClick={() => toggleDropdown('datum')}>
                                <span>{getSelectedLabel('datumi', filters.datum)}</span>
                                <FaChevronDown />
                            </button>
                            {dropdownOpen.datum && (
                                <div className="dropdown-menu">
                                    {filterOptions.datumi.map(option => (
                                        <div 
                                            key={option.value}
                                            className="dropdown-item"
                                            onClick={() => handleFilterChange('datum', option.value)}
                                        >
                                            {option.label}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                    
                    <div className="search-and-filters">
                        <div className="search-box">
                            <input
                                type="text"
                                placeholder="Pretraži fakture..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                            />
                            <button onClick={handleSearch}>
                                <FaSearch />
                            </button>
                        </div>
                        
                        {activeSearch && (
                            <div className="active-filters">
                                <div className="filter-chip">
                                    <span>Pretraga: "{activeSearch}"</span>
                                    <FaTimes className="remove-chip-icon" onClick={clearSearch} />
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                <section className="table-section">
                    <div className="table-container">
                        <div className="table-title-header">
                            <h2>Lista faktura ({pagination.count} ukupno)</h2>
                        </div>
                        <div className="table-content">
                            <div className="table-header">
                                <div className="table-col" style={{ width: '12%' }}>ID</div>
                                <div className="table-col" style={{ width: '12%' }}>Dobavljač</div>
                                <div className="table-col" style={{ width: '14%' }}>Iznos</div>
                                <div className="table-col" style={{ width: '20%' }}>Datum prijema</div>
                                <div className="table-col" style={{ width: '20%' }}>Rok plaćanja</div>
                                <div className="table-col status-col" style={{ width: '22%' }}>Status</div>
                            </div>
                            <div className="table-body">
                                {loading ? (
                                    <div className="loading-message">Učitavanje faktura...</div>
                                ) : invoices.length === 0 ? (
                                    <div className="no-data-message">Nema faktura za prikaz</div>
                                ) : (
                                    invoices.map((invoice, index) => (
                                        <div key={invoice.sifra_f} className={`table-row ${index % 2 === 0 ? 'row-even' : 'row-odd'}`}>
                                            <div className="table-col" style={{ width: '12%' }}>{invoice.sifra_f}</div>
                                            <div className="table-col" style={{ width: '12%' }}>{invoice.dobavljac_naziv}</div>
                                            <div className="table-col" style={{ width: '14%' }}>{formatAmount(invoice.iznos_f)}</div>
                                            <div className="table-col" style={{ width: '20%' }}>{formatDate(invoice.datum_prijema_f)}</div>
                                            <div className="table-col" style={{ width: '20%' }}>{formatDate(invoice.rok_placanja_f)}</div>
                                            <div className="table-col status-col" style={{ width: '22%' }}>
                                                <span className={`status-badge ${getStatusClassName(invoice.status_display)}`}>
                                                    {invoice.status_display}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                        
                        {/* Paginacija */}
                        {!loading && invoices.length > 0 && pagination.num_pages > 1 && (
                            <div className="pagination">
                                <button 
                                    onClick={() => setPagination(prev => ({ ...prev, current_page: prev.current_page - 1 }))}
                                    disabled={!pagination.has_previous}
                                    className="pagination-btn"
                                >
                                    Prethodna
                                </button>
                                <span className="pagination-info">
                                    Stranica {pagination.current_page} od {pagination.num_pages}
                                </span>
                                <button 
                                    onClick={() => setPagination(prev => ({ ...prev, current_page: prev.current_page + 1 }))}
                                    disabled={!pagination.has_next}
                                    className="pagination-btn"
                                >
                                    Sledeća
                                </button>
                            </div>
                        )}
                    </div>
                </section>
            </main>
        </div>
    );
};

export default Invoice;
