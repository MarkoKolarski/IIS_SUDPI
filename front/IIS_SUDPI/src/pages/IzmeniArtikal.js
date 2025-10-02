import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/IzmeniArtikal.css';

const IzmeniArtikal = () => {
    const { sifra_a } = useParams();
    const navigate = useNavigate();
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    
    const [formData, setFormData] = useState({
        naziv_a: '',
        osnovna_cena_a: '',
        rok_trajanja_a: ''
    });
    
    const [loading, setLoading] = useState(false);
    const [fetchLoading, setFetchLoading] = useState(true);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    // Učitaj postojeće podatke artikla
    useEffect(() => {
        fetchArtikal();
    }, [sifra_a]);

    const fetchArtikal = async () => {
        try {
            setFetchLoading(true);
            const response = await axiosInstance.get(`/artikli/${sifra_a}`);
            const artikal = response.data;
            
            setFormData({
                naziv_a: artikal.naziv_a,
                osnovna_cena_a: artikal.osnovna_cena_a,
                rok_trajanja_a: formatDateForInput(artikal.rok_trajanja_a)
            });
            setError('');
        } catch (error) {
            console.error('Greška pri učitavanju artikla:', error);
            if (error.response?.status === 404) {
                setError('Artikal nije pronađen');
            } else {
                setError('Greška pri učitavanju podataka artikla');
            }
        } finally {
            setFetchLoading(false);
        }
    };

    const formatDateForInput = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toISOString().split('T')[0]; // YYYY-MM-DD format
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Ukloni poruke kada korisnik počne da kuca
        if (error) setError('');
        if (successMessage) setSuccessMessage('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validacija
        if (!formData.naziv_a.trim()) {
            setError('Naziv artikla je obavezan');
            return;
        }
        
        if (!formData.osnovna_cena_a || parseFloat(formData.osnovna_cena_a) <= 0) {
            setError('Osnovna cena mora biti pozitivna vrednost');
            return;
        }
        
        if (!formData.rok_trajanja_a) {
            setError('Rok trajanja je obavezan');
            return;
        }

        try {
            setLoading(true);
            setError('');
            
            const response = await axiosInstance.put(`/artikli/${sifra_a}/izmeni`, formData);
            
            setSuccessMessage('Artikal je uspešno ažuriran!');
            
            // Preusmeri na pretragu nakon 2 sekunde
            setTimeout(() => {
                navigate('/pretraga-artikala');
            }, 2000);
            
        } catch (error) {
            console.error('Greška pri ažuriranju artikla:', error);
            
            if (error.response?.data?.error) {
                setError(error.response.data.error);
            } else if (error.response?.status === 404) {
                setError('Artikal nije pronađen');
            } else if (error.response?.status === 403) {
                setError('Nemate dozvolu za izmenu artikala');
            } else {
                setError('Greška pri ažuriranju artikla');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/pretraga-artikala');
    };

    if (fetchLoading) {
        return (
            <div className={`izmeni-artikal-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                <MainSideBar
                    isCollapsed={isSidebarCollapsed}
                    toggleSidebar={toggleSidebar}
                />
                <main className="izmeni-artikal-main-content">
                    <div className="izmeni-artikal-container">
                        <div className="loading-message">
                            Učitavanje podataka artikla...
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className={`izmeni-artikal-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="izmeni-artikal-main-content">
                <div className="izmeni-artikal-container">
                    <div className="izmeni-artikal-header">
                        <h1>Izmena artikala</h1>
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    {successMessage && (
                        <div className="success-message">
                            {successMessage}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="izmeni-artikal-form">
                        <div className="form-group">
                            <label htmlFor="naziv_a">Naziv</label>
                            <input
                                type="text"
                                id="naziv_a"
                                name="naziv_a"
                                value={formData.naziv_a}
                                onChange={handleInputChange}
                                className="form-input"
                                disabled={loading}
                                placeholder="Unesite naziv artikla"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="osnovna_cena_a">Osnovna cena</label>
                            <input
                                type="number"
                                id="osnovna_cena_a"
                                name="osnovna_cena_a"
                                value={formData.osnovna_cena_a}
                                onChange={handleInputChange}
                                className="form-input"
                                disabled={loading}
                                step="0.01"
                                min="0"
                                placeholder="Unesite osnovnu cenu"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="rok_trajanja_a">Rok trajanja</label>
                            <input
                                type="date"
                                id="rok_trajanja_a"
                                name="rok_trajanja_a"
                                value={formData.rok_trajanja_a}
                                onChange={handleInputChange}
                                className="form-input"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-actions">
                            <button
                                type="button"
                                onClick={handleCancel}
                                className="cancel-button"
                                disabled={loading}
                            >
                                Odustani
                            </button>
                            <button
                                type="submit"
                                className="submit-button"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="loading-spinner"></span>
                                        Čuvanje...
                                    </>
                                ) : (
                                    'Potvrdi'
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default IzmeniArtikal;