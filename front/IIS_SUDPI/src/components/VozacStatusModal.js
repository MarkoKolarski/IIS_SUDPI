import React from "react";
import '../styles/LogisticTransport.css';

const VozacStatusModal = ({ modalOpen, selectedVozac, newStatus, setNewStatus, handleConfirmStatus, statusMessage, onClose }) => {
    if (!modalOpen || !selectedVozac) return null; // ako modal nije otvoren ili nema selektovanog vozača, ništa se ne prikazuje

    return (
        <div className="modal-overlay">
            <div className="modal">
                <h3>Izmeni status vozača: {selectedVozac.ime_vo} {selectedVozac.prz_vo}</h3>
                <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                    <option value="">-- Izaberi status --</option>
                    <option value="slobodan">Slobodan</option>
                    <option value="zauzet">Zauzet</option>
                    <option value="na_odmoru">Na odmoru</option>
                </select>
                <div style={{marginTop: '10px'}}>
                    <button className="btn-confirm" onClick={handleConfirmStatus}>Potvrdi</button>
                    <button className="btn-cancel" onClick={onClose}>Zatvori</button>
                </div>
                {statusMessage && <p className="status-message">{statusMessage}</p>}
            </div>
        </div>
    );
};

export default VozacStatusModal;
