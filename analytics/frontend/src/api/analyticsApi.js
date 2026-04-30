import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:4004",
});

export const getScrapperAnalytics = () => API.get("/scrapper-analytics/");
export const getTrend              = () => API.get("/scrapper-analytics/trend");
export const getComparison         = () => API.get("/scrapper-analytics/comparison");
export const getGrowth             = () => API.get("/scrapper-analytics/growth");
export const refreshAnalytics      = () => API.post("/scrapper-analytics/refresh");
