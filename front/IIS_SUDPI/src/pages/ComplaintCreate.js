import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";
import "../styles/ComplaintCreate.css";

const ComplaintCreate = () => {
  const { supplierId } = useParams();
  const navigate = useNavigate();
  const [supplier, setSupplier] = useState(null);
  const [complaint, setComplaint] = useState({
    dobavljac_id: supplierId,
    opis_problema: "",
    jacina_zalbe: 5,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSupplier = async () => {
      try {
        const response = await axiosInstance.get(`/suppliers/${supplierId}/`);
        setSupplier(response.data);
      } catch (err) {
        setError("Greška pri učitavanju dobavljača");
      }
    };
    fetchSupplier();
  }, [supplierId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("/complaints/create/", complaint);
      navigate("/complaints");
    } catch (err) {
      setError("Greška pri kreiranju reklamacije");
    }
  };

  if (!supplier) return <div>Učitavanje...</div>;

  return (
    <div className="complaint-create-wrapper">
      <MainSideBar isCollapsed={false} />
      <main className="complaint-create-main">
        <header className="complaint-header">
          <h1>Nova reklamacija za dobavljača: {supplier.naziv}</h1>
        </header>

        <div className="complaint-form-container">
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit} className="complaint-form">
            <div className="form-group">
              <label>Opis problema:</label>
              <textarea
                value={complaint.opis_problema}
                onChange={(e) =>
                  setComplaint({
                    ...complaint,
                    opis_problema: e.target.value,
                  })
                }
                required
              />
            </div>

            <div className="form-group">
              <label>Jačina žalbe: {complaint.jacina_zalbe}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={complaint.jacina_zalbe}
                onChange={(e) =>
                  setComplaint({
                    ...complaint,
                    jacina_zalbe: parseInt(e.target.value),
                  })
                }
                className="slider"
              />
              <div className="slider-labels">
                <span>1</span>
                <span>5</span>
                <span>10</span>
              </div>
            </div>

            <div className="form-actions">
              <button type="button" onClick={() => navigate("/complaints")}>
                Odustani
              </button>
              <button type="submit">Podnesi reklamaciju</button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default ComplaintCreate;
