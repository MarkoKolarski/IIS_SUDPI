import React, { useEffect, useState, useCallback } from "react";
import "../styles/PregledRuta.css";
import axiosInstance from "../axiosInstance";
import MainSideBar from "../components/MainSideBar.js";
import MapComponent from "../components/MapComponent.js";

export default function PregledRuta({ sidebarCollapsed = false }) {
  const [rute, setRute] = useState([]);
  const [selektovanaRuta, setSelektovanaRuta] = useState(null);
  const [temperatureSve, setTemperatureSve] = useState({});
  const [pozicijeSve, setPozicijeSve] = useState({});
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(sidebarCollapsed);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggleSidebar = () => setIsSidebarCollapsed((prev) => !prev);

  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
    ucitajAktivneRute();
  }, []);

  // 🔹 Funkcija za učitavanje svih aktivnih ruta
  const ucitajAktivneRute = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axiosInstance.get("api/rute/aktivne/");
      setRute(response.data || []);
    } catch (err) {
      console.error("Greška pri učitavanju ruta:", err);
      setError("Greška pri učitavanju ruta.");
    } finally {
      setLoading(false);
    }
  };

  // ✅ Pokretanje simulacija za rutu (ako već nije pokrenuta)
  const pokreniSimulacije = async (ruta) => {
    try {
      await axiosInstance.get(`api/simulacija-rute/${ruta.sifra_r}/`);
      await axiosInstance.get(`api/simulacija-temperature/${ruta.sifra_r}/`);
      console.log(`Simulacije pokrenute za rutu ${ruta.sifra_r}`);
    } catch (err) {
      console.warn(`Simulacije već pokrenute ili nisu dostupne za rutu ${ruta.sifra_r}`);
    }
  };

  // ✅ Kada se klikne na rutu u tabeli
  const prikaziRutu = async (ruta) => {
    setSelektovanaRuta(ruta);
    await pokreniSimulacije(ruta);
  };

  // ✅ Učitavanje svih trenutnih pozicija (svakih 5 sekundi)
  const ucitajSvePozicije = useCallback(async () => {
    try {
      const novePozicije = {};
      for (const ruta of rute) {
        try { 
          const res = await axiosInstance.get(`api/voznje/${ruta.sifra_r}/trenutna/`);
          if (res.data && res.data.includes(",")) {
            const [lat, lon] = res.data.split(",").map(Number);
            novePozicije[ruta.sifra_r] = { lat, lon };
          }
        } catch {
          // može biti da simulacija još nije startovala
        }
      }
      setPozicijeSve((prev) => ({ ...prev, ...novePozicije }));
    } catch (err) {
      console.warn("Greška pri dobijanju pozicija:", err);
    }
  }, [rute]);

  // ✅ Učitavanje svih temperatura (svakih 5 sekundi)
  const ucitajSveTemperature = useCallback(async () => {
    try {
      const noveTemperature = {};
      for (const ruta of rute) {
        try {
          const res = await axiosInstance.get(`api/temperature/ruta/${ruta.sifra_r}/`);
          if (Array.isArray(res.data)) {
            noveTemperature[ruta.sifra_r] = res.data.reverse(); // najstariji prvi
          }
        } catch {
          // još nema temperature za ovu rutu
        }
      }
      setTemperatureSve((prev) => ({ ...prev, ...noveTemperature }));
    } catch (err) {
      console.warn("Greška pri dobijanju temperatura:", err);
    }
  }, [rute]);

  // 🔁 Periodično osvežavanje svih ruta (pozicije i temperature)
  useEffect(() => {
    if (!rute.length) return;
    ucitajSvePozicije();
    ucitajSveTemperature();
    const interval = setInterval(() => {
      ucitajSvePozicije();
      ucitajSveTemperature();
    }, 5000);
    return () => clearInterval(interval);
  }, [rute, ucitajSvePozicije, ucitajSveTemperature]);

  // ✅ Graf temperature za selektovanu rutu
  const renderTemperaturaGraf = () => {
    if (!selektovanaRuta) return <p className="prazno">Izaberi rutu.</p>;

    const podaci = temperatureSve[selektovanaRuta.sifra_r] || [];
    if (!podaci.length)
      return <p className="prazno">Nema podataka o temperaturi za ovu rutu.</p>;

    const granicaMax = parseFloat(podaci[0]?.max_granica ?? 30);
    const granicaMin = parseFloat(podaci[0]?.min_granica ?? 0);

    return (
      <>
        <div className="graf-container">
          <h4>Graf temperature</h4>
          <svg viewBox="0 0 800 350" className="graf">
            {(() => {
            // 1️⃣ Pronađi minimalnu i maksimalnu vrednost u podacima
            const sveVrednosti = podaci.map(t => parseFloat(t.vrednost || 0));
            const minVrednost = Math.min(...sveVrednosti, granicaMin);
            const maxVrednost = Math.max(...sveVrednosti, granicaMax);

            // 2️⃣ Izračunaj skalu da graf lepo zauzme vertikalni prostor
            const padding = 2; // dodatak da se ne lepi za ivice
            const raspon = (maxVrednost - minVrednost) || 1;
            const visina = 350;

            const scaleY = (temp) =>
                visina - ((temp - (minVrednost - padding)) / (raspon + padding * 2)) * visina;

            // 3️⃣ Crtamo crvene linije granica
            return (
                <>
                <line x1="0" y1={scaleY(granicaMax)} x2="800" y2={scaleY(granicaMax)} className="granica" />
                <line x1="0" y1={scaleY(granicaMin)} x2="800" y2={scaleY(granicaMin)} className="granica" />

                {/* 4️⃣ Glavna linija temperature */}
                {podaci.map((t, i) => {
                    const next = podaci[i + 1];
                    if (!next) return null;
                    const x1 = (i / (podaci.length - 1)) * 800;
                    const x2 = ((i + 1) / (podaci.length - 1)) * 800;
                    const y1 = scaleY(parseFloat(t.vrednost));
                    const y2 = scaleY(parseFloat(next.vrednost));
                    return (
                    <line
                        key={i}
                        x1={x1}
                        y1={y1}
                        x2={x2}
                        y2={y2}
                        className="linija-temp"
                    />
                    );
                })}
                </>
            );
            })()}
            </svg>

        </div>

        <table className="tabela-temperatura">
          <thead>
            <tr>
              <th>Vreme</th>
              <th>Vrednost (°C)</th>
              <th>Min</th>
              <th>Max</th>
            </tr>
          </thead>
          <tbody>
            {podaci.map((t, i) => (
              <tr key={i}>
                <td>{t.vreme}</td>
                <td>{parseFloat(t.vrednost).toFixed(2)}</td>
                <td>{parseFloat(t.min_granica).toFixed(1)}</td>
                <td>{parseFloat(t.max_granica).toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </>
    );
  };

  // ✅ Render glavnog layouta
  return (
    <div
      className={`pregled-ruta-container ${
        isSidebarCollapsed ? "sidebar-collapsed" : "sidebar-expanded"
      }`}
    >
      <MainSideBar
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={toggleSidebar}
        activePage="pregled_ruta"
      />

      {/* Leva kolona - liste ruta */}
      <div className="leva-kolona">
        <h3>Aktivne rute</h3>

        {error && (
          <div className="error-message">
            {error}
            <button onClick={ucitajAktivneRute} style={{ marginLeft: "10px" }}>
              Pokušaj ponovo
            </button>
          </div>
        )}

        {loading ? (
          <p>Učitavanje ruta...</p>
        ) : rute.length ? (
          <table className="tabela-rute">
            <thead>
              <tr>
                <th>ID</th>
                <th>Polazna tačka</th>
                <th>Odredište</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rute.map((ruta) => (
                <tr
                  key={ruta.sifra_r}
                  className={`${
                    selektovanaRuta?.sifra_r === ruta.sifra_r ? "selektovana" : ""
                  } ${ruta.status === "odstupanje" ? "status-odstupanje" : ""}`}
                  onClick={() => prikaziRutu(ruta)}
                >
                  <td>{ruta.sifra_r}</td>
                  <td>{ruta.polazna_tacka}</td>
                  <td>{ruta.odrediste}</td>
                  <td>{ruta.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="prazno">Nema aktivnih ruta.</p>
        )}
      </div>

      {/* Desna kolona - mapa + temperatura */}
      <div className="desna-kolona">
        <div className="mapa-sekcija">
          <h3>
            Mapa rute{" "}
            {selektovanaRuta ? `- Ruta ${selektovanaRuta.sifra_r}` : ""}
          </h3>
          {selektovanaRuta ? (
            <MapComponent
              ruta={selektovanaRuta}
              trenutnaPozicija={
                pozicijeSve[selektovanaRuta.sifra_r] || null
              }
            />
          ) : (
            <div className="mapa-fallback">
              <p>Klikni na rutu da je prikažeš na mapi.</p>
            </div>
          )}
        </div>

        <div className="temperatura-sekcija">
          <h3>
            Temperatura u vozilu{" "}
            {selektovanaRuta ? `- Ruta ${selektovanaRuta.sifra_r}` : ""}
          </h3>
          {renderTemperaturaGraf()}
        </div>
      </div>
    </div>
  );
}

// import React, { useEffect, useState } from "react";
// import "../styles/PregledRuta.css";
// import axiosInstance from "../axiosInstance";
// import MainSideBar from "../components/MainSideBar";

// export default function PregledRuta({ sidebarCollapsed }) {
//   const [rute, setRute] = useState([]);
//   const [selektovanaRuta, setSelektovanaRuta] = useState(null);
//   const [mapPreviewUrl, setMapPreviewUrl] = useState("");
//   const [temperaturaPodaci, setTemperaturaPodaci] = useState([]);
//   const [trenutnaPozicija, setTrenutnaPozicija] = useState(null);
//   const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
//   const toggleSidebar = () => setIsSidebarCollapsed(!isSidebarCollapsed);

//   // Učitaj aktivne rute
//   useEffect(() => {
//     axiosInstance
//       .get("/api/rute/aktivne/")
//       .then((response) => setRute(response.data))
//       .catch((error) => console.error("Greška pri učitavanju ruta:", error));
//   }, []);

//   // Klik na red tabele
//   const prikaziRutu = async (ruta) => {
//     try {
//       setSelektovanaRuta(ruta);

//       // Mapa rute
//       const mapResponse = await axiosInstance.get(`api/rute/${ruta.sifra_r}/map-preview/`);
//       setMapPreviewUrl(mapResponse.data.map_url);

//       // Temperatura
//       const tempResponse = await axiosInstance.get(`api/temperature/isporuka/${ruta.sifra_r}/`);
//       setTemperaturaPodaci(tempResponse.data);

//       // Lokacija vozila
//       startTracking(ruta.sifra_r);
//     } catch (err) {
//       console.error("Greška pri učitavanju podataka za rutu:", err);
//     }
//   };

//   // Praćenje pozicije vozila
//   const startTracking = (rutaId) => {
//     stopTracking();
//     const interval = setInterval(async () => {
//       try {
//         const pozResponse = await axiosInstance.get(`/api/voznje/${rutaId}/trenutna/`);
//         const [lat, lon] = pozResponse.data.split(",");
//         setTrenutnaPozicija({ lat: parseFloat(lat), lon: parseFloat(lon) });
//       } catch {
//         console.warn("Greška pri dobijanju pozicije");
//       }
//     }, 3000);
//     window._trackingInterval = interval;
//   };

//   const stopTracking = () => {
//     if (window._trackingInterval) clearInterval(window._trackingInterval);
//   };

//   // Render mape
//   const renderMapa = () => {
//     if (!mapPreviewUrl)
//       return <p className="prazno">Klikni na rutu da je prikažeš na mapi.</p>;
//     return (
//       <iframe
//         title="Pregled rute"
//         src={mapPreviewUrl}
//         className="mapa"
//         allowFullScreen
//       ></iframe>
//     );
//   };

//   // Render grafa
//   const renderTemperaturaGraf = () => {
//     if (!temperaturaPodaci.length)
//       return <p className="prazno">Nema podataka o temperaturi.</p>;

//     const granicaMax = parseFloat(temperaturaPodaci[0].max_granica);
//     const granicaMin = parseFloat(temperaturaPodaci[0].min_granica);

//     return (
//       <div className="graf-container">
//         <svg viewBox="0 0 400 200" className="graf">
//           <line x1="0" y1={200 - granicaMax} x2="400" y2={200 - granicaMax} className="granica" />
//           <line x1="0" y1={200 - granicaMin} x2="400" y2={200 - granicaMin} className="granica" />

//           {temperaturaPodaci.map((t, i) => {
//             const next = temperaturaPodaci[i + 1];
//             if (!next) return null;
//             const x1 = (i / temperaturaPodaci.length) * 400;
//             const x2 = ((i + 1) / temperaturaPodaci.length) * 400;
//             const y1 = 200 - parseFloat(t.vrednost);
//             const y2 = 200 - parseFloat(next.vrednost);
//             return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} className="linija-temp" />;
//           })}
//         </svg>
//         <div className="graf-legenda">
//           <span className="crvena">Crveno = granice</span>
//           <span className="plava">Zeleno = temperatura</span>
//         </div>
//       </div>
//     );
//   };

//   return (
//     <div
//       className={`pregled-ruta-container ${isSidebarCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}`}
//     >
//     {/* <div className="pregled-ruta-dashboard-header">
//         <h1>Pregled ruta koje su u toku</h1>
//     <div/> */}
//         <MainSideBar
//         isCollapsed={isSidebarCollapsed}
//         toggleSidebar={toggleSidebar}
//         activePage="edit_profile"
//       />
//       <div className="leva-kolona">
//         <h3>Aktivne rute</h3>
//         <p><i>Selektuj aktivnu rutu:</i></p>
//         <table className="tabela-rute">
//           <thead>
//             <tr>
//               <th>ID</th>
//               <th>Polazna tačka</th>
//               <th>Odredište</th>
//               <th>Status</th>
//             </tr>
//           </thead>
//           <tbody>
//             {rute.map((ruta) => (
//               <tr
//                 key={ruta.sifra_r}
//                 className={selektovanaRuta?.sifra_r === ruta.sifra_r ? "selektovana" : ""}
//                 onClick={() => prikaziRutu(ruta)}
//               >
//                 <td>{ruta.sifra_r}</td>
//                 <td>{ruta.polazna_tacka}</td>
//                 <td>{ruta.odrediste}</td>
//                 <td>{ruta.status}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>

//       <div className="desna-kolona">
//         <div className="mapa-sekcija">
//           <h3>Mapa rute</h3>
//           {renderMapa()}
//           {trenutnaPozicija && (
//             <p className="pozicija-info">
//               Trenutna pozicija: lat {trenutnaPozicija.lat.toFixed(5)}, lon{" "}
//               {trenutnaPozicija.lon.toFixed(5)}
//             </p>
//           )}
//         </div>

//         <div className="temperatura-sekcija">
//           <h3>Temperatura u vozilu</h3>
//           {renderTemperaturaGraf()}
//         </div>
//       </div>
      
//     </div>
//   );
// }
