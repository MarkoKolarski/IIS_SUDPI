import React, { useState, useEffect } from "react";
import axiosInstance from "../axiosInstance";
import MainSideBar from "../components/MainSideBar";
import "../styles/SpremanjeIsporuke.css";

const SpremanjeIsporuke = () => {
  const [isporuke, setIsporuke] = useState([]);
  const [selectedIsporuka, setSelectedIsporuka] = useState(null);
  //const [skladiste, setSkladiste] = useState("");
  const [skladiste, setSkladiste] = useState([]);
  const [datumIsporuke, setDatumIsporuke] = useState("");
  const [spremnaKolicina, setSpremnaKolicina] = useState("");
  const [poruka, setPoruka] = useState("");
  const [vremeUtovara, setVremeUtovara] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    axiosInstance
      .get("isporuke/u_toku/")
      .then((res) => setIsporuke(res.data))
      .catch((err) => console.error("Greška pri učitavanju isporuka:", err));
  }, []);

  const handleSelectIsporuka = (isporuka) => {
    setSelectedIsporuka(isporuka);
    setDatumIsporuke(isporuka.datum_polaska?.split("T")[0] || "");
    setPoruka("");

    axiosInstance
      .get(`api/skladiste/${isporuka.sifra_i}`)
      .then((res) => setSkladiste(res.data))
      .catch((err) => console.error("Greška pri učitavanju isporuka:", err));
      //.then((res) => setSkladiste(res.data.naziv_s || res.data.mesto_s))
      //.catch(() => setSkladiste("Nije pronađeno"));
  };
  

  // ----------------- Promena datuma isporuke -----------------
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

    try {
      // 1️⃣ proveri slobodne rampe
      const resRampe = await axiosInstance.get("api/rampe/aktivna/", {
         params: { status: "slobodna",
            skladiste: skladiste.sifra_s
         },
       });
       if (resRampe.data.lenght === 0 ) {
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
      
      await axiosInstance.put(`/api/isporuke/${selectedIsporuka.sifra_i}/`, {
        kolicina_kg: spremnaKolicina || selectedIsporuka.kolicina_kg,
        status: "spremna"
      });
      await axiosInstance.put(`/api/rampe/${resRampe.data.sifra_rp}/`, {
        status: "zauzeta"
      });
      //await axiosInstance.put(`/api/rute/${selectedIsporuka.sifra_i}/`);

      if (selectedIsporuka?.ruta) {
        console.debug("Updating ruta", selectedIsporuka.ruta);
        await axiosInstance.patch(`/api/rute/spremna/${selectedIsporuka.ruta}/`, {
          vreme_utovara: resUtovar.data.vreme_utovara
        });
      } else {
        console.debug("No ruta id available on selectedIsporuka:", selectedIsporuka);
      }
      
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
            <input type="text" value={skladiste.mesto_s} readOnly />
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
            />
          </div>

          <button className="btn-potvrdi" onClick={handlePotvrdi}>
            Potvrdi
          </button>

          {poruka && <p className="poruka">{poruka}</p>}
          {vremeUtovara && <p className="poruka">⏱ Vreme utovara: {vremeUtovara} h</p>}
        </div>
      </div>
    </div>
  );
};

export default SpremanjeIsporuke;
