import React, { useState } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DodajSkladiste.css';

const DodajSkladiste = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [formData, setFormData] = useState({
        mesto_s: '',
        status_rizika_s: 'nizak'
    });
    
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Uklanjamo greške kada korisnik počne da kuca
        if (error) setError('');
        if (message) setMessage('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validacija
        if (!formData.mesto_s.trim()) {
            setError('Mesto skladišta je obavezno');
            return;
        }

        setLoading(true);
        setError('');
        setMessage('');

        try {
            const response = await axiosInstance.post('/skladista/dodaj/', formData);
            
            setMessage('Skladište je uspešno dodato!');
            
            // Resetuj formu
            setFormData({
                mesto_s: '',
                status_rizika_s: 'nizak'
            });

            console.log('Novo skladište:', response.data.skladiste);
            
        } catch (error) {
            console.error('Greška pri dodavanju skladišta:', error);
            
            if (error.response?.data?.details) {
                // Prikaži greške validacije
                const validationErrors = error.response.data.details;
                let errorMessage = '';
                
                if (validationErrors.mesto_s) {
                    errorMessage += `Mesto: ${validationErrors.mesto_s.join(', ')}`;
                }
                if (validationErrors.status_rizika_s) {
                    errorMessage += `Status rizika: ${validationErrors.status_rizika_s.join(', ')}`;
                }
                
                setError(errorMessage || 'Neispravni podaci');
            } else if (error.response?.data?.error) {
                setError(error.response.data.error);
            } else {
                setError('Došlo je do greške pri dodavanju skladišta');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`dodaj-skladiste-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="dodaj-skladiste-main-content">
                <div className="dodaj-skladiste-container">
                    <div className="dodaj-skladiste-header">
                        <h1>Dodaj Novo Skladište</h1>
                        <p>Unesite podatke o novom skladištu</p>
                    </div>

            {message && (
                <div className="success-message">
                    {message}
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="dodaj-skladiste-form">
                <div className="form-group">
                    <label htmlFor="mesto_s">
                        Mesto skladišta *
                    </label>
                    <input
                        type="text"
                        id="mesto_s"
                        name="mesto_s"
                        value={formData.mesto_s}
                        onChange={handleInputChange}
                        placeholder="Unesite lokaciju skladišta"
                        required
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="status_rizika_s">
                        Status rizika *
                    </label>
                    <select
                        id="status_rizika_s"
                        name="status_rizika_s"
                        value={formData.status_rizika_s}
                        onChange={handleInputChange}
                        required
                        disabled={loading}
                    >
                        <option value="nizak">Nizak rizik</option>
                        <option value="umeren">Umeren rizik</option>
                        <option value="visok">Visok rizik</option>
                    </select>
                </div>

                <div className="form-actions">
                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={loading}
                    >
                        {loading ? 'Dodavanje...' : 'Dodaj Skladište'}
                    </button>
                </div>
            </form>

            <div className="form-info">
                <h3>Informacije o statusu rizika:</h3>
                <ul>
                    <li><strong>Nizak rizik:</strong> Standardno skladište sa osnovnim bezbednosnim merama</li>
                    <li><strong>Umeren rizik:</strong> Skladište za osetljive materijale sa pojačanim nadzorom</li>
                    <li><strong>Visok rizik:</strong> Skladište za opasne ili vrlo vredne materijale</li>
                </ul>
            </div>
                </div>
            </main>
        </div>
    );
};

export default DodajSkladiste;