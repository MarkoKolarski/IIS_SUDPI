import React, { useState, useEffect } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/EditProfile.css";
import axiosInstance from "../axiosInstance";

const EditProfile = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [personalData, setPersonalData] = useState({
    ime_k: "",
    prz_k: "",
    mail_k: ""
  });
  const [passwordData, setPasswordData] = useState({
    password: "",
    password_confirm: ""
  });
  const [loading, setLoading] = useState({
    personal: false,
    password: false
  });
  const [initialLoading, setInitialLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setInitialLoading(true);
        const response = await axiosInstance.get('/api/user/profile/');
        const userData = response.data;
        
        setPersonalData({
          ime_k: userData.ime_k || "",
          prz_k: userData.prz_k || "",
          mail_k: userData.mail_k || ""
        });
      } catch (err) {
        console.error("Error fetching user data:", err);
        setMessage({ 
          type: 'error', 
          text: 'Greška pri učitavanju podataka korisnika' 
        });
      } finally {
        setInitialLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const handlePersonalChange = (e) => {
    const { name, value } = e.target;
    setPersonalData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handlePersonalSubmit = async (e) => {
    e.preventDefault();
    setLoading(prev => ({ ...prev, personal: true }));
    setMessage({ type: '', text: '' });

    try {
      const response = await axiosInstance.put('/api/user/profile/update/', {
        ...personalData,
        password: "", // Pošaljemo praznu lozinku jer menjamo samo lične podatke
        password_confirm: ""
      });
      
      setMessage({ 
        type: 'success', 
        text: 'Lični podaci su uspešno ažurirani' 
      });
    } catch (err) {
      console.error("Error updating personal data:", err);
      const errorMessage = err.response?.data?.error || 
                          'Greška pri ažuriranju ličnih podataka';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(prev => ({ ...prev, personal: false }));
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(prev => ({ ...prev, password: true }));
    setMessage({ type: '', text: '' });

    // Validacija lozinki
    if (passwordData.password !== passwordData.password_confirm) {
      setMessage({ type: 'error', text: 'Lozinke se ne poklapaju' });
      setLoading(prev => ({ ...prev, password: false }));
      return;
    }

    if (passwordData.password && passwordData.password.length < 6) {
      setMessage({ type: 'error', text: 'Lozinka mora imati najmanje 6 karaktera' });
      setLoading(prev => ({ ...prev, password: false }));
      return;
    }

    try {
      const response = await axiosInstance.put('/api/user/profile/update/', {
        ...personalData, // Pošaljemo i lične podatke da se ne bi izgubili
        password: passwordData.password,
        password_confirm: passwordData.password_confirm
      });
      
      setMessage({ 
        type: 'success', 
        text: 'Lozinka je uspešno promenjena' 
      });
      
      // Reset password polja
      setPasswordData({
        password: "",
        password_confirm: ""
      });
    } catch (err) {
      console.error("Error updating password:", err);
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.password_confirm?.[0] ||
                          'Greška pri promeni lozinke';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(prev => ({ ...prev, password: false }));
    }
  };

  const handleCancel = () => {
    window.history.back();
  };

  if (initialLoading) {
    return (
      <div className="edit-profile-wrapper">
        <div className="loading-message">Učitavanje podataka...</div>
      </div>
    );
  }

  return (
    <div className={`edit-profile-wrapper ${isSidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
        activePage="edit_profile"
      />
      
      <main className="edit-profile-main">
        <header className="edit-profile-header">
          <h1>Izmena ličnih podataka</h1>
        </header>

        <div className="edit-profile-content">
          {/* Form Container */}
          <div className="form-container">
            <div className="form-header">
              <h2>Lični podaci</h2>
            </div>
            
            <div className="form-body">
              {message.text && (
                <div className={`message ${message.type}`}>
                  {message.text}
                </div>
              )}

              <div className="form-layout">
                {/* Left Column - Personal Information */}
                <div className="personal-info-section">
                  <form onSubmit={handlePersonalSubmit}>
                    <div className="section-header">
                      <h3>Osnovni podaci</h3>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="ime_k" className="form-label">Ime</label>
                      <input
                        type="text"
                        id="ime_k"
                        name="ime_k"
                        className="form-control"
                        value={personalData.ime_k}
                        onChange={handlePersonalChange}
                        required
                        placeholder="Unesite ime"
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="prz_k" className="form-label">Prezime</label>
                      <input
                        type="text"
                        id="prz_k"
                        name="prz_k"
                        className="form-control"
                        value={personalData.prz_k}
                        onChange={handlePersonalChange}
                        required
                        placeholder="Unesite prezime"
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="mail_k" className="form-label">Email</label>
                      <input
                        type="email"
                        id="mail_k"
                        name="mail_k"
                        className="form-control"
                        value={personalData.mail_k}
                        onChange={handlePersonalChange}
                        required
                        placeholder="Unesite email adresu"
                      />
                    </div>

                    <div className="button-section">
                      <button 
                        type="submit" 
                        className="btn btn-primary"
                        disabled={loading.personal}
                      >
                        {loading.personal ? "Čuvanje..." : "Potvrdi"}
                      </button>
                    </div>
                  </form>
                </div>

                {/* Right Column - Password */}
                <div className="password-section">
                  <form onSubmit={handlePasswordSubmit}>
                    <div className="section-header">
                      <h3>Promena lozinke</h3>
                    </div>

                    <div className="password-group">
                      <label className="form-label">Nova lozinka</label>
                      <input
                        type="password"
                        name="password"
                        className="form-control"
                        value={passwordData.password}
                        onChange={handlePasswordChange}
                        placeholder="Unesite novu lozinku"
                      />
                    </div>

                    <div className="password-group">
                      <label className="form-label">Ponovite lozinku</label>
                      <input
                        type="password"
                        name="password_confirm"
                        className="form-control"
                        value={passwordData.password_confirm}
                        onChange={handlePasswordChange}
                        placeholder="Ponovite lozinku"
                      />
                    </div>

                    <div className="button-section">
                      <button 
                        type="submit" 
                        className="btn btn-primary"
                        disabled={loading.password}
                      >
                        {loading.password ? "Čuvanje..." : "Potvrdi"}
                      </button>
                    </div>
                  </form>
                </div>
              </div>

              {/* Global Cancel Button */}
              <div className="global-actions">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCancel}
                >
                  Odustani
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EditProfile;