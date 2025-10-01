import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Register from "./pages/Register.js";
import Login from "./pages/Login.js";

import DashboardFA from "./pages/DashboardFA.js";
import Invoice from "./pages/Invoice.js";
import InvoiceDetails from "./pages/InvoiceDetails.js";
import Reports from "./pages/Reports.js";
import Penalties from "./pages/Penalties.js";

import DashboardNM from "./pages/DashboardNM.js";
import Suppliers from "./pages/Suppliers.js";
import DashboardKK from "./pages/DashboardKK.js";
import Visits from "./pages/Visits.js";
import Complaints from "./pages/Complaints.js";
import ComplaintCreate from "./pages/ComplaintCreate.js";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        <Route path="/dashboard-fa" element={<DashboardFA />} />
        <Route path="/invoice" element={<Invoice />} />
        <Route
          path="/invoice-details/:invoiceId"
          element={<InvoiceDetails />}
        />
        <Route path="/reports" element={<Reports />} />
        <Route path="/penalties" element={<Penalties />} />

        <Route path="/dashboard-nm" element={<DashboardNM />} />
        <Route path="/suppliers" element={<Suppliers />} />

        {/* Kontrolor Kvaliteta routes */}
        <Route path="/dashboard-kk" element={<DashboardKK />} />
        <Route path="/visits" element={<Visits />} />
        <Route path="/complaints" element={<Complaints />} />
        <Route
          path="/complaints/create/:supplierId"
          element={<ComplaintCreate />}
        />
      </Routes>
    </Router>
  );
};

export default App;
