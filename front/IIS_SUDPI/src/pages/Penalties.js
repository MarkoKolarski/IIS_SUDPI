import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import styles from "../styles/Penalties.module.css";
import axiosInstance from "../axiosInstance";
import { FaChevronDown, FaShieldAlt } from "react-icons/fa";
import PageTransition from "../components/PageTransition";

const Penalties = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [penaltiesData, setPenaltiesData] = useState([]);
  const [filterOptions, setFilterOptions] = useState({ dobavljaci: [] });
  const [analysisData, setAnalysisData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    num_pages: 0,
    current_page: 1,
    has_next: false,
    has_previous: false,
  });
  const [selectedFilters, setSelectedFilters] = useState({
    dobavljac: "svi",
    status: "svi",
  });
  const [checkingViolations, setCheckingViolations] = useState(false);
  const [violationMessage, setViolationMessage] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState({
    dobavljac: false,
    status: false,
  });

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  // Fetch podataka o penalima
  const fetchPenalties = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const params = new URLSearchParams();
      params.append("page", pagination.current_page);
      params.append("page_size", 10);
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
      setPagination({
        count: response.data.count || 0,
        num_pages: response.data.num_pages || 0,
        current_page: response.data.current_page || 1,
        has_next: Boolean(response.data.has_next),
        has_previous: Boolean(response.data.has_previous),
      });
    } catch (err) {
      console.error("Greška pri dohvatanju penala:", err);
      setError("Greška pri učitavanju podataka o penalima");
      setPenaltiesData([]);
    } finally {
      setLoading(false);
    }
  }, [pagination.current_page, selectedFilters]);

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
    setPagination((prev) => ({ ...prev, current_page: 1 }));
    setDropdownOpen((prev) => ({
      ...prev,
      [filterName]: false,
    }));
  };

  const toggleDropdown = (dropdownType) => {
    setDropdownOpen((prev) => ({
      ...prev,
      [dropdownType]: !prev[dropdownType],
    }));
  };

  const getSelectedLabel = (filterType, value) => {
    const options = filterOptions[filterType] || [];
    const selected = options.find((option) => option.value === value);
    return selected ? selected.label : "Svi";
  };

  const handlePageChange = (nextPage) => {
    if (
      nextPage < 1 ||
      nextPage > pagination.num_pages ||
      nextPage === pagination.current_page
    ) {
      return;
    }

    setPagination((prev) => ({
      ...prev,
      current_page: nextPage,
    }));
  };

  const getVisiblePages = (currentPage, totalPages, siblingCount = 1) => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pages = [1];
    const start = Math.max(2, currentPage - siblingCount);
    const end = Math.min(totalPages - 1, currentPage + siblingCount);

    if (start > 2) {
      pages.push("ellipsis-left");
    }

    for (let page = start; page <= end; page += 1) {
      pages.push(page);
    }

    if (end < totalPages - 1) {
      pages.push("ellipsis-right");
    }

    pages.push(totalPages);
    return pages;
  };

  // Handler za automatsku proveru kršenja i kreiranje penala
  const handleCheckViolations = async () => {
    try {
      setCheckingViolations(true);
      setViolationMessage(null);

      const response = await axiosInstance.post("penalties/auto-create/");
      
      const { penalties_created, violations_found } = response.data;
      
      // Prikaži success poruku
      setViolationMessage({
        type: "success",
        text: `Pronađeno: ${violations_found}, Kreirano: ${penalties_created} penala.`,
      });

      // Refresh penala i analize paralelno radi bržeg odziva UI-a
      await Promise.all([fetchPenalties(), fetchAnalysis()]);
      
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

  const visiblePages = getVisiblePages(
    pagination.current_page,
    pagination.num_pages
  );

  return (
    <PageTransition>
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
            <label>Dobavljač</label>
            <button type="button" onClick={() => toggleDropdown("dobavljac")}>
              <span>{getSelectedLabel("dobavljaci", selectedFilters.dobavljac)}</span>
              <FaChevronDown />
            </button>
            {dropdownOpen.dobavljac && (
              <div className={styles.dropdownMenu}>
                {(filterOptions.dobavljaci || []).map((option) => (
                  <div
                    key={option.value}
                    className={styles.dropdownItem}
                    onClick={() => handleFilterChange("dobavljac", option.value)}
                  >
                    {option.label}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className={styles.filterDropdown}>
            <label>Status</label>
            <button type="button" onClick={() => toggleDropdown("status")}>
              <span>{getSelectedLabel("statusi", selectedFilters.status)}</span>
              <FaChevronDown />
            </button>
            {dropdownOpen.status && (
              <div className={styles.dropdownMenu}>
                {(filterOptions.statusi || []).map((option) => (
                  <div
                    key={option.value}
                    className={styles.dropdownItem}
                    onClick={() => handleFilterChange("status", option.value)}
                  >
                    {option.label}
                  </div>
                ))}
              </div>
            )}
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
                  <FaShieldAlt className={styles.buttonIcon} aria-hidden="true" />
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

        <section className={styles.tableSection}>
          <div className={styles.tableContainer}>
            <div className={styles.tableTitleHeader}>
              <h2>Pregled penala ({pagination.count} ukupno)</h2>
            </div>
            <div className={styles.tableContent}>
              <div className={styles.tableHeader}>
                <div className={styles.tableCol} style={{ width: "12%" }}>
                  ID
                </div>
                <div className={styles.tableCol} style={{ width: "12%" }}>
                  Dobavljač
                </div>
                <div className={styles.tableCol} style={{ width: "14%" }}>
                  Ugovor
                </div>
                <div className={styles.tableCol} style={{ width: "20%" }}>
                  Datum kršenja
                </div>
                <div className={styles.tableCol} style={{ width: "20%" }}>
                  Iznos
                </div>
                <div className={`${styles.tableCol} ${styles.statusCol}`} style={{ width: "22%" }}>
                  Status
                </div>
              </div>
              <div className={styles.tableBody}>
                {loading ? (
                  <div className={styles.loadingMessage}>Učitavanje penala...</div>
                ) : error ? (
                  <div className={styles.errorMessage}>{error}</div>
                ) : penaltiesData.length === 0 ? (
                  <div className={styles.noDataMessage}>Nema penala za prikaz</div>
                ) : (
                  penaltiesData.map((row, index) => (
                    <div
                      key={row.sifra_p}
                      className={`${styles.tableRow} ${
                        index % 2 === 0 ? styles.rowEven : styles.rowOdd
                      }`}
                    >
                      <div className={styles.tableCol} style={{ width: "12%" }}>
                        {row.sifra_p}
                      </div>
                      <div className={styles.tableCol} style={{ width: "12%" }}>
                        {row.dobavljac_naziv}
                      </div>
                      <div className={styles.tableCol} style={{ width: "14%" }}>
                        {row.ugovor_sifra}
                      </div>
                      <div className={styles.tableCol} style={{ width: "20%" }}>
                        {formatDate(row.datum_p)}
                      </div>
                      <div className={styles.tableCol} style={{ width: "20%" }}>
                        {formatAmount(row.iznos_p)}
                      </div>
                      <div className={`${styles.tableCol} ${styles.statusCol}`} style={{ width: "22%" }}>
                        {getStatusBadge(row.status_display)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {!loading && penaltiesData.length > 0 && pagination.num_pages > 1 && (
              <div className={styles.pagination}>
                <button
                  onClick={() => handlePageChange(pagination.current_page - 1)}
                  disabled={!pagination.has_previous}
                  className={`${styles.paginationBtn} ${styles.paginationNavBtn}`}
                >
                  Prethodna
                </button>

                <div className={styles.paginationPageList}>
                  {visiblePages.map((page, index) =>
                    typeof page === "string" ? (
                      <span
                        key={`${page}-${index}`}
                        className={styles.paginationEllipsis}
                      >
                        ...
                      </span>
                    ) : (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`${styles.paginationBtn} ${styles.paginationPageBtn} ${
                          page === pagination.current_page
                            ? styles.paginationPageBtnActive
                            : ""
                        }`}
                        aria-current={
                          page === pagination.current_page ? "page" : undefined
                        }
                      >
                        {page}
                      </button>
                    )
                  )}
                </div>

                <button
                  onClick={() => handlePageChange(pagination.current_page + 1)}
                  disabled={!pagination.has_next}
                  className={`${styles.paginationBtn} ${styles.paginationNavBtn}`}
                >
                  Sledeća
                </button>
              </div>
            )}
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
    </PageTransition>
  );
};

export default Penalties;
