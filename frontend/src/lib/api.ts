import axios from "axios";

export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1",
});

api.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("access_token") || localStorage.getItem("token");
        const agencyId = localStorage.getItem("active_agency_id") || localStorage.getItem("activeAgencyId");

        if (token) {
            config.headers = {
                ...config.headers,
                Authorization: `Bearer ${token}`,
            };
        }
        if (agencyId) {
            config.headers = {
                ...config.headers,
                "X-Agency-ID": agencyId,
            };
        }
    }
    return config;
});