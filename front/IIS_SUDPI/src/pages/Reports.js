import React, { useState, useEffect, useCallback } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/Reports.css";
import axiosInstance from "../axiosInstance";
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

      await new Promise(resolve => setTimeout(resolve, 100));

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
      const chartSection = document.querySelector('.chart-section');
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
      
      const colWidths = {
        name: 75,
        quantity: 35,
        cost: 45,
        profit: 30
      };
      
      let xPos = margin;
      const headerHeight = 10;
      
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, headerHeight, 2, 2, 'FD');
      
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(255, 255, 255);
      
      pdf.text(encodeText(groupLabel.toUpperCase()), xPos + 3, yPosition + 7);
      xPos += colWidths.name;
      
      pdf.text(encodeText('KOLIČINA'), xPos + 3, yPosition + 7);
      xPos += colWidths.quantity;
      
      pdf.text(encodeText('UKUPAN TROŠAK'), xPos + 3, yPosition + 7);
      xPos += colWidths.cost;
      
      pdf.text('PROFIT', xPos + 3, yPosition + 7);
      
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
          pdf.text(encodeText(groupLabel.toUpperCase()), xPos + 3, yPosition + 7);
          xPos += colWidths.name;
          pdf.text(encodeText('KOLIČINA'), xPos + 3, yPosition + 7);
          xPos += colWidths.quantity;
          pdf.text(encodeText('UKUPAN TROŠAK'), xPos + 3, yPosition + 7);
          xPos += colWidths.cost;
          pdf.text('PROFIT', xPos + 3, yPosition + 7);
          
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
        
        pdf.text(formatNumber(row.quantity), xPos + 3, yPosition + 5);
        xPos += colWidths.quantity;
        
        pdf.text(encodeText(formatCurrency(row.total_cost)), xPos + 3, yPosition + 5);
        xPos += colWidths.cost;
        
        // Profitabilnost sa bojom i strelicom
        if (row.profitability >= 0) {
          pdf.setTextColor(0, 150, 0);
          pdf.text('▲ ' + formatProfitability(row.profitability), xPos + 3, yPosition + 5);
        } else {
          pdf.setTextColor(200, 0, 0);
          pdf.text('▼ ' + formatProfitability(row.profitability), xPos + 3, yPosition + 5);
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
        
        pdf.text(`${formatNumber(reportsData.total_quantity)} kom`, xPos + 3, yPosition + 7);
        xPos += colWidths.quantity;
        
        pdf.text(encodeText(formatCurrency(reportsData.total_cost)), xPos + 3, yPosition + 7);
        xPos += colWidths.cost;
        
        pdf.text(formatProfitability(reportsData.total_profitability), xPos + 3, yPosition + 7);
        
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
        pdf.text(
          encodeText('Sistem za upravljanje nabavkom'), 
          margin, 
          pageHeight - 10
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
    }
  };

  useEffect(() => {
    fetchFilterOptions();
  }, []);

  useEffect(() => {
    fetchReportsData();
  }, [fetchReportsData]);

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
      className={`reports-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <div className="reports-main-content">
        <header className="reports-header">
          <h1>Izveštaji</h1>
        </header>

        <section className="reports-filter-section">
          <div className="filter-controls">
            <div className="filter-dropdown">
              <label htmlFor="status-filter">Status</label>
              <select
                id="status-filter"
                value={filters.status}
                onChange={(e) => handleFilterChange("status", e.target.value)}
              >
                {(filterOptions.statusi || []).map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-dropdown">
              <label htmlFor="period-filter">Period</label>
              <select
                id="period-filter"
                value={filters.period}
                onChange={(e) => handleFilterChange("period", e.target.value)}
              >
                {(filterOptions.periodi || []).map((period) => (
                  <option key={period.value} value={period.value}>
                    {period.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-dropdown">
              <label htmlFor="group-by-filter">Grupiši po</label>
              <select
                id="group-by-filter"
                value={filters.group_by}
                onChange={(e) => handleFilterChange("group_by", e.target.value)}
              >
                {(filterOptions.grupiranje || []).map((group) => (
                  <option key={group.value} value={group.value}>
                    {group.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Right aligned actions (PDF download, etc.) */}
          <div className="filter-actions">
            <label htmlFor="pdf-download">&nbsp;</label>
            <button className="download-pdf-btn" onClick={downloadPDF}>
              <span className="pdf-icon">📄</span>
              Preuzmi PDF
            </button>
          </div>
        </section>

        <section className="chart-section">
          <div className="chart-card">
            <div className="chart-card-header">
              <h2>
                Profitabilnost po{" "}
                {filters.group_by === "proizvodu"
                  ? "proizvodu"
                  : filters.group_by === "dobavljacu"
                  ? "dobavljaču"
                  : "kategoriji"}
              </h2>
            </div>
            <div className="chart-card-body">
              {loading ? (
                <div className="loading">Učitava...</div>
              ) : (
                <div className="chart-placeholder">
                  <div className="chart-summary">
                    <h3>
                      Ukupna profitabilnost:{" "}
                      {formatProfitability(reportsData.total_profitability)}
                    </h3>
                    {(reportsData.chart_data?.profitability || [])
                      .slice(0, 5)
                      .map((item, index) => (
                        <div key={index} className="chart-item">
                          <span>
                            {item.name}: {formatProfitability(item.value)}
                          </span>
                          <div
                            className="chart-bar"
                            style={{ width: `${Math.abs(item.value)}%` }}
                          ></div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="chart-card">
            <div className="chart-card-header">
              <h2>
                Troškovi po{" "}
                {filters.group_by === "proizvodu"
                  ? "proizvodu"
                  : filters.group_by === "dobavljacu"
                  ? "dobavljaču"
                  : "kategoriji"}
              </h2>
            </div>
            <div className="chart-card-body">
              {loading ? (
                <div className="loading">Učitava...</div>
              ) : (
                <div className="chart-placeholder">
                  <div className="chart-summary">
                    <h3>
                      Ukupni troškovi: {formatCurrency(reportsData.total_cost)}
                    </h3>
                    {(reportsData.chart_data?.costs || [])
                      .slice(0, 5)
                      .map((item, index) => (
                        <div key={index} className="chart-item">
                          <span>
                            {item.name}: {formatCurrency(item.value)}
                          </span>
                          <div
                            className="chart-bar"
                            style={{
                              width: `${
                                (item.value / reportsData.total_cost) * 100
                              }%`,
                            }}
                          ></div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="reports-table-section">
          <div className="table-container">
            <div className="table-title-header">
              <h2>Detaljan prikaz podataka</h2>
            </div>
            {error && <div className="error-message">{error}</div>}
            {loading ? (
              <div className="loading">Učitava podatke...</div>
            ) : (
              <div className="table-content">
                <div className="reports-table-header">
                  <div className="table-col col-proizvod">
                    {filters.group_by === "proizvodu"
                      ? "Proizvod"
                      : filters.group_by === "dobavljacu"
                      ? "Dobavljač"
                      : "Kategorija"}
                  </div>
                  <div className="table-col col-kolicina">Količina</div>
                  <div className="table-col col-trosak">Ukupan trošak</div>
                  <div className="table-col col-profit">Profitabilnost</div>
                </div>
                <div className="reports-table-body">
                  {(reportsData.data || []).map((row, index) => (
                    <div
                      key={row.id || index}
                      className={`table-row ${
                        index % 2 === 0 ? "row-dark" : "row-light"
                      }`}
                    >
                      <div className="table-col col-proizvod">{row.name}</div>
                      <div className="table-col col-kolicina">
                        {formatNumber(row.quantity)}
                      </div>
                      <div className="table-col col-trosak">
                        {formatCurrency(row.total_cost)}
                      </div>
                      <div
                        className={`table-col col-profit ${
                          row.profitability >= 0
                            ? "profit-positive"
                            : "profit-negative"
                        }`}
                      >
                        <span className="arrow">
                          {row.profitability >= 0 ? "▲" : "▼"}
                        </span>
                        {formatProfitability(row.profitability)}
                      </div>
                    </div>
                  ))}
                  {(reportsData.data || []).length > 0 && (
                    <div className="table-row summary-row">
                      <div className="table-col col-proizvod">UKUPNO:</div>
                      <div className="table-col col-kolicina">
                        {formatNumber(reportsData.total_quantity)} kom
                      </div>
                      <div className="table-col col-trosak">
                        {formatCurrency(reportsData.total_cost)}
                      </div>
                      <div
                        className={`table-col col-profit ${
                          reportsData.total_profitability >= 0
                            ? "profit-positive"
                            : "profit-negative"
                        }`}
                      >
                        <span className="arrow">
                          {reportsData.total_profitability >= 0 ? "▲" : "▼"}
                        </span>
                        {formatProfitability(reportsData.total_profitability)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Reports;
