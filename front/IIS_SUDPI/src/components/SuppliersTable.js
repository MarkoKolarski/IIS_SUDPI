import React, { useEffect, useState } from "react";
import "../styles/Suppliers.css";
import "../styles/SuppliersTable.css";
import axiosInstance from "../axiosInstance";
import { FaCheck } from "react-icons/fa";

const SuppliersTable = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [search, setSearch] = useState("");
  const userType = sessionStorage.getItem("user_type");

  const fetchSuppliers = async (query = "") => {
    try {
      const token = sessionStorage.getItem("access_token");
      const response = await fetch(
        `/suppliers/?search=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSuppliers(data || []); // assuming DRF pagination
    } catch (error) {
      console.error("Error fetching dobavljaci:", error);
      setSuppliers([]);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchSuppliers(search);
    }, 300); // debounce

    return () => clearTimeout(delayDebounceFn);
  }, [search]);

  const handleSelectSupplier = async (supplierId) => {
    try {
      const response = await axiosInstance.post(
        `/suppliers/${supplierId}/select/`
      );
      if (response.data.message) {
        // Refresh the suppliers list
        fetchSuppliers();
      }
    } catch (error) {
      console.error("Error selecting supplier:", error);
    }
  };

  return (
    <div className="suppliers-container">
      <h1 className="suppliers-title">Dobavljaci</h1>
      <input
        type="text"
        className="suppliers-search"
        placeholder="Search by name, raw material, or PIB"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <table className="suppliers-table">
        <thead>
          <tr>
            <th>Naziv</th>
            <th>PIB</th>
            <th>Sirovina</th>
            <th>Email</th>
            <th>Ocena</th>
            <th>Status</th>
            {userType === "nabavni_menadzer" && <th>Akcije</th>}
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
              <td>{supplier.izabran ? "Izabran" : "Nije izabran"}</td>
              {userType === "nabavni_menadzer" && (
                <td>
                  {!supplier.izabran && (
                    <button
                      className="select-button"
                      onClick={() => handleSelectSupplier(supplier.sifra_d)}
                    >
                      Izaberi dobavljača
                    </button>
                  )}
                  {supplier.izabran && (
                    <span className="selected-badge">
                      <FaCheck /> Izabran
                    </span>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SuppliersTable;
