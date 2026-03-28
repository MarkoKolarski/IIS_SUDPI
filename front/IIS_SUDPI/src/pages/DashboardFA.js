import React, { useState, useEffect } from "react";
import styles from "../styles/DashboardFA.module.css";
import MainSideBar from "../components/MainSideBar";
import { dashboardAPI } from "../api";
import PageTransition from "../components/PageTransition";

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
  const [chartTransitionDirection, setChartTransitionDirection] = useState("older");
  const [expandedCard, setExpandedCard] = useState(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const fetchChartWindow = async (nextOffset, direction = "older") => {
    try {
      setChartTransitionDirection(direction);
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
    fetchChartWindow(chartOffset + 1, "older");
  };

  const handleNewerMonths = () => {
    if (chartLoading || chartOffset === 0) return;
    fetchChartWindow(chartOffset - 1, "newer");
  };

  const toggleCardExpansion = (cardKey) => {
    setExpandedCard((prev) => (prev === cardKey ? null : cardKey));
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

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        setExpandedCard(null);
      }
    };

    if (expandedCard) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", onKeyDown);
    }

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [expandedCard]);

  const chartMaxValue = Math.max(
    1,
    ...dashboardData.vizualizacija_troskova.map((item) => item.iznos || 0)
  );

  const chartDataKey = `${dashboardData.chart_window?.offset ?? 0}-${dashboardData.chart_window?.window_start || ""}-${dashboardData.chart_window?.window_end || ""}`;

  const chartDataMotionClass =
    chartTransitionDirection === "newer"
      ? styles.chartDataEnterFromNewer
      : styles.chartDataEnterFromOlder;

  const getProfitabilityValue = (value) => {
    const parsed = Number(String(value || "0").replace("%", ""));
    if (Number.isNaN(parsed)) return 0;
    return Math.max(0, Math.min(100, parsed));
  };

  return (
    <PageTransition>
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
            {expandedCard && (
              <button
                type="button"
                className={styles.expandedOverlay}
                aria-label="Zatvori fokus prikaz"
                onClick={() => setExpandedCard(null)}
              />
            )}
            <div
              className={`${styles.dashboardGrid} ${
                expandedCard ? styles.dashboardGridHasExpanded : ""
              }`}
            >
              {/* Card 1: Pregled finansija */}
              <div
                className={`${styles.dashboardCard} ${
                  expandedCard === "overview" ? styles.expandedCard : ""
                } ${
                  expandedCard === "overview" ? styles.expandedOverviewCard : ""
                }`}
              >
                <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                  <h3>Pregled finansija</h3>
                  <button
                    type="button"
                    className={styles.cardExpandButton}
                    onClick={() => toggleCardExpansion("overview")}
                    aria-label={
                      expandedCard === "overview"
                        ? "Smanji pregled finansija"
                        : "Proširi pregled finansija"
                    }
                    title={expandedCard === "overview" ? "Smanji" : "Proširi"}
                  >
                    {expandedCard === "overview" ? "✕" : "⤢"}
                  </button>
                </div>
                <div
                  className={`${styles.cardContent} ${
                    expandedCard === "overview" ? styles.expandedOverviewContent : ""
                  }`}
                >
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
              <div
                className={`${styles.dashboardCard} ${
                  expandedCard === "profitability" ? styles.expandedCard : ""
                } ${
                  expandedCard === "profitability"
                    ? styles.expandedProfitabilityCard
                    : ""
                }`}
              >
                <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                  <h3>Profitabilnost dobavljača</h3>
                  <button
                    type="button"
                    className={styles.cardExpandButton}
                    onClick={() => toggleCardExpansion("profitability")}
                    aria-label={
                      expandedCard === "profitability"
                        ? "Smanji profitabilnost dobavljača"
                        : "Proširi profitabilnost dobavljača"
                    }
                    title={expandedCard === "profitability" ? "Smanji" : "Proširi"}
                  >
                    {expandedCard === "profitability" ? "✕" : "⤢"}
                  </button>
                </div>
                <div
                  className={`${styles.cardContent} ${
                    expandedCard === "profitability"
                      ? styles.expandedProfitabilityContent
                      : ""
                  }`}
                >
                  {dashboardData.profitabilnost_dobavljaca.length > 0 ? (
                    <div
                      className={`${styles.scrollablePanel} ${
                        expandedCard === "profitability"
                          ? styles.expandedProfitabilityScroll
                          : ""
                      }`}
                      role="region"
                      aria-label="Lista profitabilnosti dobavljača"
                      tabIndex={0}
                    >
                      {dashboardData.profitabilnost_dobavljaca.map(
                        (supplier, index) => (
                          <div key={index} className={styles.supplierItem}>
                            <span className={styles.supplierName}>{supplier.name}</span>
                            <div className={styles.supplierMetricWrap}>
                              <span>{supplier.profitability}</span>
                              {expandedCard === "profitability" && (
                                <div className={styles.supplierProgressTrack}>
                                  <div
                                    className={styles.supplierProgressFill}
                                    style={{
                                      width: `${getProfitabilityValue(
                                        supplier.profitability
                                      )}%`,
                                    }}
                                  />
                                </div>
                              )}
                            </div>
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
              <div
                className={`${styles.dashboardCard} ${
                  expandedCard === "payments" ? styles.expandedCard : ""
                } ${
                  expandedCard === "payments" ? styles.expandedPaymentsCard : ""
                }`}
              >
                <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                  <h3>Nadolazeće isplate</h3>
                  <button
                    type="button"
                    className={styles.cardExpandButton}
                    onClick={() => toggleCardExpansion("payments")}
                    aria-label={
                      expandedCard === "payments"
                        ? "Smanji nadolazeće isplate"
                        : "Proširi nadolazeće isplate"
                    }
                    title={expandedCard === "payments" ? "Smanji" : "Proširi"}
                  >
                    {expandedCard === "payments" ? "✕" : "⤢"}
                  </button>
                </div>
                <div
                  className={`${styles.cardContent} ${
                    expandedCard === "payments" ? styles.expandedPaymentsContent : ""
                  }`}
                >
                  <div className={styles.upcomingPaymentsTable}>
                    {dashboardData.nadolazece_isplate.length > 0 ? (
                      <div
                        className={`${styles.scrollablePanel} ${
                          expandedCard === "payments"
                            ? styles.expandedPaymentsScroll
                            : ""
                        }`}
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
              <div
                className={`${styles.dashboardCard} ${
                  expandedCard === "chart" ? styles.expandedCard : ""
                } ${
                  expandedCard === "chart" ? styles.expandedChartCard : ""
                }`}
              >
                <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                  <h3>Vizualizacija troškova</h3>
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
                    <button
                      type="button"
                      className={styles.cardExpandButton}
                      onClick={() => toggleCardExpansion("chart")}
                      aria-label={
                        expandedCard === "chart"
                          ? "Smanji vizualizaciju troškova"
                          : "Proširi vizualizaciju troškova"
                      }
                      title={expandedCard === "chart" ? "Smanji" : "Proširi"}
                    >
                      {expandedCard === "chart" ? "✕" : "⤢"}
                    </button>
                  </div>
                </div>
                <div
                  className={`${styles.cardContent} ${styles.chartCardContent} ${
                    expandedCard === "chart" ? styles.expandedChartContent : ""
                  }`}
                >
                  <div
                    className={`${styles.chartPlaceholder} ${
                      expandedCard === "chart" ? styles.expandedChartPlaceholder : ""
                    } ${chartLoading ? styles.chartPlaceholderLoading : ""}`}
                    aria-busy={chartLoading}
                  >
                    {chartLoading && (
                      <div
                        className={`${styles.chartLoadingOverlay} ${
                          chartTransitionDirection === "newer"
                            ? styles.chartLoadingOverlayFromNewer
                            : styles.chartLoadingOverlayFromOlder
                        }`}
                        aria-hidden="true"
                      >
                        <div className={styles.chartLoadingPanel}>
                          <div className={styles.chartLoadingHeader}>
                            <span className={styles.chartLoadingSpinner} />
                            <div>
                              <div className={styles.chartLoadingTitle}>
                                Prebacivanje perioda
                              </div>
                              <div className={styles.chartLoadingSubtitle}>
                                Učitavam novi period sa servera
                              </div>
                            </div>
                          </div>
                          <div className={styles.chartLoadingBars}>
                            {[28, 52, 36, 68, 44, 60].map((height, index) => (
                              <div
                                key={index}
                                className={styles.chartLoadingSkeletonBar}
                                style={{ height: `${height}%` }}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                    {chartError ? (
                      <div className={styles.chartError}>{chartError}</div>
                    ) : dashboardData.vizualizacija_troskova.length > 0 ? (
                      <div
                        key={chartDataKey}
                        className={`${styles.chartData} ${
                          expandedCard === "chart" ? styles.expandedChartData : ""
                        } ${chartLoading ? styles.chartDataDimmed : ""} ${chartDataMotionClass}`}
                      >
                        {dashboardData.vizualizacija_troskova.map(
                          (item, index) => (
                            <div
                              key={index}
                              className={styles.chartItem}
                              style={{ "--item-index": index }}
                            >
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
    </PageTransition>
  );
};

export default DashboardFA;
