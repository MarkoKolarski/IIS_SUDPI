import React, { useState, useEffect } from "react";
import "../styles/DashboardKK.css";
import MainSideBar from "../components/MainSideBar";
import { sidebarLinksKK } from "./DashboardKK";
import ComplaintSupplierTable from "../components/ComplaintSupplierTable";
import axiosInstance from "../axiosInstance";

const Complaints = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    fetchComplaints();
    fetchSuppliers();
  }, []);

  const fetchComplaints = async () => {
    try {
      const response = await axiosInstance.get("/complaints/");
      setComplaints(response.data);
      setError(null);
    } catch (err) {
      setError("Greška pri učitavanju reklamacija");
      console.error("Error fetching complaints:", err);
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
          <h1>Reklamacije dobavljača</h1>
        </header>

        <div className="dashboard-content">
          <ComplaintSupplierTable suppliers={suppliers} />

          <div className="complaints-list">
            <h2>Lista reklamacija</h2>
            {loading && <div className="loading">Učitavanje...</div>}
            {error && <div className="error">{error}</div>}

            <table className="complaints-table">
              <thead>
                <tr>
                  <th>Dobavljač</th>
                  <th>Datum prijema</th>
                  <th>Status</th>
                  <th>Opis problema</th>
                  <th>Jačina žalbe</th>
                  <th>Vreme trajanja</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((complaint) => (
                  <tr key={complaint.reklamacija_id}>
                    <td>{complaint.dobavljac}</td>
                    <td>
                      {new Date(complaint.datum_prijema).toLocaleDateString()}
                    </td>
                    <td>{complaint.status}</td>
                    <td>{complaint.opis_problema}</td>
                    <td>{complaint.jacina_zalbe}/10</td>
                    <td>{complaint.vreme_trajanja} dana</td>
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

export default Complaints;
