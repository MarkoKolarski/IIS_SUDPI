import React, { useState, useEffect } from "react";
import "../styles/DashboardKK.css";
import MainSideBar from "../components/MainSideBar";
import { sidebarLinksKK } from "./DashboardKK";
import Calendar from "react-calendar";
import axiosInstance from "../axiosInstance";

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
          <div className="create-visit-form">
            <h2>Zakaži novu posetu</h2>
            <form onSubmit={handleCreateVisit}>
              <select
                value={newVisit.dobavljac_id}
                onChange={(e) =>
                  setNewVisit({ ...newVisit, dobavljac_id: e.target.value })
                }
                required
              >
                <option value="">Izaberite dobavljača</option>
                {suppliers.map((supplier) => (
                  <option key={supplier.sifra_d} value={supplier.sifra_d}>
                    {supplier.naziv}
                  </option>
                ))}
              </select>

              <input
                type="datetime-local"
                value={newVisit.datum_od}
                onChange={(e) =>
                  setNewVisit({ ...newVisit, datum_od: e.target.value })
                }
                required
              />

              <input
                type="datetime-local"
                value={newVisit.datum_do}
                onChange={(e) =>
                  setNewVisit({ ...newVisit, datum_do: e.target.value })
                }
                required
              />

              <button type="submit">Zakaži posetu</button>
            </form>
          </div>

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
