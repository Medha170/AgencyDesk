"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
    const router = useRouter();
    const { login, agencies, activeAgencyId, switchAgency } = useAuth();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        try {
            // 1. Post credentials using standard URLSearchParams
            const params = new URLSearchParams();
            params.append("username", username);
            params.append("password", password);

            const response = await api.post("/auth/login", params, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            // 2. Extract access token
            const token = response.data.access_token;

            if (!token) {
                throw new Error("No access token returned from server.");
            }

            // 3. Store token & user context
            const userData = response.data.user || {
                id: "user-1",
                email: username,
                role: "agency_admin",
            };

            login(token, userData);
            setIsLoggedIn(true);
        } catch (err: any) {
            console.error("Login Error:", err);
            const detail = err.response?.data?.detail;
            if (typeof detail === "string") {
                setError(detail);
            } else if (Array.isArray(detail)) {
                setError(detail[0]?.msg || "Validation error during login.");
            } else {
                setError(err.message || "Invalid login credentials.");
            }
        }
    };

    const handleProceedToApp = () => {
        if (!activeAgencyId && agencies.length > 0) {
            switchAgency(agencies[0].id);
        }
        router.push("/projects");
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-1 text-center">
                    AgencyDesk Portal
                </h1>
                <p className="text-xs text-gray-600 text-center mb-6">
                    Multi-tenant client & project management
                </p>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-300 text-red-700 text-xs font-semibold rounded-md">
                        {error}
                    </div>
                )}

                {!isLoggedIn ? (
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
                                Username / Email
                            </label>
                            <input
                                type="text"
                                required
                                placeholder="e.g. test@example.com"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full text-sm font-medium text-gray-900 bg-gray-50 p-3 border border-gray-300 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
                                Password
                            </label>
                            <input
                                type="password"
                                required
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full text-sm font-medium text-gray-900 bg-gray-50 p-3 border border-gray-300 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition"
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full py-3 bg-blue-600 text-white font-semibold text-sm rounded-lg hover:bg-blue-700 active:bg-blue-800 transition shadow-sm mt-2"
                        >
                            Log In
                        </button>
                    </form>
                ) : (
                    <div className="space-y-4">
                        <div className="p-3 bg-green-50 border border-green-300 text-green-800 text-xs font-semibold rounded-md">
                            Authenticated successfully!
                        </div>

                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
                                Select Active Agency Context (`X-Agency-ID`):
                            </label>
                            <select
                                value={activeAgencyId || ""}
                                onChange={(e) => switchAgency(e.target.value)}
                                className="w-full text-sm font-medium text-gray-900 bg-gray-50 p-3 border border-gray-300 rounded-lg focus:bg-white outline-none"
                            >
                                {agencies.map((agency) => (
                                    <option key={agency.id} value={agency.id} className="text-gray-900">
                                        {agency.name} ({agency.id.slice(0, 8)}...)
                                    </option>
                                ))}
                            </select>
                        </div>

                        <button
                            onClick={handleProceedToApp}
                            className="w-full py-3 bg-gray-900 text-white font-semibold text-sm rounded-lg hover:bg-gray-800 transition shadow-sm"
                        >
                            Open Agency Dashboard ➔
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}