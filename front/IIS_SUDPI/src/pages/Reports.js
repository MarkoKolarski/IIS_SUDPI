import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import styles from "../styles/Reports.module.css";
import axiosInstance from "../axiosInstance";
import { FaChevronDown } from "react-icons/fa";
import { FaFilePdf } from "react-icons/fa";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import "jspdf-autotable";

const Reports = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [reportsData, setReportsData] = useState({
    total_profitability: 0,
    total_cost: 0,
    total_quantity: 0,
    data: [],
    chart_data: {
      profitability: [],
      costs: [],
    },
  });
  const [filterOptions, setFilterOptions] = useState({
    periodi: [],
    grupiranje: [],
    statusi: [],
  });
  const [filters, setFilters] = useState({
    status: "sve",
    period: "sve",
    group_by: "proizvodu",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState({
    status: false,
    period: false,
    group_by: false,
  });
  const [expandedCard, setExpandedCard] = useState(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [pagination, setPagination] = useState({
    current_page: 1,
    page_size: 10,
  });

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axiosInstance.get("/reports/filter-options/");
      setFilterOptions(response.data);
    } catch (err) {
      console.error("Error fetching filter options:", err);
    }
  };

  const fetchReportsData = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();

      if (filters.status) params.append("status", filters.status);
      if (filters.period) params.append("period", filters.period);
      if (filters.group_by) params.append("group_by", filters.group_by);

      const response = await axiosInstance.get(
        `/reports/?${params.toString()}`
      );
      setReportsData(response.data);
      setPagination((prev) => ({ ...prev, current_page: 1 }));
      setError(null);
    } catch (err) {
      console.error("Error fetching reports data:", err);
      setError("Greška pri učitavanju podataka");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const handleFilterChange = (filterType, value) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [filterType]: value,
    }));
    setDropdownOpen((prev) => ({
      ...prev,
      [filterType]: false,
    }));
    setPagination((prev) => ({ ...prev, current_page: 1 }));
  };

  const handlePageChange = (nextPage) => {
    const totalItems = reportsData.data?.length || 0;
    const numPages = Math.ceil(totalItems / pagination.page_size) || 1;
    
    if (
      nextPage < 1 ||
      nextPage > numPages ||
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

  const formatNumber = (number) => {
    return new Intl.NumberFormat("sr-RS").format(number);
  };

  const formatCurrency = (amount) => {
    return `${formatNumber(amount)} RSD`;
  };

  const formatProfitability = (profit) => {
    const sign = profit >= 0 ? "+" : "";
    return `${sign}${profit.toFixed(1)}%`;
  };

  // PDF-safe format (ASCII only) to avoid broken glyphs with built-in jsPDF fonts.
  const formatProfitabilityForPdf = (profit) => {
    const numericProfit = Number(profit) || 0;
    const sign = numericProfit >= 0 ? "+" : "-";
    const absolute = Math.abs(numericProfit).toFixed(1);
    return `${sign}${absolute}%`;
  };

  const getGroupColumnLabel = (groupBy, uppercase = false) => {
    const labelMap = {
      proizvodu: uppercase ? "PROIZVOD" : "Proizvod",
      dobavljacu: uppercase ? "DOBAVLJAČ" : "Dobavljač",
      kategoriji: uppercase ? "KATEGORIJA" : "Kategorija",
    };

    return labelMap[groupBy] || (uppercase ? "PROIZVOD" : "Proizvod");
  };

  const downloadPDF = async () => {
    try {
      // Prikaži loading indikator
      const loadingDiv = document.createElement('div');
      loadingDiv.className = 'pdf-loading';
      loadingDiv.textContent = 'Generisanje PDF-a...';
      loadingDiv.style.position = 'fixed';
      loadingDiv.style.top = '50%';
      loadingDiv.style.left = '50%';
      loadingDiv.style.transform = 'translate(-50%, -50%)';
      loadingDiv.style.padding = '30px 50px';
      loadingDiv.style.background = 'white';
      loadingDiv.style.border = '3px solid #14b8a6';
      loadingDiv.style.borderRadius = '12px';
      loadingDiv.style.zIndex = '10000';
      loadingDiv.style.fontSize = '18px';
      loadingDiv.style.fontWeight = '600';
      loadingDiv.style.color = '#14b8a6';
      loadingDiv.style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
      document.body.appendChild(loadingDiv);

      setExpandedCard(null);
      setIsGeneratingPdf(true); // Toggle unpaginated/unconstrained view
      await new Promise(resolve => setTimeout(resolve, 500)); // Wait for render

      const pdf = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4',
        putOnlyUsedFonts: true,
        compress: true
      });
      
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;
      let yPosition = margin;
      
      // Helper funkcija za formatiranje datuma
      const formatDate = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}.`;
      };
      
      // Helper funkcija za pretvaranje teksta u format koji PDF podržava
      const encodeText = (text) => {
        if (!text) return '';
        return text
          .replace(/č/g, 'c').replace(/Č/g, 'C')
          .replace(/ć/g, 'c').replace(/Ć/g, 'C')
          .replace(/đ/g, 'dj').replace(/Đ/g, 'Dj')
          .replace(/š/g, 's').replace(/Š/g, 'S')
          .replace(/ž/g, 'z').replace(/Ž/g, 'Z');
      };

      // HEADER - Naslov sa pozadinom
      pdf.setFillColor(20, 184, 166); // Zelena boja
      pdf.rect(0, 0, pageWidth, 35, 'F');
      
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(255, 255, 255);
      pdf.text(encodeText('IZVEŠTAJ O TROŠKOVIMA I PROFITABILNOSTI'), pageWidth / 2, 15, { align: 'center' });
      
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
      const currentDate = new Date();
      const formattedDate = formatDate(currentDate);
      pdf.text(`Generisano: ${formattedDate}`, pageWidth / 2, 25, { align: 'center' });
      
      yPosition = 45;

      // INFORMACIJE O FILTERIMA - u okviru
      const statusLabel = filterOptions.statusi.find(s => s.value === filters.status)?.label || filters.status;
      const periodLabel = filterOptions.periodi.find(p => p.value === filters.period)?.label || filters.period;
      const groupLabel = filterOptions.grupiranje.find(g => g.value === filters.group_by)?.label || filters.group_by;
      const pdfGroupHeaderLabel = encodeText(getGroupColumnLabel(filters.group_by, true));
      
      pdf.setFillColor(236, 253, 245); // Svetlo zelena
      pdf.setDrawColor(167, 243, 208);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 20, 3, 3, 'FD');
      
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(19, 78, 74);
      
      const filterY = yPosition + 7;
      pdf.text('STATUS:', margin + 5, filterY);
      pdf.setFont('helvetica', 'normal');
      pdf.text(encodeText(statusLabel), margin + 25, filterY);
      
      pdf.setFont('helvetica', 'bold');
      pdf.text('PERIOD:', margin + 5, filterY + 6);
      pdf.setFont('helvetica', 'normal');
      pdf.text(encodeText(periodLabel), margin + 25, filterY + 6);
      
      pdf.setFont('helvetica', 'bold');
      pdf.text('GRUPISANO PO:', margin + 80, filterY);
      pdf.setFont('helvetica', 'normal');
      pdf.text(encodeText(groupLabel), margin + 115, filterY);
      
      yPosition += 28;

      // GRAFIČKI PRIKAZI
      const chartSection = document.querySelector(`.${styles.chartSection}`);
      if (chartSection) {
        pdf.setFontSize(14);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(20, 184, 166);
        pdf.text(encodeText('VIZUALIZACIJA PODATAKA'), margin, yPosition);
        yPosition += 2;
        
        // Linija ispod naslova
        pdf.setDrawColor(20, 184, 166);
        pdf.setLineWidth(0.5);
        pdf.line(margin, yPosition, pageWidth - margin, yPosition);
        yPosition += 5;
        
        const canvas = await html2canvas(chartSection, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff'
        });
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = pageWidth - (2 * margin);
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        
        if (yPosition + imgHeight > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        
        pdf.addImage(imgData, 'PNG', margin, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 10;
      }

      // TABELA SA DETALJIMA
      if (yPosition + 50 > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }

      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(20, 184, 166);
      pdf.text(encodeText('DETALJAN PRIKAZ PODATAKA'), margin, yPosition);
      yPosition += 2;
      
      pdf.setDrawColor(20, 184, 166);
      pdf.setLineWidth(0.5);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 5;

      // Header tabele
      pdf.setFillColor(20, 184, 166);
      pdf.setDrawColor(20, 184, 166);

      const drawAlignedHeaderText = (text, startX, width, align = 'left') => {
        if (align === 'right') {
          pdf.text(encodeText(text), startX + width - 3, yPosition + 7, { align: 'right' });
        } else {
          pdf.text(encodeText(text), startX + 3, yPosition + 7);
        }
      };
      
      const colWidths = {
        name: 70,
        quantity: 30,
        cost: 45,
        profit: 35
      };
      
      let xPos = margin;
      const headerHeight = 10;
      
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, headerHeight, 2, 2, 'FD');
      
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(255, 255, 255);
      
      drawAlignedHeaderText(pdfGroupHeaderLabel, xPos, colWidths.name, 'left');
      xPos += colWidths.name;
      
      drawAlignedHeaderText('KOLIČINA', xPos, colWidths.quantity, 'right');
      xPos += colWidths.quantity;
      
      drawAlignedHeaderText('UKUPAN TROŠAK', xPos, colWidths.cost, 'right');
      xPos += colWidths.cost;
      
      drawAlignedHeaderText('PROFIT', xPos, colWidths.profit, 'right');
      
      yPosition += headerHeight + 2;

      // Redovi tabele
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(9);
      
      (reportsData.data || []).forEach((row, index) => {
        if (yPosition + 8 > pageHeight - margin - 15) {
          pdf.addPage();
          yPosition = margin;
          
          // Ponovi header na novoj stranici
          pdf.setFillColor(20, 184, 166);
          pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, headerHeight, 2, 2, 'FD');
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(255, 255, 255);
          
          xPos = margin;
          drawAlignedHeaderText(pdfGroupHeaderLabel, xPos, colWidths.name, 'left');
          xPos += colWidths.name;
          drawAlignedHeaderText('KOLIČINA', xPos, colWidths.quantity, 'right');
          xPos += colWidths.quantity;
          drawAlignedHeaderText('UKUPAN TROŠAK', xPos, colWidths.cost, 'right');
          xPos += colWidths.cost;
          drawAlignedHeaderText('PROFIT', xPos, colWidths.profit, 'right');
          
          yPosition += headerHeight + 2;
          pdf.setFont('helvetica', 'normal');
          pdf.setFontSize(9);
        }

        const rowHeight = 7;
        
        // Alternativne boje redova
        if (index % 2 === 0) {
          pdf.setFillColor(249, 249, 249);
          pdf.rect(margin, yPosition, pageWidth - 2 * margin, rowHeight, 'F');
        }
        
        // Granica reda
        pdf.setDrawColor(220, 220, 220);
        pdf.setLineWidth(0.1);
        pdf.line(margin, yPosition + rowHeight, pageWidth - margin, yPosition + rowHeight);

        xPos = margin;
        pdf.setTextColor(40, 40, 40);
        
        // Tekst sa truncate ako je predugačak
        const maxNameLength = 35;
        const displayName = row.name.length > maxNameLength 
          ? row.name.substring(0, maxNameLength) + '...' 
          : row.name;
        pdf.text(encodeText(displayName), xPos + 3, yPosition + 5);
        xPos += colWidths.name;
        
        pdf.text(
          formatNumber(row.quantity),
          xPos + colWidths.quantity - 3,
          yPosition + 5,
          { align: 'right' }
        );
        xPos += colWidths.quantity;
        
        pdf.text(
          encodeText(formatCurrency(row.total_cost)),
          xPos + colWidths.cost - 3,
          yPosition + 5,
          { align: 'right' }
        );
        xPos += colWidths.cost;
        
        // Profitabilnost sa bojom (bez nepouzdanih unicode simbola u PDF-u)
        if (row.profitability >= 0) {
          pdf.setTextColor(0, 150, 0);
          pdf.text(
            formatProfitabilityForPdf(row.profitability),
            xPos + colWidths.profit - 3,
            yPosition + 5,
            { align: 'right' }
          );
        } else {
          pdf.setTextColor(200, 0, 0);
          pdf.text(
            formatProfitabilityForPdf(row.profitability),
            xPos + colWidths.profit - 3,
            yPosition + 5,
            { align: 'right' }
          );
        }
        
        yPosition += rowHeight;
      });

      // UKUPNI RED - istaknuto
      if ((reportsData.data || []).length > 0) {
        if (yPosition + 12 > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }

        yPosition += 2;
        const summaryHeight = 10;
        
        pdf.setFillColor(20, 184, 166);
        pdf.setDrawColor(20, 184, 166);
        pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, summaryHeight, 2, 2, 'FD');
        
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(10);
        pdf.setTextColor(255, 255, 255);
        
        xPos = margin;
        pdf.text('UKUPNO:', xPos + 3, yPosition + 7);
        xPos += colWidths.name;
        
        pdf.text(
          `${formatNumber(reportsData.total_quantity)} kom`,
          xPos + colWidths.quantity - 3,
          yPosition + 7,
          { align: 'right' }
        );
        xPos += colWidths.quantity;
        
        pdf.text(
          encodeText(formatCurrency(reportsData.total_cost)),
          xPos + colWidths.cost - 3,
          yPosition + 7,
          { align: 'right' }
        );
        xPos += colWidths.cost;
        
        pdf.text(
          formatProfitabilityForPdf(reportsData.total_profitability),
          xPos + colWidths.profit - 3,
          yPosition + 7,
          { align: 'right' }
        );
        
        yPosition += summaryHeight + 5;
      }

      // FOOTER na svakoj stranici
      const totalPages = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setFont('helvetica', 'normal');
        pdf.setTextColor(150, 150, 150);
        pdf.text(
          `Strana ${i} od ${totalPages}`, 
          pageWidth / 2, 
          pageHeight - 10, 
          { align: 'center' }
        );
      }

      // Sačuvaj PDF
      const fileName = `Izvestaj_${formattedDate.replace(/\./g, '-')}.pdf`;
      pdf.save(fileName);

      document.body.removeChild(loadingDiv);
    } catch (error) {
      console.error('Greška pri generisanju PDF-a:', error);
      alert('Došlo je do greške pri generisanju PDF-a');
      const loadingDiv = document.querySelector('.pdf-loading');
      if (loadingDiv) {
        document.body.removeChild(loadingDiv);
      }
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  useEffect(() => {
    fetchFilterOptions();
  }, []);

  useEffect(() => {
    fetchReportsData();
  }, [fetchReportsData]);

  // Handle outside click for expanded card
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setExpandedCard(null);
      }
    };

    if (expandedCard && !isGeneratingPdf) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [expandedCard, isGeneratingPdf]);

  const totalItems = reportsData.data?.length || 0;
  const numPages = Math.ceil(totalItems / pagination.page_size) || 1;
  const totalCost = Number(reportsData.total_cost) || 0;
  
  const paginatedData = isGeneratingPdf 
    ? (reportsData.data || []) 
    : (reportsData.data || []).slice(
        (pagination.current_page - 1) * pagination.page_size,
        pagination.current_page * pagination.page_size
      );

  const visiblePages = getVisiblePages(pagination.current_page, numPages);

  // Emergency fallback if there are critical errors
  if (error === "CRITICAL_ERROR") {
    return (
      <div style={{ padding: "20px", color: "red" }}>
        <h1>Greška u učitavanju stranice</h1>
        <p>Molimo proverite konekciju ili kontaktirajte administratora.</p>
      </div>
    );
  }

  return (
    <div
      className={`${styles.reportsWrapper} ${
        isSidebarCollapsed ? styles.sidebarCollapsed : ""
      } ${isGeneratingPdf ? styles.pdfMode : ""}`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <div className={styles.reportsMainContent}>
        <header className={styles.reportsHeader}>
          <h1>Izveštaji</h1>
        </header>

        <section className={styles.reportsFilterSection}>
          <div className={styles.filterControls}>
            <div className={styles.filterDropdown}>
              <label>Status</label>
              <button type="button" onClick={() => toggleDropdown("status")}>
                <span>{getSelectedLabel("statusi", filters.status)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.status && (
                <div className={styles.dropdownMenu}>
                  {(filterOptions.statusi || []).map((status) => (
                    <div
                      key={status.value}
                      className={styles.dropdownItem}
                      onClick={() => handleFilterChange("status", status.value)}
                    >
                      {status.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className={styles.filterDropdown}>
              <label>Period</label>
              <button type="button" onClick={() => toggleDropdown("period")}>
                <span>{getSelectedLabel("periodi", filters.period)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.period && (
                <div className={styles.dropdownMenu}>
                  {(filterOptions.periodi || []).map((period) => (
                    <div
                      key={period.value}
                      className={styles.dropdownItem}
                      onClick={() => handleFilterChange("period", period.value)}
                    >
                      {period.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className={styles.filterDropdown}>
              <label>Grupiši po</label>
              <button type="button" onClick={() => toggleDropdown("group_by")}>
                <span>{getSelectedLabel("grupiranje", filters.group_by)}</span>
                <FaChevronDown />
              </button>
              {dropdownOpen.group_by && (
                <div className={styles.dropdownMenu}>
                  {(filterOptions.grupiranje || []).map((group) => (
                    <div
                      key={group.value}
                      className={styles.dropdownItem}
                      onClick={() => handleFilterChange("group_by", group.value)}
                    >
                      {group.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right aligned actions (PDF download, etc.) */}
          <div className={styles.filterActions}>
            <label htmlFor="pdf-download">&nbsp;</label>
            <button className={styles.downloadPdfBtn} onClick={downloadPDF}>
              <FaFilePdf className={styles.buttonIcon} aria-hidden="true" />
              Preuzmi PDF
            </button>
          </div>
        </section>

        <section
          className={`${styles.chartSection} ${
            expandedCard ? styles.chartSectionHasExpanded : ""
          } ${isGeneratingPdf ? styles.chartSectionPdfMode : ""}`}
        >
          {expandedCard && !isGeneratingPdf && (
            <div
              className={styles.expandedOverlay}
              onClick={() => setExpandedCard(null)}
            ></div>
          )}
          <div
            className={`${styles.chartCard} ${
              expandedCard === "profitability"
                ? `${styles.expandedCard} ${styles.expandedProfitabilityCard}`
                : ""
            }`}
          >
            <div className={styles.chartCardHeader}>
              <div className={styles.cardHeaderWithControls}>
                <h2>
                  Profitabilnost po{" "}
                  {filters.group_by === "proizvodu"
                    ? "proizvodu"
                    : filters.group_by === "dobavljacu"
                    ? "dobavljaču"
                    : "kategoriji"}
                </h2>
                {!isGeneratingPdf && (
                  <button
                    type="button"
                    className={styles.cardExpandButton}
                    onClick={() => setExpandedCard(expandedCard === "profitability" ? null : "profitability")}
                    aria-label={
                      expandedCard === "profitability"
                        ? "Smanji profitabilnost"
                        : "Proširi profitabilnost"
                    }
                    title={expandedCard === "profitability" ? "Smanji" : "Proširi"}
                  >
                    {expandedCard === "profitability" ? "✕" : "⤢"}
                  </button>
                )}
              </div>
            </div>
            <div
              className={`${styles.chartCardBody} ${
                expandedCard === "profitability" ? styles.expandedChartCardBody : ""
              }`}
            >
              {loading ? (
                <div className={styles.loading}>Učitava...</div>
              ) : (
                <div className={styles.chartPlaceholder}>
                  <div className={styles.chartSummary}>
                    <h3>
                      Ukupna profitabilnost:{" "}
                      {formatProfitability(reportsData.total_profitability)}
                    </h3>
                    <div
                      className={`${styles.chartScrollableList} ${
                        expandedCard === "profitability"
                          ? styles.expandedChartScrollableList
                          : ""
                      } ${isGeneratingPdf ? styles.pdfChartScrollableList : ""}`}
                      role="region"
                      aria-label="Lista profitabilnosti"
                      tabIndex={0}
                    >
                      {(isGeneratingPdf || expandedCard === "profitability"
                        ? reportsData.chart_data?.profitability || []
                        : (reportsData.chart_data?.profitability || []).slice(0, 5)
                      ).map((item, index) => (
                        <div key={index} className={styles.chartItem}>
                          <span>
                            {item.name}: {formatProfitability(item.value)}
                          </span>
                          <div
                            className={styles.chartBar}
                            style={{ width: `${Math.abs(item.value)}%` }}
                          ></div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div
            className={`${styles.chartCard} ${
              expandedCard === "costs"
                ? `${styles.expandedCard} ${styles.expandedCostsCard}`
                : ""
            }`}
          >
            <div className={styles.chartCardHeader}>
              <div className={styles.cardHeaderWithControls}>
                <h2>
                  Troškovi po{" "}
                  {filters.group_by === "proizvodu"
                    ? "proizvodu"
                    : filters.group_by === "dobavljacu"
                    ? "dobavljaču"
                    : "kategoriji"}
                </h2>
                {!isGeneratingPdf && (
                  <button
                    type="button"
                    className={styles.cardExpandButton}
                    onClick={() => setExpandedCard(expandedCard === "costs" ? null : "costs")}
                    aria-label={expandedCard === "costs" ? "Smanji troškove" : "Proširi troškove"}
                    title={expandedCard === "costs" ? "Smanji" : "Proširi"}
                  >
                    {expandedCard === "costs" ? "✕" : "⤢"}
                  </button>
                )}
              </div>
            </div>
            <div
              className={`${styles.chartCardBody} ${
                expandedCard === "costs" ? styles.expandedChartCardBody : ""
              }`}
            >
              {loading ? (
                <div className={styles.loading}>Učitava...</div>
              ) : (
                <div className={styles.chartPlaceholder}>
                  <div className={styles.chartSummary}>
                    <h3>
                      Ukupni troškovi: {formatCurrency(reportsData.total_cost)}
                    </h3>
                    <div
                      className={`${styles.chartScrollableList} ${
                        expandedCard === "costs" ? styles.expandedChartScrollableList : ""
                      } ${isGeneratingPdf ? styles.pdfChartScrollableList : ""}`}
                      role="region"
                      aria-label="Lista troškova"
                      tabIndex={0}
                    >
                      {(isGeneratingPdf || expandedCard === "costs"
                        ? reportsData.chart_data?.costs || []
                        : (reportsData.chart_data?.costs || []).slice(0, 5)
                      ).map((item, index) => (
                        <div key={index} className={styles.chartItem}>
                          <span>
                            {item.name}: {formatCurrency(item.value)}
                          </span>
                          <div
                            className={styles.chartBar}
                            style={{
                              width: `${
                                totalCost > 0
                                  ? Math.min(100, Math.max(0, (item.value / totalCost) * 100))
                                  : 0
                              }%`,
                            }}
                          ></div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className={styles.reportsTableSection}>
          <div className={styles.tableContainer}>
            <div className={styles.tableTitleHeader}>
              <h2>Detaljan prikaz podataka</h2>
            </div>
            {error && <div className={styles.errorMessage}>{error}</div>}
            {loading ? (
              <div className={styles.loading}>Učitava podatke...</div>
            ) : (
              <div className={styles.tableContent}>
                <div className={styles.reportsTableHeader}>
                  <div className={`${styles.tableCol} ${styles.colProizvod}`}>
                    {getGroupColumnLabel(filters.group_by)}
                  </div>
                  <div className={`${styles.tableCol} ${styles.colKolicina}`}>
                    Količina
                  </div>
                  <div className={`${styles.tableCol} ${styles.colTrosak}`}>
                    Ukupan trošak
                  </div>
                  <div className={`${styles.tableCol} ${styles.colProfit}`}>
                    Profitabilnost
                  </div>
                </div>
                <div className={styles.reportsTableBody}>
                  {paginatedData.map((row, index) => (
                    <div
                      key={row.id || index}
                      className={`${styles.tableRow} ${
                        index % 2 === 0 ? styles.rowDark : styles.rowLight
                      }`}
                    >
                      <div className={`${styles.tableCol} ${styles.colProizvod}`}>
                        {row.name}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colKolicina}`}>
                        {formatNumber(row.quantity)}
                      </div>
                      <div className={`${styles.tableCol} ${styles.colTrosak}`}>
                        {formatCurrency(row.total_cost)}
                      </div>
                      <div
                        className={`${styles.tableCol} ${styles.colProfit} ${
                          row.profitability >= 0
                            ? styles.profitPositive
                            : styles.profitNegative
                        }`}
                      >
                        <span className={styles.arrow}>
                          {row.profitability >= 0 ? "▲" : "▼"}
                        </span>
                        {formatProfitability(row.profitability)}
                      </div>
                    </div>
                  ))}

                  {(reportsData.data || []).length > 0 && (
                    <div className={`${styles.tableRow} ${styles.summaryRow}`}>
                      <div className={`${styles.tableCol} ${styles.colProizvod}`}>
                        UKUPNO:
                      </div>
                      <div className={`${styles.tableCol} ${styles.colKolicina}`}>
                        {formatNumber(reportsData.total_quantity)} kom
                      </div>
                      <div className={`${styles.tableCol} ${styles.colTrosak}`}>
                        {formatCurrency(reportsData.total_cost)}
                      </div>
                      <div
                        className={`${styles.tableCol} ${styles.colProfit} ${
                          reportsData.total_profitability >= 0
                            ? styles.profitPositive
                            : styles.profitNegative
                        }`}
                      >
                        <span className={styles.arrow}>
                          {reportsData.total_profitability >= 0 ? "▲" : "▼"}
                        </span>
                        {formatProfitability(reportsData.total_profitability)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Pagination Controls */}
            {!loading && (reportsData.data || []).length > 0 && numPages > 1 && !isGeneratingPdf && (
              <div className={styles.pagination}>
                <button
                  onClick={() => handlePageChange(pagination.current_page - 1)}
                  disabled={pagination.current_page === 1}
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
                  disabled={pagination.current_page === numPages}
                  className={`${styles.paginationBtn} ${styles.paginationNavBtn}`}
                >
                  Sledeća
                </button>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Reports;
