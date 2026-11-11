import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
  timeout: 30000,
});

export const getDashboard = () => api.get("/dashboard/");
export const getAccidents = () => api.get("/accidents/");
export const getHotspots = () => api.get("/hotspots/");
export const uploadCsv = (file) => {
  const data = new FormData();
  data.append("file", file);
  return api.post("/accidents/upload/", data, { headers: { "Content-Type": "multipart/form-data" } });
};
export const runAnalysis = () => api.post("/analysis/run/", { dataset_name: "Uploaded accident CSV" });
export default api;
