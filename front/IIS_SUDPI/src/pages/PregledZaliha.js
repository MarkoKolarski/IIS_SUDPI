import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/PregledZaliha.css';

const PregledZaliha = () => {
    const navigate = useNavigate();
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [skladista, setSkladista] = useState([]);
    const [selectedSkladiste, setSelectedSkladiste] = useState('');
    const [zalihe, setZalihe] = useState([]);
    const [loading, setLoading] = useState(false);
    const [skladistaLoading, setSkladistaLoading] = useState(true);
    const [error, setError] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchSkladista = async () => {
        try {
            setSkladistaLoading(true);
            const response = await axiosInstance.get('/skladista/');
            setSkladista(response.data);
            setError('');
        } catch (error) {
            console.error('Greška pri učitavanju skladišta:', error);
            setError('Greška pri učitavanju skladišta');
        } finally {
            setSkladistaLoading(false);
        }
    };

    const fetchZalihe = useCallback(async () => {
        try {
            setLoading(true);
            setError('');
            
            let url = '/zalihe/';
            if (selectedSkladiste) {
                url += `?skladiste=${selectedSkladiste}`;
            }
            
            const response = await axiosInstance.get(url);
            setZalihe(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju zaliha:', error);
            console.error('Error response:', error.response);
            console.error('Error data:', error.response?.data);
            setError('Greška pri učitavanju zaliha');
            setZalihe([]);
        } finally {
            setLoading(false);
        }
    }, [selectedSkladiste]);

    // Učitaj zalihe kada se promeni selected skladište
    useEffect(() => {
        fetchSkladista();
        fetchZalihe();
    }, [selectedSkladiste, fetchZalihe]);

    const handleSkladisteChange = (e) => {
        setSelectedSkladiste(e.target.value);
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('sr-Latn-RS');
    };

    const handleAzuriraj = (zalihaId) => {
        navigate(`/izmena-zaliha/${zalihaId}`);
    };

    if (skladistaLoading) {
        return (
            <div className={`pregled-zaliha-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                <MainSideBar
                    isCollapsed={isSidebarCollapsed}
                    toggleSidebar={toggleSidebar}
                />
                <main className="pregled-zaliha-main-content">
                    <div className="pregled-zaliha-container">
                        <div className="loading-message">
                            Učitavanje skladišta...
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className={`pregled-zaliha-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="pregled-zaliha-main-content">
                <div className="pregled-zaliha-container">
                    <div className="pregled-zaliha-header">
                        <h1>Pregled stanja zaliha</h1>
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    {/* Dropdown za odabir skladišta */}
                    <div className="skladiste-selection">
                        <label htmlFor="skladiste-select">Odaberi skladište...</label>
                        <select
                            id="skladiste-select"
                            value={selectedSkladiste}
                            onChange={handleSkladisteChange}
                            className="skladiste-dropdown"
                        >
                            <option value="">Sva skladišta</option>
                            {skladista.map((skladiste) => (
                                <option key={skladiste.sifra_s} value={skladiste.sifra_s}>
                                    {skladiste.mesto_s}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Tabela zaliha */}
                    {loading ? (
                        <div className="loading-message">
                            Učitavanje zaliha...
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="zalihe-table">
                                <thead>
                                    <tr>
                                        <th>Artikal</th>
                                        <th>Količina</th>
                                        <th>Datum ažuriranja stanja</th>
                                        <th>Akcije</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {zalihe.length > 0 ? (
                                        zalihe.map((zaliha) => (
                                            <tr key={zaliha.id}>
                                                <td>{zaliha.artikal_naziv || 'N/A'}</td>
                                                <td>{zaliha.trenutna_kolicina_a}</td>
                                                <td>{formatDate(zaliha.datum_azuriranja)}</td>
                                                <td>
                                                    <button
                                                        className="azuriraj-button"
                                                        onClick={() => handleAzuriraj(zaliha.id)}
                                                    >
                                                        Ažuriraj
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="4" className="no-results">
                                                {selectedSkladiste 
                                                    ? 'Nema zaliha u odabranom skladištu' 
                                                    : 'Nema zaliha u sistemu'
                                                }
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default PregledZaliha;