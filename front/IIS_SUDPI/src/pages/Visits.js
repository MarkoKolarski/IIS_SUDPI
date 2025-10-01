import React, { useState, useEffect } from "react";
import "../styles/DashboardKK.css";
import MainSideBar from "../components/MainSideBar";
import { sidebarLinksKK } from "./DashboardKK";
import Calendar from "react-calendar";
import axiosInstance from "../axiosInstance";
import VisitSupplierTable from "../components/VisitSupplierTable";

const Visits = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [newVisit, setNewVisit] = useState({
    dobavljac_id: "",
    datum_od: "",
    datum_do: "",
  });
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

  const handleCreateVisit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("/visits/create/", newVisit);
      fetchVisits();
      setNewVisit({ dobavljac_id: "", datum_od: "", datum_do: "" });
    } catch (err) {
      setError("Greška pri kreiranju posete");
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

  const handleSupplierSelect = (supplier, selectedDate) => {
    setNewVisit({
      dobavljac_id: supplier.sifra_d,
      datum_od: selectedDate.toISOString(),
      datum_do: new Date(
        selectedDate.getTime() + 2 * 60 * 60 * 1000
      ).toISOString(), // 2 hours duration by default
    });
    // Open the form section or modal for additional details
    // You can implement this based on your UI requirements
  };

  return (
    <div
      className={`dashboard-kk-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        links={sidebarLinksKK}
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-kk-main-content">
        <header className="dashboard-header">
          <h1>Planiranje poseta dobavljačima</h1>
        </header>

        <div className="dashboard-content">
          <VisitSupplierTable
            suppliers={suppliers}
            existingVisits={visits}
            onSupplierSelect={handleSupplierSelect}
          />

          <div className="visits-list">
            <h2>Zakazane posete</h2>
            {loading && <div className="loading">Učitavanje...</div>}
            {error && <div className="error">{error}</div>}

            <table className="visits-table">
              <thead>
                <tr>
                  <th>Dobavljač</th>
                  <th>Datum od</th>
                  <th>Datum do</th>
                  <th>Status</th>
                  <th>Akcije</th>
                </tr>
              </thead>
              <tbody>
                {visits.map((visit) => (
                  <tr key={visit.poseta_id}>
                    <td>{visit.dobavljac}</td>
                    <td>{new Date(visit.datum_od).toLocaleString()}</td>
                    <td>{new Date(visit.datum_do).toLocaleString()}</td>
                    <td>{visit.status}</td>
                    <td>
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
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Visits;
