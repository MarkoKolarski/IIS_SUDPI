import React, { useState, useEffect } from 'react';
import '../styles/LogisticTransport.css';
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";
import { useNavigate } from "react-router-dom";
import VozacStatusModal from "../components/VozacStatusModal";

const LogisticTransport = () => {
    const [vozila, setVozila] = useState([]);
    const [vozaci, setVozaci] = useState([]);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    // Modal state
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedVozac, setSelectedVozac] = useState(null);
    const [newStatus, setNewStatus] = useState('');
    const [statusMessage, setStatusMessage] = useState('');

    const navigate = useNavigate();

    const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);

   /*
    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    };
    */

    const fetchUser = async () => {
        try {
            const response = await axiosInstance.get('/api/user/profile/');
            if (response.status === 200) setUser(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju korisnika:', error);
        }
    };

    const fetchVozila = async () => {
        try {
            setLoading(true);
            const response = await axiosInstance.get('/api/vozila/');
            if (response.status === 200) setVozila(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju vozila:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchVozaci = async () => {
        try {
            setLoading(true);
            const response = await axiosInstance.get('/api/vozaci/');
            if (response.status === 200) setVozaci(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju vozača:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUser();
        fetchVozila();
        fetchVozaci();
    }, []);

    const handleEditVozilo = (vozilo) => navigate(`/vozila/update/${vozilo.sifra_v}`);

    // Otvaranje modal
    const handleEditVozac = (vozac) => {
        setSelectedVozac(vozac);
        setNewStatus(vozac.status || '');
        setStatusMessage('');
        setModalOpen(true);
    };

    // Potvrda statusa
    const handleConfirmStatus = async () => {
        if (!selectedVozac || !newStatus) return;
        try {
            const response = await axiosInstance.put(
                `vozaci/update-status/${selectedVozac.sifra_vo}/`,
                { status: newStatus }
            );
            if (response.status === 200) {
                setStatusMessage('Status je uspešno ažuriran.');
                fetchVozaci();
            } else {
                setStatusMessage('Došlo je do greške prilikom ažuriranja.');
            }
        } catch {
            setStatusMessage('Došlo je do greške prilikom ažuriranja.');
        }
    };

    const getStatusBadgeClass = (status) => {
        switch (status) {
            case 'aktivno':
            case 'slobodan': return 'status-active';
            case 'zauzeto':
            case 'zauzet': return 'status-busy';
            case 'na odmoru': return 'status-inactive';
            default: return 'status-inactive';
        }
    };

    return (
        <div className={`logistic-transport-container ${isSidebarCollapsed ? 'collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
                activePage="logistics-transport"
            />
            <div className="main-content">
                <div className="header">
                    <h1>Logistika i transport</h1>
                    <div className="user-profile">
                        <div className="user-info">
                            <div>Administrator</div>
                            <div className="user-email">{user ? user.mail_k : 'Učitavanje...'}</div>
                        </div>
                        <div className="user-avatar">
                            <div className="avatar-placeholder">A</div>
                        </div>
                    </div>
                </div>

                {/* Vozila */}
                <section className="transport-section">
                    <div className="section-header"><h2 className="section-title">Pregled svih vozila</h2></div>
                    {loading ? <div className="loading">Učitavanje podataka...</div> :
                        <div className="table-container">
                            <table className="transport-table">
                                <thead>
                                    <tr>
                                        <th>Šifra vozila</th>
                                        <th>Status</th>
                                        <th>Istek registracije</th>
                                        <th>Kapacitet</th>
                                        <th>Akcije</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {vozila.length > 0 ? vozila.map(v => (
                                        <tr key={v.sifra_v}>
                                            <td>{v.sifra_v}</td>
                                            <td><span className={`status-badge ${getStatusBadgeClass(v.status)}`}>{v.status}</span></td>
                                            {/* <td>{formatDate(v.registracija)}</td> */}
                                            <td>{v.registracija}</td>
                                            <td>{v.kapacitet}</td>
                                            <td><button className="btn-edit" onClick={() => handleEditVozilo(v)}>Izmeni</button></td>
                                        </tr>
                                    )) : <tr><td colSpan="5" style={{textAlign:'center', padding:'20px'}}>Nema podataka o vozilima</td></tr>}
                                </tbody>
                            </table>
                        </div>}
                </section>

                {/* Vozači */}
                <section className="transport-section">
                    <div className="section-header"><h2 className="section-title">Pregled svih vozača</h2></div>
                    {loading ? <div className="loading">Učitavanje podataka...</div> :
                        <div className="table-container">
                            <table className="transport-table">
                                <thead>
                                    <tr>
                                        <th>Ime</th>
                                        <th>Prezime</th>
                                        <th>Status</th>
                                        <th>Broj vožnji</th>
                                        <th>Akcije</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {vozaci.length > 0 ? vozaci.map(v => (
                                        <tr key={v.sifra_vo}>
                                            <td>{v.ime_vo}</td>
                                            <td>{v.prz_vo}</td>
                                            <td><span className={`status-badge ${getStatusBadgeClass(v.status)}`}>{v.status}</span></td>
                                            <td>{v.br_voznji}</td>
                                            <td><button className="btn-edit" onClick={() => handleEditVozac(v)}>Izmeni</button></td>
                                        </tr>
                                    )) : <tr><td colSpan="5" style={{textAlign:'center', padding:'20px'}}>Nema podataka o vozačima</td></tr>}
                                </tbody>
                            </table>
                        </div>}
                </section>

                {/* Modal */}
                <VozacStatusModal
                    modalOpen={modalOpen}
                    selectedVozac={selectedVozac}
                    newStatus={newStatus}
                    setNewStatus={setNewStatus}
                    handleConfirmStatus={handleConfirmStatus}
                    statusMessage={statusMessage}
                    onClose={() => setModalOpen(false)}
                />
            </div>
        </div>
    );
};

export default LogisticTransport;
