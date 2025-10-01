import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import MainSideBar from "../components/MainSideBar";
import "react-calendar/dist/Calendar.css";
import "../styles/DashboardKK.css";
import axiosInstance from "../axiosInstance";

export const sidebarLinksKK = [
  {
    href: "/dashboard-kk",
    title: "Kontrolna tabla",
    description: "Pregled zakazanih poseta",
  },
  {
    href: "/visits",
    title: "Planiranje poseta",
    description: "Zakazivanje poseta dobavljačima",
  },
  {
    href: "/complaints",
    title: "Reklamacije",
    description: "Upravljanje reklamacijama",
  },
];

const DashboardKK = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVisits = async () => {
      try {
        const response = await axiosInstance.get("/visits/");
        setVisits(response.data);
        setError(null);
      } catch (err) {
        setError("Greška pri učitavanju poseta");
        console.error("Error fetching visits:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchVisits();
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  // Function to check if a date has visits
  const hasVisits = (date) => {
    return visits.some((visit) => {
      const visitDate = new Date(visit.datum_od);
      return visitDate.toDateString() === date.toDateString();
    });
  };

  // Function to get visits for a specific date
  const getVisitsForDate = (date) => {
    return visits.filter((visit) => {
      const visitDate = new Date(visit.datum_od);
      return visitDate.toDateString() === date.toDateString();
    });
  };

  return (
    <div
      className={`dashboard-kk-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
        links={sidebarLinksKK}
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
      />
      <main className="dashboard-kk-main-content">
        <header className="dashboard-header">
          <h1>Kontrolna tabla - Kontrolor kvaliteta</h1>
        </header>

        {loading && (
          <div className="loading-message">Učitavanje podataka...</div>
        )}
        {error && <div className="error-message">{error}</div>}

        {!loading && !error && (
          <div className="dashboard-content">
            <div className="calendar-section">
              <Calendar
                className="visits-calendar"
                tileClassName={({ date }) =>
                  hasVisits(date) ? "has-visits" : null
                }
                tileContent={({ date }) => {
                  const dayVisits = getVisitsForDate(date);
                  return dayVisits.length > 0 ? (
                    <div className="visit-indicator">{dayVisits.length}</div>
                  ) : null;
                }}
              />
            </div>

            <div className="upcoming-visits">
              <h2>Predstojeće posete</h2>
              <div className="visits-list">
                {visits
                  .filter((visit) => new Date(visit.datum_od) >= new Date())
                  .sort((a, b) => new Date(a.datum_od) - new Date(b.datum_od))
                  .map((visit, index) => (
                    <div key={visit.poseta_id} className="visit-item">
                      <div className="visit-date">
                        {new Date(visit.datum_od).toLocaleDateString()}
                      </div>
                      <div className="visit-details">
                        <span className="visit-supplier">
                          {visit.dobavljac}
                        </span>
                        <span className="visit-status">{visit.status}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardKK;
