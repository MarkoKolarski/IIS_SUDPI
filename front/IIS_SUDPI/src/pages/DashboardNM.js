import React, { useState, useEffect } from "react";
import "../styles/DashboardNM.css";
import MainSideBar from "../components/MainSideBar";
import { dashboardAPI } from "../api";

const DashboardNM = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    profitabilnost_dobavljaca: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getFinansijskiAnalitičarData();
        setDashboardData(response.data);
        setError(null);
      } catch (error) {
        console.error("Greška pri dohvatanju dashboard podataka:", error);
        setError("Greška pri učitavanju podataka. Molimo pokušajte ponovo.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div
      className={`dashboard-fa-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-fa-main-content">
        <header className="dashboard-header">
          <h1>Kontrolna tabla - Nabavni menadzer</h1>
        </header>

        {loading && (
          <div className="loading-message">Učitavanje podataka...</div>
        )}

        {error && <div className="error-message">{error}</div>}

        {!loading && !error && (
          <div className="dashboard-content">
            <div className="dashboard-grid">
              {/* Card 1: Profitabilnost dobavljača */}
              <div className="dashboard-card">
                <div className="card-header">
                  <h3>Profitabilnost dobavljača</h3>
                </div>
                <div className="card-content">
                  {dashboardData.profitabilnost_dobavljaca.length > 0 ? (
                    dashboardData.profitabilnost_dobavljaca.map(
                      (supplier, index) => (
                        <div key={index} className="supplier-item">
                          <span>{supplier.name}</span>
                          <span>{supplier.profitability}</span>
                        </div>
                      )
                    )
                  ) : (
                    <div className="no-data">Nema podataka o dobavljačima</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardNM;
