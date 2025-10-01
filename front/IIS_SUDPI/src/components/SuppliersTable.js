import React, { useEffect, useState } from "react";
import "../styles/Suppliers.css";
import "../styles/SuppliersTable.css";

const SuppliersTable = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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

  const handleSelect = async (supplierId) => {
    try {
      setIsLoading(true);
      const token = sessionStorage.getItem("access_token");
      const response = await fetch(`/suppliers/${supplierId}/select/`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      // Refresh the suppliers list
      await fetchSuppliers(search);
    } catch (error) {
      console.error("Error selecting supplier:", error);
      alert(error.message || "Failed to select supplier");
    } finally {
      setIsLoading(false);
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
            <th>Email</th>
            <th>Sirovina</th>
            <th>Cena</th>
            <th>Rok isporuke</th>
            <th>Ocena</th>
            <th>Datum ocenjivanja</th>
            <th>Izabran</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((d) => (
            <tr key={d.sifra_d}>
              <td>{d.naziv}</td>
              <td>{d.pib_d}</td>
              <td>{d.email}</td>
              <td>{d.ime_sirovine}</td>
              <td>{d.cena}</td>
              <td>{d.rok_isporuke}</td>
              <td>{d.ocena}</td>
              <td>{new Date(d.datum_ocenjivanja).toLocaleDateString()}</td>
              <td className={d.izabran ? "selected" : "not-selected"}>
                {d.izabran ? "Da" : "Ne"}
              </td>
              <td>
                <button
                  className="select-button"
                  onClick={() => handleSelect(d.sifra_d)}
                  disabled={d.izabran || isLoading}
                >
                  {d.izabran ? "Izabran" : "Izaberi"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SuppliersTable;
