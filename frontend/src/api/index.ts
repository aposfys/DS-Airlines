import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = (data) => api.post("/auth/token", data);
export const register = (data) => api.post("/auth/register", data);
export const getMe = () => api.get("/auth/me");

export const searchFlights = (params) => api.get("/flights", { params });
export const getFlight = (code) => api.get(`/flights/${code}`);

export const createBooking = (data) => api.post("/bookings", data);
export const getMyBookings = () => api.get("/bookings");
export const cancelBooking = (id) => api.delete(`/bookings/${id}`);

export const createFlight = (data) => api.post("/flights", data);
export const updateFlight = (code, data) => api.put(`/flights/${code}`, data);
export const deleteFlight = (code) => api.delete(`/flights/${code}`);

export default api;
