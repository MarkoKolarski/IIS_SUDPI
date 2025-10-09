import React, { useEffect, useState } from "react";
import axiosInstance from "../axiosInstance";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/VoziloEdit.css";
import MainSideBar from "../components/MainSideBar";

const EditVozilo = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    status: "",
    kapacitet: "",
    registracija: "",
  });
  const [servisi, setServisi] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const toggleSidebar = () => {
          setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const voziloRes = await axiosInstance.get(`/vozila/${id}/`);
        const servisiRes = await axiosInstance.get(`/vozila/${id}/servisi/`);
        setFormData({
          status: voziloRes.data.status || "",
          kapacitet: voziloRes.data.kapacitet || "",
          /* registracija: voziloRes.data.registracija?.split("T")[0] || "",*/
          registracija: voziloRes.data.registracija?.split("T")[0] || "",
        });
        setServisi(servisiRes.data);
      } catch (error) {
        console.error("Greška pri učitavanju:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ 
      ...prev, 
      [name]: value 
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.put(`/vozila/update/${id}/`, formData);
      alert("Podaci uspešno ažurirani!");
      navigate("/logistics-transport");
    } catch (err) {
      if (err.response) {
        console.error("Status:", err.response.status);
        console.error("Data:", err.response.data);
    }
      console.error("Greška pri čuvanju:", err);
      alert("Došlo je do greške pri čuvanju podataka.");
    }
  };

  if (loading) return <p>Učitavanje...</p>;

  return (
    <div className={`edit-vozilo-wrapper ${isSidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <MainSideBar
                isCollapsed={isSidebarCollapsed}
                toggleSidebar={toggleSidebar}
                activePage="edit-vozilo"
            />
      <div className="edit-vozilo-main">
      <div className="edit-vozilo-header">
        <h2>Izmena podataka o vozilu</h2>
      </div>
      <div className="edit-vozilo-content">
        {/* LEVO: forma */}
        <form onSubmit={handleSubmit} className="edit-vozilo-form">
          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="">Izaberi status</option>
              <option value="slobodno">Slobodno</option>
              <option value="zauzeto">Zauzeto</option>
              <option value="u_kvaru">U kvaru</option>
              <option value="na_servisu">Na servisu</option>
            </select>
          </div>

          <div className="form-group">
            <label>Istek registracije</label>
            <input
              type="date"
              name="registracija"
              value={formData.registracija}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Kapacitet</label>
            <input
              type="text"
              name="kapacitet"
              value={formData.kapacitet}
              onChange={handleChange}
            />
          </div>

          <div className="edit-vozilo-buttons">
            <button
              type="button"
              onClick={() => navigate("/logistika-transport")}
              className="cancel-btn"
            >
              Odustani
            </button>
            <button
              type="submit"
              className="save-btn"
            >
              Potvrdi
            </button>
          </div>
        </form>

        {/* DESNO: servisi */}
        <div className="servis-section">
          <h3>Servisi</h3>
          <table className="servis-table">
            <thead>
              <tr>
                <th>Datum</th>
                <th>Vrsta</th>
                <th>Napomena</th>
              </tr>
            </thead>
            <tbody>
              {servisi.length === 0 ? (
                <tr>
                  <td colSpan="3" className="no-servis">
                    Nema servisa za ovo vozilo
                  </td>
                </tr>
              ) : (
                servisi.map((s, i) => (
                  <tr key={i}>
                    <td>{s.datum_servisa}</td>
                    <td>{s.vrsta}</td>
                    <td>{s.napomena}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        </div>
      </div>
    </div>
  );
};

export default EditVozilo;