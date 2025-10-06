import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import ConfirmDeleteModal from '../components/ConfirmDeleteModal';
import '../styles/PretragaArtikala.css';

const PretragaArtikala = () => {
    const navigate = useNavigate();
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [artikli, setArtikli] = useState([]);
    const [filteredArtikli, setFilteredArtikli] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [artikalToDelete, setArtikalToDelete] = useState(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchArtikli = useCallback(async () => {
        try {
            setLoading(true);
            const response = await axiosInstance.get('/artikli/');
            setArtikli(response.data);
            setError('');
        } catch (error) {
            console.error('Greška pri učitavanju artikala:', error);
            setError('Nije moguće učitati artikle');
        } finally {
            setLoading(false);
        }
    }, []);

    // Učitavanje artikala na početku
    useEffect(() => {
        fetchArtikli();
    }, [fetchArtikli]);

    // Filtriranje artikala kada se promeni search term
    useEffect(() => {
        if (searchTerm.trim() === '') {
            setFilteredArtikli(artikli);
        } else {
            const filtered = artikli.filter(artikal =>
                artikal.naziv_a.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredArtikli(filtered);
        }
    }, [searchTerm, artikli]);

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
    };

    const handleEdit = (artikalId) => {
        // Navigiraj na stranicu za izmenu artikla
        navigate(`/izmeni-artikal/${artikalId}`);
    };

    const handleDelete = (artikalId) => {
        // Pronađi artikal za brisanje
        const artikal = artikli.find(a => a.sifra_a === artikalId);
        if (artikal) {
            setArtikalToDelete(artikal);
            setShowDeleteModal(true);
        }
    };

    const confirmDelete = async () => {
        if (!artikalToDelete) return;

        try {
            setIsDeleting(true);
            console.log('Brisanje artikla sa ID:', artikalToDelete.sifra_a);
            
            const response = await axiosInstance.delete(`/artikli/${artikalToDelete.sifra_a}/obrisi`);
            console.log('Odgovor servera:', response.data);
            
            // Ažuriraj listu artikala - ukloni obrisani artikal
            setArtikli(prevArtikli => prevArtikli.filter(artikal => artikal.sifra_a !== artikalToDelete.sifra_a));
            
            // Zatvaraj modal
            setShowDeleteModal(false);
            setArtikalToDelete(null);
            
            // Prikaži poruku o uspešnom brisanju (bez alert popup-a)
            setSuccessMessage(response.data.message || 'Artikal je uspešno obrisan');
            
            // Ukloni poruku nakon 5 sekundi
            setTimeout(() => {
                setSuccessMessage('');
            }, 5000);
            
        } catch (error) {
            console.error('Kompletna greška:', error);
            console.error('Error response:', error.response);
            console.error('Error status:', error.response?.status);
            console.error('Error data:', error.response?.data);
            
            let errorMessage = 'Greška pri brisanju artikla';
            if (error.response?.data?.error) {
                errorMessage = error.response.data.error;
            } else if (error.response?.data?.details) {
                errorMessage = `${error.response.data.error}: ${error.response.data.details}`;
            } else if (error.response?.status === 404) {
                errorMessage = 'Artikal nije pronađen';
            } else if (error.response?.status === 403) {
                errorMessage = 'Nemate dozvolu za brisanje artikala';
            } else if (error.response?.status === 401) {
                errorMessage = 'Niste ulogovani';
            } else if (error.message) {
                errorMessage = `Mrežna greška: ${error.message}`;
            }
            
            alert(errorMessage);
        } finally {
            setIsDeleting(false);
        }
    };

    const cancelDelete = () => {
        setShowDeleteModal(false);
        setArtikalToDelete(null);
    };

    // Automatski ukloni success poruku kada se promeni lista artikala
    useEffect(() => {
        if (successMessage) {
            setError(''); // Ukloni error poruke ako postoje
        }
    }, [successMessage]);

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('sr-Latn-RS');
    };

    const getStatusClass = (status) => {
        switch(status) {
            case 'ok': return 'status-ok';
            case 'isteklo': return 'status-expired';
            case 'rizik': return 'status-risk';
            default: return 'status-unknown';
        }
    };

    const getStatusLabel = (status) => {
        switch(status) {
            case 'ok': return 'Aktivan';
            case 'isteklo': return 'Istekao';
            case 'rizik': return 'Ističe';
            default: return 'Nepoznat';
        }
    };

    // Auto-refresh funkcionalnost
    useEffect(() => {
        const interval = setInterval(() => {
            fetchArtikli();
        }, 30000); // Osvežava svakih 30 sekundi

        return () => clearInterval(interval);
    }, [fetchArtikli]);

    return (
        <div className={`pretraga-artikala-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="pretraga-artikala-main-content">
                <div className="pretraga-artikala-container">
                    <div className="pretraga-artikala-header">
                        <h1>Pretraga artikala</h1>
                    </div>

                    <div className="search-section">
                        <input
                            type="text"
                            placeholder="Pretraži..."
                            value={searchTerm}
                            onChange={handleSearchChange}
                            className="search-input"
                        />
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

                    {loading ? (
                        <div className="loading-message">
                            Učitavanje artikala...
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="artikli-table">
                                <thead>
                                    <tr>
                                        <th>Naziv</th>
                                        <th>Cena</th>
                                        <th>Rok trajanja</th>
                                        <th>Status</th>
                                        <th>Akcije</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredArtikli.length > 0 ? (
                                        filteredArtikli.map((artikal) => (
                                            <tr key={artikal.sifra_a}>
                                                <td>{artikal.naziv_a}</td>
                                                <td>{artikal.osnovna_cena_a} RSD</td>
                                                <td>{formatDate(artikal.rok_trajanja_a)}</td>
                                                <td className="status-cell">
                                                    <span className={`status-badge ${getStatusClass(artikal.status || 'ok')}`}>
                                                        {getStatusLabel(artikal.status || 'ok')}
                                                    </span>
                                                </td>
                                                <td className="actions-cell">
                                                    <button
                                                        className="btn-edit"
                                                        onClick={() => handleEdit(artikal.sifra_a)}
                                                    >
                                                        Izmeni
                                                    </button>
                                                    <button
                                                        className="btn-delete"
                                                        onClick={() => handleDelete(artikal.sifra_a)}
                                                    >
                                                        Obriši
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="5" className="no-results">
                                                {searchTerm ? 'Nema rezultata pretrage' : 'Nema artikala'}
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>

            {/* Custom Delete Confirmation Modal */}
            <ConfirmDeleteModal
                isOpen={showDeleteModal}
                onClose={cancelDelete}
                onConfirm={confirmDelete}
                artikalNaziv={artikalToDelete?.naziv_a || ''}
                loading={isDeleting}
            />
        </div>
    );
};

export default PretragaArtikala;
