import React, { useState, useEffect} from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DashboardLK.css';
import { useNavigate } from 'react-router-dom';

const PregledIsporuka = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);
  //const { isCollapsed } = useContext(MainSideBar);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);

  const fetchUserProfile = async () => {
    try {
      const response = await axiosInstance.get('/user/profile/');
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };


  const fetchDeliveries = async () => {
    try {
      const response = await axiosInstance.get('isporuke/');
      setDeliveries(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching deliveries:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchDeliveries();
    }
  }, [currentUser]);

  const formatDate = (dateString) => {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    return new Date(dateString).toLocaleDateString('sr-RS', options);
  };

  return (
    <div className={`dashboard-container ${isSidebarCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}>
      <MainSideBar
      isCollapsed={isSidebarCollapsed}
      toggleSidebar={toggleSidebar}
      activePage="dashboard" />
      <div className="dashboard-header">
        <h1>Pregled svih isporuka</h1>
      </div>

      <div className="dashboard-content">
        <div className="section-divider"></div>

        {/* Deliveries Section */}
        <section className="deliveries-section">
          <div className="deliveries-table-container">
            {loading ? (
              <div className="loading">Učitavanje...</div>
            ) : (
              <table className="deliveries-table">
                <thead>
                  <tr>
                    <th>Naziv</th>
                    <th>Datum</th>
                    <th>Količina (kg)</th>
                    <th>Rok Isporuke</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {deliveries.map(delivery => (
                    <tr key={delivery.sifra_i} className="delivery-row">
                      <td>{delivery.naziv || `Isporuka ${delivery.sifra_i}`}</td>
                      <td>{formatDate(delivery.datum_kreiranja)}</td>
                      <td>{delivery.kolicina_kg || 'N/A'}</td>
                      <td>{formatDate(delivery.rok_is) || 'N/A'}</td>
                      <td>{delivery.status}</td>
                    </tr>
                  ))}
                  {deliveries.length === 0 && (
                    <tr>
                      <td colSpan="5" className="no-data">Nemaisporuka</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default PregledIsporuka;