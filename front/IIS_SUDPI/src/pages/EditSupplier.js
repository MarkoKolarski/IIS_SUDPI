import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";
import "../styles/EditSupplier.css";

const EditSupplier = () => {
  const { supplierId } = useParams();
  const navigate = useNavigate();
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [supplier, setSupplier] = useState({
    naziv: "",
    PIB_d: "",
    ime_sirovine: "",
    email: "",
    cena: "",
    rok_isporuke: "",
    ocena: "",
    datum_ocenjivanja: "",
  });
  const [loading, setLoading] = useState(supplierId !== "new");
  const [error, setError] = useState(null);

  const fetchSupplier = useCallback(async () => {
    try {
      const response = await axiosInstance.get(`/suppliers/${supplierId}/`);
      setSupplier(response.data);
    } catch (error) {
      setError("Greška pri učitavanju dobavljača");
    } finally {
      setLoading(false);
    }
  }, [supplierId]);

  useEffect(() => {
    if (supplierId !== "new") {
      fetchSupplier();
    }
  }, [supplierId, fetchSupplier]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Create a copy of supplier data without readonly fields
      const supplierData = { ...supplier };
      delete supplierData.ocena;
      delete supplierData.datum_ocenjivanja;

      if (supplierId === "new") {
        await axiosInstance.post("/suppliers/", supplierData);
      } else {
        await axiosInstance.put(`/suppliers/${supplierId}/`, supplierData);
      }
      navigate("/edit/suppliers");
    } catch (error) {
      setError("Greška pri čuvanju dobavljača");
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSupplier((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleDelete = async () => {
    if (
      window.confirm("Da li ste sigurni da želite da obrišete ovog dobavljača?")
    ) {
      try {
        await axiosInstance.delete(`/suppliers/${supplierId}/`);
        navigate("/edit/suppliers");
      } catch (error) {
        setError("Greška pri brisanju dobavljača");
      }
    }
  };

  if (loading) return <div>Učitavanje...</div>;

  return (
    <div
      className={`edit-supplier-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="edit-supplier-main-content">
        <header className="edit-supplier-header">
          <h1>
            {supplierId === "new" ? "Novi dobavljač" : "Izmena dobavljača"}
          </h1>
        </header>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="supplier-form">
          <div className="form-group">
            <label htmlFor="naziv">Naziv</label>
            <input
              type="text"
              id="naziv"
              name="naziv"
              value={supplier.naziv}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="PIB_d">PIB</label>
            <input
              type="text"
              id="PIB_d"
              name="PIB_d"
              value={supplier.PIB_d}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="ime_sirovine">Sirovina</label>
            <input
              type="text"
              id="ime_sirovine"
              name="ime_sirovine"
              value={supplier.ime_sirovine}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={supplier.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="cena">Cena</label>
            <input
              type="number"
              id="cena"
              name="cena"
              value={supplier.cena}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="rok_isporuke">Rok isporuke (dani)</label>
            <input
              type="number"
              id="rok_isporuke"
              name="rok_isporuke"
              value={supplier.rok_isporuke}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="ocena">Ocena (0-10)</label>
            <input
              type="number"
              id="ocena"
              name="ocena"
              min="0"
              max="10"
              step="0.1"
              value={supplier.ocena}
              onChange={handleChange}
              readOnly
              disabled
              className="readonly-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="datum_ocenjivanja">Datum ocenjivanja</label>
            <input
              type="date"
              id="datum_ocenjivanja"
              name="datum_ocenjivanja"
              value={supplier.datum_ocenjivanja}
              onChange={handleChange}
              readOnly
              disabled
              className="readonly-input"
            />
          </div>

          <div className="form-actions">
            {supplierId !== "new" && (
              <button
                type="button"
                onClick={handleDelete}
                className="delete-btn"
              >
                Obriši dobavljača
              </button>
            )}
            <div className="form-actions-right">
              <button
                type="button"
                onClick={() => navigate("/edit/suppliers")}
                className="cancel-btn"
              >
                Odustani
              </button>
              <button type="submit" className="save-btn">
                {supplierId === "new" ? "Dodaj dobavljača" : "Sačuvaj izmene"}
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};

export default EditSupplier;
