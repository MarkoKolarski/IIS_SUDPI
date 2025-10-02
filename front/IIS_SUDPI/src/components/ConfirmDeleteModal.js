import React from 'react';
import '../styles/ConfirmDeleteModal.css';

const ConfirmDeleteModal = ({ isOpen, onClose, onConfirm, artikalNaziv, loading }) => {
    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className="confirm-modal-backdrop" onClick={handleBackdropClick}>
            <div className="confirm-modal">
                <div className="confirm-modal-header">
                    <h3>Potvrda brisanja</h3>
                    <button 
                        className="close-button"
                        onClick={onClose}
                        disabled={loading}
                    >
                        ×
                    </button>
                </div>
                
                <div className="confirm-modal-body">
                    <div className="warning-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                            <path 
                                d="M12 9v3.75m0 3.75h.007v.008H12v-.008zM12 2l8.485 16.515a.5.5 0 01-.485.485H3.515a.5.5 0 01-.485-.485L11.515 2a.5.5 0 01.97 0z" 
                                stroke="#ef4444" 
                                strokeWidth="2" 
                                strokeLinecap="round" 
                                strokeLinejoin="round"
                            />
                        </svg>
                    </div>
                    <p>Da li ste sigurni da želite da obrišete artikal:</p>
                    <strong className="artikal-naziv">"{artikalNaziv}"</strong>
                    <p className="warning-text">
                        Ova akcija se ne može poništiti. Artikal i sve povezane zalihe će biti trajno obrisani.
                    </p>
                </div>
                
                <div className="confirm-modal-footer">
                    <button 
                        className="cancel-button"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Otkaži
                    </button>
                    <button 
                        className="delete-button"
                        onClick={onConfirm}
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="loading-spinner"></span>
                                Brisanje...
                            </>
                        ) : (
                            'Obriši artikal'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmDeleteModal;