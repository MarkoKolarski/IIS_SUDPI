import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/VisitSupplierTable.css";

const VisitSupplierTable = ({ suppliers }) => {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const handleSupplierClick = (supplierId) => {
    navigate(`/visits/schedule/${supplierId}`);
  };

  const filteredSuppliers = suppliers.filter(
    (d) =>
      d.naziv.toLowerCase().includes(search.toLowerCase()) ||
      d.ime_sirovine.toLowerCase().includes(search.toLowerCase()) ||
      d.PIB_d.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="visit-supplier-container">
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
                  className="schedule-visit-button"
                  onClick={() => handleSupplierClick(d.sifra_d)}
                >
                  Zakaži posetu
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default VisitSupplierTable;
