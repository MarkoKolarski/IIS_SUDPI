import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
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
import ScheduleVisit from "./pages/ScheduleVisit.js";
import DashboardAdmin from "./pages/DashboardAdmin";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        {/* Finansijski analiticar routes */}
        <Route
          path="/dashboard-fa"
          element={
            <ProtectedRoute allowedRoles={["finansijski_analiticar"]}>
              <DashboardFA />
            </ProtectedRoute>
          }
        />
        <Route
          path="/invoice"
          element={
            <ProtectedRoute allowedRoles={["finansijski_analiticar"]}>
              <Invoice />
            </ProtectedRoute>
          }
        />
        <Route
          path="/invoice-details/:invoiceId"
          element={
            <ProtectedRoute allowedRoles={["finansijski_analiticar"]}>
              <InvoiceDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["finansijski_analiticar"]}>
              <Reports />
            </ProtectedRoute>
          }
        />

        {/* Shared routes between FA and NM */}
        <Route
          path="/penalties"
          element={
            <ProtectedRoute
              allowedRoles={["finansijski_analiticar", "nabavni_menadzer"]}
            >
              <Penalties />
            </ProtectedRoute>
          }
        />

        {/* Nabavni menadzer routes */}
        <Route
          path="/dashboard-nm"
          element={
            <ProtectedRoute allowedRoles={["nabavni_menadzer"]}>
              <DashboardNM />
            </ProtectedRoute>
          }
        />

        {/* Shared routes between NM and KK */}
        <Route
          path="/suppliers"
          element={
            <ProtectedRoute
              allowedRoles={["nabavni_menadzer", "kontrolor_kvaliteta"]}
            >
              <Suppliers />
            </ProtectedRoute>
          }
        />

        {/* Kontrolor kvaliteta routes */}
        <Route
          path="/dashboard-kk"
          element={
            <ProtectedRoute allowedRoles={["kontrolor_kvaliteta"]}>
              <DashboardKK />
            </ProtectedRoute>
          }
        />
        <Route
          path="/visits"
          element={
            <ProtectedRoute allowedRoles={["kontrolor_kvaliteta"]}>
              <Visits />
            </ProtectedRoute>
          }
        />
        <Route
          path="/complaints"
          element={
            <ProtectedRoute allowedRoles={["kontrolor_kvaliteta"]}>
              <Complaints />
            </ProtectedRoute>
          }
        />
        <Route
          path="/complaints/create/:supplierId"
          element={
            <ProtectedRoute allowedRoles={["kontrolor_kvaliteta"]}>
              <ComplaintCreate />
            </ProtectedRoute>
          }
        />
        <Route
          path="/visits/schedule/:supplierId"
          element={
            <ProtectedRoute allowedRoles={["kontrolor_kvaliteta"]}>
              <ScheduleVisit />
            </ProtectedRoute>
          }
        />

        {/* Admin routes */}
        <Route
          path="/dashboard-admin"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <DashboardAdmin />
            </ProtectedRoute>
          }
        />
        <Route
          path="/register"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <Register />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit/suppliers"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <Suppliers />
            </ProtectedRoute>
          }
        />

        {/* Catch all route - redirect to appropriate dashboard or login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
