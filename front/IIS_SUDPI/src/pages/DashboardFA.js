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
      broj_faktura_na_cekanju: 0,
      udeo_na_cekanju: 0,
    },
    profitabilnost_dobavljaca: [],
    nadolazece_isplate: [],
    vizualizacija_troskova: [],
    chart_window: {
      offset: 0,
      window_start: "",
      window_end: "",
    },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartOffset, setChartOffset] = useState(0);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const fetchChartWindow = async (nextOffset) => {
    try {
      setChartLoading(true);
      setChartError(null);

      const response = await dashboardAPI.getFinansijskiAnaliticarCostsTrend(
        nextOffset,
        6
      );

      setDashboardData((prev) => ({
        ...prev,
        vizualizacija_troskova: response.data.vizualizacija_troskova || [],
        chart_window: {
          offset: response.data.offset ?? nextOffset,
          window_start: response.data.window_start || "",
          window_end: response.data.window_end || "",
        },
      }));
      setChartOffset(response.data.offset ?? nextOffset);
    } catch (chartFetchError) {
      console.error("Greška pri dohvatanju podataka za grafikon:", chartFetchError);
      setChartError("Neuspešno učitavanje grafikona. Pokušajte ponovo.");
    } finally {
      setChartLoading(false);
    }
  };

  const handleOlderMonths = () => {
    if (chartLoading) return;
    fetchChartWindow(chartOffset + 1);
  };

  const handleNewerMonths = () => {
    if (chartLoading || chartOffset === 0) return;
    fetchChartWindow(chartOffset - 1);
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getFinansijskiAnalitičarData();
        setDashboardData(response.data);
        setChartOffset(response.data?.chart_window?.offset || 0);
        setChartError(null);
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

  const chartMaxValue = Math.max(
    1,
    ...dashboardData.vizualizacija_troskova.map((item) => item.iznos || 0)
  );

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
                  <div className={styles.financeOverviewItem}>
                    <span>Broj faktura na čekanju:</span>
                    <strong>
                      {dashboardData.pregled_finansija.broj_faktura_na_cekanju}
                    </strong>
                  </div>
                  <div className={styles.financeOverviewItem}>
                    <span>Udeo sredstava na čekanju:</span>
                    <strong>
                      {Number(
                        dashboardData.pregled_finansija.udeo_na_cekanju || 0
                      ).toLocaleString("sr-Latn-RS", {
                        minimumFractionDigits: 1,
                        maximumFractionDigits: 1,
                      })}
                      %
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
                    <div
                      className={styles.scrollablePanel}
                      role="region"
                      aria-label="Lista profitabilnosti dobavljača"
                      tabIndex={0}
                    >
                      {dashboardData.profitabilnost_dobavljaca.map(
                        (supplier, index) => (
                          <div key={index} className={styles.supplierItem}>
                            <span>{supplier.name}</span>
                            <span>{supplier.profitability}</span>
                          </div>
                        )
                      )}
                    </div>
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
                    {dashboardData.nadolazece_isplate.length > 0 ? (
                      <div
                        className={styles.scrollablePanel}
                        role="region"
                        aria-label="Tabela nadolazećih isplata"
                        tabIndex={0}
                      >
                        {dashboardData.nadolazece_isplate.map((payment) => (
                          <div key={payment.id} className={styles.tableRow}>
                            <div className={`${styles.tableCol} ${styles.supplierCol}`}>
                              {payment.supplier}
                            </div>
                            <div className={`${styles.tableCol} ${styles.amountCol}`}>
                              {Number(payment.amount || 0).toLocaleString(
                                "sr-Latn-RS"
                              )}{" "}
                              RSD
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className={styles.noData}>Nema nadolazećih isplata</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Card 4: Vizualizacija troškova */}
              <div className={styles.dashboardCard}>
                <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                  <h3>Vizualizacija troškova (poslednih 6 meseci)</h3>
                  <div className={styles.chartControls}>
                    <button
                      type="button"
                      className={styles.chartNavButton}
                      onClick={handleOlderMonths}
                      disabled={chartLoading}
                      aria-label="Prikaži starijih 6 meseci"
                      title="Prikaži starijih 6 meseci"
                    >
                      ←
                    </button>
                    <button
                      type="button"
                      className={styles.chartNavButton}
                      onClick={handleNewerMonths}
                      disabled={chartLoading || chartOffset === 0}
                      aria-label="Prikaži novijih 6 meseci"
                      title="Prikaži novijih 6 meseci"
                    >
                      →
                    </button>
                  </div>
                </div>
                <div className={`${styles.cardContent} ${styles.chartCardContent}`}>
                  <div className={styles.chartPlaceholder}>
                    {chartLoading ? (
                      <div className={styles.chartInfo}>Učitavanje grafikona...</div>
                    ) : chartError ? (
                      <div className={styles.chartError}>{chartError}</div>
                    ) : dashboardData.vizualizacija_troskova.length > 0 ? (
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
                                    (item.iznos / chartMaxValue) *
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
                  <div className={styles.chartWindowLabel}>
                    Period: {dashboardData.chart_window?.window_start || "-"} -{" "}
                    {dashboardData.chart_window?.window_end || "-"}
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
