import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import styles from "../styles/Penalties.module.css";
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
  const [checkingViolations, setCheckingViolations] = useState(false);
  const [violationMessage, setViolationMessage] = useState(null);

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

  // Handler za automatsku proveru kršenja i kreiranje penala
  const handleCheckViolations = async () => {
    try {
      setCheckingViolations(true);
      setViolationMessage(null);

      const response = await axiosInstance.post("penalties/auto-create/");
      
      const { message, penalties_created, violations_found } = response.data;
      
      // Prikaži success poruku
      setViolationMessage({
        type: "success",
        text: `${message} Pronađeno: ${violations_found}, Kreirano: ${penalties_created} penala.`,
      });

      // Refresh penala i analize
      await fetchPenalties();
      await fetchAnalysis();
      
      // Sakrij poruku nakon 5 sekundi
      setTimeout(() => {
        setViolationMessage(null);
      }, 5000);
      
    } catch (err) {
      console.error("Greška pri proveri kršenja:", err);
      setViolationMessage({
        type: "error",
        text: err.response?.data?.error || "Greška pri proveri kršenja ugovora",
      });
      
      // Sakrij poruku nakon 5 sekundi
      setTimeout(() => {
        setViolationMessage(null);
      }, 5000);
    } finally {
      setCheckingViolations(false);
    }
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
        return <span className={`${styles.statusBadge} ${styles.statusResolved}`}>{status}</span>;
      case "obavešten":
        return <span className={`${styles.statusBadge} ${styles.statusNotified}`}>{status}</span>;
      default:
        return <span className={styles.statusBadge}>{status}</span>;
    }
  };

  return (
    <div
      className={`${styles.penaltiesWrapper} ${
        isSidebarCollapsed ? styles.sidebarCollapsed : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <div className={styles.penaltiesMainContent}>
        <header className={styles.penaltiesHeader}>
          <h1>Penali</h1>
        </header>

        <section className={styles.penaltiesFilterSection}>
          <div className={styles.filterDropdown}>
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
          <div className={styles.filterDropdown}>
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
          <div className={styles.filterDropdown} style={{ marginLeft: 'auto' }}>
            <label>&nbsp;</label>
            <button
              className={styles.checkViolationsBtn}
              onClick={handleCheckViolations}
              disabled={checkingViolations}
            >
              {checkingViolations ? (
                <>
                  <span className={styles.spinner}></span>
                  Proveravam...
                </>
              ) : (
                <>
                  <span>🔍</span>
                  Proveri kršenja ugovora
                </>
              )}
            </button>
          </div>
        </section>

        {violationMessage && (
          <div className={`${styles.violationMessage} ${styles[violationMessage.type]}`}>
            {violationMessage.text}
          </div>
        )}

        <section className={styles.penaltiesTableSection}>
          <div className={styles.tableContainer}>
            <div className={styles.tableTitleHeader}>
              <h2>Pregled penala</h2>
            </div>
            <div className={styles.tableContent}>
              <div className={styles.penaltiesTableHeader}>
                <div className={`${styles.tableCol} ${styles.colId}`}>ID</div>
                <div className={`${styles.tableCol} ${styles.colDobavljac}`}>Dobavljač</div>
                <div className={`${styles.tableCol} ${styles.colUgovor}`}>Ugovor</div>
                <div className={`${styles.tableCol} ${styles.colDatum}`}>Datum kršenja</div>
                <div className={`${styles.tableCol} ${styles.colIznos}`}>Iznos</div>
                <div className={`${styles.tableCol} ${styles.colStatus}`}>Status</div>
              </div>
              <div className={styles.penaltiesTableBody}>
                {loading ? (
                  <div className={styles.tableRow}>
                    <div
                      className={styles.tableCol}
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
                  <div className={styles.tableRow}>
                    <div
                      className={styles.tableCol}
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
                  <div className={styles.tableRow}>
                    <div
                      className={styles.tableCol}
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
                        index % 2 === 0 ? styles.rowDark : styles.rowLight
                      }`}
                    >
                      <div className={`${styles.tableCol} ${styles.colId}`}>{row.sifra_p}</div>
                      <div className={`${styles.tableCol} ${styles.colDobavljac}`}>
                        {row.dobavljac_naziv}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colUgovor}`}>
                        {row.ugovor_sifra}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colDatum}`}>
                        {formatDate(row.datum_p)}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colIznos}`}>
                        {formatAmount(row.iznos_p)}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colStatus}`}>
                        {getStatusBadge(row.status_display)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>

        <section className={styles.analysisSection}>
          <div className={styles.analysisContainer}>
            <div className={styles.analysisTitleHeader}>
              <h2>Automatska analiza saradnje</h2>
            </div>
            <div className={styles.analysisCardsWrapper}>
              {analysisData.length === 0 ? (
                <div className={styles.analysisCard}>
                  <p style={{ textAlign: "center", padding: "20px" }}>
                    Nema dovoljno podataka za analizu
                  </p>
                </div>
              ) : (
                analysisData.map((analiza, index) => (
                  <div key={index} className={styles.analysisCard}>
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
