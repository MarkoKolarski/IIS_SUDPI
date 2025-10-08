import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axiosInstance from '../axiosInstance';
import styles from '../styles/PaymentSimulationModal.module.css';

const PaymentSimulationModal = ({ isOpen, onClose, invoiceId }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isSimulating, setIsSimulating] = useState(false);
    const [simulationComplete, setSimulationComplete] = useState(false);
    const [error, setError] = useState(null);
    const [transactionData, setTransactionData] = useState(null);

    const steps = useMemo(() => [
        { id: 1, text: 'Pokretanje simulacije...', duration: 1500 },
        { id: 2, text: 'Slanje notifikacije klijentu...', duration: 2000 },
        { id: 3, text: 'Automatsko skidanje sredstava...', duration: 1800 },
        { id: 4, text: 'Potvrda transakcije...', duration: 1600 },
        { id: 5, text: 'Simulacija uspešno završena!', duration: 0 }
    ], []);

    const startSimulation = useCallback(async () => {
        if (!invoiceId) {
            setError('ID fakture nije prosleđen');
            return;
        }

        setIsSimulating(true);
        setCurrentStep(1);
        setError(null);
        
        try {
            // Pozovi backend za stvarno plaćanje
            const response = await axiosInstance.post(`invoices/${invoiceId}/simulate-payment/`);
            
            // Procesiranje koraka sa backend odgovorima
            for (let i = 0; i < steps.length; i++) {
                setCurrentStep(i + 1);
                await new Promise(resolve => setTimeout(resolve, steps[i].duration));
            }
            
            // Sačuvaj podatke o transakciji
            setTransactionData(response.data);
            setSimulationComplete(true);
            
        } catch (err) {
            console.error('Greška pri simulaciji:', err);
            const errorMessage = err.response?.data?.error 
                || err.response?.data?.detail
                || err.message 
                || 'Greška pri izvršavanju plaćanja';
            setError(errorMessage);
            setIsSimulating(false);
        } finally {
            setIsSimulating(false);
        }
    }, [invoiceId, steps]);

    const resetSimulation = useCallback(() => {
        setCurrentStep(0);
        setIsSimulating(false);
        setSimulationComplete(false);
        setError(null);
        setTransactionData(null);
    }, []);

    useEffect(() => {
        if (isOpen && !isSimulating && !simulationComplete && !error) {
            startSimulation();
        }
        if (!isOpen) {
            resetSimulation();
        }
    }, [isOpen, isSimulating, simulationComplete, error, startSimulation, resetSimulation]);

    const handleClose = useCallback(() => {
        if (isSimulating) {
            const confirmClose = window.confirm('Da li ste sigurni da želite da prekinete simulaciju?');
            if (!confirmClose) return;
        }
        onClose();
    }, [isSimulating, onClose]);

    const handleOverlayClick = useCallback((e) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    }, [handleClose]);

    const handleKeyDown = useCallback((e) => {
        if (e.key === 'Escape') {
            handleClose();
        }
    }, [handleClose]);

    useEffect(() => {
        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'hidden';
        }
        
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, handleKeyDown]);

    if (!isOpen) return null;

    return (
        <div 
            className={styles.paymentModalOverlay} 
            onClick={handleOverlayClick}
            role="dialog" 
            aria-modal="true"
            aria-labelledby="simulation-modal-title"
            aria-describedby="simulation-progress-list"
        >
            <div className={styles.paymentModalContainer}>
                <h2 id="simulation-modal-title" className={styles.paymentModalTitle}>
                    Simulacija plaćanja
                </h2>

                {error && (
                    <div className={styles.paymentErrorMessage}>
                        <span className={styles.errorIcon}>⚠️</span>
                        <p>{error}</p>
                    </div>
                )}

                {!error && (
                    <>
                        <div className={styles.paymentProgressBar}>
                            <div 
                                className={styles.paymentProgressFill} 
                                style={{ width: `${(currentStep / steps.length) * 100}%` }}
                            />
                        </div>

                        <ol id="simulation-progress-list" className={styles.paymentStepsList} aria-live="polite">
                            {steps.map((step, index) => {
                                const stepNumber = index + 1;
                                const isActive = currentStep === stepNumber && isSimulating;
                                const isCompleted = currentStep > stepNumber || (currentStep === stepNumber && simulationComplete);
                                const isPending = currentStep < stepNumber;
                                const isFinalStep = stepNumber === steps.length;

                                return (
                                    <li key={step.id} className={styles.paymentStepItem}>
                                        <div className={styles.paymentStepContent}>
                                            <div className={`${styles.paymentStepCircle} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''} ${isPending ? styles.pending : ''}`}>
                                                {isCompleted ? (
                                                    <span className={styles.paymentCheckmark}>✓</span>
                                                ) : isActive ? (
                                                    <div className={styles.paymentSpinner}></div>
                                                ) : (
                                                    <span className={styles.paymentStepNumber}>{stepNumber}</span>
                                                )}
                                            </div>
                                            <span className={`${styles.paymentStepText} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''} ${isPending ? styles.pending : ''} ${isFinalStep && simulationComplete ? styles.final : ''}`}>
                                                {step.text}
                                            </span>
                                        </div>
                                        {index < steps.length - 1 && (
                                            <div className={`${styles.paymentStepConnector} ${isCompleted ? styles.completed : ''}`}></div>
                                        )}
                                    </li>
                                );
                            })}
                        </ol>

                        {simulationComplete && transactionData && (
                            <div className={styles.paymentSuccessInfo}>
                                <h3>✓ Plaćanje uspešno izvršeno</h3>
                                <div className={styles.transactionDetails}>
                                    <p><strong>Broj potvrde:</strong> {transactionData.transaction?.confirmation_number}</p>
                                    <p><strong>Iznos:</strong> {transactionData.transaction?.amount} RSD</p>
                                    <p><strong>Dobavljač:</strong> {transactionData.invoice?.supplier}</p>
                                    {transactionData.notifications?.payment_notification_sent && (
                                        <p className={styles.notificationStatus}>📧 Notifikacija poslata</p>
                                    )}
                                    {transactionData.notifications?.confirmation_sent && (
                                        <p className={styles.notificationStatus}>📧 Potvrda poslata</p>
                                    )}
                                </div>
                            </div>
                        )}
                    </>
                )}

                <button 
                    className={styles.paymentModalCloseBtn}
                    onClick={handleClose}
                    autoFocus
                >
                    {isSimulating ? 'Prekini' : 'Zatvori'}
                </button>
            </div>
        </div>
    );
};

export default PaymentSimulationModal;