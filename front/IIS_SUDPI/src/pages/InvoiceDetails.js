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

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const openPaymentSimulation = () => {
    setIsPaymentModalOpen(true);
  };

  const closePaymentSimulation = () => {
    setIsPaymentModalOpen(false);
    // Osveži podatke fakture nakon zatvaranja simulacije
    loadInvoiceDetails();
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

  const handleInvoiceAction = async (action, reason = "") => {
    setActionLoading(true);
    try {
      const response = await axiosInstance.post(
        `/invoices/${invoiceId}/action/`,
        {
          action: action,
          reason: reason,
        }
      );

      // Refresh invoice data after action
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
                <span className={styles.summaryValue}>
                  {formatAmount(invoice.iznos_f)}
                </span>
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
              {invoice.ugovor && (
                <div className={styles.summaryCol}>
                  <span className={styles.summaryLabel}>Ugovor ID:</span>
                  <span className={styles.summaryValue}>
                    {invoice.ugovor.sifra_u}
                  </span>
                </div>
              )}
            </div>
          </section>

          <section className={styles.processFlow}>
            <div className={styles.processFlowHeader}>
              <h3>Vizuelni tok procesa</h3>
            </div>
            <div className={styles.processFlowBody}>
              {invoice.process_steps &&
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
                ))}
            </div>
          </section>

          <section className={styles.bottomCards}>
            {invoice.razlog_cekanja_f && (
              <div className={styles.discrepancyCard}>
                <div className={styles.cardHeader}>
                  <h3>Razlog čekanja</h3>
                </div>
                <div className={styles.cardBody}>
                  <p>
                    <strong>Razlog:</strong> {invoice.razlog_cekanja_f}
                  </p>
                </div>
              </div>
            )}

            {invoice.stavke && invoice.stavke.length > 0 && (
              <div className={styles.itemsCard}>
                <div className={styles.cardHeader}>
                  <h3>Stavke fakture</h3>
                </div>
                <div className={styles.cardBody}>
                  {invoice.stavke.map((stavka) => (
                    <div key={stavka.sifra_sf} className={styles.invoiceItem}>
                      <p>
                        <strong>{stavka.naziv_sf}</strong>
                      </p>
                      <p>
                        Količina: {stavka.kolicina_sf} | Cena po jedinici:{" "}
                        {formatAmount(stavka.cena_po_jed)}
                      </p>
                      {stavka.opis_sf && <p>Opis: {stavka.opis_sf}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(invoice.status_f === "primljena" ||
              invoice.status_f === "verifikovana") && (
              <div className={styles.notificationCard}>
                <div className={styles.cardHeader}>
                  <h3>Akcije</h3>
                </div>
                <div className={styles.cardBody}>
                  <p className={styles.notificationQuestion}>
                    {invoice.status_f === "primljena"
                      ? "Da li želite da verifikujete fakturu?"
                      : "Da li želite da odobrite isplatu?"}
                  </p>
                  <div className={styles.notificationActions}>
                    <button
                      className={`${styles.notificationBtn} ${styles.confirm}`}
                      onClick={() => handleInvoiceAction("approve")}
                      disabled={actionLoading}
                    >
                      {actionLoading ? "Procesiranje..." : "Odobri"}
                    </button>
                    <button
                      className={`${styles.notificationBtn} ${styles.decline}`}
                      onClick={() => {
                        const reason = prompt("Unesite razlog odbacivanja:");
                        if (reason) handleInvoiceAction("reject", reason);
                      }}
                      disabled={actionLoading}
                    >
                      Odbaci
                    </button>
                  </div>
                </div>
              </div>
            )}

            {invoice.transakcija && (
              <div className={styles.transactionCard}>
                <div className={styles.cardHeader}>
                  <h3>Transakcija</h3>
                </div>
                <div className={styles.cardBody}>
                  <p>
                    <strong>ID transakcije:</strong>{" "}
                    {invoice.transakcija.sifra_t}
                  </p>
                  <p>
                    <strong>Datum:</strong>{" "}
                    {formatDate(invoice.transakcija.datum_t)}
                  </p>
                  <p>
                    <strong>Potvrda:</strong> {invoice.transakcija.potvrda_t}
                  </p>
                  <p>
                    <strong>Status:</strong> {invoice.transakcija.status_t}
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>

        <div className={styles.actionButtons}>
          <button className={styles.backBtn} onClick={() => navigate("/invoice")}>
            ← Nazad na listu faktura
          </button>
          {invoice.status_f === "verifikovana" && (
            <button
              className={styles.simulatePaymentBtn}
              onClick={openPaymentSimulation}
            >
              Simulacija plaćanja
            </button>
          )}
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
