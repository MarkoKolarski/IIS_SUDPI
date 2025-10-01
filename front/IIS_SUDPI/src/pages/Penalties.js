import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/Penalties.css";
import axiosInstance from "../axiosInstance";

const Penalties = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [penaltiesData, setPenaltiesData] = useState([]);
  const [filterOptions, setFilterOptions] = useState({ dobavljaci: [] });
  const [analysisData, setAnalysisData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilters, setSelectedFilters] = useState({
    dobavljac: "svi",
    status: "svi",
  });

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  // Fetch podataka o penalima
  const fetchPenalties = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedFilters.dobavljac !== "svi") {
        params.append("dobavljac", selectedFilters.dobavljac);
      }
      if (selectedFilters.status !== "svi") {
        params.append("status", selectedFilters.status);
      }

      const response = await axiosInstance.get(
        `penalties/?${params.toString()}`
      );
      setPenaltiesData(response.data.results || []);
    } catch (err) {
      console.error("Greška pri dohvatanju penala:", err);
      setError("Greška pri učitavanju podataka o penalima");
    } finally {
      setLoading(false);
    }
  }, [selectedFilters]);

  // Fetch opcija za filtere
  const fetchFilterOptions = async () => {
    try {
      const response = await axiosInstance.get("penalties/filter-options/");
      setFilterOptions(response.data);
    } catch (err) {
      console.error("Greška pri dohvatanju filter opcija:", err);
    }
  };

  // Fetch analize dobavljača
  const fetchAnalysis = async () => {
    try {
      const response = await axiosInstance.get("penalties/analysis/");
      setAnalysisData(response.data.dobavljaci_analiza || []);
    } catch (err) {
      console.error("Greška pri dohvatanju analize:", err);
    }
  };

  // UseEffect za inicijalno učitavanje
  useEffect(() => {
    fetchFilterOptions();
    fetchAnalysis();
  }, []);

  // UseEffect za učitavanje penala kad se promene filteri
  useEffect(() => {
    fetchPenalties();
  }, [fetchPenalties]);

  // Handler za promenu filtera
  const handleFilterChange = (filterName, value) => {
    setSelectedFilters((prev) => ({
      ...prev,
      [filterName]: value,
    }));
  };

  // Formatiranje datuma
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("sr-Latn-RS");
  };

  // Formatiranje iznosa
  const formatAmount = (amount) => {
    return `${parseFloat(amount).toLocaleString("sr-Latn-RS")} RSD`;
  };

  const getStatusBadge = (status) => {
    switch (status.toLowerCase()) {
      case "rešen":
        return <span className="status-badge status-resolved">{status}</span>;
      case "obavešten":
        return <span className="status-badge status-notified">{status}</span>;
      default:
        return <span className="status-badge">{status}</span>;
    }
  };

  return (
    <div
      className={`penalties-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <div className="penalties-main-content">
        <header className="penalties-header">
          <h1>Penali</h1>
        </header>

        <section className="penalties-filter-section">
          <div className="filter-dropdown">
            <label htmlFor="dobavljac-filter">Dobavljač</label>
            <select
              id="dobavljac-filter"
              value={selectedFilters.dobavljac}
              onChange={(e) => handleFilterChange("dobavljac", e.target.value)}
            >
              {filterOptions.dobavljaci?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-dropdown">
            <label htmlFor="status-filter">Status</label>
            <select
              id="status-filter"
              value={selectedFilters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
            >
              {filterOptions.statusi?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </section>

        <section className="penalties-table-section">
          <div className="table-container">
            <div className="table-title-header">
              <h2>Pregled penala</h2>
            </div>
            <div className="table-content">
              <div className="penalties-table-header">
                <div className="table-col col-id">ID</div>
                <div className="table-col col-dobavljac">Dobavljač</div>
                <div className="table-col col-ugovor">Ugovor</div>
                <div className="table-col col-datum">Datum kršenja</div>
                <div className="table-col col-iznos">Iznos</div>
                <div className="table-col col-status">Status</div>
              </div>
              <div className="penalties-table-body">
                {loading ? (
                  <div className="table-row">
                    <div
                      className="table-col"
                      style={{
                        textAlign: "center",
                        padding: "20px",
                        gridColumn: "1 / -1",
                      }}
                    >
                      Učitavanje...
                    </div>
                  </div>
                ) : error ? (
                  <div className="table-row">
                    <div
                      className="table-col"
                      style={{
                        textAlign: "center",
                        padding: "20px",
                        gridColumn: "1 / -1",
                        color: "red",
                      }}
                    >
                      {error}
                    </div>
                  </div>
                ) : penaltiesData.length === 0 ? (
                  <div className="table-row">
                    <div
                      className="table-col"
                      style={{
                        textAlign: "center",
                        padding: "20px",
                        gridColumn: "1 / -1",
                      }}
                    >
                      Nema penala za prikaz
                    </div>
                  </div>
                ) : (
                  penaltiesData.map((row, index) => (
                    <div
                      key={row.sifra_p}
                      className={`table-row ${
                        index % 2 === 0 ? "row-dark" : "row-light"
                      }`}
                    >
                      <div className="table-col col-id">{row.sifra_p}</div>
                      <div className="table-col col-dobavljac">
                        {row.dobavljac_naziv}
                      </div>
                      <div className="table-col col-ugovor">
                        {row.ugovor_sifra}
                      </div>
                      <div className="table-col col-datum">
                        {formatDate(row.datum_p)}
                      </div>
                      <div className="table-col col-iznos">
                        {formatAmount(row.iznos_p)}
                      </div>
                      <div className="table-col col-status">
                        {getStatusBadge(row.status_display)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>

        <section className="analysis-section">
          <div className="analysis-container">
            <div className="analysis-title-header">
              <h2>Automatska analiza saradnje</h2>
            </div>
            <div className="analysis-cards-wrapper">
              {analysisData.length === 0 ? (
                <div className="analysis-card">
                  <p style={{ textAlign: "center", padding: "20px" }}>
                    Nema dovoljno podataka za analizu
                  </p>
                </div>
              ) : (
                analysisData.map((analiza, index) => (
                  <div key={index} className="analysis-card">
                    <h3>{analiza.naziv}</h3>
                    <p>
                      <strong>Broj penala:</strong> {analiza.broj_penala}
                    </p>
                    <p>
                      <strong>Broj prekršenih ugovora:</strong>{" "}
                      {analiza.ugovori_sa_penalima} od {analiza.ukupno_ugovora}
                    </p>
                    <p>
                      <strong>Ukupan iznos:</strong>{" "}
                      {formatAmount(analiza.ukupan_iznos)}
                    </p>
                    <p
                      className={
                        analiza.stopa_krsenja >= 50
                          ? "critical-metric"
                          : analiza.stopa_krsenja >= 25
                          ? "warning-metric"
                          : "positive-metric"
                      }
                    >
                      <strong>Stopa kršenja:</strong> {analiza.stopa_krsenja}%
                      ugovora
                    </p>
                    <p className={`recommendation-${analiza.tip_preporuke}`}>
                      <strong>Preporuka:</strong> {analiza.preporuka}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Penalties;
