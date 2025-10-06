import React, { useState } from "react";
import "../styles/DashboardNM.css";
import MainSideBar from "../components/MainSideBar";
import SuppliersTable from "../components/SuppliersTable";

const Suppliers = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div
      className={`dashboard-fa-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-fa-main-content">
        <header className="dashboard-header">
          <h1>Pregled dobavljača</h1>
        </header>

        <div className="dashboard-content">
          <SuppliersTable />
        </div>
      </main>
    </div>
  );
};

export default Suppliers;
