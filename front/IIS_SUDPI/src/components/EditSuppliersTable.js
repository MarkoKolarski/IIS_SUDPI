import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../axiosInstance";
import { FaSearch, FaEdit } from "react-icons/fa";

const EditSuppliersTable = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      const response = await axiosInstance.get("/suppliers/");
      setSuppliers(response.data);
    } catch (error) {
      console.error("Error fetching suppliers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axiosInstance.get(
        `/suppliers/?search=${searchQuery}`
      );
      setSuppliers(response.data);
    } catch (error) {
      console.error("Error searching suppliers:", error);
    }
  };

  const handleEdit = (supplierId) => {
    navigate(`/edit/supplier/${supplierId}`);
  };

  return (
    <div className="suppliers-table-container">
      <div className="suppliers-table-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Pretraži dobavljače..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch}>
            <FaSearch />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">Učitavanje...</div>
      ) : (
        <table className="suppliers-table">
          <thead>
            <tr>
              <th>Naziv</th>
              <th>PIB</th>
              <th>Sirovina</th>
              <th>Email</th>
              <th>Ocena</th>
              <th>Akcije</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier) => (
              <tr key={supplier.sifra_d}>
                <td>{supplier.naziv}</td>
                <td>{supplier.PIB_d}</td>
                <td>{supplier.ime_sirovine}</td>
                <td>{supplier.email}</td>
                <td>{supplier.ocena}/10</td>
                <td>
                  <button
                    className="edit-button"
                    onClick={() => handleEdit(supplier.sifra_d)}
                  >
                    <FaEdit /> Izmeni
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default EditSuppliersTable;
