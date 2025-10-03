import React, { useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DodajArtikal.css';

const DodajArtikal = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [formData, setFormData] = useState({
        naziv_a: '',
        osnovna_cena_a: '',
        rok_trajanja_a: '',
        sifra_s: '',
        trenutna_kolicina_a: ''
    });
    
    const [skladista, setSkladista] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    // Učitavanje skladišta
    useEffect(() => {
        fetchSkladista();
    }, []);

    const fetchSkladista = async () => {
        try {
            const response = await axiosInstance.get('/skladista/');
            setSkladista(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju skladišta:', error);
            setError('Nije moguće učitati skladišta');
        }
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
        if (!formData.naziv_a.trim()) {
            setError('Naziv artikla je obavezan');
            return;
        }
        if (!formData.osnovna_cena_a || parseInt(formData.osnovna_cena_a) <= 0) {
            setError('Osnovna cena mora biti pozitivan ceo broj');
            return;
        }
        if (!formData.rok_trajanja_a) {
            setError('Rok trajanja je obavezan');
            return;
        }
        if (!formData.sifra_s) {
            setError('Skladište je obavezno');
            return;
        }
        if (!formData.trenutna_kolicina_a || parseInt(formData.trenutna_kolicina_a) < 0) {
            setError('Količina mora biti pozitivna vrednost');
            return;
        }

        setLoading(true);
        setError('');
        setMessage('');

        try {
            const response = await axiosInstance.post('/artikli/dodaj/', {
                ...formData,
                osnovna_cena_a: parseInt(formData.osnovna_cena_a),
                sifra_s: parseInt(formData.sifra_s),
                trenutna_kolicina_a: parseInt(formData.trenutna_kolicina_a)
            });
            
            setMessage('Artikal je uspešno dodat!');
            
            // Resetuj formu
            setFormData({
                naziv_a: '',
                osnovna_cena_a: '',
                rok_trajanja_a: '',
                sifra_s: '',
                trenutna_kolicina_a: ''
            });

            console.log('Novi artikal:', response.data);
            
        } catch (error) {
            console.error('Greška pri dodavanju artikla:', error);
            
            if (error.response?.data?.details) {
                // Prikaži greške validacije
                const validationErrors = error.response.data.details;
                let errorMessage = '';
                
                Object.keys(validationErrors).forEach(key => {
                    if (validationErrors[key]) {
                        errorMessage += `${key}: ${validationErrors[key].join(', ')}\n`;
                    }
                });
                
                setError(errorMessage || 'Neispravni podaci');
            } else if (error.response?.data?.error) {
                setError(error.response.data.error);
            } else {
                setError('Došlo je do greške pri dodavanju artikla');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`dodaj-artikal-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="dodaj-artikal-main-content">
                <div className="dodaj-artikal-container">
                    <div className="dodaj-artikal-header">
                        <h1>Dodavanje artikala</h1>
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

            <form onSubmit={handleSubmit} className="dodaj-artikal-form">
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="naziv_a">
                            Naziv
                        </label>
                        <input
                            type="text"
                            id="naziv_a"
                            name="naziv_a"
                            value={formData.naziv_a}
                            onChange={handleInputChange}
                            placeholder=""
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="trenutna_kolicina_a">
                            Količina
                        </label>
                        <input
                            type="number"
                            min="0"
                            id="trenutna_kolicina_a"
                            name="trenutna_kolicina_a"
                            value={formData.trenutna_kolicina_a}
                            onChange={handleInputChange}
                            placeholder=""
                            required
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="osnovna_cena_a">
                            Osnovna cena
                        </label>
                        <input
                            type="number"
                            step="1"
                            min="1"
                            id="osnovna_cena_a"
                            name="osnovna_cena_a"
                            value={formData.osnovna_cena_a}
                            onChange={handleInputChange}
                            placeholder=""
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="rok_trajanja_a">
                            Rok trajanja
                        </label>
                        <input
                            type="date"
                            id="rok_trajanja_a"
                            name="rok_trajanja_a"
                            value={formData.rok_trajanja_a}
                            onChange={handleInputChange}
                            required
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="form-row full-width">
                    <div className="form-group">
                        <label htmlFor="sifra_s">
                            Skladište
                        </label>
                        <select
                            id="sifra_s"
                            name="sifra_s"
                            value={formData.sifra_s}
                            onChange={handleInputChange}
                            required
                            disabled={loading}
                        >
                            <option value="">-- Izaberite skladište --</option>
                            {skladista.map(skladiste => (
                                <option key={skladiste.sifra_s} value={skladiste.sifra_s}>
                                    {skladiste.mesto_s} (Rizik: {skladiste.status_rizika_s})
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="form-actions">
                    <button
                        type="button"
                        className="cancel-btn"
                        disabled={loading}
                    >
                        Odustani
                    </button>
                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={loading}
                    >
                        Potvrdi
                    </button>
                </div>
            </form>
                </div>
            </main>
        </div>
    );
};

export default DodajArtikal;