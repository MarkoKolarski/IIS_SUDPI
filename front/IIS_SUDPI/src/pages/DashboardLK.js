import React, { useState, useEffect} from 'react';
import axiosInstance from '../axiosInstance';
import MainSideBar from '../components/MainSideBar';
import '../styles/DashboardLK.css';
const DashboardLK = () => {
  const [notifications, setNotifications] = useState([]);
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

  const fetchUserNotifications = async (currentUser) => {
    try {
      const response = await axiosInstance.get(`/notifikacije/user/${currentUser.sifra_k}/`);
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const fetchActiveDeliveries = async () => {
    try {
      const response = await axiosInstance.get('/isporuke/aktivne/');
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
      fetchUserNotifications(currentUser);
      fetchActiveDeliveries();
    }
  }, [currentUser]);


  const markNotificationAsRead = async (notificationId) => {
    try {
      await axiosInstance.put(`/notifikacije/${notificationId}/mark-as-read/`);

      setNotifications(prevNotifications =>
        prevNotifications.map(notif =>
          notif.sifra_n === notificationId 
            ? { ...notif, procitana_n: true }
            : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleSelectDelivery = (deliveryId) => {

    //window.location.href = `/isporuke/${deliveryId}`;
  };

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
        <h1>Kontrolna tabla</h1>
      </div>

      <div className="dashboard-content">
        {/* Notifications Section */}
        <section className="notifications-section">
          <h2>Notifikacije</h2>
          <div className="notifications-table-container">
            <table className="notifications-table">
              <thead>
                <tr>
                  <th>Datum</th>
                  <th>Poruka</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {notifications.map(notification => (
                  <tr 
                    key={notification.sifra_n}
                    className={`notification-row ${notification.procitana_n ? 'read' : 'unread'}`}
                    onClick={() => !notification.procitana_n && markNotificationAsRead(notification.sifra_n)}
                    style={{ cursor: !notification.procitana_n ? 'pointer' : 'default' }}
                  >
                    <td>{formatDate(notification.datum_n)}</td>
                    <td>{notification.poruka_n}</td>
                    <td>
                      <span className={`status-badge ${notification.procitana_n ? 'status-read' : 'status-unread'}`}>
                        {notification.procitana_n ? 'Pročitano' : 'Nepročitano'}
                      </span>
                    </td>
                  </tr>
                ))}
                {notifications.length === 0 && (
                  <tr>
                    <td colSpan="3" className="no-data">Nema notifikacija</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <div className="section-divider"></div>

        {/* Deliveries Section */}
        <section className="deliveries-section">
          <h2>Isplaniraj isporuku:</h2>
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
                    <th>Akcija</th>
                  </tr>
                </thead>
                <tbody>
                  {deliveries.map(delivery => (
                    <tr key={delivery.sifra_i} className="delivery-row">
                      <td>{delivery.naziv || `Isporuka ${delivery.sifra_i}`}</td>
                      <td>{formatDate(delivery.datum_kreiranja)}</td>
                      <td>{delivery.kolicina_kg || 'N/A'}</td>
                      <td>{delivery.rok_isporuke || 'N/A'}</td>
                      <td>
                        <button 
                          className="select-button"
                          onClick={() => handleSelectDelivery(delivery.sifra_i)}
                        >
                          Izaberi
                        </button>
                      </td>
                    </tr>
                  ))}
                  {deliveries.length === 0 && (
                    <tr>
                      <td colSpan="5" className="no-data">Nema aktivnih isporuka</td>
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

export default DashboardLK;