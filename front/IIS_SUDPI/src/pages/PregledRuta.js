import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import MainSideBar from '../components/MainSideBar';
import axiosInstance from '../axiosInstance';
import '../styles/PregledRuta.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const PregledRuta = () => {
  const [activeRoutes, setActiveRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [routeGeometry, setRouteGeometry] = useState(null);
  const [vehiclePosition, setVehiclePosition] = useState(null);
  const [temperatureData, setTemperatureData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const mapRef = useRef();
  const simulationIntervalRef = useRef();

  const minTemp = 2;
  const maxTemp = 8;

  // Fetch active routes
  useEffect(() => {
    fetchActiveRoutes();
  }, []);

  const fetchActiveRoutes = async () => {
    try {
      const response = await axiosInstance.get('/api/rute/aktivne/');
      setActiveRoutes(response.data);
      if (response.data.length > 0) {
        handleRouteSelect(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching routes:', error);
    }
  };

  const handleRouteSelect = async (route) => {
    setSelectedRoute(route);
    
    try {
      // Fetch route details with geometry
      const response = await axiosInstance.get(`/api/rute/${route.sifra_r}/directions/`);
      const routeData = response.data;
      
      if (routeData.geometry) {
        setRouteGeometry(routeData.geometry);
        
        // Start vehicle simulation
        startVehicleSimulation(routeData.geometry);
      }
      
      // Start temperature monitoring for this route
      startTemperatureMonitoring(route.sifra_r);
      
    } catch (error) {
      console.error('Error fetching route details:', error);
    }
  };

  const startVehicleSimulation = (geometry) => {
    if (simulationIntervalRef.current) {
      clearInterval(simulationIntervalRef.current);
    }

    const coordinates = decodePolyline(geometry);
    let currentIndex = 0;

    simulationIntervalRef.current = setInterval(() => {
      if (currentIndex < coordinates.length) {
        setVehiclePosition(coordinates[currentIndex]);
        currentIndex++;
        
        if (Math.random() < 0.1 && currentIndex > 10) {
          simulateRouteDeviation(coordinates, currentIndex);
        }
      } else {
        clearInterval(simulationIntervalRef.current);
      }
    }, 1000);
  };

  const simulateRouteDeviation = async (originalCoords, currentIndex) => {
    const deviationAlert = {
      id: Date.now(),
      type: 'odstupanje',
      message: 'Vozilo je skrenulo sa planirane rute! Preračunavam optimalnu rutu...',
      timestamp: new Date().toLocaleTimeString()
    };
    
    setAlerts(prev => [deviationAlert, ...prev]);
    
    // Send alert to backend
    try {
      await axiosInstance.post('/api/upozorenja/', {
        isporuka: selectedRoute.sifra_r,
        tip: 'odstupanje',
        poruka: 'Vozilo je skrenulo sa planirane rute!'
      });
    } catch (error) {
      console.error('Error sending alert:', error);
    }
    
    // In a real app, you would call your backend to recalculate the route
    // For simulation, we'll just modify the remaining path slightly
    const remainingCoords = originalCoords.slice(currentIndex);
    const deviatedCoords = remainingCoords.map(coord => [
      coord[0] + (Math.random() - 0.5) * 0.01,
      coord[1] + (Math.random() - 0.5) * 0.01
    ]);
    
    // Replace the remaining coordinates with deviated ones
    const newGeometry = {
      ...routeGeometry,
      coordinates: [...originalCoords.slice(0, currentIndex), ...deviatedCoords]
    };
    
    setRouteGeometry(newGeometry);
  };

  const startTemperatureMonitoring = (routeId) => {
    // Clear existing temperature data
    setTemperatureData([]);
    
    // Simulate temperature readings every 4 minutes (240000 ms)
    // For demo, we'll use 10 seconds
    const temperatureInterval = setInterval(() => {
      const newTemp = Math.random() * 10 + 2; // Random temp between 2-12°C
      const timestamp = new Date().toLocaleTimeString();
      
      const newDataPoint = {
        timestamp,
        temperature: newTemp,
        routeId
      };
      
      setTemperatureData(prev => {
        const newData = [...prev, newDataPoint].slice(-20); // Keep last 20 readings
        return newData;
      });
      
      // Check temperature limits
      if (newTemp < minTemp || newTemp > maxTemp) {
        const tempAlert = {
          id: Date.now(),
          type: 'temperatura',
          message: `Temperatura izvan granica: ${newTemp.toFixed(1)}°C (Granice: ${minTemp}-${maxTemp}°C)`,
          timestamp
        };
        
        setAlerts(prev => [tempAlert, ...prev]);
        
        // Send alert to backend
        try {
          axiosInstance.post('/api/upozorenja/', {
            isporuka: routeId,
            tip: 'temperatura',
            poruka: tempAlert.message
          });
        } catch (error) {
          console.error('Error sending temperature alert:', error);
        }
      }
      
    }, 10000); // 10 seconds for demo, change to 240000 for 4 minutes
    
    return () => clearInterval(temperatureInterval);
  };

  // Polyline decoding function
  const decodePolyline = (geometry) => {
    if (!geometry || !geometry.coordinates) return [];
    return geometry.coordinates.map(coord => [coord[1], coord[0]]); // Leaflet uses [lat, lng]
  };

  // Chart data configuration
  const chartData = {
    labels: temperatureData.map(data => data.timestamp),
    datasets: [
      {
        label: 'Temperatura (°C)',
        data: temperatureData.map(data => data.temperature),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      },
      {
        label: 'Gornja granica',
        data: temperatureData.map(() => maxTemp),
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        fill: false
      },
      {
        label: 'Donja granica',
        data: temperatureData.map(() => minTemp),
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        fill: false
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Temperaturni monitoring'
      }
    },
    scales: {
      y: {
        min: 0,
        max: 15,
        title: {
          display: true,
          text: 'Temperatura (°C)'
        }
      }
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="dashboard-container">
      <MainSideBar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      
      <div className={`main-content-wrapper ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="dashboard-header">
          <button className="sidebar-toggle" onClick={toggleSidebar}>
            ☰
          </button>
          <h1>Pregled aktivnih ruta</h1>
        </div>

        <div className="dashboard-content">
          <div className="routes-sidebar">
            <h3>Izaberi rutu:</h3>
            <div className="routes-list">
              {activeRoutes.map(route => (
                <div
                  key={route.sifra_r}
                  className={`route-item ${selectedRoute?.sifra_r === route.sifra_r ? 'selected' : ''}`}
                  onClick={() => handleRouteSelect(route)}
                >
                  <strong>Ruta {route.sifra_r}</strong>
                  <div>{route.polazna_tacka} → {route.odrediste}</div>
                  <div className="route-info">
                    {route.duzina_km} km • {route.vreme_dolaska}
                  </div>
                  <div className={`route-status ${route.status}`}>
                    {route.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="main-content">
            <div className="map-container">
              {selectedRoute && (
                <MapContainer
                  center={[44.787197, 20.457273]} // Default to Belgrade
                  zoom={10}
                  style={{ height: '400px', width: '100%' }}
                  ref={mapRef}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  
                  {routeGeometry && (
                    <Polyline
                      positions={decodePolyline(routeGeometry)}
                      color="green"
                      weight={4}
                    />
                  )}
                  
                  {vehiclePosition && (
                    <Marker position={vehiclePosition}>
                      <Popup>
                        Vozilo na ruti {selectedRoute.sifra_r}
                        <br />
                        {selectedRoute.polazna_tacka} → {selectedRoute.odrediste}
                      </Popup>
                    </Marker>
                  )}
                </MapContainer>
              )}
            </div>

            <div className="alerts-container">
              <h3>Upozorenja</h3>
              <div className="alerts-list">
                {alerts.map(alert => (
                  <div key={alert.id} className={`alert alert-${alert.type}`}>
                    <div className="alert-time">{alert.timestamp}</div>
                    <div className="alert-message">{alert.message}</div>
                  </div>
                ))}
                {alerts.length === 0 && (
                  <div className="no-alerts">Nema upozorenja</div>
                )}
              </div>
            </div>

            <div className="temperature-container">
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PregledRuta;
