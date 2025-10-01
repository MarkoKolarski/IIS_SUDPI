import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import MainSideBar from "../components/MainSideBar";
import EditSuppliersTable from "../components/EditSuppliersTable";
import "../styles/EditSuppliers.css";

const EditSuppliers = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleAddSupplier = () => {
    navigate("/edit/supplier/new");
  };

  return (
    <div
      className={`edit-suppliers-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="edit-suppliers-main-content">
        <header className="edit-suppliers-header">
          <h1>Upravljanje dobavljačima</h1>
          <button className="add-supplier-btn" onClick={handleAddSupplier}>
            + Dodaj dobavljača
          </button>
        </header>

        <div className="edit-suppliers-content">
          <EditSuppliersTable />
        </div>
      </main>
    </div>
  );
};

export default EditSuppliers;
