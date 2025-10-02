import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import MainSideBar from "../components/MainSideBar";
import axiosInstance from "../axiosInstance";
import "../styles/ScheduleVisit.css";

const ScheduleVisit = () => {
  const { supplierId } = useParams();
  const navigate = useNavigate();
  const [supplier, setSupplier] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [visitTime, setVisitTime] = useState("09:00");
  const [duration, setDuration] = useState(2);
  const [error, setError] = useState(null);
  const [busySlots, setBusySlots] = useState([]);

  useEffect(() => {
    const fetchSupplier = async () => {
      try {
        const response = await axiosInstance.get(`/suppliers/${supplierId}/`);
        setSupplier(response.data);
      } catch (err) {
        setError("Greška pri učitavanju dobavljača");
      }
    };

    const fetchBusySlots = async () => {
      try {
        const response = await axiosInstance.get("/visits/busy-slots/");
        setBusySlots(
          response.data.map((slot) => ({
            start: new Date(slot.datum_od),
            end: new Date(slot.datum_do),
          }))
        );
      } catch (err) {
        console.error("Error fetching busy slots:", err);
      }
    };

    fetchSupplier();
    fetchBusySlots();
  }, [supplierId]);

  const isDateBusy = (date) => {
    return busySlots.some((slot) => {
      const slotDate = new Date(slot.start);
      return slotDate.toDateString() === date.toDateString();
    });
  };

  const isTimeSlotBusy = (selectedDateTime) => {
    return busySlots.some((slot) => {
      const startTime = new Date(slot.start);
      const endTime = new Date(slot.end);
      return selectedDateTime >= startTime && selectedDateTime <= endTime;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const visitDate = new Date(selectedDate);
      const [hours, minutes] = visitTime.split(":");
      visitDate.setHours(parseInt(hours), parseInt(minutes));

      const endDate = new Date(visitDate);
      endDate.setHours(endDate.getHours() + duration);

      // Check if the selected time slot is busy
      if (isTimeSlotBusy(visitDate)) {
        setError(
          "Izabrani termin je već zauzet. Molimo izaberite drugi termin."
        );
        return;
      }

      await axiosInstance.post("/visits/create/", {
        dobavljac_id: supplierId,
        datum_od: visitDate.toISOString(),
        datum_do: endDate.toISOString(),
      });

      navigate("/visits");
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Greška pri zakazivanju posete");
      }
    }
  };

  const tileClassName = ({ date }) => {
    return isDateBusy(date) ? "busy" : "";
  };

  if (!supplier) return <div>Učitavanje...</div>;

  return (
    <div className="schedule-visit-wrapper">
      <MainSideBar isCollapsed={false} />
      <main className="schedule-visit-main">
        <header className="schedule-visit-header">
          <h1>Zakazivanje posete za dobavljača: {supplier.naziv}</h1>
        </header>

        <div className="schedule-visit-content">
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit} className="schedule-visit-form">
            <div className="calendar-section">
              <Calendar
                onChange={setSelectedDate}
                value={selectedDate}
                minDate={new Date()}
                className="visit-calendar"
                tileClassName={tileClassName}
              />
              {isDateBusy(selectedDate) && (
                <div className="time-slot-warning">
                  Izabrani datum ima već zakazane posete. Proverite dostupne
                  termine.
                </div>
              )}
            </div>

            <div className="visit-details">
              <div className="form-group">
                <label>Vreme posete:</label>
                <input
                  type="time"
                  value={visitTime}
                  onChange={(e) => setVisitTime(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Trajanje (sati):</label>
                <input
                  type="number"
                  min="1"
                  max="8"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  required
                />
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => navigate("/visits")}>
                  Odustani
                </button>
                <button type="submit">Zakaži posetu</button>
              </div>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default ScheduleVisit;
