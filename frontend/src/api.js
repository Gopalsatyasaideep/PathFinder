import axios from "axios";

// Create a shared axios instance that reads base URL from environment.
// Vite replaces import.meta.env.VITE_API_URL at build time.
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  withCredentials: true, // if you use cookies or auth
});

export default API;
