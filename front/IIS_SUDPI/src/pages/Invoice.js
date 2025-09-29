import React, { useState } from 'react';
import SideBar from '../components/SideBar';
import '../styles/Invoice.css';
import { FaChevronDown, FaTimes } from 'react-icons/fa';

const Invoice = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const invoices = [
        { id: '12345', supplier: 'A', amount: '500€', received: '10.09.2025', due: '15.09.2025', status: 'Čeka verifikaciju' },
        { id: '12346', supplier: 'B', amount: '700€', received: '12.09.2025', due: '17.09.2025', status: 'Plaćeno' },
        { id: '12347', supplier: 'C', amount: '350€', received: '11.09.2025', due: '16.09.2025', status: 'Primljeno' },
        { id: '12348', supplier: 'D', amount: '950€', received: '12.09.2025', due: '18.09.2025', status: 'Primljeno' },
        { id: '12349', supplier: 'E', amount: '550€', received: '13.09.2025', due: '19.09.2025', status: 'Primljeno' },
    ];

    const getStatusClassName = (status) => {
        switch (status) {
            case 'Čeka verifikaciju':
                return 'status-waiting';
            case 'Plaćeno':
                return 'status-paid';
            case 'Primljeno':
                return 'status-received';
            default:
                return '';
        }
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
                            <button>
                                <span>Svi statusi</span>
                                <FaChevronDown />
                            </button>
                        </div>
                        <div className="filter-dropdown">
                            <label>Dobavljač</label>
                            <button>
                                <span>Svi dobavljači</span>
                                <FaChevronDown />
                            </button>
                        </div>
                        <div className="filter-dropdown">
                            <label>Datum</label>
                            <button>
                                <span>Svi datumi</span>
                                <FaChevronDown />
                            </button>
                        </div>
                    </div>
                    <div className="active-filters">
                        <div className="filter-chip">
                            <span>Pretraga</span>
                            <FaTimes className="remove-chip-icon" />
                        </div>
                    </div>
                </section>

                <section className="table-section">
                    <div className="table-container">
                        <div className="table-title-header">
                            <h2>Lista faktura</h2>
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
                                {invoices.map((invoice, index) => (
                                    <div key={invoice.id} className={`table-row ${index % 2 === 0 ? 'row-even' : 'row-odd'}`}>
                                        <div className="table-col" style={{ width: '12%' }}>{invoice.id}</div>
                                        <div className="table-col" style={{ width: '12%' }}>{invoice.supplier}</div>
                                        <div className="table-col" style={{ width: '14%' }}>{invoice.amount}</div>
                                        <div className="table-col" style={{ width: '20%' }}>{invoice.received}</div>
                                        <div className="table-col" style={{ width: '20%' }}>{invoice.due}</div>
                                        <div className="table-col status-col" style={{ width: '22%' }}>
                                            <span className={`status-badge ${getStatusClassName(invoice.status)}`}>
                                                {invoice.status}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default Invoice;
