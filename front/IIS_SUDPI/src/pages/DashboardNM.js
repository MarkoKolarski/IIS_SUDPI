import React, { useState, useEffect } from "react";
import "../styles/DashboardNM.css";
import MainSideBar from "../components/MainSideBar";
import { dashboardAPI } from "../api";
import axiosInstance from "../api";

const DashboardNM = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    profitabilnost_dobavljaca: [],
  });
  const [expCertificates, setExpCertificates] = useState([]);
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

    const fetchExpiringCertificates = async () => {
      try {
        const response = await axiosInstance.get("/expiring-certificates/");
        if (response && response.data) {
          // Sort certificates by days_left in ascending order (most critical first)
          const sortedCertificates = [...response.data].sort(
            (a, b) => a.days_left - b.days_left
          );
          setExpCertificates(sortedCertificates);
        }
      } catch (error) {
        console.error("Greška pri dohvatanju sertifikata:", error);
        // Don't set global error, just handle silently for this component
      }
    };

    fetchDashboardData();
    fetchExpiringCertificates();
  }, []);

  // Helper function to determine certificate urgency class
  const getCertificateUrgencyClass = (daysLeft) => {
    if (daysLeft <= 7) return "certificate-critical";
    if (daysLeft <= 14) return "certificate-warning";
    return "certificate-notice";
  };

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
            {/* Certificate Expiration Notifications */}
            {expCertificates && expCertificates.length > 0 && (
              <div className="certificates-notification-section">
                <h2>Obaveštenja o sertifikatima</h2>
                <div className="certificates-container">
                  {expCertificates.map((cert) => (
                    <div
                      key={cert.sertifikat_id}
                      className={`certificate-card ${getCertificateUrgencyClass(
                        cert.days_left
                      )}`}
                    >
                      <div className="certificate-header">
                        <span className="certificate-type">{cert.tip}</span>
                        <span className="days-left">
                          {cert.days_left}{" "}
                          {cert.days_left === 1 ? "dan" : "dana"}
                        </span>
                      </div>
                      <h3 className="certificate-name">{cert.naziv}</h3>
                      <div className="certificate-supplier">
                        Dobavljač: {cert.dobavljac_naziv}
                      </div>
                      <div className="certificate-dates">
                        <div>
                          Izdavanje:{" "}
                          {new Date(cert.datum_izdavanja).toLocaleDateString(
                            "sr-RS"
                          )}
                        </div>
                        <div>
                          Ističe:{" "}
                          {new Date(cert.datum_isteka).toLocaleDateString(
                            "sr-RS"
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

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
