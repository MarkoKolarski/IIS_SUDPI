import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axiosInstance from "../axiosInstance";

import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import iconRetina from "leaflet/dist/images/marker-icon-2x.png";

// Popravka za ikone
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
});

// Automatsko centriranje mape
function MapAutoPan({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.flyTo(position, 11, { animate: true });
    }
  }, [position, map]);
  return null;
}

const MapComponent = ({ ruta, trenutnaPozicija }) => {
  const [rutaKoordinate, setRutaKoordinate] = useState([]);

  const defaultPosition = [44.7866, 20.4489]; // Beograd

  const position = trenutnaPozicija
    ? [trenutnaPozicija.lat, trenutnaPozicija.lon]
    : defaultPosition;

  // 🔹 Učitavanje rute (putanje) sa servera
useEffect(() => {
  if (!ruta) return;

  const fetchRutaKoordinate = async () => {
    try {
      const response = await axiosInstance.get(`api/rute/${ruta.sifra_r}/directions/`);
      const data = response.data;

      if (data.geometry && Array.isArray(data.geometry.coordinates)) {
        // ✅ Prebacujemo iz [lon, lat] u [lat, lon]
        const coords = data.geometry.coordinates.map(coord => [coord[1], coord[0]]);
        setRutaKoordinate(coords);
      } else {
        console.warn("Neispravan format rute:", data);
        setRutaKoordinate([]);
      }
    } catch (error) {
      console.error("Greška pri dobavljanju putanje rute:", error);
      setRutaKoordinate([]);
    }
  };

  fetchRutaKoordinate();
}, [ruta]);


  return (
    <div style={{ height: "400px", width: "100%", borderRadius: "10px", overflow: "hidden" }}>
      <MapContainer
        center={position}
        zoom={10}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 🔹 Crtanje linije rute */}
        {rutaKoordinate.length > 1 && (
          <Polyline positions={rutaKoordinate} color="blue" />
        )}

        {/* 🔹 Marker trenutne pozicije */}
        {trenutnaPozicija && (
          <Marker position={position}>
            <Popup>
              <strong>🚚 Trenutna pozicija</strong><br />
              Ruta: {ruta?.sifra_r}<br />
              Lat: {trenutnaPozicija.lat.toFixed(5)}<br />
              Lon: {trenutnaPozicija.lon.toFixed(5)}
            </Popup>
          </Marker>
        )}

        {/* 🔹 Markeri polazne i krajnje tačke */}
        {ruta && ruta.polaziste_koordinate && ruta.odrediste_koordinate && (
  <>
    <Marker position={[ruta.polaziste_koordinate[1], ruta.polaziste_koordinate[0]]}>
      <Popup>Polazna tačka: {ruta.polazna_tacka}</Popup>
    </Marker>
    <Marker position={[ruta.odrediste_koordinate[1], ruta.odrediste_koordinate[0]]}>
      <Popup>Odredište: {ruta.odrediste}</Popup>
    </Marker>
  </>
)}

        <MapAutoPan position={position} />
      </MapContainer>
    </div>
  );
};

export default MapComponent;
