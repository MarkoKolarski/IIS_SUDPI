import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import PaymentSimulationModal from "../components/PaymentSimulationModal";
import styles from "../styles/InvoiceDetails.module.css";
import { useParams, useNavigate } from "react-router-dom";
import axiosInstance from "../axiosInstance";

const InvoiceDetails = () => {
  const { invoiceId } = useParams();
  const navigate = useNavigate();
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [expandedCard, setExpandedCard] = useState(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const openPaymentSimulation = () => {
    setIsPaymentModalOpen(true);
  };

  const loadInvoiceDetails = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(`/invoices/${invoiceId}/`);
      setInvoice(response.data);
    } catch (error) {
      console.error("Greška pri učitavanju detalja fakture:", error);
      if (error.response?.status === 404) {
        navigate("/invoice");
      }
    } finally {
      setLoading(false);
    }
  }, [invoiceId, navigate]);

  const closePaymentSimulation = () => {
    setIsPaymentModalOpen(false);
    loadInvoiceDetails();
  };

  const handleInvoiceAction = async (action, reason = "") => {
    setActionLoading(true);
    try {
      const response = await axiosInstance.post(`/invoices/${invoiceId}/action/`, {
        action,
        reason,
      });

      await loadInvoiceDetails();
      alert(response.data.message);
    } catch (error) {
      console.error("Greška pri izvršavanju akcije:", error);
      alert("Greška pri izvršavanju akcije. Pokušajte ponovo.");
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("sr-RS");
  };

  const formatAmount = (amount) => {
    return `${parseFloat(amount).toFixed(2)} RSD`;
  };

  useEffect(() => {
    loadInvoiceDetails();
  }, [loadInvoiceDetails]);

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

  const hasProcessSteps =
    Array.isArray(invoice?.process_steps) && invoice.process_steps.length > 0;
  const hasItems = Array.isArray(invoice?.stavke) && invoice.stavke.length > 0;
  const canApproveReject =
    invoice?.status_f === "primljena" || invoice?.status_f === "verifikovana";
  const hasTransaction = Boolean(invoice?.transakcija);

  const handleRejectAction = () => {
    const reason = prompt("Unesite razlog odbacivanja:");
    if (reason) {
      handleInvoiceAction("reject", reason);
    }
  };

  if (loading) {
    return (
      <div
        className={`${styles.invoiceDetailsWrapper} ${
          isSidebarCollapsed ? styles.sidebarCollapsed : ""
        }`}
      >
        <MainSideBar
          isCollapsed={isSidebarCollapsed}
          toggleSidebar={toggleSidebar}
        />
        <main className={styles.invoiceDetailsMain}>
          <div className={styles.loadingMessage}>Učitavanje detalja fakture...</div>
        </main>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div
        className={`${styles.invoiceDetailsWrapper} ${
          isSidebarCollapsed ? styles.sidebarCollapsed : ""
        }`}
      >
        <MainSideBar
          isCollapsed={isSidebarCollapsed}
          toggleSidebar={toggleSidebar}
        />
        <main className={styles.invoiceDetailsMain}>
          <div className={styles.errorMessage}>Faktura nije pronađena.</div>
        </main>
      </div>
    );
  }

  return (
    <div
      className={`${styles.invoiceDetailsWrapper} ${
        isSidebarCollapsed ? styles.sidebarCollapsed : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className={styles.invoiceDetailsMain}>
        <header className={styles.invoiceDetailsHeader}>
          <h1>Detalji fakture</h1>
        </header>

        <div className={styles.invoiceDetailsContent}>
          {expandedCard && (
            <button
              type="button"
              className={styles.expandedOverlay}
              aria-label="Zatvori fokus prikaz"
              onClick={() => setExpandedCard(null)}
            />
          )}

          <section className={styles.invoiceSummaryCard}>
            <div className={styles.invoiceSummaryHeader}>
              <h2>Faktura ID: {invoice.sifra_f}</h2>
            </div>
            <div className={`${styles.invoiceSummaryRow} ${styles.rowLight}`}>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Dobavljač:</span>
                <span className={styles.summaryValue}>{invoice.dobavljac_naziv}</span>
              </div>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Iznos:</span>
                <span className={styles.summaryValue}>{formatAmount(invoice.iznos_f)}</span>
              </div>
            </div>
            <div className={`${styles.invoiceSummaryRow} ${styles.rowMedium}`}>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Datum prijema:</span>
                <span className={styles.summaryValue}>
                  {formatDate(invoice.datum_prijema_f)}
                </span>
              </div>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Rok plaćanja:</span>
                <span className={styles.summaryValue}>
                  {formatDate(invoice.rok_placanja_f)}
                </span>
              </div>
            </div>
            <div className={`${styles.invoiceSummaryRow} ${styles.rowLight}`}>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Status:</span>
                <span className={styles.summaryValue}>{invoice.status_display}</span>
              </div>
              <div className={styles.summaryCol}>
                <span className={styles.summaryLabel}>Ugovor ID:</span>
                <span className={styles.summaryValue}>
                  {invoice.ugovor?.sifra_u || "Nema ugovora"}
                </span>
              </div>
            </div>
          </section>

          <section className={styles.processFlow}>
            <div className={styles.processFlowHeader}>
              <h3>Vizuelni tok procesa</h3>
            </div>
            <div className={styles.processFlowBody}>
              {hasProcessSteps ? (
                invoice.process_steps.map((step, index) => (
                  <React.Fragment key={step.number}>
                    <div className={`${styles.processStep} ${styles[step.status]}`}>
                      <div className={styles.stepCircle}>{step.number}</div>
                      <span className={styles.stepLabel}>{step.label}</span>
                    </div>
                    {index < invoice.process_steps.length - 1 && (
                      <div className={styles.stepConnector} aria-hidden="true" />
                    )}
                  </React.Fragment>
                ))
              ) : (
                <div className={styles.noData}>Nema podataka o koracima procesa</div>
              )}
            </div>
          </section>

          <section className={styles.bottomCards}>
            <div
              className={`${styles.itemsCard} ${
                expandedCard === "items" ? styles.expandedCard : ""
              } ${expandedCard === "items" ? styles.expandedItemsCard : ""}`}
            >
              <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                <h3>Stavke fakture</h3>
                <button
                  type="button"
                  className={styles.cardExpandButton}
                  onClick={() =>
                    setExpandedCard((prev) => (prev === "items" ? null : "items"))
                  }
                  aria-label={
                    expandedCard === "items"
                      ? "Smanji stavke fakture"
                      : "Proširi stavke fakture"
                  }
                  title={expandedCard === "items" ? "Smanji" : "Proširi"}
                >
                  {expandedCard === "items" ? "✕" : "⤢"}
                </button>
              </div>
              <div className={styles.cardBody}>
                <div
                  className={`${styles.scrollablePanel} ${
                    expandedCard === "items" ? styles.expandedScrollablePanel : ""
                  }`}
                  role="region"
                  aria-label="Lista stavki fakture"
                  tabIndex={0}
                >
                  {hasItems ? (
                    invoice.stavke.map((stavka) => (
                      <div key={stavka.sifra_sf} className={styles.invoiceItem}>
                        <div className={styles.invoiceItemHeader}>
                          <p className={styles.invoiceItemTitle}>{stavka.naziv_sf}</p>
                          <span className={styles.invoiceItemPrice}>
                            {formatAmount(
                              Number(stavka.kolicina_sf) * Number(stavka.cena_po_jed)
                            )}
                          </span>
                        </div>
                        <div className={styles.invoiceItemMeta}>
                          <div>
                            <span className={styles.invoiceItemMetaLabel}>Količina</span>
                            <span className={styles.invoiceItemMetaValue}>
                              {stavka.kolicina_sf}
                            </span>
                          </div>
                          <div>
                            <span className={styles.invoiceItemMetaLabel}>
                              Cena po jedinici
                            </span>
                            <span className={styles.invoiceItemMetaValue}>
                              {formatAmount(stavka.cena_po_jed)}
                            </span>
                          </div>
                        </div>
                        {stavka.opis_sf && (
                          <p className={styles.invoiceItemDescription}>{stavka.opis_sf}</p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className={styles.noData}>Nema stavki fakture</div>
                  )}
                </div>
              </div>
            </div>

            <div
              className={`${styles.discrepancyCard} ${
                expandedCard === "reason" ? styles.expandedCard : ""
              } ${expandedCard === "reason" ? styles.expandedReasonCard : ""}`}
            >
              <div className={`${styles.cardHeader} ${styles.cardHeaderWithControls}`}>
                <h3>Razlog čekanja</h3>
                <button
                  type="button"
                  className={styles.cardExpandButton}
                  onClick={() =>
                    setExpandedCard((prev) => (prev === "reason" ? null : "reason"))
                  }
                  aria-label={
                    expandedCard === "reason"
                      ? "Smanji razlog čekanja"
                      : "Proširi razlog čekanja"
                  }
                  title={expandedCard === "reason" ? "Smanji" : "Proširi"}
                >
                  {expandedCard === "reason" ? "✕" : "⤢"}
                </button>
              </div>
              <div className={styles.cardBody}>
                <div
                  className={`${styles.scrollablePanel} ${
                    expandedCard === "reason" ? styles.expandedScrollablePanel : ""
                  }`}
                  role="region"
                  aria-label="Razlog čekanja fakture"
                  tabIndex={0}
                >
                  <div className={styles.reasonContent}>
                    {invoice.razlog_cekanja_f ? (
                      <p className={styles.reasonText}>{invoice.razlog_cekanja_f}</p>
                    ) : (
                      <div className={styles.noData}>Nema razloga čekanja za ovu fakturu</div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.transactionCard}>
              <div className={styles.cardHeader}>
                <h3>Transakcija</h3>
              </div>
              <div className={styles.cardBody}>
                {hasTransaction ? (
                  <div className={styles.transactionGrid}>
                    <div className={styles.transactionField}>
                      <span className={styles.transactionLabel}>ID transakcije</span>
                      <span className={styles.transactionValue}>{invoice.transakcija.sifra_t}</span>
                    </div>
                    <div className={styles.transactionField}>
                      <span className={styles.transactionLabel}>Datum</span>
                      <span className={styles.transactionValue}>
                        {formatDate(invoice.transakcija.datum_t)}
                      </span>
                    </div>
                    <div className={styles.transactionField}>
                      <span className={styles.transactionLabel}>Potvrda</span>
                      <span className={styles.transactionValue}>{invoice.transakcija.potvrda_t}</span>
                    </div>
                    <div className={styles.transactionField}>
                      <span className={styles.transactionLabel}>Status</span>
                      <span className={styles.transactionValue}>{invoice.transakcija.status_t}</span>
                    </div>
                  </div>
                ) : (
                  <div className={styles.noData}>Nema transakcije za ovu fakturu</div>
                )}
              </div>
            </div>

            <div className={styles.notificationCard}>
              <div className={styles.cardHeader}>
                <h3>Akcije</h3>
              </div>
              <div className={styles.cardBody}>
                {canApproveReject ? (
                  <>
                    <p className={styles.notificationQuestion}>
                      {invoice.status_f === "primljena"
                        ? "Da li želite da verifikujete fakturu?"
                        : "Da li želite da izvršite plaćanje (simulacija)?"}
                    </p>
                    <div className={styles.notificationActions}>
                      {invoice.status_f === "primljena" ? (
                        <button
                          className={`${styles.notificationBtn} ${styles.confirm}`}
                          onClick={() => handleInvoiceAction("approve")}
                          disabled={actionLoading}
                        >
                          {actionLoading ? "Procesiranje..." : "Verifikuj"}
                        </button>
                      ) : (
                        <button
                          className={`${styles.notificationBtn} ${styles.confirm}`}
                          onClick={openPaymentSimulation}
                          disabled={actionLoading}
                        >
                          Izvrši plaćanje
                        </button>
                      )}
                      <button
                        className={`${styles.notificationBtn} ${styles.decline}`}
                        onClick={handleRejectAction}
                        disabled={actionLoading}
                      >
                        Odbaci
                      </button>
                    </div>
                  </>
                ) : (
                  <div className={styles.noData}>Za trenutni status nema dostupnih akcija</div>
                )}
              </div>
            </div>
          </section>

          <div className={styles.actionButtons}>
            <button className={styles.backBtn} onClick={() => navigate("/invoice")}>
              ← Nazad na listu faktura
            </button>
          </div>
        </div>
      </main>

      <PaymentSimulationModal
        isOpen={isPaymentModalOpen}
        onClose={closePaymentSimulation}
        invoiceId={invoiceId}
      />
    </div>
  );
};

export default InvoiceDetails;
