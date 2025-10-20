import React, { useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/UpozorenjaDashboard.css';

const UpozorenjaDashboard = () => {
    const [upozorenja, setUpozorenja] = useState([]);
    const [selectedUpozorenja, setSelectedUpozorenja] = useState([]);
    const [tipIzvestaja, setTipIzvestaja] = useState('');
    const [datum, setDatum] = useState(new Date().toISOString().split('T')[0]);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const [loading, setLoading] = useState(false);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [pdfGenerated, setPdfGenerated] = useState(false);

    const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);
    useEffect(() => {
        fetchUpozorenja();
        
        // Cleanup function za URL objekat
        return () => {
            if (pdfUrl) {
                URL.revokeObjectURL(pdfUrl);
            }
        };
    }, []);

    const fetchUpozorenja = async () => {
        try {
            const response = await axiosInstance.get('api/upozorenja/');
            setUpozorenja(response.data);
        } catch (error) {
            console.error('Error fetching upozorenja:', error);
        }
    };

    const handleUpozorenjeSelection = (sifraU) => {
        setSelectedUpozorenja(prev => {
            if (prev.includes(sifraU)) {
                return prev.filter(id => id !== sifraU);
            } else {
                return [...prev, sifraU];
            }
        });
    };

    const handleSelectAll = () => {
        if (selectedUpozorenja.length === upozorenja.length) {
            setSelectedUpozorenja([]);
        } else {
            setSelectedUpozorenja(upozorenja.map(u => u.sifra_u));
        }
    };

    const handleGenerisiIzvestaj = async () => {
        if (!tipIzvestaja) {
            alert('Molimo odaberite tip izveštaja');
            return;
        }

        setLoading(true);
        try {
            const response = await axiosInstance.post('/api/generisi-izvestaj/', {
                tip_izvestaja: tipIzvestaja,
                datum: datum,
                selected_upozorenja: selectedUpozorenja
            }, {
                responseType: 'blob'
            });

            // Kreiraj Blob URL za prikaz u iframe-u
            const blob = new Blob([response.data], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            setPdfUrl(url);
            setPdfGenerated(true);

            // Reset selektovanih upozorenja nakon uspešnog generisanja
            setSelectedUpozorenja([]);
            
        } catch (error) {
            console.error('Error generating report:', error);
            alert('Došlo je do greške prilikom generisanja izveštaja');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPdf = () => {
        if (pdfUrl) {
            const link = document.createElement('a');
            link.href = pdfUrl;
            link.setAttribute('download', `izvestaj_${datum}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
    };

    const tipoviIzvestaja = [
        { value: 'zalihe', label: 'Izveštaj o zalihama' },
        { value: 'finansijski', label: 'Finansijski izveštaj' },
        { value: 'dobavljaci', label: 'Izveštaj o dobavljačima' },
        { value: 'kvalitet', label: 'Izveštaj o kvalitetu' },
        { value: 'temperature', label: 'Izveštaj o temperaturama' },
        { value: 'koordinator', label: 'Izveštaj logističkog koordinatora' },
    ];

    return (
        <div className="upozorenja-dashboard-container">
            <MainSideBar
            isCollapsed={isSidebarCollapsed}
            toggleSidebar={toggleSidebar}/>
            <div className={`upozorenja-main-content ${isSidebarCollapsed ? 'collapsed' : ''}`}>
                <div className="upozorenja-dashboard-header">
                    <h1>Pregled upozorenja</h1>
                </div>
                
                <div className="upozorenja-two-column-layout">
                    {/* Leva kolona - Upravljanje upozorenjima i formom */}
                    <div className="upozorenja-left-column">
                            
                            <div className="upozorenja-list">
                                {upozorenja.map(upozorenje => (
                                    <div 
                                        key={upozorenje.sifra_u} 
                                        className={`upozorenja-item ${selectedUpozorenja.includes(upozorenje.sifra_u) ? 'selected' : ''}`}
                                        onClick={() => handleUpozorenjeSelection(upozorenje.sifra_u)}
                                    >
                                        <div className="upozorenja-checkbox">
                                            <input
                                                type="checkbox"
                                                checked={selectedUpozorenja.includes(upozorenje.sifra_u)}
                                                onChange={() => {}}
                                            />
                                        </div>
                                        <div className="upozorenja-content">
                                            <span className="upozorenja-tip">{upozorenje.tip_display}</span>
                                            <p className="upozorenja-poruka">{upozorenje.poruka}</p>
                                            <span className="upozorenja-vreme">{upozorenje.vreme_formatirano}</span>
                                        </div>
                                    </div>
                                ))}
                                {upozorenja.length === 0 && (
                                    <div className="upozorenja-no-items">
                                        Nema aktivnih upozorenja
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="upozorenja-izvestaj-section">
                            <h2>Izgeneriši izveštaj:</h2>
                            
                            <div className="upozorenja-form-grid">
                                <div className="upozorenja-form-group">
                                    <label>Datum:</label>
                                    <input 
                                        type="date" 
                                        value={datum} 
                                        onChange={(e) => setDatum(e.target.value)}
                                        className="upozorenja-form-input"
                                    />
                                </div>
                                
                                <div className="upozorenja-form-group">
                                    <label>Tip izveštaja:</label>
                                    <select 
                                        value={tipIzvestaja} 
                                        onChange={(e) => setTipIzvestaja(e.target.value)}
                                        className="upozorenja-form-select"
                                    >
                                        <option value="">Izaberi tip izveštaja</option>
                                        {tipoviIzvestaja.map(tip => (
                                            <option key={tip.value} value={tip.value}>
                                                {tip.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="upozorenja-selected-count">
                                Odabrano upozorenja: {selectedUpozorenja.length}
                            </div>

                            <button 
                                className={`upozorenja-generate-btn ${loading ? 'loading' : ''}`}
                                onClick={handleGenerisiIzvestaj}
                                disabled={loading || !tipIzvestaja}
                            >
                                {loading ? 'Generisanje...' : 'Generiši izveštaj'}
                            </button>
                        </div>
                    </div>

                    {/* Desna kolona - Prikaz PDF-a */}
                    <div className="upozorenja-right-column">
                        <div className="upozorenja-preview-section">
                            <h2>Pregled izveštaja</h2>
                            
                            {pdfGenerated ? (
                                <div className="upozorenja-pdf-container">
                                    <div className="upozorenja-pdf-actions">
                                        <button 
                                            className="upozorenja-download-btn"
                                            onClick={handleDownloadPdf}
                                        >
                                            Preuzmi PDF
                                        </button>
                                        <button 
                                            className="upozorenja-regenerate-btn"
                                            onClick={() => setPdfGenerated(false)}
                                        >
                                            Novi izveštaj
                                        </button>
                                    </div>
                                    
                                    <div className="upozorenja-pdf-viewer">
                                        {pdfUrl ? (
                                            <iframe 
                                                src={pdfUrl} 
                                                width="100%" 
                                                height="600"
                                                title="PDF prikaz"
                                                className="upozorenja-pdf-iframe"
                                            />
                                        ) : (
                                            <div className="upozorenja-pdf-placeholder">
                                                PDF se generiše...
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <div className="upozorenja-preview-placeholder">
                                    <div className="upozorenja-preview-icon">
                                        📄
                                    </div>
                                    <h3>Izveštaj će se prikazati ovde</h3>
                                    <p>Generišite izveštaj da biste videli njegov pregled</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        
    );
};

export default UpozorenjaDashboard;