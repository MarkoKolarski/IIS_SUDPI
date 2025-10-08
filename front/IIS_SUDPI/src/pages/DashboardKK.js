import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import MainSideBar from "../components/MainSideBar";
import "react-calendar/dist/Calendar.css";
import "../styles/DashboardKK.css";
import axiosInstance from "../axiosInstance";
import {
  formatDateTimeSR,
  formatFullDateTimeSR,
  compareDates,
  isSameDay,
} from "../utils/dateUtils";

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

  // Function to get visits for a specific date
  const getVisitsForDate = (date) => {
    return visits.filter((visit) => {
      const visitDate = new Date(visit.datum_od);
      return isSameDay(visitDate, date);
    });
  };

  // Helper function to get today's visits
  const getTodayVisits = () => {
    const today = new Date();
    return visits.filter((visit) => {
      const visitDate = new Date(visit.datum_od);
      return isSameDay(visitDate, today);
    });
  };

  // Helper function to get visits by status
  const getVisitsByStatus = (status) => {
    return visits.filter((visit) => visit.status === status);
  };

  const updateVisitStatus = async (visitId, newStatus) => {
    try {
      await axiosInstance.put(`/visits/${visitId}/`, { status: newStatus });
      const response = await axiosInstance.get("/visits/");
      setVisits(response.data);
    } catch (err) {
      setError("Greška pri ažuriranju statusa posete");
      console.error("Error updating visit status:", err);
    }
  };

  // Helper function to calculate duration
  const calculateDuration = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const hours = Math.round(
      (end.getTime() - start.getTime()) / (1000 * 60 * 60)
    );
    return `${hours} ${hours === 1 ? "sat" : "sati"}`;
  };

  // Update the calendar tile class function
  const getTileClassName = ({ date }) => {
    const dayVisits = getVisitsForDate(date);
    if (dayVisits.length === 0) return "";

    const statusClasses = dayVisits.map(
      (visit) => `has-visits ${visit.status}`
    );
    return statusClasses.join(" ");
  };

  // Update the calendar tile content function
  const getTileContent = ({ date }) => {
    const dayVisits = getVisitsForDate(date);
    if (dayVisits.length === 0) return null;

    return (
      <div className="calendar-visits-info">
        <div className="visit-count">{dayVisits.length}</div>
        {dayVisits.map((visit, index) => (
          <div key={index} className={`visit-time ${visit.status}`}>
            {formatDateTimeSR(visit.datum_od, {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div
      className={`dashboard-kk-wrapper ${
        isSidebarCollapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <MainSideBar
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
          <div className="dashboard-grid">
            {/* Status Cards Column */}
            <div className="status-cards">
              <div className="status-card today">
                <h3>Današnje posete</h3>
                <div className="card-number">{getTodayVisits().length}</div>
              </div>
              <div className="status-card scheduled">
                <h3>Zakazane</h3>
                <div className="card-number">
                  {getVisitsByStatus("zakazana").length}
                </div>
              </div>
              <div className="status-card in-progress">
                <h3>U toku</h3>
                <div className="card-number">
                  {getVisitsByStatus("u_toku").length}
                </div>
              </div>
              <div className="status-card completed">
                <h3>Završene</h3>
                <div className="card-number">
                  {getVisitsByStatus("zavrsena").length}
                </div>
              </div>
            </div>

            <div className="vists-container">
              {/* Calendar Column */}
              <div className="calendar-container">
                <h2>Kalendar poseta</h2>
                <Calendar
                  className="visits-calendar"
                  tileClassName={getTileClassName}
                  tileContent={getTileContent}
                />
              </div>
              {/* Upcoming Visits Column */}
              <div className="upcoming-visits-container">
                <h2>Predstojeće posete</h2>
                <div className="visits-timeline">
                  {visits
                    .filter(
                      (visit) => compareDates(visit.datum_od, new Date()) >= 0
                    )
                    .sort((a, b) => compareDates(a.datum_od, b.datum_od))
                    .slice(0, 5)
                    .map((visit) => (
                      <div
                        key={visit.poseta_id}
                        className={`timeline-item ${visit.status}`}
                      >
                        <div className="timeline-date">
                          {formatDateTimeSR(visit.datum_od, {
                            day: "numeric",
                            month: "short",
                          })}
                        </div>
                        <div className="timeline-content">
                          <h4>{visit.dobavljac}</h4>
                          <div className="timeline-time">
                            {new Intl.DateTimeFormat("sr-RS", {
                              timeZone: "Europe/Belgrade",
                              hour: "2-digit",
                              minute: "2-digit",
                            }).format(new Date(visit.datum_od))}
                          </div>
                          <div className="visit-duration">
                            Trajanje:{" "}
                            {calculateDuration(visit.datum_od, visit.datum_do)}
                          </div>
                          <select
                            className="visit-status-select"
                            value={visit.status}
                            onChange={(e) =>
                              updateVisitStatus(visit.poseta_id, e.target.value)
                            }
                          >
                            <option value="zakazana">Zakazana</option>
                            <option value="u_toku">U toku</option>
                            <option value="zavrsena">Završena</option>
                            <option value="otkazana">Otkazana</option>
                          </select>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardKK;
