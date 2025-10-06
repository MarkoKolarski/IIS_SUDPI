import React, { useState, useEffect, useCallback } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DashboardSO.css';

const DashboardSO = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [skladista, setSkladista] = useState([]);
    const [rizicniArtikli, setRizicniArtikli] = useState([]);
    const [statistike, setStatistike] = useState(null);
    const [grafikonData, setGrafikonData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingArtikli, setLoadingArtikli] = useState(true);
    const [loadingStatistike, setLoadingStatistike] = useState(true);
    const [loadingGrafikon, setLoadingGrafikon] = useState(true);
    const [error, setError] = useState('');
    const [errorArtikli, setErrorArtikli] = useState('');
    const [errorStatistike, setErrorStatistike] = useState('');
    const [errorGrafikon, setErrorGrafikon] = useState('');

    const toggleSidebar = () => {
        setSidebarCollapsed(!isSidebarCollapsed);
    };

    const fetchSkladista = useCallback(async () => {
        try {
            setLoading(true);
            setError('');
            
            // Debug token pre poziva
            const token = sessionStorage.getItem('access_token');
            console.log('Token za skladista API:', token ? 'Postoji' : 'Ne postoji');
            
            const response = await axiosInstance.get('/skladista/');
            setSkladista(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju skladišta:', error);
            console.error('Error response:', error.response);
            
            if (error.response?.status === 401) {
                console.log('Token expired ili nemate dozvolu - redirect na login');
                setError('Sesija je istekla. Molimo prijavite se ponovo.');
                
                // Ukloni token iz sessionStorage
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('refresh_token');
                
                // Redirect na login nakon 3 sekunde
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                setError('Greška pri učitavanju skladišta');
            }
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchRizicniArtikli = useCallback(async () => {
        try {
            setLoadingArtikli(true);
            setErrorArtikli('');
            
            // Debug token pre poziva
            const token = sessionStorage.getItem('access_token');
            console.log('Token za rizicni artikli API:', token ? 'Postoji' : 'Ne postoji');
            
            const response = await axiosInstance.get('/rizicni-artikli/');
            setRizicniArtikli(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju rizičnih artikala:', error);
            console.error('Error response:', error.response);
            
            if (error.response?.status === 401) {
                console.log('Token expired ili nemate dozvolu - redirect na login');
                setErrorArtikli('Sesija je istekla. Molimo prijavite se ponovo.');
                
                // Ukloni token iz sessionStorage
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('refresh_token');
                
                // Redirect na login nakon 3 sekunde
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                setErrorArtikli('Greška pri učitavanju rizičnih artikala');
            }
        } finally {
            setLoadingArtikli(false);
        }
    }, []);

    const fetchStatistike = useCallback(async () => {
        try {
            setLoadingStatistike(true);
            setErrorStatistike('');
            
            const token = sessionStorage.getItem('access_token');
            console.log('Token za statistike API:', token ? 'Postoji' : 'Ne postoji');
            
            const response = await axiosInstance.get('/artikli/statistike/');
            setStatistike(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju statistika:', error);
            console.error('Error response:', error.response);
            
            if (error.response?.status === 401) {
                console.log('Token expired ili nemate dozvolu - redirect na login');
                setErrorStatistike('Sesija je istekla. Molimo prijavite se ponovo.');
                
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('refresh_token');
                
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                setErrorStatistike('Greška pri učitavanju statistika');
            }
        } finally {
            setLoadingStatistike(false);
        }
    }, []);

    const fetchGrafikon = useCallback(async () => {
        try {
            setLoadingGrafikon(true);
            setErrorGrafikon('');
            
            const token = sessionStorage.getItem('access_token');
            console.log('Token za grafikon API:', token ? 'Postoji' : 'Ne postoji');
            
            const response = await axiosInstance.get('/artikli/grafikon-po-nedeljama/');
            setGrafikonData(response.data);
        } catch (error) {
            console.error('Greška pri učitavanju grafikona:', error);
            console.error('Error response:', error.response);
            
            if (error.response?.status === 401) {
                console.log('Token expired ili nemate dozvolu - redirect na login');
                setErrorGrafikon('Sesija je istekla. Molimo prijavite se ponovo.');
                
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('refresh_token');
                
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                setErrorGrafikon('Greška pri učitavanju grafikona');
            }
        } finally {
            setLoadingGrafikon(false);
        }
    }, []);

    useEffect(() => {
        fetchSkladista();
        fetchRizicniArtikli();
        fetchStatistike();
        fetchGrafikon();
        
        // Auto-refresh svakih 30 sekundi da povuče najnovije podatke
        const interval = setInterval(() => {
            fetchSkladista();
            fetchRizicniArtikli();
            fetchStatistike();
            fetchGrafikon();
        }, 30000);
        
        // Cleanup interval kada se komponenta unmount-uje
        return () => clearInterval(interval);
    }, [fetchSkladista, fetchRizicniArtikli, fetchStatistike, fetchGrafikon]);

    const getTemperatureDisplayColor = (temperatura) => {
        if (temperatura === null) return '#6b7280'; // siva za N/A
        if (temperatura <= 2) return '#3b82f6'; // plava za nisku
        if (temperatura <= 5) return '#16a34a'; // zelena za umereenu
        return '#dc2626'; // crvena za visoku
    };

    const getRizikDisplayText = (statusRizika) => {
        const map = {
            'nizak': 'ne',
            'umeren': 'umereno', 
            'visok': 'da'
        };
        return map[statusRizika] || statusRizika;
    };

    const formatCena = (cena) => {
        if (cena === null || cena === undefined) return 'N/A';
        return `${parseFloat(cena).toFixed(2)} RSD`;
    };

    const getDaniDoIstekaColor = (dani) => {
        if (dani <= 1) return '#dc2626'; // crvena - kritično
        if (dani <= 3) return '#f97316'; // narandžasta - upozorenje
        if (dani <= 7) return '#eab308'; // žuta - pažnja
        return '#16a34a'; // zelena - ok
    };

    const getDaniDoIstekaText = (dani) => {
        if (dani < 0) return `Istekao pre ${Math.abs(dani)} dana`;
        if (dani === 0) return 'Ističe danas';
        if (dani === 1) return 'Ističe sutra';
        return `Ističe za ${dani} dana`;
    };

    return (
        <div className={`dashboard-so-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
            />
            <main className="dashboard-so-main-content">
                <header className="dashboard-header">
                    <h1>Kontrolna tabla - Skladišni operater</h1>
                </header>

                <div className="dashboard-content">
                    <div className="dashboard-grid">
                        {/* Stanje u skladištima */}
                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Stanje u skladištima</h3>
                            </div>
                            <div className="card-content">
                                {loading && <div className="loading">Učitavanje skladišta...</div>}
                                {error && <div className="error">{error}</div>}
                                
                                {!loading && !error && (
                                    <div className="skladista-table-container">
                                        <table className="skladista-table">
                                            <thead>
                                                <tr>
                                                    <th>Mesto</th>
                                                    <th>Temperatura</th>
                                                    <th>Rizik</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {skladista.length > 0 ? (
                                                    skladista.map((skladiste) => (
                                                        <tr key={skladiste.sifra_s}>
                                                            <td>{skladiste.mesto_s}</td>
                                                            <td style={{
                                                                color: getTemperatureDisplayColor(skladiste.poslednja_temperatura)
                                                            }}>
                                                                {skladiste.poslednja_temperatura !== null ? skladiste.poslednja_temperatura : 'N/A'}
                                                            </td>
                                                            <td>{getRizikDisplayText(skladiste.status_rizika_s)}</td>
                                                        </tr>
                                                    ))
                                                ) : (
                                                    <tr>
                                                        <td colSpan="3" className="no-data">
                                                            Nema skladišta za prikaz
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Trenutno rizični artikli</h3>
                            </div>
                            <div className="card-content">
                                {loadingArtikli && <div className="loading">Učitavanje artikala...</div>}
                                {errorArtikli && <div className="error">{errorArtikli}</div>}
                                
                                {!loadingArtikli && !errorArtikli && (
                                    <div className="artikli-table-container">
                                        <table className="artikli-table">
                                            <thead>
                                                <tr>
                                                    <th>Artikal</th>
                                                    <th>Osnovna cena</th>
                                                    <th>Nova cena</th>
                                                    <th>Isteka</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {rizicniArtikli.length > 0 ? (
                                                    rizicniArtikli.map((artikal) => (
                                                        <tr key={artikal.sifra_a}>
                                                            <td>
                                                                {artikal.naziv_a}
                                                            </td>
                                                            <td className="price-cell">
                                                                {formatCena(artikal.osnovna_cena_a)}
                                                            </td>
                                                            <td className="price-cell discount-price">
                                                                {artikal.popust_cena ? (
                                                                    <span className="discounted">
                                                                        {formatCena(artikal.popust_cena)}
                                                                    </span>
                                                                ) : (
                                                                    <span className="no-discount">Nema popusta</span>
                                                                )}
                                                            </td>
                                                            <td style={{
                                                                color: getDaniDoIstekaColor(artikal.dani_do_isteka),
                                                                fontSize: '0.9em'
                                                            }}>
                                                                {getDaniDoIstekaText(artikal.dani_do_isteka)}
                                                            </td>
                                                        </tr>
                                                    ))
                                                ) : (
                                                    <tr>
                                                        <td colSpan="4" className="no-data">
                                                            Nema rizičnih artikala za prikaz
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Detalji o artiklima</h3>
                            </div>
                            <div className="card-content">
                                {loadingStatistike && <div className="loading">Učitavanje statistika...</div>}
                                {errorStatistike && <div className="error">{errorStatistike}</div>}
                                
                                {!loadingStatistike && !errorStatistike && statistike && (
                                    <div className="statistike-container">
                                        <div className="statistika-item">
                                            <div className="statistika-label">Ukupno različitih artikala:</div>
                                            <div className="statistika-value">{statistike.ukupno_artikala}</div>
                                        </div>
                                        <div className="statistika-item">
                                            <div className="statistika-label">Ukupno rizičnih artikala:</div>
                                            <div className="statistika-value rizicni">{statistike.rizicni_artikli}</div>
                                        </div>
                                        <div className="statistika-item">
                                            <div className="statistika-label">Ukupno propalih artikala:</div>
                                            <div className="statistika-value propali">{statistike.propali_artikli}</div>
                                        </div>
                                        <div className="statistika-item">
                                            <div className="statistika-label">Gubitak na propalim artiklima:</div>
                                            <div className="statistika-value steta">{statistike.ukupna_steta.toLocaleString()}.000</div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="dashboard-card">
                            <div className="card-header">
                                <h3>Grafik - Artikli po isteku roka</h3>
                            </div>
                            <div className="card-content">
                                {loadingGrafikon && <div className="loading">Učitavanje grafikona...</div>}
                                {errorGrafikon && <div className="error">{errorGrafikon}</div>}
                                
                                {!loadingGrafikon && !errorGrafikon && grafikonData && (
                                    <div className="grafikon-container">
                                        <div className="grafikon-stubici">
                                            {grafikonData.grafikon_data.map((podatak, index) => {
                                                const maxVrednost = Math.max(...grafikonData.grafikon_data.map(d => d.broj_artikala));
                                                const visina = maxVrednost > 0 ? (podatak.broj_artikala / maxVrednost) * 100 : 0;
                                                
                                                return (
                                                    <div key={index} className="grafikon-stubic-wrapper">
                                                        <div className="grafikon-vrednost">
                                                            {podatak.broj_artikala}
                                                        </div>
                                                        <div 
                                                            className="grafikon-stubic"
                                                            style={{ height: `${Math.max(visina, 5)}%` }}
                                                        ></div>
                                                        <div className="grafikon-label">
                                                            {podatak.nedelja}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardSO;