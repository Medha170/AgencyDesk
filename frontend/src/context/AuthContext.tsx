"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "@/lib/api";

interface User {
    id: string;
    email: string;
    role: "agency_admin" | "agency_member" | "client_user";
}

interface Agency {
    id: string;
    name: string;
}

interface AuthContextType {
    user: User | null;
    activeAgencyId: string | null;
    agencies: Agency[];
    login: (token: string, userData?: User) => void;
    logout: () => void;
    switchAgency: (agencyId: string) => void;
    fetchAgencies: () => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [activeAgencyId, setActiveAgencyId] = useState<string | null>(null);
    const [agencies, setAgencies] = useState<Agency[]>([]);

    useEffect(() => {
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("access_token") || localStorage.getItem("token");
            const storedAgencyId = localStorage.getItem("active_agency_id") || localStorage.getItem("activeAgencyId");
            const storedUser = localStorage.getItem("user_info");

            if (token) {
                if (storedUser) {
                    try {
                        setUser(JSON.parse(storedUser));
                    } catch (e) {
                        console.error("Failed to parse stored user info", e);
                    }
                }
                if (storedAgencyId) setActiveAgencyId(storedAgencyId);
                fetchAgencies();
            }
        }
    }, []);

    const fetchAgencies = async () => {
        try {
            const response = await api.get("/tenants/agencies");
            setAgencies(response.data);

            const currentAgencyId = localStorage.getItem("active_agency_id") || localStorage.getItem("activeAgencyId");
            if (response.data.length > 0 && !currentAgencyId) {
                switchAgency(response.data[0].id);
            }
        } catch (err) {
            console.error("Failed to fetch agencies:", err);
        }
    };

    const login = (token: string, userData?: User) => {
        localStorage.setItem("access_token", token);
        localStorage.setItem("token", token);
        if (userData) {
            localStorage.setItem("user_info", JSON.stringify(userData));
            setUser(userData);
        }
        fetchAgencies();
    };

    const logout = () => {
        localStorage.clear();
        setUser(null);
        setActiveAgencyId(null);
        setAgencies([]);
        window.location.href = "/login";
    };

    const switchAgency = (agencyId: string) => {
        localStorage.setItem("active_agency_id", agencyId);
        localStorage.setItem("activeAgencyId", agencyId);
        setActiveAgencyId(agencyId);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                activeAgencyId,
                agencies,
                login,
                logout,
                switchAgency,
                fetchAgencies,
                isAuthenticated: typeof window !== "undefined" && !!(localStorage.getItem("access_token") || localStorage.getItem("token")),
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};