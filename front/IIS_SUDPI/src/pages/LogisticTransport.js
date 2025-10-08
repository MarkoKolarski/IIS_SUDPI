import React, { useState, useEffect } from 'react';
import '../styles/LogisticTransport.css';
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";

const LogisticTransport = () => {
    const [vozila, setVozila] = useState([]);
    const [vozaci, setVozaci] = useState([]);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    // Funkcija za toggle sidebar
    const toggleSidebar = () => {
        setIsSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchUser = async () => {
        try {
            //const userId = sessionStorage.getItem('user_id');
            //const response = await axiosInstance.get(`/api/users/${userId}/`);
            const response = await axiosInstance.get('/api/user/profile/');
            //const user = response.data;
            if (response.status === 200) {
                const userData = response.data;         
                setUser(userData);
                //console.log('Učitani podaci o korisniku:', userData);
                console.log('Učitani podaci o korisniku:', userData);
                if (userData.mail_k) {
                    console.log('Email korisnika:', userData.mail_k);
                }
            } else {
                console.error('Greška pri učitavanju podataka o korisniku:', response.data.error);
            }
        } catch (error) {
            console.error('Greška pri učitavanju podataka o korisniku:', error);
        }
    };

    // useEffect(() => {
    //     fetchUser();
    // }, []);

    // Funkcija za dobavljanje vozila sa axios
    const fetchVozila = async () => {
        try {
            setLoading(true);
            const response = await axiosInstance.get('/api/vozila/');
            
            if (response.status === 200) {
                setVozila(response.data);
            } else {
                console.error('Greška pri učitavanju vozila:', response.data.error);
            }
        } catch (error) {
            console.error('Greška pri učitavanju vozila:', error);
            if (error.response) {
                console.error('Status:', error.response.status);
                console.error('Data:', error.response.data);
            }
        } finally {
            setLoading(false);
        }
    };

    // Funkcija za dobavljanje vozača sa axios
    const fetchVozaci = async () => {
        try {
            setLoading(true);
            const response = await axiosInstance.get('/api/vozaci/');
            
            if (response.status === 200) {
                setVozaci(response.data);
            } else {
                console.error('Greška pri učitavanju vozača:', response.data.error);
            }
        } catch (error) {
            console.error('Greška pri učitavanju vozača:', error);
            if (error.response) {
                console.error('Status:', error.response.status);
                console.error('Data:', error.response.data);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUser();
        fetchVozila();
        fetchVozaci();
    }, []);

    const handleEditVozilo = (vozilo) => {
        console.log('Izmena vozila:', vozilo);
        // Logika za izmenu vozila
    };

    const handleEditVozac = (vozac) => {
        console.log('Izmena vozača:', vozac);
        // Logika za izmenu vozača
    };

    const getStatusBadgeClass = (status) => {
        switch (status) {
            case 'aktivno':
            case 'slobodan':
                return 'status-active';
            case 'zauzeto':
            case 'zauzet':
                return 'status-busy';
            case 'neaktívno':
            case 'na odmoru':
                return 'status-inactive';
            default:
                return 'status-inactive';
        }
    };

    return (
        <div className="logistic-transport-container">
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
                activePage="logistics-transport"
            />
            <div className={`main-content ${isSidebarCollapsed ? 'collapsed' : ''}`}>
                <div className="header">
                    <button className="sidebar-toggle" onClick={toggleSidebar}>
                        ☰
                    </button>
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

                {/* Sekcija za vozila */}
                <section className="transport-section">
                    <div className="section-header">
                        <h2 className="section-title">Pregled svih vozila</h2>
                        {/* <div className="section-actions">
                            <button className="btn btn-primary">Dodaj vozilo</button>
                            <button className="btn btn-secondary">Izvezi podatke</button>
                        </div> */}
                    </div>

                    {loading ? (
                        <div className="loading">Učitavanje podataka...</div>
                    ) : (
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
                                    {vozila && vozila.length > 0 ? (
                                        vozila.map(vozilo => (
                                            <tr key={vozilo.sifra_v}>
                                                <td>{vozilo.sifra_v}</td>
                                                <td>
                                                    <span className={`status-badge ${getStatusBadgeClass(vozilo.status)}`}>
                                                        {vozilo.status}
                                                    </span>
                                                </td>
                                                <td>{vozilo.istek_registracije}</td>
                                                <td>{vozilo.kapacitet}</td>
                                                <td>
                                                    <button 
                                                        className="btn-edit"
                                                        onClick={() => handleEditVozilo(vozilo)}
                                                    >
                                                        Izmeni
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="5" style={{textAlign: 'center', padding: '20px'}}>
                                                Nema podataka o vozilima
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>

                {/* Sekcija za vozače */}
                <section className="transport-section">
                    <div className="section-header">
                        <h2 className="section-title">Pregled svih vozača</h2>
                        {/* <div className="section-actions">
                            <button className="btn btn-primary">Dodaj vozača</button>
                            <button className="btn btn-secondary">Izvezi podatke</button>
                        </div> */}
                    </div>

                    {loading ? (
                        <div className="loading">Učitavanje podataka...</div>
                    ) : (
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
                                    {vozaci && vozaci.length > 0 ? (
                                        vozaci.map(vozac => (
                                            <tr key={vozac.sifra_vo}>
                                                <td>{vozac.ime_vo}</td>
                                                <td>{vozac.prz_vo}</td>
                                                <td>
                                                    <span className={`status-badge ${getStatusBadgeClass(vozac.status)}`}>
                                                        {vozac.status}
                                                    </span>
                                                </td>
                                                <td>{vozac.br_voznji}</td>
                                                <td>
                                                    <button 
                                                        className="btn-edit"
                                                        onClick={() => handleEditVozac(vozac)}
                                                    >
                                                        Izmeni
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="5" style={{textAlign: 'center', padding: '20px'}}>
                                                Nema podataka o vozačima
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
};

export default LogisticTransport;