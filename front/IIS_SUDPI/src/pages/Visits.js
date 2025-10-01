import React, { useState, useEffect } from "react";
import "../styles/DashboardKK.css";
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";
import VisitSupplierTable from "../components/VisitSupplierTable";

const Visits = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    fetchVisits();
    fetchSuppliers();
  }, []);

  const fetchVisits = async () => {
    try {
      const response = await axiosInstance.get("/visits/");
      setVisits(response.data);
      setError(null);
    } catch (err) {
      setError("Greška pri učitavanju poseta");
      console.error("Error fetching visits:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await axiosInstance.get("/suppliers/");
      setSuppliers(response.data);
    } catch (err) {
      console.error("Error fetching suppliers:", err);
    }
  };

  const updateVisitStatus = async (visitId, newStatus) => {
    try {
      await axiosInstance.put(`/visits/${visitId}/`, { status: newStatus });
      fetchVisits();
    } catch (err) {
      setError("Greška pri ažuriranju statusa posete");
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div
      className={`dashboard-kk-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-kk-main-content">
        <header className="dashboard-header">
          <h1>Planiranje poseta dobavljačima</h1>
        </header>

        <div className="dashboard-content">
          <VisitSupplierTable suppliers={suppliers} existingVisits={visits} />

          <div className="visits-list">
            <h2>Zakazane posete</h2>
            {loading && <div className="loading">Učitavanje...</div>}
            {error && <div className="error">{error}</div>}

            {!loading && !error && visits.length === 0 && (
              <div className="empty-visits">Nema zakazanih poseta</div>
            )}

            {visits.length > 0 && (
              <table className="visits-table">
                <thead>
                  <tr>
                    <th>Dobavljač</th>
                    <th>Datum početka</th>
                    <th>Datum završetka</th>
                    <th>Trajanje</th>
                    <th>Status</th>
                    <th>Akcije</th>
                  </tr>
                </thead>
                <tbody>
                  {visits.map((visit) => {
                    const startDate = new Date(visit.datum_od);
                    const endDate = new Date(visit.datum_do);
                    const duration = Math.round(
                      (endDate - startDate) / (1000 * 60 * 60)
                    );

                    return (
                      <tr key={visit.poseta_id}>
                        <td>
                          <span className="visit-supplier">
                            {visit.dobavljac}
                          </span>
                        </td>
                        <td>
                          <span className="visit-date">
                            {startDate.toLocaleString("sr-RS", {
                              day: "2-digit",
                              month: "2-digit",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </td>
                        <td>
                          <span className="visit-date">
                            {endDate.toLocaleString("sr-RS", {
                              day: "2-digit",
                              month: "2-digit",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </td>
                        <td>
                          <span className="visit-duration">
                            {duration} {duration === 1 ? "sat" : "sati"}
                          </span>
                        </td>
                        <td>
                          <span className={`visit-status ${visit.status}`}>
                            {visit.status.charAt(0).toUpperCase() +
                              visit.status.slice(1).replace("_", " ")}
                          </span>
                        </td>
                        <td className="visit-actions">
                          <select
                            value={visit.status}
                            onChange={(e) =>
                              updateVisitStatus(visit.poseta_id, e.target.value)
                            }
                          >
                            <option value="zakazana">Zakazana</option>
                            <option value="u_toku">U toku</option>
                            <option value="zavrsena">Završena</option>
                            <option value="otkazana">Otkazana</option>
                          </select>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Visits;
