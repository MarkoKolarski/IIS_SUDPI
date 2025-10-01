import React, { useState, useEffect } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/DashboardAdmin.css";
import axiosInstance from "../axiosInstance";

const DashboardAdmin = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [stats, setStats] = useState({
    totalUsers: 0,
    usersByType: {},
    totalSuppliers: 0,
    activeSuppliers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAdminStats = async () => {
      try {
        setLoading(true);
        // You'll need to create this endpoint in your backend
        const response = await axiosInstance.get("/admin/stats/");
        setStats(response.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching admin stats:", err);
        setError("Greška pri učitavanju podataka");
      } finally {
        setLoading(false);
      }
    };

    fetchAdminStats();
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div
      className={`dashboard-admin-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-admin-main-content">
        <header className="dashboard-header">
          <h1>Administratorska kontrolna tabla</h1>
        </header>

        {loading ? (
          <div className="loading-message">Učitavanje podataka...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <div className="dashboard-content">
            <div className="dashboard-grid">
              <div className="dashboard-card">
                <div className="card-header">
                  <h3>Pregled korisnika</h3>
                </div>
                <div className="card-content">
                  <div className="stat-item">
                    <span>Ukupno korisnika:</span>
                    <strong>{stats.totalUsers}</strong>
                  </div>
                  {Object.entries(stats.usersByType).map(([type, count]) => (
                    <div key={type} className="stat-item">
                      <span>{type}:</span>
                      <strong>{count}</strong>
                    </div>
                  ))}
                </div>
              </div>

              <div className="dashboard-card">
                <div className="card-header">
                  <h3>Pregled dobavljača</h3>
                </div>
                <div className="card-content">
                  <div className="stat-item">
                    <span>Ukupno dobavljača:</span>
                    <strong>{stats.totalSuppliers}</strong>
                  </div>
                  <div className="stat-item">
                    <span>Aktivni dobavljači:</span>
                    <strong>{stats.activeSuppliers}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardAdmin;
