import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000/",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    // Lista javnih endpoint-a koji ne zahtevaju autentifikaciju
    const publicEndpoints = ["/register/", "/login/"];

    // Proveravamo da li je trenutni zahtev za javni endpoint
    const isPublicEndpoint = publicEndpoints.some(
      (endpoint) => config.url && config.url.includes(endpoint)
    );

    // Dodajemo Authorization header samo ako nije javni endpoint i token postoji
    if (!isPublicEndpoint) {
      const token = sessionStorage.getItem("access_token");
      if (token && token !== "null" && token !== "undefined") {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;
