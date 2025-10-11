import React, { useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/PlanIsporuke.css';
import { useNavigate } from 'react-router-dom';
import { useParams } from 'react-router-dom';

const PlanIsporuke = () => {
  const navigate = useNavigate();
  const { isporukaId } = useParams();
  console.log("Isporuka ID iz URL-a:", isporukaId);
  const [formData, setFormData] = useState({
    naziv: '',
    vozac_id: '',
    datum_isporuke: '',
    rok_isporuke: '',
    datum_dolaska: '',
    polazna_tacka: '',
    odrediste: '',
    ruta_id: ''
  });
  
  const [predlozeniVozac, setPredlozeniVozac] = useState(null);
  const [predlozenaRuta, setPredlozenaRuta] = useState(null);
  const [vozaci, setVozaci] = useState([]);
  const [loading, setLoading] = useState(false);
  const [rutaLoading, setRutaLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  
  const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);
//   useEffect(() => {
//   if (isporukaId) {
//     axiosInstance.get(`api/isporuka/${isporukaId}/`)
//       .then(res => setFormData(res.data))
//       .catch(err => console.error('Greška pri učitavanju isporuke:', err));
//   }
// }, [isporukaId]);
  useEffect(() => {
    fetchPredlozeniVozac();
    fetchSviVozaci();
  }, []);

  const fetchPredlozeniVozac = async () => {
    try {
      const response = await axiosInstance.get('/api/predlozi-vozaca/');
      setPredlozeniVozac(response.data);
      if (response.data) {
        setFormData(prev => ({ ...prev, vozac_id: response.data.sifra_vo }));
      }
    } catch (error) {
      console.error('Greška pri učitavanju predloženog vozača:', error);
    }
  };

  const fetchSviVozaci = async () => {
    try {  //'api/vozaci/'
      const response = await axiosInstance.get('api/vozaci/');
      setVozaci(response.data);
    } catch (error) {
      console.error('Greška pri učitavanju vozača:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Automatsko izračunavanje datuma dolaska kada se promeni datum isporuke
    if (name === 'datum_isporuke' && value && predlozenaRuta) {
      izracunajDatumDolaska(value, predlozenaRuta.sifra_r);
    }
  };

  const predloziRutu = async () => {
    if (!formData.polazna_tacka || !formData.odrediste) {
      alert('Molimo unesite polaznu tačku i odredište');
      return;
    }

    setRutaLoading(true);
    try {
      const response = await axiosInstance.post('api/predlozi-rutu/', {
        polazna_tacka: formData.polazna_tacka,
        odrediste: formData.odrediste
      });
      
      setPredlozenaRuta(response.data);
      
      setFormData(prev => ({ 
        ...prev, 
        ruta_id: response.data.sifra_r 
      }));

      // Automatski izračunaj datum dolaska ako je dostupan datum isporuke
      if (formData.datum_isporuke) {
        izracunajDatumDolaska(formData.datum_isporuke, response.data.sifra_r);
      }

    } catch (error) {
      console.error('Greška pri predlaganju rute:', error);
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        alert('Došlo je do greške pri pronalaženju rute. Proverite unete adrese.');
      }
    } finally {
      setRutaLoading(false);
    }
  };

  const izracunajDatumDolaska = async (datumIsporuke, rutaId) => {
    try {
      const response = await axiosInstance.get('api/izracunaj-datum-dolaska/', {
        params: {
          datum_isporuke: datumIsporuke,
          ruta_id: rutaId
        }
      });
      
      setFormData(prev => ({ 
        ...prev, 
        datum_dolaska: response.data.datum_dolaska 
      }));
    } catch (error) {
      console.error('Greška pri izračunavanju datuma dolaska:', error);
    }
  };

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!predlozenaRuta) {
    alert('Molimo prvo predložite rutu');
    return;
  }

  setLoading(true);
  try {
    if (!isporukaId) {
      alert("Nije prosleđen ID isporuke. Proveri navigaciju!");
      return;
    }

    const response = await axiosInstance.put(`/api/kreiraj-isporuku/${isporukaId}`, formData);

    alert('Isporuka je uspešno ažurirana!');
    
    setFormData({
      naziv: '',
      vozac_id: predlozeniVozac?.id || '',
      datum_isporuke: '',
      rok_isporuke: '',
      datum_dolaska: '',
      polazna_tacka: '',
      odrediste: '',
      ruta_id: ''
    });
    setPredlozenaRuta(null);
    
    fetchPredlozeniVozac();

  } catch (error) {
    console.error('Greška pri ažuriranju isporuke:', error);
    if (error.response?.data?.error) {
      alert(error.response.data.error);
    } else {
      alert('Došlo je do greške pri ažuriranju isporuke.');
    }
  } finally {
    setLoading(false);
  }
};

  const handleOdustani = () => {
    // Vrati se na dashboard
    navigate('/dashboardLK');
  };

  // Formatiranje datuma za input polja
  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  return (
    <div className={`plan-isporuke-container ${isSidebarCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}>
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
        activePage="plan-isporuke"
      />
      
      <div className="plan-isporuke-header">
        <h1>Plan isporuke</h1>
      </div>

      <div className="plan-isporuke-content">
        <form onSubmit={handleSubmit} className="isporuka-form">
          {/* Sekcija Isporuka */}
          <section className="isporuka-section">
            <h2>Isporuka</h2>
            
            <div className="form-group">
              <label htmlFor="naziv">Naziv isporuke *</label>
              <input
                type="text"
                id="naziv"
                name="naziv"
                value={formData.naziv}
                onChange={handleInputChange}
                required
                placeholder="Unesite naziv isporuke"
              />
            </div>

            <div className="form-group">
              <label htmlFor="vozac_id">Vozač *</label>
              <select
                id="vozac_id"
                name="vozac_id"
                value={formData.vozac_id}
                onChange={handleInputChange}
                required
              >
                <option value="">Izaberite vozača</option>
                {vozaci.map(vozac => (
                  <option key={vozac.sifra_vo} value={vozac.sifra_vo}>
                    {vozac.ime_vo} {vozac.prz_vo} 
                    {vozac.sifra_vo === predlozeniVozac?.sifra_vo && ' (Sistem predlaže)'}
                  </option>
                ))}
              </select>
              <small className="predlog-text">
                Sistem predlaže: {predlozeniVozac ? 
                  `${predlozeniVozac.ime_vo} ${predlozeniVozac.prz_vo}` : 
                  'nema podataka'}
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="datum_isporuke">Datum isporuke *</label>
              <input
                type="date"
                id="datum_isporuke"
                name="datum_isporuke"
                value={formData.datum_isporuke}
                onChange={handleInputChange}
                min={getMinDate()}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="rok_isporuke">Rok isporuke *</label>
              <input
                type="date"
                id="rok_isporuke"
                name="rok_isporuke"
                value={formData.rok_isporuke}
                onChange={handleInputChange}
                min={getTodayDate()}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="datum_dolaska">Datum dolaska *</label>
              <input
                type="date"
                id="datum_dolaska"
                name="datum_dolaska"
                value={formData.datum_dolaska}
                onChange={handleInputChange}
                required
                readOnly
              />
              <small className="predlog-text">
                Sistem automatski izračunava na osnovu rute
              </small>
            </div>

            <div className="form-actions">
              <button 
                type="submit" 
                className="btn-confirm"
                disabled={loading || !predlozenaRuta}
              >
                {loading ? 'Potvrđuje se...' : 'Potvrdi isporuku'}
              </button>
              <button 
                type="button" 
                className="btn-cancel"
                onClick={handleOdustani}
              >
                Odustani
              </button>
            </div>
          </section>

          {/* Sekcija Ruta */}
          <section className="ruta-section">
            <h2>Ruta</h2>
            
            <div className="form-group">
              <label htmlFor="polazna_tacka">Polazna tačka *</label>
              <input
                type="text"
                id="polazna_tacka"
                name="polazna_tacka"
                value={formData.polazna_tacka}
                onChange={handleInputChange}
                required
                placeholder="Unesite polaznu tačku (npr. Beograd, Srbija)"
              />
            </div>

            <div className="form-group">
              <label htmlFor="odrediste">Odredište *</label>
              <input
                type="text"
                id="odrediste"
                name="odrediste"
                value={formData.odrediste}
                onChange={handleInputChange}
                required
                placeholder="Unesite odredišnu tačku (npr. Novi Sad, Srbija)"
              />
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                className="btn-confirm"
                onClick={predloziRutu}
                disabled={!formData.polazna_tacka || !formData.odrediste || rutaLoading}
              >
                {rutaLoading ? 'Tražim rutu...' : 'Pronađi rutu'}
              </button>
            </div>

            {predlozenaRuta && (
              <div className="ruta-info">
                <h3>Pronađena ruta</h3>
                <div className="ruta-details">
                  <p><strong>Polazna tačka:</strong> {predlozenaRuta.polazna_tacka}</p>
                  <p><strong>Odredište:</strong> {predlozenaRuta.odrediste}</p>
                  <p><strong>Dužina:</strong> {predlozenaRuta.duzina_km} km</p>
                  {/*<p><strong>Procenjeno vreme putovanja:</strong> {predlozenaRuta.vreme_putovanja_formatirano}</p>*/}
                  <p><strong>Procenjeno vreme putovanja:</strong> {predlozenaRuta.vreme_dolaska}</p>
                  <p><strong>Status:</strong> {predlozenaRuta.status}</p>
                  <p className="map-napomena">
                    <em>Ruta je pronađena koristeći OpenStreetMap podatke</em>
                  </p>
                </div>
              </div>
            )}
          </section>
        </form>
      </div>
    </div>
  );
};

export default PlanIsporuke;