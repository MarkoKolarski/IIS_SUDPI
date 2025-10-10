document.addEventListener("DOMContentLoaded", function () {
  // Initialize Select2
  if ($.fn.select2) {
    $("#supplierCompare").select2({
      placeholder: "Izaberite dobavljače za poređenje",
      width: "100%",
    });
  }

  // Check if the microservice is available
  checkServiceHealth();

  // Load suppliers list
  loadSuppliers();

  // Setup event listeners
  setupEventListeners();
});

function checkServiceHealth() {
  fetch("/api/supplier-analysis/health/")
    .then((response) => response.json())
    .then((data) => {
      const statusBadge = document.getElementById("serviceStatus");
      if (data.status === "online") {
        statusBadge.textContent = "Servis dostupan";
        statusBadge.classList.remove("status-offline");
        statusBadge.classList.add("status-online");
      } else {
        statusBadge.textContent = "Servis nije dostupan";
        statusBadge.classList.remove("status-online");
        statusBadge.classList.add("status-offline");
      }
    })
    .catch((error) => {
      console.error("Error checking service health:", error);
      const statusBadge = document.getElementById("serviceStatus");
      statusBadge.textContent = "Greška pri proveri servisa";
      statusBadge.classList.remove("status-online");
      statusBadge.classList.add("status-offline");
    });
}

function loadSuppliers() {
  showSpinner();
  fetch("/api/supplier-analysis/suppliers/") // Changed from "/suppliers/"
    .then((response) => response.json())
    .then((suppliers) => {
      const supplierSelect = document.getElementById("supplierId");
      const supplierCompare = document.getElementById("supplierCompare");

      // Clear existing options
      supplierSelect.innerHTML =
        '<option value="">-- Izaberite dobavljača --</option>';
      supplierCompare.innerHTML = "";

      // Add suppliers to both selects
      suppliers.forEach((supplier) => {
        const option1 = document.createElement("option");
        option1.value = supplier.sifra_d;
        option1.textContent = `${supplier.naziv} (${supplier.ime_sirovine})`;
        supplierSelect.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = supplier.sifra_d;
        option2.textContent = `${supplier.naziv} (${supplier.ime_sirovine})`;
        supplierCompare.appendChild(option2);
      });

      // Extract unique material names
      const materialNames = [...new Set(suppliers.map((s) => s.ime_sirovine))];

      const materialSelect = document.getElementById("materialName");
      const altMaterialSelect = document.getElementById("altMaterialName");

      // Clear existing options
      materialSelect.innerHTML =
        '<option value="">-- Izaberite materijal --</option>';
      altMaterialSelect.innerHTML =
        '<option value="">-- Izaberite materijal --</option>';

      // Add material options
      materialNames.forEach((material) => {
        const option1 = document.createElement("option");
        option1.value = material;
        option1.textContent = material;
        materialSelect.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = material;
        option2.textContent = material;
        altMaterialSelect.appendChild(option2);
      });

      hideSpinner();
    })
    .catch((error) => {
      console.error("Error loading suppliers:", error);
      hideSpinner();
      showAlert(
        "Greška pri učitavanju dobavljača. Pokušajte ponovo.",
        "danger"
      );
    });
}

function setupEventListeners() {
  // Sync buttons
  document
    .getElementById("syncSuppliers")
    .addEventListener("click", syncSuppliers);
  document
    .getElementById("syncComplaints")
    .addEventListener("click", syncComplaints);
  document
    .getElementById("syncCertificates")
    .addEventListener("click", syncCertificates);

  // Report forms
  document
    .getElementById("supplierReportForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      generateSupplierReport();
    });

  document
    .getElementById("comparisonReportForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      generateComparisonReport();
    });

  document
    .getElementById("materialReportForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      generateMaterialReport();
    });

  // Risk analysis button
  document
    .getElementById("getRiskAnalysis")
    .addEventListener("click", getRiskAnalysis);

  // Alternative suppliers form
  document
    .getElementById("alternativeSuppliersForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      findAlternativeSuppliers();
    });
}

function syncSuppliers() {
  showSpinner();
  fetch("/api/supplier-analysis/sync/suppliers/")
    .then((response) => response.json())
    .then((data) => {
      hideSpinner();
      showSyncResults(
        `Uspešno sinhronizovano ${data.success_count} od ${data.total_suppliers} dobavljača.`
      );
    })
    .catch((error) => {
      console.error("Error syncing suppliers:", error);
      hideSpinner();
      showSyncResults("Greška pri sinhronizaciji dobavljača.", true);
    });
}

function syncComplaints() {
  showSpinner();
  fetch("/api/supplier-analysis/sync/complaints/")
    .then((response) => response.json())
    .then((data) => {
      hideSpinner();
      showSyncResults(
        `Uspešno sinhronizovano ${data.success_count} od ${data.total_complaints} reklamacija.`
      );
    })
    .catch((error) => {
      console.error("Error syncing complaints:", error);
      hideSpinner();
      showSyncResults("Greška pri sinhronizaciji reklamacija.", true);
    });
}

function syncCertificates() {
  showSpinner();
  fetch("/api/supplier-analysis/sync/certificates/")
    .then((response) => response.json())
    .then((data) => {
      hideSpinner();
      showSyncResults(
        `Uspešno sinhronizovano ${data.success_count} od ${data.total_certificates} sertifikata.`
      );
    })
    .catch((error) => {
      console.error("Error syncing certificates:", error);
      hideSpinner();
      showSyncResults("Greška pri sinhronizaciji sertifikata.", true);
    });
}

function showSyncResults(message, isError = false) {
  const resultsDiv = document.getElementById("syncResults");
  resultsDiv.textContent = message;
  resultsDiv.style.display = "block";

  if (isError) {
    resultsDiv.classList.remove("alert-info");
    resultsDiv.classList.add("alert-danger");
  } else {
    resultsDiv.classList.remove("alert-danger");
    resultsDiv.classList.add("alert-info");
  }

  // Hide after 5 seconds
  setTimeout(() => {
    resultsDiv.style.display = "none";
  }, 5000);
}

function generateSupplierReport() {
  const supplierId = document.getElementById("supplierId").value;

  if (!supplierId) {
    showAlert("Molimo izaberite dobavljača.", "warning");
    return;
  }

  // Open report in new window
  window.open(
    `/api/supplier-analysis/reports/supplier/${supplierId}/`,
    "_blank"
  );
}

function generateComparisonReport() {
  const supplierIds = Array.from(
    document.getElementById("supplierCompare").selectedOptions
  ).map((option) => option.value);

  if (supplierIds.length < 2) {
    showAlert(
      "Molimo izaberite najmanje dva dobavljača za poređenje.",
      "warning"
    );
    return;
  }

  // Send POST request for comparison report
  showSpinner();

  fetch("/api/supplier-analysis/reports/supplier-comparison/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ supplier_ids: supplierIds }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then((blob) => {
      hideSpinner();
      // Create URL for the blob and open in new window
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");
    })
    .catch((error) => {
      console.error("Error generating comparison report:", error);
      hideSpinner();
      showAlert("Greška pri generisanju uporednog izveštaja.", "danger");
    });
}

function generateMaterialReport() {
  const materialName = document.getElementById("materialName").value;

  if (!materialName) {
    showAlert("Molimo izaberite materijal.", "warning");
    return;
  }

  // Use POST method to avoid URL encoding issues with UTF-8 characters
  showSpinner();

  fetch("/api/supplier-analysis/reports/material/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      material_name: materialName,
      min_rating: 0.0,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then((blob) => {
      hideSpinner();
      // Create URL for the blob and open in new window
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");

      // Clean up the URL after a delay
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 10000);
    })
    .catch((error) => {
      console.error("Error generating material report:", error);
      hideSpinner();
      showAlert("Greška pri generisanju izveštaja za materijal.", "danger");
    });
}

function generatePerformanceTrendsReport() {
  window.open(`/api/supplier-analysis/reports/performance-trends/`, "_blank");
}

function generateRiskAnalysisReport() {
  window.open(`/api/supplier-analysis/reports/risk-analysis/`, "_blank");
}

function findAlternativeSuppliers() {
  const materialName = document.getElementById("altMaterialName").value;
  const minRating = document.getElementById("minRating").value;

  if (!materialName) {
    showAlert("Molimo izaberite materijal.", "warning");
    return;
  }

  showSpinner();

  // Use POST method for better UTF-8 support
  fetch("/api/supplier-analysis/analysis/alternative-suppliers/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      material_name: materialName,
      min_rating: parseFloat(minRating) || 0.0,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      hideSpinner();

      if (data && data.suppliers) {
        const alternativeTable = document.getElementById("alternativeTable");
        alternativeTable.innerHTML = "";

        if (data.suppliers.length === 0) {
          document.getElementById("alternativeResults").style.display = "block";
          alternativeTable.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center">Nema alternativnih dobavljača za ovaj materijal</td>
                        </tr>
                    `;
          return;
        }

        data.suppliers.forEach((supplier) => {
          const row = document.createElement("tr");

          row.innerHTML = `
                        <td>${supplier.name}</td>
                        <td>${supplier.rating}/10</td>
                        <td>${supplier.price} RSD</td>
                        <td>${supplier.delivery_time} dana</td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="generateSupplierReportDirect(${supplier.supplier_id})">
                                <i class="far fa-file-pdf"></i> Izveštaj
                            </button>
                        </td>
                    `;

          alternativeTable.appendChild(row);
        });

        document.getElementById("alternativeResults").style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error finding alternative suppliers:", error);
      hideSpinner();
      showAlert("Greška pri pretraživanju alternativnih dobavljača.", "danger");
    });
}

// Helper function to generate supplier report directly
function generateSupplierReportDirect(supplierId) {
  window.open(
    `/api/supplier-analysis/reports/supplier/${supplierId}/`,
    "_blank"
  );
}

function showSpinner() {
  document.getElementById("spinner").classList.add("show");
}

function hideSpinner() {
  document.getElementById("spinner").classList.remove("show");
}

function showAlert(message, type = "info") {
  // Create alert element
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = "alert";

  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;

  // Insert at the top of the container
  const container = document.querySelector(".container");
  container.insertBefore(alertDiv, container.firstChild);

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove("show");
    setTimeout(() => {
      alertDiv.remove();
    }, 150);
  }, 5000);
}

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getRiskAnalysis() {
  showSpinner();
  fetch("/api/supplier-analysis/risk-analysis/")
    .then((response) => response.json())
    .then((data) => {
      hideSpinner();

      if (data && data.patterns) {
        const riskTable = document.getElementById("riskTable");
        riskTable.innerHTML = "";

        if (data.patterns.length === 0) {
          document.getElementById("riskAnalysisResults").style.display =
            "block";
          riskTable.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">Nema rizičnih dobavljača</td>
                        </tr>
                    `;
          return;
        }

        data.patterns.forEach((pattern) => {
          const row = document.createElement("tr");

          // Add risk class to the row
          if (pattern.risk_level === "high_risk") {
            row.classList.add("table-danger");
          } else if (pattern.risk_level === "medium_risk") {
            row.classList.add("table-warning");
          }

          row.innerHTML = `
                        <td>${pattern.supplier_name}</td>
                        <td>${pattern.material}</td>
                        <td>${pattern.complaint_count}</td>
                        <td>
                            <span class="risk-${
                              pattern.risk_level === "high_risk"
                                ? "high"
                                : pattern.risk_level === "medium_risk"
                                ? "medium"
                                : "low"
                            }">
                                ${
                                  pattern.risk_level === "high_risk"
                                    ? "Visok rizik"
                                    : pattern.risk_level === "medium_risk"
                                    ? "Srednji rizik"
                                    : "Nizak rizik"
                                }
                            </span>
                        </td>
                    `;

          riskTable.appendChild(row);
        });

        document.getElementById("riskAnalysisResults").style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error getting risk analysis:", error);
      hideSpinner();
      showAlert("Greška pri dobavljanju analize rizika.", "danger");
    });
}
