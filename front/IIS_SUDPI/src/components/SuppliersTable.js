import React, { useEffect, useState } from "react";
import "../styles/Suppliers.css";

const SuppliersTable = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [search, setSearch] = useState("");

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
      console.log("fetched suppliers:", data);
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

  return (
    <div style={{ padding: "20px" }}>
      <h1>Dobavljaci</h1>
      <input
        type="text"
        placeholder="Search by name, raw material, or PIB"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: "20px", padding: "8px", width: "300px" }}
      />
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr style={{ backgroundColor: "#f2f2f2" }}>
            <th>Naziv</th>
            <th>PIB</th>
            <th>Email</th>
            <th>Sirovina</th>
            <th>Cena</th>
            <th>Rok isporuke</th>
            <th>Ocena</th>
            <th>Datum ocenjivanja</th>
            <th>Izabran</th>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((d) => (
            <tr key={d.id}>
              <td>{d.naziv}</td>
              <td>{d.pib_d}</td>
              <td>{d.email}</td>
              <td>{d.ime_sirovine}</td>
              <td>{d.cena}</td>
              <td>{d.rok_isporuke}</td>
              <td>{d.ocena}</td>
              <td>{new Date(d.datum_ocenjivanja).toLocaleDateString()}</td>
              <td>{d.izabran ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SuppliersTable;
