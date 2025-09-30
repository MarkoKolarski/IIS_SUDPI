import React, { useState, useEffect, useCallback } from 'react';
import SideBar from '../components/SideBar';
import PaymentSimulationModal from '../components/PaymentSimulationModal';
import '../styles/InvoiceDetails.css';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../axiosInstance';

const InvoiceDetails = () => {
    const { invoiceId } = useParams();
    const navigate = useNavigate();
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
    const [invoice, setInvoice] = useState(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const openPaymentSimulation = () => {
        setIsPaymentModalOpen(true);
    };

    const closePaymentSimulation = () => {
        setIsPaymentModalOpen(false);
    };

    const loadInvoiceDetails = useCallback(async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`/invoices/${invoiceId}/`);
            setInvoice(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju detalja fakture:', error);
            if (error.response?.status === 404) {
                navigate('/invoice');
            }
        } finally {
            setLoading(false);
        }
    }, [invoiceId, navigate]);

    const handleInvoiceAction = async (action, reason = '') => {
        setActionLoading(true);
        try {
            const response = await axiosInstance.post(`/invoices/${invoiceId}/action/`, {
                action: action,
                reason: reason
            });
            
            // Refresh invoice data after action
            await loadInvoiceDetails();
            
            alert(response.data.message);
        } catch (error) {
            console.error('Greška pri izvršavanju akcije:', error);
            alert('Greška pri izvršavanju akcije. Pokušajte ponovo.');
        } finally {
            setActionLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('sr-RS');
    };

    const formatAmount = (amount) => {
        return `${parseFloat(amount).toFixed(2)} RSD`;
    };

    useEffect(() => {
        loadInvoiceDetails();
    }, [loadInvoiceDetails]);

    if (loading) {
        return (
            <div className={`invoice-details-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
                <main className="invoice-details-main">
                    <div className="loading-message">Učitavanje detalja fakture...</div>
                </main>
            </div>
        );
    }

    if (!invoice) {
        return (
            <div className={`invoice-details-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
                <main className="invoice-details-main">
                    <div className="error-message">Faktura nije pronađena.</div>
                </main>
            </div>
        );
    }

    return (
        <div className={`invoice-details-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <SideBar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
            <main className="invoice-details-main">
                <header className="invoice-details-header">
                    <h1>Detalji fakture</h1>
                </header>

                <div className="invoice-details-content">
                    <section className="invoice-summary-card">
                        <div className="invoice-summary-header">
                            <h2>Faktura ID: {invoice.sifra_f}</h2>
                        </div>
                        <div className="invoice-summary-row row-light">
                            <div className="summary-col">
                                <span className="summary-label">Dobavljač:</span>
                                <span className="summary-value">{invoice.dobavljac_naziv}</span>
                            </div>
                            <div className="summary-col">
                                <span className="summary-label">Iznos:</span>
                                <span className="summary-value">{formatAmount(invoice.iznos_f)}</span>
                            </div>
                        </div>
                        <div className="invoice-summary-row row-medium">
                            <div className="summary-col">
                                <span className="summary-label">Datum prijema:</span>
                                <span className="summary-value">{formatDate(invoice.datum_prijema_f)}</span>
                            </div>
                            <div className="summary-col">
                                <span className="summary-label">Rok plaćanja:</span>
                                <span className="summary-value">{formatDate(invoice.rok_placanja_f)}</span>
                            </div>
                        </div>
                        <div className="invoice-summary-row row-light">
                            <div className="summary-col">
                                <span className="summary-label">Status:</span>
                                <span className="summary-value">{invoice.status_display}</span>
                            </div>
                            {invoice.ugovor && (
                                <div className="summary-col">
                                    <span className="summary-label">Ugovor ID:</span>
                                    <span className="summary-value">{invoice.ugovor.sifra_u}</span>
                                </div>
                            )}
                        </div>
                    </section>

                    <section className="process-flow">
                        <div className="process-flow-header">
                            <h3>Vizuelni tok procesa</h3>
                        </div>
                        <div className="process-flow-body">
                            {invoice.process_steps && invoice.process_steps.map((step, index) => (
                                <React.Fragment key={step.number}>
                                    <div className={`process-step ${step.status}`}>
                                        <div className="step-circle">{step.number}</div>
                                        <span className="step-label">{step.label}</span>
                                    </div>
                                    {index < invoice.process_steps.length - 1 && <div className="step-connector" aria-hidden="true" />}
                                </React.Fragment>
                            ))}
                        </div>
                    </section>

                    <section className="bottom-cards">
                        {invoice.razlog_cekanja_f && (
                            <div className="discrepancy-card">
                                <div className="card-header">
                                    <h3>Razlog čekanja</h3>
                                </div>
                                <div className="card-body">
                                    <p><strong>Razlog:</strong> {invoice.razlog_cekanja_f}</p>
                                </div>
                            </div>
                        )}

                        {invoice.stavke && invoice.stavke.length > 0 && (
                            <div className="items-card">
                                <div className="card-header">
                                    <h3>Stavke fakture</h3>
                                </div>
                                <div className="card-body">
                                    {invoice.stavke.map(stavka => (
                                        <div key={stavka.sifra_sf} className="invoice-item">
                                            <p><strong>{stavka.naziv_sf}</strong></p>
                                            <p>Količina: {stavka.kolicina_sf} | Cena po jedinici: {formatAmount(stavka.cena_po_jed)}</p>
                                            {stavka.opis_sf && <p>Opis: {stavka.opis_sf}</p>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(invoice.status_f === 'primljena' || invoice.status_f === 'verifikovana') && (
                            <div className="notification-card">
                                <div className="card-header">
                                    <h3>Akcije</h3>
                                </div>
                                <div className="card-body">
                                    <p className="notification-question">
                                        {invoice.status_f === 'primljena' 
                                            ? 'Da li želite da verifikujete fakturu?' 
                                            : 'Da li želite da odobrite isplatu?'}
                                    </p>
                                    <div className="notification-actions">
                                        <button 
                                            className="notification-btn confirm" 
                                            onClick={() => handleInvoiceAction('approve')}
                                            disabled={actionLoading}
                                        >
                                            {actionLoading ? 'Procesiranje...' : 'Odobri'}
                                        </button>
                                        <button 
                                            className="notification-btn decline" 
                                            onClick={() => {
                                                const reason = prompt('Unesite razlog odbacivanja:');
                                                if (reason) handleInvoiceAction('reject', reason);
                                            }}
                                            disabled={actionLoading}
                                        >
                                            Odbaci
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {invoice.transakcija && (
                            <div className="transaction-card">
                                <div className="card-header">
                                    <h3>Transakcija</h3>
                                </div>
                                <div className="card-body">
                                    <p><strong>ID transakcije:</strong> {invoice.transakcija.sifra_t}</p>
                                    <p><strong>Datum:</strong> {formatDate(invoice.transakcija.datum_t)}</p>
                                    <p><strong>Potvrda:</strong> {invoice.transakcija.potvrda_t}</p>
                                    <p><strong>Status:</strong> {invoice.transakcija.status_t}</p>
                                </div>
                            </div>
                        )}
                    </section>
                </div>

                <div className="action-buttons">
                    <button className="back-btn" onClick={() => navigate('/invoice')}>
                        ← Nazad na listu faktura
                    </button>
                    {invoice.status_f === 'verifikovana' && (
                        <button className="simulate-payment-btn" onClick={openPaymentSimulation}>
                            Simulacija plaćanja
                        </button>
                    )}
                </div>
            </main>
            
            <PaymentSimulationModal 
                isOpen={isPaymentModalOpen} 
                onClose={closePaymentSimulation} 
            />
        </div>
    );
};

export default InvoiceDetails;
