import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import PaymentSimulationModal from "../components/PaymentSimulationModal";
import PageTransition from "../components/PageTransition";
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
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [rejectReasonError, setRejectReasonError] = useState("");
  const [actionFeedback, setActionFeedback] = useState(null);

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

  const closeRejectModal = useCallback(() => {
    if (actionLoading) {
      return;
    }

    setIsRejectModalOpen(false);
    setRejectReason("");
    setRejectReasonError("");
  }, [actionLoading]);

  const openRejectModal = () => {
    setActionFeedback(null);
    setRejectReason("");
    setRejectReasonError("");
    setIsRejectModalOpen(true);
  };

  const handleInvoiceAction = async (action, reason = "") => {
    setActionLoading(true);
    setActionFeedback(null);

    try {
      const response = await axiosInstance.post(`/invoices/${invoiceId}/action/`, {
        action,
        reason,
      });

      await loadInvoiceDetails();
      setActionFeedback({
        type: "success",
        message: response.data.poruka || "Akcija je uspešno izvršena.",
      });
      return true;
    } catch (error) {
      console.error("Greška pri izvršavanju akcije:", error);
      setActionFeedback({
        type: "error",
        message:
          error.response?.data?.detail ||
          "Greška pri izvršavanju akcije. Pokušajte ponovo.",
      });
      return false;
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
    if (!actionFeedback) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setActionFeedback(null);
    }, 4500);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [actionFeedback]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key !== "Escape") {
        return;
      }

      if (isRejectModalOpen) {
        closeRejectModal();
        return;
      }

      if (expandedCard) {
        setExpandedCard(null);
      }
    };

    if (expandedCard || isRejectModalOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", onKeyDown);
    }

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [expandedCard, isRejectModalOpen, closeRejectModal]);

  const hasProcessSteps =
    Array.isArray(invoice?.process_steps) && invoice.process_steps.length > 0;
  const hasItems = Array.isArray(invoice?.stavke) && invoice.stavke.length > 0;
  const canApproveReject =
    invoice?.status_f === "primljena" || invoice?.status_f === "verifikovana";
  const hasTransaction = Boolean(invoice?.transakcija);

  const resolveStatusTone = (statusCode) => {
    const normalizedStatus = String(statusCode || "").toLowerCase();

    if (["primljena", "na_cekanju", "ceka_verifikaciju"].includes(normalizedStatus)) {
      return "statusPending";
    }

    if (["verifikovana", "spremna_za_placanje", "u_obradi"].includes(normalizedStatus)) {
      return "statusInfo";
    }

    if (["placena", "isplacena", "zavrsena"].includes(normalizedStatus)) {
      return "statusSuccess";
    }

    if (["odbijena", "stornirana", "ponistena"].includes(normalizedStatus)) {
      return "statusRejected";
    }

    return "statusNeutral";
  };

  const statusToneClass = resolveStatusTone(invoice?.status_f);

  const resolvePanelTone = (statusCode, requiresAction) => {
    const normalizedStatus = String(statusCode || "").toLowerCase();

    if (requiresAction) {
      return "panelActionRequired";
    }

    if (["placena", "isplacena", "zavrsena"].includes(normalizedStatus)) {
      return "panelCompleted";
    }

    if (["odbijena", "stornirana", "ponistena"].includes(normalizedStatus)) {
      return "panelRejected";
    }

    if (["verifikovana", "spremna_za_placanje", "u_obradi"].includes(normalizedStatus)) {
      return "panelInProgress";
    }

    return "panelNeutral";
  };

  const panelToneClass = resolvePanelTone(invoice?.status_f, canApproveReject);

  const resolveProcessTone = (toneClass) => {
    if (toneClass === "statusPending") {
      return "processTonePending";
    }

    if (toneClass === "statusInfo") {
      return "processToneInfo";
    }

    if (toneClass === "statusSuccess") {
      return "processToneSuccess";
    }

    if (toneClass === "statusRejected") {
      return "processToneRejected";
    }

    return "processToneNeutral";
  };

  const processToneClass = resolveProcessTone(statusToneClass);

  const handleRejectAction = async () => {
    const normalizedReason = rejectReason.trim();

    if (!normalizedReason) {
      setRejectReasonError("Unesite razlog odbacivanja pre potvrde.");
      return;
    }

    setRejectReasonError("");
    const succeeded = await handleInvoiceAction("reject", normalizedReason);
    if (succeeded) {
      closeRejectModal();
    }
  };

  if (loading) {
    return (
      <PageTransition>
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
      </PageTransition>
    );
  }

  if (!invoice) {
    return (
      <PageTransition>
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
      </PageTransition>
    );
  }

  return (
    <PageTransition>
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
          <section className={`${styles.quickActionsPanel} ${styles[panelToneClass]}`}>
            <div className={styles.quickActionsInfo}>
              <h2>{canApproveReject ? "Faktura očekuje akciju" : "Pregled statusa fakture"}</h2>
              <p>
                {canApproveReject
                  ? invoice.status_f === "primljena"
                    ? "Potrebno je da fakturu verifikujete ili odbacite sa obrazloženjem."
                    : "Faktura je verifikovana i čeka završnu akciju plaćanja ili odbacivanja."
                  : "Za trenutni status nema dostupnih akcija."}
              </p>
              <div className={styles.quickActionsStatusWrap}>
                <span className={styles.quickActionsStatusLabel}>Status fakture</span>
                <span
                  className={`${styles.quickActionsStatus} ${styles[statusToneClass]}`}
                >
                  {invoice.status_display}
                </span>
              </div>
            </div>

            {canApproveReject ? (
              <div className={styles.quickActionsButtons}>
                {invoice.status_f === "primljena" ? (
                  <button
                    className={`${styles.notificationBtn} ${styles.confirm} ${styles.quickActionPrimary}`}
                    onClick={() => handleInvoiceAction("approve")}
                    disabled={actionLoading}
                  >
                    {actionLoading ? "Procesiranje..." : "Verifikuj fakturu"}
                  </button>
                ) : (
                  <button
                    className={`${styles.notificationBtn} ${styles.confirm} ${styles.quickActionPrimary}`}
                    onClick={openPaymentSimulation}
                    disabled={actionLoading}
                  >
                    Izvrši plaćanje
                  </button>
                )}

                <button
                  className={`${styles.notificationBtn} ${styles.decline} ${styles.quickActionSecondary}`}
                  onClick={openRejectModal}
                  disabled={actionLoading}
                >
                  Odbaci fakturu
                </button>
              </div>
            ) : (
              <div className={styles.quickActionsEmpty}>Nema akcija za ovaj status.</div>
            )}
          </section>

          {actionFeedback && (
            <div
              className={`${styles.actionFeedback} ${
                actionFeedback.type === "success"
                  ? styles.actionFeedbackSuccess
                  : styles.actionFeedbackError
              }`}
              role={actionFeedback.type === "error" ? "alert" : "status"}
              aria-live="polite"
            >
              <span>{actionFeedback.message}</span>
              <button
                type="button"
                className={styles.actionFeedbackClose}
                aria-label="Zatvori poruku"
                onClick={() => setActionFeedback(null)}
              >
                ×
              </button>
            </div>
          )}

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
                <span className={styles.summaryValue}>{invoice.naziv_db}</span>
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

          <section className={`${styles.processFlow} ${styles[processToneClass]}`}>
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
                              Number(stavka.kolicina_sf) * Number(stavka.cena_po_jed_sf)
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
                              {formatAmount(stavka.cena_po_jed_sf)}
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
                      <span className={styles.transactionValue}>{invoice.transakcija.broj_potvrde_t}</span>
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
          </section>

          <div className={styles.actionButtons}>
            <button className={styles.backBtn} onClick={() => navigate("/invoice")}>
              ← Nazad na listu faktura
            </button>
          </div>
        </div>
        </main>

        {isRejectModalOpen && (
          <div
            className={styles.rejectModalOverlay}
            onClick={(event) => {
              if (event.target === event.currentTarget) {
                closeRejectModal();
              }
            }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="reject-modal-title"
          >
            <div className={styles.rejectModalCard}>
              <div className={styles.rejectModalHeader}>
                <h2 id="reject-modal-title">Odbacivanje fakture</h2>
                <button
                  type="button"
                  className={styles.rejectModalClose}
                  onClick={closeRejectModal}
                  disabled={actionLoading}
                  aria-label="Zatvori prozor"
                >
                  ×
                </button>
              </div>

              <div className={styles.rejectModalBody}>

              <p className={styles.rejectModalDescription}>
                Unesite razlog odbacivanja. Ova poruka će biti evidentirana uz fakturu.
              </p>

              <label htmlFor="reject-reason" className={styles.rejectModalLabel}>
                Razlog odbacivanja
              </label>
              <textarea
                id="reject-reason"
                className={styles.rejectModalTextarea}
                value={rejectReason}
                onChange={(event) => {
                  setRejectReason(event.target.value);
                  if (rejectReasonError) {
                    setRejectReasonError("");
                  }
                }}
                placeholder="Npr. Stavke fakture nisu usklađene sa ugovorom."
                rows={5}
                maxLength={500}
                autoFocus
                disabled={actionLoading}
              />

              <div className={styles.rejectModalMeta}>
                <span className={styles.rejectModalCounter}>{rejectReason.length}/500</span>
                {rejectReasonError && (
                  <span className={styles.rejectModalError}>{rejectReasonError}</span>
                )}
              </div>

              <div className={styles.rejectModalActions}>
                <button
                  type="button"
                  className={styles.rejectModalCancelBtn}
                  onClick={closeRejectModal}
                  disabled={actionLoading}
                >
                  Otkaži
                </button>
                <button
                  type="button"
                  className={styles.rejectModalConfirmBtn}
                  onClick={handleRejectAction}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Odbacivanje..." : "Potvrdi odbacivanje"}
                </button>
              </div>
              </div>
            </div>
          </div>
        )}

        <PaymentSimulationModal
          isOpen={isPaymentModalOpen}
          onClose={closePaymentSimulation}
          invoiceId={invoiceId}
        />
      </div>
    </PageTransition>
  );
};

export default InvoiceDetails;
