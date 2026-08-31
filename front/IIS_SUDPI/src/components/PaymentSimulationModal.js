import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axiosInstance from '../axiosInstance';
import styles from '../styles/PaymentSimulationModal.module.css';

const PaymentSimulationModal = ({ isOpen, onClose, invoiceId }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isSimulating, setIsSimulating] = useState(false);
    const [simulationComplete, setSimulationComplete] = useState(false);
    const [error, setError] = useState(null);
    const [transactionData, setTransactionData] = useState(null);
    const [showStopConfirm, setShowStopConfirm] = useState(false);

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
        setShowStopConfirm(false);
        
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
            // Greška (npr. nedovoljno sredstava) nastaje u koraku "Automatsko
            // skidanje sredstava" - zaustavi progress bar tu, ne na početku.
            setCurrentStep(3);
            const errorMessage = err.response?.data?.detail
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
        setShowStopConfirm(false);
    }, []);

    useEffect(() => {
        if (isOpen && !isSimulating && !simulationComplete && !error) {
            startSimulation();
        }
        if (!isOpen) {
            resetSimulation();
        }
    }, [isOpen, isSimulating, simulationComplete, error, startSimulation, resetSimulation]);

    useEffect(() => {
        // If simulation finished while confirm was open, hide it to avoid stale messaging.
        if (!isSimulating && showStopConfirm) {
            setShowStopConfirm(false);
        }
    }, [isSimulating, showStopConfirm]);

    const handleClose = useCallback(() => {
        if (isSimulating) {
            setShowStopConfirm(true);
            return;
        }

        onClose();
    }, [isSimulating, onClose]);

    const confirmStopSimulation = useCallback(() => {
        setShowStopConfirm(false);
        onClose();
    }, [onClose]);

    const cancelStopSimulation = useCallback(() => {
        setShowStopConfirm(false);
    }, []);

    const handleOverlayClick = useCallback((e) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    }, [handleClose]);

    const handleKeyDown = useCallback((e) => {
        if (e.key === 'Escape') {
            if (showStopConfirm) {
                setShowStopConfirm(false);
                return;
            }

            handleClose();
        }
    }, [handleClose, showStopConfirm]);

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

                {(!error || currentStep > 0) && (
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

                        {error && (
                            <div className={styles.paymentErrorMessage}>
                                <span className={styles.errorIcon}>⚠️</span>
                                <p>{error}</p>
                            </div>
                        )}

                        {simulationComplete && transactionData && (
                            <div className={styles.paymentSuccessInfo}>
                                <h3>✓ Plaćanje uspešno izvršeno</h3>
                                <div className={styles.transactionDetails}>
                                    <p><strong>Broj potvrde:</strong> {transactionData.transakcija?.broj_potvrde_t}</p>
                                    <p><strong>Iznos:</strong> {transactionData.transakcija?.iznos_t} {transactionData.transakcija?.oznaka_v || "RSD"}</p>
                                    <p><strong>Dobavljač:</strong> {transactionData.faktura?.naziv_db}</p>
                                    {transactionData.notifikacije?.obavestenje_poslato && (
                                        <p className={styles.notificationStatus}>📧 Notifikacija poslata</p>
                                    )}
                                    {transactionData.notifikacije?.potvrda_poslata && (
                                        <p className={styles.notificationStatus}>📧 Potvrda poslata</p>
                                    )}
                                </div>
                            </div>
                        )}

                        {showStopConfirm && (
                            <div className={styles.stopConfirmBox} role="alertdialog" aria-live="assertive">
                                <div className={styles.stopConfirmHeader}>
                                    <span className={styles.stopConfirmIcon} aria-hidden="true">!</span>
                                    <div>
                                        <p className={styles.stopConfirmTitle}>Prekinuti simulaciju?</p>
                                        <p className={styles.stopConfirmMessage}>
                                            Simulacija je u toku. Da li želite da je prekinete?
                                        </p>
                                    </div>
                                </div>
                                <div className={styles.stopConfirmActions}>
                                    <button
                                        type="button"
                                        className={styles.stopConfirmContinueBtn}
                                        onClick={cancelStopSimulation}
                                    >
                                        Nastavi simulaciju
                                    </button>
                                    <button
                                        type="button"
                                        className={styles.stopConfirmStopBtn}
                                        onClick={confirmStopSimulation}
                                    >
                                        Prekini simulaciju
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}

                {!showStopConfirm && (
                    <button 
                        className={styles.paymentModalCloseBtn}
                        onClick={handleClose}
                        autoFocus
                    >
                        {isSimulating ? 'Prekini' : 'Zatvori'}
                    </button>
                )}
            </div>
        </div>
    );
};

export default PaymentSimulationModal;