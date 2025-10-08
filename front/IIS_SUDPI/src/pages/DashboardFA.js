import React, { useState, useEffect } from "react";
import styles from "../styles/DashboardFA.module.css";
import MainSideBar from "../components/MainSideBar";
import { dashboardAPI } from "../api";

const DashboardFA = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    pregled_finansija: {
      ukupno_placeno: 0,
      na_cekanju: 0,
      prosecno_vreme_placanja: 0,
    },
    profitabilnost_dobavljaca: [],
    nadolazece_isplate: [],
    vizualizacija_troskova: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getFinansijskiAnalitičarData();
        setDashboardData(response.data);
        setError(null);
      } catch (error) {
        console.error("Greška pri dohvatanju dashboard podataka:", error);
        setError("Greška pri učitavanju podataka. Molimo pokušajte ponovo.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div
      className={`${styles.dashboardFaWrapper} ${
        isSidebarCollapsed ? styles.sidebarCollapsed : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className={styles.dashboardFaMainContent}>
        <header className={styles.dashboardHeader}>
          <h1>Kontrolna tabla - Finansijski analitičar</h1>
        </header>

        {loading && (
          <div className={styles.loadingMessage}>Učitavanje podataka...</div>
        )}

        {error && <div className={styles.errorMessage}>{error}</div>}

        {!loading && !error && (
          <div className={styles.dashboardContent}>
            <div className={styles.dashboardGrid}>
              {/* Card 1: Pregled finansija */}
              <div className={styles.dashboardCard}>
                <div className={styles.cardHeader}>
                  <h3>Pregled finansija</h3>
                </div>
                <div className={styles.cardContent}>
                  <div className={styles.financeOverviewItem}>
                    <span>Ukupno plaćeno:</span>
                    <strong>
                      {dashboardData.pregled_finansija.ukupno_placeno?.toLocaleString(
                        "sr-Latn-RS"
                      )}{" "}
                      RSD
                    </strong>
                  </div>
                  <div className={styles.financeOverviewItem}>
                    <span>Na čekanju:</span>
                    <strong>
                      {dashboardData.pregled_finansija.na_cekanju?.toLocaleString(
                        "sr-Latn-RS"
                      )}{" "}
                      RSD
                    </strong>
                  </div>
                  <div className={styles.financeOverviewItem}>
                    <span>Prosečno vreme plaćanja:</span>
                    <strong>
                      {dashboardData.pregled_finansija.prosecno_vreme_placanja}d
                    </strong>
                  </div>
                </div>
              </div>

              {/* Card 2: Profitabilnost dobavljača */}
              <div className={styles.dashboardCard}>
                <div className={styles.cardHeader}>
                  <h3>Profitabilnost dobavljača</h3>
                </div>
                <div className={styles.cardContent}>
                  {dashboardData.profitabilnost_dobavljaca.length > 0 ? (
                    dashboardData.profitabilnost_dobavljaca.map(
                      (supplier, index) => (
                        <div key={index} className={styles.supplierItem}>
                          <span>{supplier.name}</span>
                          <span>{supplier.profitability}</span>
                        </div>
                      )
                    )
                  ) : (
                    <div className={styles.noData}>Nema podataka o dobavljačima</div>
                  )}
                </div>
              </div>

              {/* Card 3: Nadolazeće isplate */}
              <div className={styles.dashboardCard}>
                <div className={styles.cardHeader}>
                  <h3>Nadolazeće isplate</h3>
                </div>
                <div className={styles.cardContent}>
                  <div className={styles.upcomingPaymentsTable}>
                    <div className={styles.tableHeaderRow}>
                      <div className={`${styles.tableCol} ${styles.idCol}`}>ID</div>
                      <div className={`${styles.tableCol} ${styles.supplierCol}`}>Dobavljač</div>
                      <div className={`${styles.tableCol} ${styles.amountCol}`}>Iznos</div>
                    </div>
                    {dashboardData.nadolazece_isplate.length > 0 ? (
                      dashboardData.nadolazece_isplate.map((payment) => (
                        <div key={payment.id} className={styles.tableRow}>
                          <div className={`${styles.tableCol} ${styles.idCol}`}>{payment.id}</div>
                          <div className={`${styles.tableCol} ${styles.supplierCol}`}>
                            {payment.supplier}
                          </div>
                          <div className={`${styles.tableCol} ${styles.amountCol}`}>
                            {parseFloat(payment.amount).toLocaleString(
                              "sr-Latn-RS"
                            )}{" "}
                            RSD
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className={styles.noData}>Nema nadolazećih isplata</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Card 4: Vizualizacija troškova */}
              <div className={styles.dashboardCard}>
                <div className={styles.cardHeader}>
                  <h3>Vizualizacija troškova (poslednih 6 meseci)</h3>
                </div>
                <div className={styles.cardContent}>
                  <div className={styles.chartPlaceholder}>
                    {dashboardData.vizualizacija_troskova.length > 0 ? (
                      <div className={styles.chartData}>
                        {dashboardData.vizualizacija_troskova.map(
                          (item, index) => (
                            <div key={index} className={styles.chartItem}>
                              <div className={styles.chartMonth}>{item.mesec}</div>
                              <div
                                className={styles.chartBar}
                                style={{
                                  height: `${Math.max(
                                    10,
                                    (item.iznos /
                                      Math.max(
                                        ...dashboardData.vizualizacija_troskova.map(
                                          (i) => i.iznos
                                        )
                                      )) *
                                      100 || 10
                                  )}px`,
                                  backgroundColor: "#3b82f6",
                                }}
                              ></div>
                              <div className={styles.chartAmount}>
                                {item.iznos.toLocaleString("sr-Latn-RS")} RSD
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    ) : (
                      <div className={styles.noData}>Nema podataka o troškovima</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardFA;
