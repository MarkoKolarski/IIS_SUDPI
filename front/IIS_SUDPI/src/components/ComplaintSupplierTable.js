import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Suppliers.css";

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
