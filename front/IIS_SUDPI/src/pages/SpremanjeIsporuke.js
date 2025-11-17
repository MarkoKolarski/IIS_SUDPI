import React, { useState, useEffect } from "react";
import axiosInstance from "../axiosInstance";
import MainSideBar from "../components/MainSideBar";
import "../styles/SpremanjeIsporuke.css";

const SpremanjeIsporuke = () => {
  const [isporuke, setIsporuke] = useState([]);
  const [selectedIsporuka, setSelectedIsporuka] = useState(null);
  //const [skladiste, setSkladiste] = useState("");
  const [skladista, setSkladista] = useState([]);
  const [izabranoSkladiste, setIzabranoSkladiste] = useState(null);
  const [datumIsporuke, setDatumIsporuke] = useState("");
  const [spremnaKolicina, setSpremnaKolicina] = useState("");
  const [poruka, setPoruka] = useState("");
  const [vremeUtovara, setVremeUtovara] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [greskaKolicina, setGreskaKolicina] = useState("");


  useEffect(() => {
    axiosInstance
      .get("isporuke/u_toku/")
      .then((res) => setIsporuke(res.data))
      .catch((err) => console.error("Greška pri učitavanju isporuka:", err));
  }, []);
  useEffect(() => {
    const fetchSkladista = async () => {
      try { 
        const res = await axiosInstance.get("skladista/");
        setSkladista(res.data);
      } catch (err) {
        console.error("Greška pri učitavanju skladišta:", err);
      }
    };
    fetchSkladista();
  }, []);

  const handleSelectIsporuka = (isporuka) => {
    setSelectedIsporuka(isporuka);
    setDatumIsporuke(isporuka.datum_polaska?.split("T")[0] || "");
    setPoruka("");
    setGreskaKolicina(""); 
    // axiosInstance
    //   .get(`api/skladiste/${isporuka.sifra_i}`)
    //   .then((res) => setSkladiste(res.data.mesto_s))
    //   .catch((err) => console.error("Greška pri učitavanju isporuka:", err));
      //.then((res) => setSkladiste(res.data.naziv_s || res.data.mesto_s))
      //.catch(() => setSkladiste("Nije pronađeno"));
  };

  const validateKolicina = (kolicina) => {
    if (!selectedIsporuka) return "";
    
    const kolicinaNum = parseFloat(kolicina);
    const maxKolicina = parseFloat(selectedIsporuka.kolicina_kg);
    
    if (kolicinaNum > maxKolicina) {
      return `Količina ne sme da bude veća od ${maxKolicina} kg`;
    }
    if (kolicinaNum <= 0) {
      return "Količina mora biti veća od 0";
    }
    return "";
  };
  const handleSpremnaKolicinaChange = (e) => {
    const value = e.target.value;
    setSpremnaKolicina(value);
    
    const greska = validateKolicina(value);
    setGreskaKolicina(greska);
    
    if (greska) {
      setPoruka(greska);
    } else {
      setPoruka(""); 
    }
  };
  
  
  const handleDatumChange = async (e) => {
    const newDatum = e.target.value;
    setDatumIsporuke(newDatum);

    if (!selectedIsporuka) return;

    try {
      const res = await axiosInstance.get("api/izracunaj-datum-dolaska/", {
        params: {
          datum_isporuke: selectedIsporuka.datum_polaska,
          ruta_id: selectedIsporuka.ruta,
        },
      });
      setPoruka(
        `Novi datum dolaska: ${res.data.datum_dolaska} (vreme putovanja: ${res.data.vreme_putovanja_sati}h)`
      );

      // ažuriranje isporuke
      await axiosInstance.put(`api/isporuke/${selectedIsporuka.sifra_i}/`, {
        rok_is: newDatum,
      });
    } catch (error) {
      console.error("Greška pri promeni datuma:", error);
    }
  };

  // ----------------- Potvrđivanje i izračunavanje utovara -----------------
  const handlePotvrdi = async () => {
    if (!selectedIsporuka) {
      setPoruka("Selektuj isporuku pre potvrde.");
      return;
    }
    if (greskaKolicina) {
      setPoruka(greskaKolicina);
      return;
    }
    const finalnaGreska = validateKolicina(spremnaKolicina);
    if (finalnaGreska) {
      setPoruka(finalnaGreska);
      return;
    }

    try {
      // 1️⃣ proveri slobodne rampe
      const resRampe = await axiosInstance.get("api/rampe/aktivna/", {
         params: { status: "slobodna",
            skladiste: izabranoSkladiste.sifra_s
         },
       });
       if (resRampe.data.length === 0 ) {
         setPoruka("Sačekajte — nema slobodnih rampi.");
        //  await axiosInstance.post("/api/kreiraj_notifikaciju/", {
        //     poruka_n: "Nema slobodnih rampi za utovar.",  
        //  });
        }
      //const resRampe = await axiosInstance.get("api/rampe/aktivna/");
    //   const resRampe = await axiosInstance.get("api/rampe/", {
    //     params: { status: "slobodna" },
    //   });

    //   if (resRampe.data.length === 0) {
    //     setPoruka("Sačekajte — nema slobodnih rampi.");
    //     await axiosInstance.post("/api/kreiraj_notifikaciju/", {
    //       poruka_n: "Nema slobodnih rampi za utovar.",
    //       tip: "upozorenje",
    //     });
    //     return;
    //   }
      const resUtovar = await axiosInstance.get("api/izracunaj-vreme-utovara/", {
        params: {
          kolicina: spremnaKolicina || selectedIsporuka.kolicina_kg,
          vozilo: selectedIsporuka.vozilo,
        },
      });
      setVremeUtovara(resUtovar.data.vreme_utovara);
      setPoruka(`Slobodna rampa ${resRampe.data.oznaka} pronađena.`); // Vreme utovara: ${resUtovar.data.vreme_utovara} h
     
      //'/api/isporuke/${selectedIsporuka.sifra_i}/
      await axiosInstance.put(`api/rampe/${resRampe.data.sifra_rp}/`, {
        status: "zauzeta"
      });
      //await axiosInstance.put(`/api/rute/${selectedIsporuka.sifra_i}/`);
      console.log("Updating ruta", selectedIsporuka.ruta_id);
      if (selectedIsporuka?.ruta_id) {
        console.debug("Updating ruta", selectedIsporuka.ruta_id);
        await axiosInstance.put(`api/rute/spremna/${selectedIsporuka.ruta_id}/`, {
          status: "u_toku",
          vreme_utovara: resUtovar.data.vreme_utovara
        });
      } else {
        console.debug("No ruta id available on selectedIsporuka:", selectedIsporuka);
      }
            
      await axiosInstance.put(`api/isporuke/${selectedIsporuka.sifra_i}/`, {
        kolicina_kg: spremnaKolicina || selectedIsporuka.kolicina_kg,
        status: "spremna"
      });
      
    // await axiosInstance.put(`api/isporuke/spremi/${selectedIsporuka.sifra_i}/`);
    } catch (error) {
      console.error("Greška pri potvrdi:", error);
      setPoruka("Došlo je do greške prilikom potvrde.");
    }
  };

  return (
    <div className={`spremanje-container ${isSidebarCollapsed ? "collapsed" : ""}`}>
      <MainSideBar onCollapseChange={setIsSidebarCollapsed} />
      <div className="content">
        <h2 className="pi-h2">Pregled svih isporuka</h2>
        <table className="isporuke-table">
          <thead>
            <tr>
              <th>Naziv</th>
              <th>Datum</th>
              <th>Količina (kg)</th>
              <th>Rok Isporuke</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {isporuke.map((i) => (
              <tr
                key={i.sifra_i}
                onClick={() => handleSelectIsporuka(i)}
                className={selectedIsporuka?.sifra_i === i.sifra_i ? "selected-row" : ""}
              >
                <td>{i.naziv || `Isporuka ${i.sifra_i}`}</td>
               {/* <td>{new Date(i.datum_kreiranja).toLocaleDateString()}</td>*/}
                <td>{new Date(i.datum_polaska).toLocaleDateString() ? new Date(i.datum_polaska).toLocaleDateString(): "-"}</td>
                <td>{i.kolicina_kg}</td>
                <td>{new Date(i.rok_isporuke).toLocaleDateString() ? new Date(i.rok_isporuke).toLocaleDateString()  : "-"}</td>
                <td>{i.status}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="pi-form-section">
          <div className="form-row">
            <label>Isporuka</label>
            <input
              type="text"
              value={selectedIsporuka ? `Isporuka ${selectedIsporuka.sifra_i}` : ""}
              readOnly
            />
          </div>

          <div className="form-row">
            <label>Skladište</label>
            {/* <input type="text" value={skladiste} readOnly /> */}
            <input
              list="skladistaLista"
              onChange={(e) => {
                const selected = skladista.find(
                  (s) => s.mesto_s === e.target.value
                );
                setIzabranoSkladiste(selected);
              }}
              placeholder="Odaberi ili unesi skladište"
            />
            <datalist id="skladistaLista">
              {skladista.map((s) => (
                <option key={s.sifra_s} value={s.mesto_s}>
                  {s.mesto_s}
                </option>
              ))}
            </datalist>
          </div>

          {/* <div className="form-row">
            <label>Datum isporuke</label>
            <input type="date" value={datumIsporuke} onChange={handleDatumChange} />
          </div> */}
          <div className="form-row">
            <label>Datum isporuke</label>
            {/*<input type="date" value={selectedIsporuka?.datum_polaska} onChange={handleDatumChange} />*/}
            <input type="date" value={datumIsporuke} onChange={handleDatumChange} />
          </div>

          <div className="form-row">
            <label>Spremna količina (kg)</label>
            <input
              type="number"
              value={spremnaKolicina}
              onChange={(e) => setSpremnaKolicina(e.target.value)}
              placeholder="Unesi količinu"
              className={greskaKolicina ? "error-input" : ""}
            />
            {greskaKolicina && <div className="error-message">{greskaKolicina}</div>}
          </div>

          <button className="btn-potvrdi" onClick={handlePotvrdi} disabled={!!greskaKolicina}>
            Potvrdi
          </button>

          {poruka && (
            <p className={`poruka ${greskaKolicina ? "error-poruka" : ""}`}>
              {poruka}
            </p>
          )}
          {vremeUtovara && <p className="poruka">⏱ Vreme utovara: {vremeUtovara} h</p>}
        </div>
      </div>
    </div>
  );
};

export default SpremanjeIsporuke;
