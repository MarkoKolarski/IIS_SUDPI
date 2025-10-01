import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
});

// Modify the public endpoints list and interceptor
const publicEndpoints = ["register", "login"];

axiosInstance.interceptors.request.use(
  (config) => {
    const isPublicEndpoint = publicEndpoints.some((endpoint) =>
      config.url.startsWith(endpoint)
    );

    if (!isPublicEndpoint) {
      const token = sessionStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
