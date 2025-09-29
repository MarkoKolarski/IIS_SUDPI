import React, { useState } from 'react';
import SideBar from '../components/SideBar';
import PaymentSimulationModal from '../components/PaymentSimulationModal';
import '../styles/InvoiceDetails.css';

const InvoiceDetails = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const openPaymentSimulation = () => {
        setIsPaymentModalOpen(true);
    };

    const closePaymentSimulation = () => {
        setIsPaymentModalOpen(false);
    };

    const invoice = {
        id: '12345',
        supplier: 'A',
        amount: '500 RSD',
        receivedDate: '10.09.2025',
        dueDate: '15.09.2025',
        discrepancyReason: 'Iznos na fakturi ne odgovara ugovorenom iznosu.'
    };

    const steps = [
        { number: 1, label: 'Prijem fakture', status: 'completed' },
        { number: 2, label: 'Verifikacija', status: 'active' },
        { number: 3, label: 'Isplata', status: 'upcoming' }
    ];

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
                            <h2>Faktura ID: {invoice.id}</h2>
                        </div>
                        <div className="invoice-summary-row row-light">
                            <div className="summary-col">
                                <span className="summary-label">Dobavljač:</span>
                                <span className="summary-value">{invoice.supplier}</span>
                            </div>
                            <div className="summary-col">
                                <span className="summary-label">Iznos:</span>
                                <span className="summary-value">{invoice.amount}</span>
                            </div>
                        </div>
                        <div className="invoice-summary-row row-medium">
                            <div className="summary-col">
                                <span className="summary-label">Datum prijema:</span>
                                <span className="summary-value">{invoice.receivedDate}</span>
                            </div>
                            <div className="summary-col">
                                <span className="summary-label">Rok plaćanja:</span>
                                <span className="summary-value">{invoice.dueDate}</span>
                            </div>
                        </div>
                    </section>

                    <section className="process-flow">
                        <div className="process-flow-header">
                            <h3>Vizuelni tok procesa</h3>
                        </div>
                        <div className="process-flow-body">
                            {steps.map((step, index) => (
                                <React.Fragment key={step.number}>
                                    <div className={`process-step ${step.status}`}>
                                        <div className="step-circle">{step.number}</div>
                                        <span className="step-label">{step.label}</span>
                                    </div>
                                    {index < steps.length - 1 && <div className="step-connector" aria-hidden="true" />}
                                </React.Fragment>
                            ))}
                        </div>
                    </section>

                    <section className="bottom-cards">
                        <div className="discrepancy-card">
                            <div className="card-header">
                                <h3>Neusklađenost</h3>
                            </div>
                            <div className="card-body">
                                <p><strong>Razlog:</strong> {invoice.discrepancyReason}</p>
                            </div>
                        </div>

                        <div className="notification-card">
                            <div className="card-header">
                                <h3>Notifikacija</h3>
                            </div>
                            <div className="card-body">
                                <p className="notification-question">Da li želite da potpišete za nastavak procesa?</p>
                                <div className="notification-actions">
                                    <button className="notification-btn confirm">Potpiši</button>
                                    <button className="notification-btn decline">Odbij</button>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <button className="simulate-payment-btn" onClick={openPaymentSimulation}>
                    Simulacija plaćanja
                </button>
            </main>
            
            <PaymentSimulationModal 
                isOpen={isPaymentModalOpen} 
                onClose={closePaymentSimulation} 
            />
        </div>
    );
};

export default InvoiceDetails;
