import React, { useState, useEffect, useCallback, useMemo } from 'react';
import '../styles/PaymentSimulationModal.css';

const PaymentSimulationModal = ({ isOpen, onClose }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isSimulating, setIsSimulating] = useState(false);
    const [simulationComplete, setSimulationComplete] = useState(false);

    const steps = useMemo(() => [
        { id: 1, text: 'Pokretanje simulacije...', duration: 1500 },
        { id: 2, text: 'Slanje notifikacije klijentu...', duration: 2000 },
        { id: 3, text: 'Automatsko skidanje sredstava...', duration: 1800 },
        { id: 4, text: 'Potvrda transakcije...', duration: 1600 },
        { id: 5, text: 'Simulacija uspešno završena!', duration: 0 }
    ], []);

    const startSimulation = useCallback(() => {
        setIsSimulating(true);
        setCurrentStep(1);
        
        let stepIndex = 0;
        
        const processStep = () => {
            if (stepIndex < steps.length - 1) {
                setTimeout(() => {
                    stepIndex++;
                    setCurrentStep(stepIndex + 1);
                    processStep();
                }, steps[stepIndex].duration);
            } else {
                setIsSimulating(false);
                setSimulationComplete(true);
            }
        };
        
        processStep();
    }, [steps]);

    const resetSimulation = useCallback(() => {
        setCurrentStep(0);
        setIsSimulating(false);
        setSimulationComplete(false);
    }, []);

    useEffect(() => {
        if (isOpen && !isSimulating && !simulationComplete) {
            startSimulation();
        }
        if (!isOpen) {
            resetSimulation();
        }
    }, [isOpen, isSimulating, simulationComplete, startSimulation, resetSimulation]);



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
            className="payment-modal-overlay" 
            onClick={handleOverlayClick}
            role="dialog" 
            aria-modal="true"
            aria-labelledby="simulation-modal-title"
            aria-describedby="simulation-progress-list"
        >
            <div className="payment-modal-container">
                <h2 id="simulation-modal-title" className="payment-modal-title">
                    Simulacija plaćanja
                </h2>

                <div className="payment-progress-bar">
                    <div 
                        className="payment-progress-fill" 
                        style={{ width: `${(currentStep / steps.length) * 100}%` }}
                    />
                </div>

                <ol id="simulation-progress-list" className="payment-steps-list" aria-live="polite">
                    {steps.map((step, index) => {
                        const stepNumber = index + 1;
                        const isActive = currentStep === stepNumber && isSimulating;
                        const isCompleted = currentStep > stepNumber || (currentStep === stepNumber && simulationComplete);
                        const isPending = currentStep < stepNumber;
                        const isFinalStep = stepNumber === steps.length;

                        return (
                            <li key={step.id} className="payment-step-item">
                                <div className="payment-step-content">
                                    <div className={`payment-step-circle ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isPending ? 'pending' : ''}`}>
                                        {isCompleted ? (
                                            <span className="payment-checkmark">✓</span>
                                        ) : isActive ? (
                                            <div className="payment-spinner"></div>
                                        ) : (
                                            <span className="payment-step-number">{stepNumber}</span>
                                        )}
                                    </div>
                                    <span className={`payment-step-text ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isPending ? 'pending' : ''} ${isFinalStep && simulationComplete ? 'final' : ''}`}>
                                        {step.text}
                                    </span>
                                </div>
                                {index < steps.length - 1 && (
                                    <div className={`payment-step-connector ${isCompleted ? 'completed' : ''}`}></div>
                                )}
                            </li>
                        );
                    })}
                </ol>

                <button 
                    className="payment-modal-close-btn"
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