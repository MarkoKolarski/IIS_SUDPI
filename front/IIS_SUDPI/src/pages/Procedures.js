import React, { useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from "../components/MainSideBar";
import styles from '../styles/SbpProcedures.module.css';
import { FaSpinner } from 'react-icons/fa';

const SbpProcedures = () => {
  const [activeTab, setActiveTab] = useState('zadatak1');
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };
  
  const [zadatak1, setZadatak1] = useState({
    fakture: [],
    proizvodi: [],
    selectedFaktura: '',
    selectedProizvod: '',
    naziv: '',
    kolicina: '',
    cena: '',
    loading: false,
    result: null,
    error: null
  });

  const [zadatak2, setZadatak2] = useState({
    dobavljaci: [],
    ukupanDug: 0,
    loading: false,
    error: null
  });

  const [zadatak3, setZadatak3] = useState({
    rezultatBezIndeksa: null,
    rezultatSaIndeksom: null,
    generisanjeFaktura: false,
    kreiranjeIndeksa: false,
    loading: false,
    error: null,
    indeksKreiran: false
  });

  const [zadatak4, setZadatak4] = useState({
    mesec: new Date().getMonth() + 1,
    godina: new Date().getFullYear(),
    izvestaj: null,
    loading: false,
    error: null
  });

  useEffect(() => {
    if (activeTab === 'zadatak1') {
      fetchFaktureIProizvode();
    } else if (activeTab === 'zadatak2') {
      fetchDugDobavljaca();
    }
  }, [activeTab]);

  const fetchFaktureIProizvode = async () => {
    setZadatak1(prev => ({ ...prev, loading: true }));
    try {
      const [faktureRes, proizvodiRes] = await Promise.all([
        axiosInstance.get('/api/sbp/zadatak1/fakture/'),
        axiosInstance.get('/api/sbp/zadatak1/proizvodi/')
      ]);
      
      setZadatak1(prev => ({
        ...prev,
        fakture: faktureRes.data.fakture,
        proizvodi: proizvodiRes.data.proizvodi,
        loading: false
      }));
    } catch (error) {
      setZadatak1(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri učitavanju podataka',
        loading: false
      }));
    }
  };

  const handleDodajStavku = async (e) => {
    e.preventDefault();
    setZadatak1(prev => ({ ...prev, loading: true, result: null, error: null }));
    
    try {
      const response = await axiosInstance.post('/api/sbp/zadatak1/dodaj-stavku/', {
        faktura_id: zadatak1.selectedFaktura,
        proizvod_id: zadatak1.selectedProizvod,
        naziv_sf: zadatak1.naziv,
        kolicina_sf: zadatak1.kolicina,
        cena_po_jed: zadatak1.cena
      });

      setZadatak1(prev => ({
        ...prev,
        loading: false,
        result: response.data,
        selectedFaktura: '',
        selectedProizvod: '',
        naziv: '',
        kolicina: '',
        cena: ''
      }));

      await fetchFaktureIProizvode();
    } catch (error) {
      setZadatak1(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.error || 'Greška pri dodavanju stavke'
      }));
    }
  };

  const fetchDugDobavljaca = async () => {
    setZadatak2(prev => ({ ...prev, loading: true }));
    try {
      const response = await axiosInstance.get('/api/sbp/zadatak2/dug-dobavljaca/');
      setZadatak2({
        dobavljaci: response.data.dobavljaci,
        ukupanDug: response.data.ukupan_dug_svi,
        loading: false,
        error: null
      });
    } catch (error) {
      setZadatak2(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri učitavanju podataka',
        loading: false
      }));
    }
  };

  const testBezIndeksa = async () => {
    setZadatak3(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await axiosInstance.get('/api/sbp/zadatak3/test-bez-indeksa/');
      setZadatak3(prev => ({
        ...prev,
        rezultatBezIndeksa: response.data,
        loading: false
      }));
    } catch (error) {
      setZadatak3(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri testiranju',
        loading: false
      }));
    }
  };

  const testSaIndeksom = async () => {
    setZadatak3(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await axiosInstance.get('/api/sbp/zadatak3/test-sa-indeksom/');
      setZadatak3(prev => ({
        ...prev,
        rezultatSaIndeksom: response.data,
        loading: false
      }));
    } catch (error) {
      setZadatak3(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri testiranju',
        loading: false
      }));
    }
  };

  const generisiFakture = async () => {
    if (!window.confirm('Ova operacija će kreirati 800,000 faktura. Može potrajati nekoliko minuta. Želite li nastaviti?')) {
      return;
    }

    setZadatak3(prev => ({ ...prev, generisanjeFaktura: true, error: null }));
    try {
      const response = await axiosInstance.post('/api/sbp/zadatak3/generiši-test-fakture/');
      alert(response.data.message);
      setZadatak3(prev => ({ ...prev, generisanjeFaktura: false }));
    } catch (error) {
      setZadatak3(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri generisanju faktura',
        generisanjeFaktura: false
      }));
    }
  };

  const kreirajIndeks = async () => {
    setZadatak3(prev => ({ ...prev, kreiranjeIndeksa: true, error: null }));
    try {
      const response = await axiosInstance.post('/api/sbp/zadatak3/kreiraj-indeks/');
      alert(response.data.message);
      setZadatak3(prev => ({ 
        ...prev, 
        kreiranjeIndeksa: false,
        indeksKreiran: true 
      }));
    } catch (error) {
      setZadatak3(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri kreiranju indeksa',
        kreiranjeIndeksa: false
      }));
    }
  };

  const obrisiIndeks = async () => {
    setZadatak3(prev => ({ ...prev, kreiranjeIndeksa: true, error: null }));
    try {
      const response = await axiosInstance.post('/api/sbp/zadatak3/obrisi-indeks/');
      alert(response.data.message);
      setZadatak3(prev => ({ 
        ...prev, 
        kreiranjeIndeksa: false,
        indeksKreiran: false 
      }));
    } catch (error) {
      setZadatak3(prev => ({
        ...prev,
        error: error.response?.data?.error || 'Greška pri brisanju indeksa',
        kreiranjeIndeksa: false
      }));
    }
  };

  const generisiIzvestaj = async (e) => {
    e.preventDefault();
    setZadatak4(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await axiosInstance.post('/api/sbp/zadatak4/generiši-izvestaj/', {
        mesec: zadatak4.mesec,
        godina: zadatak4.godina
      });

      if (response.data.success) {
        setZadatak4(prev => ({
          ...prev,
          loading: false,
          izvestaj: response.data.izvestaj
        }));
      } else {
        setZadatak4(prev => ({
          ...prev,
          loading: false,
          error: response.data.message
        }));
      }
    } catch (error) {
      setZadatak4(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.error || 'Greška pri generisanju izveštaja'
      }));
    }
  };

  const ucitajPoslednjiIzvestaj = async () => {
    setZadatak4(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await axiosInstance.get('/api/sbp/zadatak4/poslednji-izvestaj/');
      setZadatak4(prev => ({
        ...prev,
        loading: false,
        izvestaj: response.data.izvestaj
      }));
    } catch (error) {
      setZadatak4(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.error || 'Greška pri učitavanju izveštaja'
      }));
    }
  };

  return (
    <div className={`${styles.sbpWrapper} ${
      isSidebarCollapsed ? styles.sidebarCollapsed : ""
    }`}>
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className={styles.sbpMainContent}>
        <header className={styles.sbpHeader}>
          <h1>Procedure</h1>
        </header>

        <div className={styles.tabsContainer}>
          <div className={styles.navTabs}>
            <button
              className={`${styles.navLink} ${activeTab === 'zadatak1' ? styles.active : ''}`}
              onClick={() => setActiveTab('zadatak1')}
            >
              Dodaj stavku fakture
            </button>
            <button
              className={`${styles.navLink} ${activeTab === 'zadatak2' ? styles.active : ''}`}
              onClick={() => setActiveTab('zadatak2')}
            >
              Dug dobavljačima
            </button>
            <button
              className={`${styles.navLink} ${activeTab === 'zadatak3' ? styles.active : ''}`}
              onClick={() => setActiveTab('zadatak3')}
            >
              Testiranje indeksa
            </button>
            <button
              className={`${styles.navLink} ${activeTab === 'zadatak4' ? styles.active : ''}`}
              onClick={() => setActiveTab('zadatak4')}
            >
              Generisanje izveštaja
            </button>
          </div>
        </div>

        <div className={styles.cardContainer}>
          {/* ZADATAK 1: TRIGER */}
          {activeTab === 'zadatak1' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h5>Dodaj stavku fakture & Azuriraj fakturu nakon unosa automatski</h5>
              </div>
              <div className={styles.cardBody}>
                {zadatak1.error && (
                  <div className={`${styles.alertContainer} ${styles.alertDanger}`}>
                    <strong>Greška:</strong> {zadatak1.error}
                  </div>
                )}
                {zadatak1.result && (
                  <div className={`${styles.alertContainer} ${styles.alertSuccess}`}>
                    <strong>Uspešno!</strong> {zadatak1.result.message}
                    <div className={styles.mt2}>
                      <div>Stari iznos fakture: <strong>{zadatak1.result.stari_iznos} RSD</strong></div>
                      <div>Novi iznos fakture: <strong>{zadatak1.result.novi_iznos} RSD</strong></div>
                      <div className={styles.tableSuccess}>Razlika: +{zadatak1.result.razlika} RSD</div>
                    </div>
                  </div>
                )}

                <form onSubmit={handleDodajStavku}>
                  <div className={styles.row}>
                    <div className={styles.colHalf}>
                      <div>
                        <label className={styles.formLabel}>Faktura</label>
                        <select
                          className={styles.formSelect}
                          value={zadatak1.selectedFaktura}
                          onChange={(e) => setZadatak1(prev => ({ ...prev, selectedFaktura: e.target.value }))}
                          required
                          disabled={zadatak1.loading}
                        >
                          <option value="">Izaberite fakturu...</option>
                          {zadatak1.fakture.map(f => (
                            <option key={f.sifra_f} value={f.sifra_f}>
                              ID: {f.sifra_f} | {f.dobavljac} | {f.iznos_f} RSD | {f.status_f}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className={styles.colHalf}>
                      <div>
                        <label className={styles.formLabel}>Proizvod</label>
                        <select
                          className={styles.formSelect}
                          value={zadatak1.selectedProizvod}
                          onChange={(e) => setZadatak1(prev => ({ ...prev, selectedProizvod: e.target.value }))}
                          required
                          disabled={zadatak1.loading}
                        >
                          <option value="">Izaberite proizvod...</option>
                          {zadatak1.proizvodi.map(p => (
                            <option key={p.sifra_pr} value={p.sifra_pr}>
                              {p.naziv_pr}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className={styles.row}>
                    <div className={styles.colThird}>
                      <div>
                        <label className={styles.formLabel}>Naziv stavke</label>
                        <input
                          type="text"
                          className={styles.formControl}
                          value={zadatak1.naziv}
                          onChange={(e) => setZadatak1(prev => ({ ...prev, naziv: e.target.value }))}
                          placeholder="Unesite naziv"
                          required
                          disabled={zadatak1.loading}
                        />
                      </div>
                    </div>
                    <div className={styles.colThird}>
                      <div>
                        <label className={styles.formLabel}>Količina</label>
                        <input
                          type="number"
                          className={styles.formControl}
                          value={zadatak1.kolicina}
                          onChange={(e) => setZadatak1(prev => ({ ...prev, kolicina: e.target.value }))}
                          placeholder="Unesite količinu"
                          min="1"
                          required
                          disabled={zadatak1.loading}
                        />
                      </div>
                    </div>
                    <div className={styles.colThird}>
                      <div>
                        <label className={styles.formLabel}>Cena po jedinici (RSD)</label>
                        <input
                          type="number"
                          step="0.01"
                          className={styles.formControl}
                          value={zadatak1.cena}
                          onChange={(e) => setZadatak1(prev => ({ ...prev, cena: e.target.value }))}
                          placeholder="Unesite cenu"
                          min="0.01"
                          required
                          disabled={zadatak1.loading}
                        />
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className={`${styles.button} ${styles.buttonPrimary}`}
                    disabled={zadatak1.loading}
                  >
                    {zadatak1.loading ? (
                      <>
                        <FaSpinner className="animate-spin" />
                        Dodavanje...
                      </>
                    ) : 'Dodaj stavku fakture'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* ZADATAK 2: FUNKCIJA */}
          {activeTab === 'zadatak2' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h5>Izračunaj dug prema dobavljačima</h5>
              </div>
              <div className={styles.cardBody}>
                {zadatak2.error && (
                  <div className={`${styles.alertContainer} ${styles.alertDanger}`}>
                    <strong>Greška:</strong> {zadatak2.error}
                  </div>
                )}

                <div className={styles.row}>
                  <div className={styles.colFull}>
                    <div className={`${styles.performanceCard}`}>
                      <div className={styles.textEnd} style={{ marginBottom: '16px' }}>
                        <button
                          className={`${styles.button} ${styles.buttonSuccess}`}
                          onClick={fetchDugDobavljaca}
                          disabled={zadatak2.loading}
                        >
                          {zadatak2.loading ? (
                            <>
                              <FaSpinner className="animate-spin" />
                              Učitavanje...
                            </>
                          ) : 'Osveži podatke'}
                        </button>
                      </div>

                      <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#ecfdf5', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                        <strong style={{ color: '#065f46' }}>
                          Ukupan naš dug prema svim dobavljačima: {zadatak2.ukupanDug.toFixed(2)} RSD
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>

                {zadatak2.loading ? (
                  <div className={styles.loadingContainer}>
                    <FaSpinner className="animate-spin" style={{ fontSize: '32px', color: '#14b8a6' }} />
                  </div>
                ) : (
                  <div className={styles.tableResponsive}>
                    <table className={styles.table}>
                      <thead className={styles.tableHeader}>
                        <tr>
                          <th>Šifra dobavljača</th>
                          <th>Naziv dobavljača</th>
                          <th className={styles.tableTextEnd}>Ukupan dug (RSD)</th>
                        </tr>
                      </thead>
                      <tbody className={styles.tableBody}>
                        {zadatak2.dobavljaci.map((dob, idx) => (
                          <tr key={idx}>
                            <td>{dob.SIFRA_D}</td>
                            <td>{dob.NAZIV}</td>
                            <td className={styles.tableTextEnd}>
                              <span className={dob.UKUPAN_DUG > 0 ? styles.tableDanger : styles.tableSuccess}>
                                {parseFloat(dob.UKUPAN_DUG).toFixed(2)}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ZADATAK 3: INDEKSI */}
          {activeTab === 'zadatak3' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h5>IDX_FAKTURA_STATUS_ROK Indeks</h5>
                <small>Testiranje performansi upita sa i bez indeksa</small>
              </div>
              <div className={styles.cardBody}>
                {zadatak3.error && (
                  <div className={`${styles.alertContainer} ${styles.alertDanger}`}>
                    <strong>Greška:</strong> {zadatak3.error}
                  </div>
                )}

                <div className={styles.row}>
                  <div className={styles.colFull}>
                    <div className={styles.performanceCard}>
                      <div className={styles.h6}>Upravljanje test podacima</div>
                      <button
                        className={`${styles.button} ${styles.buttonWarning}`}
                        onClick={generisiFakture}
                        disabled={zadatak3.generisanjeFaktura}
                      >
                        {zadatak3.generisanjeFaktura ? (
                          <>
                            <FaSpinner className="animate-spin" />
                            Generisanje 800,000 faktura...
                          </>
                        ) : 'Generiši 800,000 test faktura'}
                      </button>
                      <span className={styles.textSmall}>
                        Ova operacija može potrajati nekoliko minuta
                      </span>
                    </div>
                  </div>
                </div>

                <div className={styles.row}>
                  <div className={styles.colFull}>
                    <div className={styles.performanceCard}>
                      <div className={styles.h6}>Upravljanje indeksom</div>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <button
                          className={`${styles.button} ${styles.buttonSuccess}`}
                          onClick={kreirajIndeks}
                          disabled={zadatak3.kreiranjeIndeksa}
                        >
                          {zadatak3.kreiranjeIndeksa ? (
                            <>
                              <FaSpinner className="animate-spin" />
                              Kreiranje...
                            </>
                          ) : 'Kreiraj indeks'}
                        </button>
                        <button
                          className={`${styles.button} ${styles.buttonDanger}`}
                          onClick={obrisiIndeks}
                          disabled={zadatak3.kreiranjeIndeksa}
                        >
                          {zadatak3.kreiranjeIndeksa ? (
                            <>
                              <FaSpinner className="animate-spin" />
                              Brisanje...
                            </>
                          ) : 'Obriši indeks'}
                        </button>
                        {zadatak3.indeksKreiran && (
                          <span className={`${styles.badge} ${styles.badgeSuccess}`}>
                            ✓ Indeks kreiran
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className={styles.row}>
                  <div className={styles.colHalf}>
                    <div className={`${styles.performanceCard} ${styles.performanceCardDanger}`}>
                      <div className={`${styles.performanceHeader} ${styles.performanceHeaderDanger}`}>
                        Performanse BEZ indeksa
                      </div>
                      <button
                        className={`${styles.button} ${styles.buttonDanger} ${styles.buttonFull}`}
                        onClick={testBezIndeksa}
                        disabled={zadatak3.loading}
                        style={{ marginBottom: '16px' }}
                      >
                        {zadatak3.loading ? 'Testiranje...' : 'Testiraj bez indeksa'}
                      </button>

                      {zadatak3.rezultatBezIndeksa && (
                        <div>
                          <div className={styles.performanceValue}>
                            <span className={styles.performanceValueLabel}>Broj redova:</span>
                            <span className={styles.performanceValueData}>{zadatak3.rezultatBezIndeksa.count}</span>
                          </div>
                          <div className={styles.performanceValue}>
                            <span className={styles.performanceValueLabel}>Prosečan iznos:</span>
                            <span className={styles.performanceValueData}>{zadatak3.rezultatBezIndeksa.avg_iznos.toFixed(2)} RSD</span>
                          </div>
                          <div className={styles.performanceAlertBox} style={{ marginTop: '8px' }}>
                            <strong>Vreme izvršavanja:</strong> {zadatak3.rezultatBezIndeksa.execution_time_seconds.toFixed(4)} sekundi
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className={styles.colHalf}>
                    <div className={`${styles.performanceCard} ${styles.performanceCardSuccess}`}>
                      <div className={`${styles.performanceHeader} ${styles.performanceHeaderSuccess}`}>
                        Performanse SA indeksom
                      </div>
                      <button
                        className={`${styles.button} ${styles.buttonSuccess} ${styles.buttonFull}`}
                        onClick={testSaIndeksom}
                        disabled={zadatak3.loading}
                        style={{ marginBottom: '16px' }}
                      >
                        {zadatak3.loading ? 'Testiranje...' : 'Testiraj sa indeksom'}
                      </button>

                      {zadatak3.rezultatSaIndeksom && (
                        <div>
                          <div className={styles.performanceValue}>
                            <span className={styles.performanceValueLabel}>Broj redova:</span>
                            <span className={styles.performanceValueData}>{zadatak3.rezultatSaIndeksom.count}</span>
                          </div>
                          <div className={styles.performanceValue}>
                            <span className={styles.performanceValueLabel}>Prosečan iznos:</span>
                            <span className={styles.performanceValueData}>{zadatak3.rezultatSaIndeksom.avg_iznos.toFixed(2)} RSD</span>
                          </div>
                          <div className={styles.performanceAlertBox} style={{ marginTop: '8px', backgroundColor: '#ecfdf5', color: '#065f46' }}>
                            <strong>Vreme izvršavanja:</strong> {zadatak3.rezultatSaIndeksom.execution_time_seconds.toFixed(4)} sekundi
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {zadatak3.rezultatBezIndeksa && zadatak3.rezultatSaIndeksom && (
                  <div className={`${styles.alertContainer} ${styles.alertInfo}`}>
                    <h6 style={{ margin: '0 0 12px 0', color: '#0c4a6e' }}>Poređenje performansi:</h6>
                    <div>
                      Ubrzanje sa indeksom:
                      <strong className={styles.ms2}>
                        {(zadatak3.rezultatBezIndeksa.execution_time_seconds / zadatak3.rezultatSaIndeksom.execution_time_seconds).toFixed(2)}x
                      </strong>
                    </div>
                    <div style={{ marginTop: '8px' }}>
                      Ušteda vremena:
                      <strong className={styles.ms2}>
                        {((zadatak3.rezultatBezIndeksa.execution_time_seconds - zadatak3.rezultatSaIndeksom.execution_time_seconds) * 1000).toFixed(2)} ms
                      </strong>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ZADATAK 4: IZVEŠTAJ */}
          {activeTab === 'zadatak4' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h5>Generisi mesečni izveštaj profitabilnosti</h5>
              </div>
              <div className={styles.cardBody}>
                {zadatak4.error && (
                  <div className={`${styles.alertContainer} ${styles.alertDanger}`}>
                    <strong>Greška:</strong> {zadatak4.error}
                  </div>
                )}

                <div className={styles.row}>
                  <div className={styles.colHalf}>
                    <form onSubmit={generisiIzvestaj}>
                      <div className={styles.row}>
                        <div className={styles.colHalf}>
                          <div>
                            <label className={styles.formLabel}>Mesec</label>
                            <select
                              className={styles.formSelect}
                              value={zadatak4.mesec}
                              onChange={(e) => setZadatak4(prev => ({ ...prev, mesec: e.target.value }))}
                              disabled={zadatak4.loading}
                            >
                              {[...Array(12)].map((_, i) => (
                                <option key={i + 1} value={i + 1}>
                                  {new Date(2000, i, 1).toLocaleDateString('sr-RS', { month: 'long' })}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <div className={styles.colHalf}>
                          <div>
                            <label className={styles.formLabel}>Godina</label>
                            <input
                              type="number"
                              className={styles.formControl}
                              value={zadatak4.godina}
                              onChange={(e) => setZadatak4(prev => ({ ...prev, godina: e.target.value }))}
                              min="2020"
                              max="2030"
                              disabled={zadatak4.loading}
                            />
                          </div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                        <button
                          type="submit"
                          className={`${styles.button} ${styles.buttonInfo}`}
                          disabled={zadatak4.loading}
                        >
                          {zadatak4.loading ? (
                            <>
                              <FaSpinner className="animate-spin" />
                              Generisanje...
                            </>
                          ) : 'Generiši izveštaj'}
                        </button>
                        <button
                          type="button"
                          className={`${styles.button} ${styles.buttonSecondary}`}
                          onClick={ucitajPoslednjiIzvestaj}
                          disabled={zadatak4.loading}
                        >
                          Učitaj poslednji izveštaj
                        </button>
                      </div>
                    </form>
                  </div>
                </div>

                {zadatak4.izvestaj && (
                  <div style={{ marginTop: '24px' }}>
                    <div className={`${styles.alertContainer} ${styles.alertInfo}`}>
                      <strong>{zadatak4.izvestaj.izvestaj}</strong>
                      <div className={styles.mt2}>
                        Period: {zadatak4.izvestaj.mesec}/{zadatak4.izvestaj.godina}
                      </div>
                    </div>

                    {zadatak4.izvestaj.stavke && zadatak4.izvestaj.stavke.length > 0 ? (
                      <div className={styles.tableResponsive} style={{ marginTop: '20px' }}>
                        <table className={styles.table}>
                          <thead className={styles.tableHeader}>
                            <tr>
                              <th>Kategorija proizvoda</th>
                              <th className={styles.tableTextEnd}>Ukupan prihod (RSD)</th>
                              <th className={styles.tableTextEnd}>Broj prodatih artikala</th>
                            </tr>
                          </thead>
                          <tbody className={styles.tableBody}>
                            {zadatak4.izvestaj.stavke.map((stavka, idx) => (
                              <tr key={idx}>
                                <td>
                                  <strong>{stavka.kategorija}</strong>
                                </td>
                                <td className={styles.tableTextEnd}>
                                  <span className={`${styles.badge} ${styles.badgeSuccess}`}>
                                    {parseFloat(stavka.ukupan_prihod).toFixed(2)}
                                  </span>
                                </td>
                                <td className={styles.tableTextEnd}>{stavka.broj_prodatih_artikala}</td>
                              </tr>
                            ))}
                            <tr style={{ backgroundColor: '#a7f3d0', fontWeight: '600' }}>
                              <td style={{ color: '#065f46' }}>UKUPNO</td>
                              <td className={styles.tableTextEnd} style={{ color: '#065f46' }}>
                                {zadatak4.izvestaj.stavke.reduce((sum, s) => sum + parseFloat(s.ukupan_prihod), 0).toFixed(2)} RSD
                              </td>
                              <td className={styles.tableTextEnd} style={{ color: '#065f46' }}>
                                {zadatak4.izvestaj.stavke.reduce((sum, s) => sum + s.broj_prodatih_artikala, 0)}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className={`${styles.alertContainer} ${styles.alertWarning}`}>
                        Nema podataka za izabrani period. Možda nema dovoljno plaćenih faktura ili prihod po kategoriji je manji od 1000 RSD.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default SbpProcedures;
