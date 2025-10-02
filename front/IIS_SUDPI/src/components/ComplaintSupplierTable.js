import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/SuppliersTable.css";

const ComplaintSupplierTable = ({ suppliers }) => {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const handleSupplierClick = (supplierId) => {
    navigate(`/complaints/create/${supplierId}`);
  };

  const filteredSuppliers = suppliers.filter(
    (d) =>
      d.naziv.toLowerCase().includes(search.toLowerCase()) ||
      d.ime_sirovine.toLowerCase().includes(search.toLowerCase()) ||
      d.PIB_d.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (dateString) => {
    if (!dateString) return "Nije ocenjen";
    const date = new Date(dateString);
    return date.toLocaleDateString("sr-RS", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  return (
    <div className="suppliers-container">
      <input
        type="text"
        className="suppliers-search"
        placeholder="Pretraži dobavljače po nazivu, sirovini ili PIB-u"
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
            <th>Ocena</th>
            <th>Datum ocenjivanja</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          {filteredSuppliers.map((d) => (
            <tr key={d.sifra_d}>
              <td>{d.naziv}</td>
              <td>{d.PIB_d}</td>
              <td>{d.email}</td>
              <td>{d.ime_sirovine}</td>
              <td>{d.ocena}/10</td>
              <td>{formatDate(d.datum_ocenjivanja)}</td>
              <td>
                <button
                  className="supplier-action-button complaint"
                  onClick={() => handleSupplierClick(d.sifra_d)}
                >
                  Podnesi reklamaciju
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComplaintSupplierTable;
