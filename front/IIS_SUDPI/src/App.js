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
import EditSuppliers from "./pages/EditSuppliers";
import EditSupplier from "./pages/EditSupplier";
import DodajArtikal from "./pages/DodajArtikal";
import DodajSkladiste from "./pages/DodajSkladiste";
import PretragaArtikala from "./pages/PretragaArtikala";
import IzmeniArtikal from "./pages/IzmeniArtikal";
import PregledZaliha from "./pages/PregledZaliha";
import IzmenaZaliha from "./pages/IzmenaZaliha";
import DashboardSO from "./pages/DashboardSO";
import EditProfile from "./pages/EditProfile.js";
import EditOtherProfile from "./pages/EditOtherProfile.js";
import LogisticTransport from "./pages/LogisticTransport.js";
import EditVozilo from "./pages/VoziloEdit.js";
import DashboardLK from "./pages/DashboardLK.js";
import PlanIsporuke from "./pages/PlanIsporuke.js";
import Procedures from "./pages/Procedures.js";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<EditProfile />} />
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
        <Route
          path="/sbp-procedures"
          element={
            <ProtectedRoute allowedRoles={["finansijski_analiticar"]}>
              <Procedures />
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

        {/* Skladisni operater routes */}
        <Route
          path="/dashboard-so"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <DashboardSO />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dodaj-artikal"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <DodajArtikal />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dodaj-skladiste"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <DodajSkladiste />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pretraga-artikala"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <PretragaArtikala />
            </ProtectedRoute>
          }
        />
        <Route
          path="/izmeni-artikal/:sifra_a"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <IzmeniArtikal />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pregled-zaliha"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <PregledZaliha />
            </ProtectedRoute>
          }
        />
        <Route
          path="/izmena-zaliha/:zalihaId"
          element={
            <ProtectedRoute allowedRoles={["skladisni_operater"]}>
              <IzmenaZaliha />
            </ProtectedRoute>
          }
        />
        {/* Logisticki kordinator routes */}
        <Route
          path="/dashboard-lk"
          element={
            <ProtectedRoute allowedRoles={["logisticki_koordinator"]}>
              <DashboardLK />
            </ProtectedRoute>
          }
        />
        <Route
          path="/plan-isporuke/:isporukaId"
          element={
            <ProtectedRoute allowedRoles={["logisticki_koordinator"]}>
              <PlanIsporuke />
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
              <EditSuppliers />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit/supplier/:supplierId"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <EditSupplier />
            </ProtectedRoute>
          }
        />
        <Route
          path="/logistics-transport"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <LogisticTransport />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit-profile"
          element={
            <ProtectedRoute allowedRoles={["administrator"]}>
              <EditOtherProfile />
            </ProtectedRoute>
          }
        />
        <Route path="/vozila/update/:id" element={<EditVozilo />} />

        {/* Catch all route - redirect to appropriate dashboard or login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
