import React, { useState, useEffect } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/EditProfile.css";
import axiosInstance from "../axiosInstance";

const EditOtherProfiles = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [originalData, setOriginalData] = useState({});
  const [formData, setFormData] = useState({
    ime_k: "",
    prz_k: "",
    mail_k: "",
    tip_k: "",
    password: "",
    password_confirm: ""
  });
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setInitialLoading(true);
        const response = await axiosInstance.get('/api/users/');
        setUsers(response.data);
      } catch (err) {
        console.error("Error fetching users:", err);
        setMessage({ 
          type: 'error', 
          text: 'Greška pri učitavanju liste korisnika' 
        });
      } finally {
        setInitialLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleUserSelect = async (user) => {
    try {
      setSelectedUser(user);
      const response = await axiosInstance.get(`/api/user/profile/${user.sifra_k}/`);
      const userData = response.data;
      
      setFormData({
        ime_k: userData.ime_k || "",
        prz_k: userData.prz_k || "",
        mail_k: userData.mail_k || "",
        tip_k: userData.tip_k || "",
        password: userData.password || "",
        password_confirm: userData.password || ""
      });
    } catch (err) {
      console.error("Error fetching user data:", err);
      setMessage({ type: 'error', text: 'Greška pri učitavanju podataka korisnika' });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUser) {
      setMessage({ type: 'error', text: 'Morate odabrati korisnika' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axiosInstance.put(
        `/api/user/profile/update/${selectedUser.sifra_k}/`, 
        formData
      );
      
      setMessage({ 
        type: 'success', 
        text: response.data.message || 'Profil je uspešno ažuriran' 
      });
      
      // Reset password polja
      setFormData(prev => ({
        ...prev,
        password: "",
        password_confirm: ""
      }));

      // Ažuriraj listu korisnika
      const usersResponse = await axiosInstance.get('/api/users/');
      setUsers(usersResponse.data);
    } catch (err) {
      console.error("Error updating profile:", err);
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.password_confirm?.[0] ||
                          'Greška pri ažuriranju profila';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setSelectedUser(null);
    setFormData({
      ime_k: "",
      prz_k: "",
      mail_k: "",
      tip_k: "",
      password: "",
      password_confirm: ""
    });
    setMessage({ type: '', text: '' });
  };

  const filteredUsers = users.filter(user => 
    user.ime_k.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.prz_k.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.mail_k.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.tip_k_display.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const userTypes = {
    'logisticki_koordinator': 'Logistički koordinator',
    'skladisni_operater': 'Skladišni operater', 
    'nabavni_menadzer': 'Nabavni menadžer',
    'finansijski_analiticar': 'Finansijski analitičar',
    'kontrolor_kvaliteta': 'Kontrolor kvaliteta',
    'administrator': 'Administrator'
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
        activePage="edit_other_profiles"
      />
      
      <main className="edit-profile-main">
        <header className="edit-profile-header">
          <h1>Upravljanje korisničkim profilima</h1>
        </header>

        <div className="edit-profile-content">
          {/* Search Section */}
          <div className="search-section">
            <input 
              type="text" 
              className="search-input"
              placeholder="Pretraži korisnike po imenu, prezimenu, emailu ili poziciji..."
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </div>

          <div className="admin-layout">
            {/* Left Column - Users List */}
            <div className="users-list-section">
              <div className="section-header">
                <h3>Lista korisnika</h3>
                <span className="users-count">({filteredUsers.length})</span>
              </div>
              
              <div className="users-list">
                {filteredUsers.map(user => (
                  <div 
                    key={user.sifra_k}
                    className={`user-item ${selectedUser?.sifra_k === user.sifra_k ? 'selected' : ''}`}
                    onClick={() => handleUserSelect(user)}
                  >
                    <div className="user-info">
                      <div className="user-name">{user.ime_k} {user.prz_k}</div>
                      <div className="user-email">{user.mail_k}</div>
                      <div className="user-role">{user.tip_k_display}</div>
                    </div>
                  </div>
                ))}
                
                {filteredUsers.length === 0 && (
                  <div className="no-users">Nema pronađenih korisnika</div>
                )}
              </div>
            </div>

            {/* Right Column - Edit Form */}
            <div className="edit-form-section">
              <div className={`form-container ${loading ? 'loading' : ''}`}>
                <div className="form-header">
                  <h2>
                    {selectedUser 
                      ? `Izmena podataka za: ${selectedUser.ime_k} ${selectedUser.prz_k}`
                      : 'Izaberite korisnika za uređivanje'
                    }
                  </h2>
                </div>
                
                <div className="form-body">
                  {message.text && (
                    <div className={`message ${message.type}`}>
                      {message.text}
                    </div>
                  )}

                  {selectedUser ? (
                    <form onSubmit={handleSubmit}>
                      <div className="form-layout">
                        {/* Left Column - Personal Information */}
                        <div className="personal-info">
                          <div className="form-group">
                            <label htmlFor="ime_k" className="form-label">Ime</label>
                            <input
                              type="text"
                              id="ime_k"
                              name="ime_k"
                              className="form-control"
                              value={formData.ime_k}
                              onChange={handleChange}
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
                              value={formData.prz_k}
                              onChange={handleChange}
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
                              value={formData.mail_k}
                              onChange={handleChange}
                              required
                              placeholder="Unesite email adresu"
                            />
                          </div>

                          <div className="form-group">
                            <label htmlFor="tip_k" className="form-label">Radno mesto</label>
                            <select
                              id="tip_k"
                              name="tip_k"
                              className="form-control"
                              value={formData.tip_k}
                              onChange={handleChange}
                              required
                            >
                              <option value="">Izaberite radno mesto</option>
                              {Object.entries(userTypes).map(([value, label]) => (
                                <option key={value} value={value}>
                                  {label}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>

                        {/* Right Column - Password */}
                        <div className="password-section">
                          <div className="password-group">
                            <label className="form-label">Nova lozinka</label>
                            <input
                              type="password"
                              name="password"
                              className="form-control"
                              value={formData.password}
                              onChange={handleChange}
                              placeholder="Ostavite prazno ako ne želite promenu"
                            />
                          </div>

                          <div className="password-group">
                            <label className="form-label">Ponovite lozinku</label>
                            <input
                              type="password"
                              name="password_confirm"
                              className="form-control"
                              value={formData.password_confirm}
                              onChange={handleChange}
                              placeholder="Ponovite lozinku"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Buttons */}
                      <div className="button-section">
                        <button 
                          type="button" 
                          className="btn btn-secondary"
                          onClick={handleCancel}
                          disabled={loading}
                        >
                          Poništi
                        </button>
                        <button 
                          type="submit" 
                          className="btn btn-primary"
                          disabled={loading}
                        >
                          {loading ? "Čuvanje..." : "Ažuriraj korisnika"}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="no-selection-message">
                      Izaberite korisnika sa liste da biste uređivali njegove podatke
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EditOtherProfiles;