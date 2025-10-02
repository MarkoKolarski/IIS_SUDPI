import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/IzmenaZaliha.css';

const IzmenaZaliha = () => {
    const { zalihaId } = useParams();
    const navigate = useNavigate();
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    
    const [formData, setFormData] = useState({
        trenutna_kolicina_a: '',
        skladiste: ''
    });
    
    const [artikalNaziv, setArtikalNaziv] = useState('');
    const [skladista, setSkladista] = useState([]);
    const [loading, setLoading] = useState(false);
    const [fetchLoading, setFetchLoading] = useState(true);
    const [skladistaLoading, setSkladistaLoading] = useState(true);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    // Učitaj postojeće podatke zalihe i skladišta
    useEffect(() => {
        fetchZaliha();
        fetchSkladista();
    }, [zalihaId]);

    const fetchZaliha = async () => {
        try {
            setFetchLoading(true);
            const response = await axiosInstance.get(`/zalihe/${zalihaId}/`);
            const zaliha = response.data;
            
            setFormData({
                trenutna_kolicina_a: zaliha.trenutna_kolicina_a,
                skladiste: zaliha.skladiste_sifra
            });
            setArtikalNaziv(zaliha.artikal_naziv);
            setError('');
        } catch (error) {
            console.error('Greška pri učitavanju zalihe:', error);
            if (error.response?.status === 404) {
                setError('Zaliha nije pronađena');
            } else {
                setError('Greška pri učitavanju podataka zalihe');
            }
        } finally {
            setFetchLoading(false);
        }
    };

    const fetchSkladista = async () => {
        try {
            setSkladistaLoading(true);
            const response = await axiosInstance.get('/skladista/');
            setSkladista(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju skladišta:', error);
            setError('Greška pri učitavanju skladišta');
        } finally {
            setSkladistaLoading(false);
        }
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
        if (!formData.trenutna_kolicina_a || parseInt(formData.trenutna_kolicina_a) < 0) {
            setError('Količina mora biti pozitivna vrednost');
            return;
        }
        
        if (!formData.skladiste) {
            setError('Skladište je obavezno');
            return;
        }

        try {
            setLoading(true);
            setError('');
            
            const updateData = {
                trenutna_kolicina_a: parseInt(formData.trenutna_kolicina_a),
                skladiste: formData.skladiste
            };
            
            const response = await axiosInstance.put(`/zalihe/${zalihaId}/izmeni/`, updateData);
            
            setSuccessMessage('Stanje zalihe je uspešno ažurirano!');
            
            // Preusmeri na pregled zaliha nakon 2 sekunde
            setTimeout(() => {
                navigate('/pregled-zaliha');
            }, 2000);
            
        } catch (error) {
            console.error('Greška pri ažuriranju zalihe:', error);
            
            if (error.response?.data?.error) {
                setError(error.response.data.error);
            } else if (error.response?.status === 404) {
                setError('Zaliha nije pronađena');
            } else if (error.response?.status === 403) {
                setError('Nemate dozvolu za izmenu zaliha');
            } else {
                setError('Greška pri ažuriranju zalihe');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/pregled-zaliha');
    };

    if (fetchLoading || skladistaLoading) {
        return (
            <div className={`izmena-zaliha-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                <MainSideBar
                    isCollapsed={isSidebarCollapsed}
                    toggleSidebar={toggleSidebar}
                />
                <main className="izmena-zaliha-main-content">
                    <div className="izmena-zaliha-container">
                        <div className="loading-message">
                            Učitavanje podataka...
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className={`izmena-zaliha-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="izmena-zaliha-main-content">
                <div className="izmena-zaliha-container">
                    <div className="izmena-zaliha-header">
                        <h1>Izmena stanja zaliha</h1>
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

                    {/* Artikal naziv - read-only display */}
                    <div className="artikal-display">
                        <h2>{artikalNaziv}</h2>
                    </div>

                    <form onSubmit={handleSubmit} className="izmena-zaliha-form">
                        <div className="form-group">
                            <label htmlFor="trenutna_kolicina_a">Količina</label>
                            <input
                                type="number"
                                id="trenutna_kolicina_a"
                                name="trenutna_kolicina_a"
                                value={formData.trenutna_kolicina_a}
                                onChange={handleInputChange}
                                className="form-input"
                                disabled={loading}
                                min="0"
                                placeholder="Unesite količinu"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="skladiste">Skladište</label>
                            <select
                                id="skladiste"
                                name="skladiste"
                                value={formData.skladiste}
                                onChange={handleInputChange}
                                className="form-select"
                                disabled={loading}
                            >
                                <option value="">Odaberite skladište</option>
                                {skladista.map((skladiste) => (
                                    <option key={skladiste.sifra_s} value={skladiste.sifra_s}>
                                        {skladiste.mesto_s}
                                    </option>
                                ))}
                            </select>
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

export default IzmenaZaliha;