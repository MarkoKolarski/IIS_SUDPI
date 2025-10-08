import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import styles from "../styles/Invoice.module.css";
import { FaChevronDown, FaTimes, FaSearch } from "react-icons/fa";
import axiosInstance from "../axiosInstance";
import { useNavigate } from "react-router-dom";

const Invoice = () => {
  const navigate = useNavigate();
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [invoices, setInvoices] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    statusi: [],
    dobavljaci: [],
    datumi: [],
  });
  const [filters, setFilters] = useState({
    status: "svi",
    dobavljac: "svi",
    datum: "svi",
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [pagination, setPagination] = useState({
    count: 0,
    num_pages: 0,
    current_page: 1,
    has_next: false,
    has_previous: false,
  });
  const [loading, setLoading] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState({
    status: false,
    dobavljac: false,
    datum: false,
  });

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const loadFilterOptions = async () => {
    try {
      const response = await axiosInstance.get("/invoices/filter-options/");
      setFilterOptions(response.data);
    } catch (error) {
      console.error("Greška pri učitavanju filter opcija:", error);
    }
  };

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        status: filters.status,
        dobavljac: filters.dobavljac,
        datum: filters.datum,
        page: pagination.current_page,
        page_size: 10,
      });

      if (activeSearch) {
        params.append("search", activeSearch);
      }

      const response = await axiosInstance.get(`/invoices/?${params}`);
      setInvoices(response.data.results);
      setPagination({
        count: response.data.count,
        num_pages: response.data.num_pages,
        current_page: response.data.current_page,
        has_next: response.data.has_next,
        has_previous: response.data.has_previous,
      });
    } catch (error) {
      console.error("Greška pri učitavanju faktura:", error);
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  }, [filters, activeSearch, pagination.current_page]);

  const handleFilterChange = (filterType, value) => {
    setFilters((prev) => ({
      ...prev,
      [filterType]: value,
    }));
    setPagination((prev) => ({ ...prev, current_page: 1 }));
    setDropdownOpen((prev) => ({ ...prev, [filterType]: false }));
  };

  const handleSearch = () => {
    setActiveSearch(searchQuery);
    setPagination((prev) => ({ ...prev, current_page: 1 }));
  };

  const clearSearch = () => {
    setSearchQuery("");
    setActiveSearch("");
    setPagination((prev) => ({ ...prev, current_page: 1 }));
  };

  const toggleDropdown = (dropdownType) => {
    setDropdownOpen((prev) => ({
      ...prev,
      [dropdownType]: !prev[dropdownType],
    }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("sr-RS");
  };

  const formatAmount = (amount) => {
    return `${parseFloat(amount).toFixed(0)} RSD`;
  };

  const getStatusClassName = (status) => {
    switch (status) {
      case "Čeka verifikaciju":
        return "statusWaiting";
      case "Plaćeno":
        return "statusPaid";
      case "Primljeno":
        return "statusReceived";
      case "Odbačeno":
        return "statusRejected";
      default:
        return "";
    }
  };

  const getSelectedLabel = (filterType, value) => {
    const options = filterOptions[filterType] || [];
    const selected = options.find((option) => option.value === value);
    return selected ? selected.label : "Svi";
  };

  const handleInvoiceClick = (invoiceId) => {
    navigate(`/invoice-details/${invoiceId}`);
  };

  // Učitavanje filter opcija prilikom mount-a
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Učitavanje faktura kada se promene filteri
  useEffect(() => {
    loadInvoices();
  }, [loadInvoices]);

  return (
    <div
      className={`${styles.invoiceWrapper} ${
        isSidebarCollapsed ? styles.sidebarCollapsed : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className={styles.invoiceMainContent}>
        <header className={styles.invoiceHeader}>
          <h1>Fakture</h1>
        </header>

        <section className={styles.filterSection}>
          <div className={styles.filterControls}>
            <div className={styles.filterDropdown}>
              <label>Status</label>
              <button onClick={() => toggleDropdown("status")}>
                <span>{getSelectedLabel("statusi", filters.status)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.status && (
                <div className={styles.dropdownMenu}>
                  {filterOptions.statusi.map((option) => (
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
            <div className={styles.filterDropdown}>
              <label>Dobavljač</label>
              <button onClick={() => toggleDropdown("dobavljac")}>
                <span>{getSelectedLabel("dobavljaci", filters.dobavljac)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.dobavljac && (
                <div className={styles.dropdownMenu}>
                  {filterOptions.dobavljaci.map((option) => (
                    <div
                      key={option.value}
                      className={styles.dropdownItem}
                      onClick={() =>
                        handleFilterChange("dobavljac", option.value)
                      }
                    >
                      {option.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className={styles.filterDropdown}>
              <label>Datum</label>
              <button onClick={() => toggleDropdown("datum")}>
                <span>{getSelectedLabel("datumi", filters.datum)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.datum && (
                <div className={styles.dropdownMenu}>
                  {filterOptions.datumi.map((option) => (
                    <div
                      key={option.value}
                      className={styles.dropdownItem}
                      onClick={() => handleFilterChange("datum", option.value)}
                    >
                      {option.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className={styles.searchAndFilters}>
            <div className={styles.searchBox}>
              <input
                type="text"
                placeholder="Pretraži fakture..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />
              <button onClick={handleSearch}>
                <FaSearch />
              </button>
            </div>

            {activeSearch && (
              <div className={styles.activeFilters}>
                <div className={styles.filterChip}>
                  <span>Pretraga: "{activeSearch}"</span>
                  <FaTimes className={styles.removeChipIcon} onClick={clearSearch} />
                </div>
              </div>
            )}
          </div>
        </section>

        <section className={styles.tableSection}>
          <div className={styles.tableContainer}>
            <div className={styles.tableTitleHeader}>
              <h2>Lista faktura ({pagination.count} ukupno)</h2>
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
                  Iznos
                </div>
                <div className={styles.tableCol} style={{ width: "20%" }}>
                  Datum prijema
                </div>
                <div className={styles.tableCol} style={{ width: "20%" }}>
                  Rok plaćanja
                </div>
                <div className={`${styles.tableCol} ${styles.statusCol}`} style={{ width: "22%" }}>
                  Status
                </div>
              </div>
              <div className={styles.tableBody}>
                {loading ? (
                  <div className={styles.loadingMessage}>Učitavanje faktura...</div>
                ) : invoices.length === 0 ? (
                  <div className={styles.noDataMessage}>Nema faktura za prikaz</div>
                ) : (
                  invoices.map((invoice, index) => (
                    <div
                      key={invoice.sifra_f}
                      className={`${styles.tableRow} ${
                        index % 2 === 0 ? styles.rowEven : styles.rowOdd
                      } ${styles.clickableRow}`}
                      onClick={() => handleInvoiceClick(invoice.sifra_f)}
                    >
                      <div className={styles.tableCol} style={{ width: "12%" }}>
                        {invoice.sifra_f}
                      </div>
                      <div className={styles.tableCol} style={{ width: "12%" }}>
                        {invoice.dobavljac_naziv}
                      </div>
                      <div className={styles.tableCol} style={{ width: "14%" }}>
                        {formatAmount(invoice.iznos_f)}
                      </div>
                      <div className={styles.tableCol} style={{ width: "20%" }}>
                        {formatDate(invoice.datum_prijema_f)}
                      </div>
                      <div className={styles.tableCol} style={{ width: "20%" }}>
                        {formatDate(invoice.rok_placanja_f)}
                      </div>
                      <div
                        className={`${styles.tableCol} ${styles.statusCol}`}
                        style={{ width: "22%" }}
                      >
                        <span
                          className={`${styles.statusBadge} ${styles[getStatusClassName(
                            invoice.status_display
                          )]}`}
                        >
                          {invoice.status_display}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Paginacija */}
            {!loading && invoices.length > 0 && pagination.num_pages > 1 && (
              <div className={styles.pagination}>
                <button
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      current_page: prev.current_page - 1,
                    }))
                  }
                  disabled={!pagination.has_previous}
                  className={styles.paginationBtn}
                >
                  Prethodna
                </button>
                <span className={styles.paginationInfo}>
                  Stranica {pagination.current_page} od {pagination.num_pages}
                </span>
                <button
                  onClick={() =>
                    setPagination((prev) => ({
                      ...prev,
                      current_page: prev.current_page + 1,
                    }))
                  }
                  disabled={!pagination.has_next}
                  className={styles.paginationBtn}
                >
                  Sledeća
                </button>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Invoice;
