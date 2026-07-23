"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
    const pathname = usePathname();
    const { user, activeAgencyId, agencies, switchAgency, logout } = useAuth();

    // Hide Navbar on Login page
    if (pathname === "/login") return null;

    return (
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex justify-between items-center text-sm shadow-sm sticky top-0 z-50">
            <div className="flex items-center gap-6">
                <span className="font-bold text-gray-900 text-base tracking-tight">AgencyDesk</span>
                <nav className="flex gap-4">
                    <Link
                        href="/dashboard"
                        className={`font-semibold transition ${pathname === "/dashboard" ? "text-blue-600" : "text-gray-600 hover:text-gray-900"
                            }`}
                    >
                        Dashboard
                    </Link>
                    <Link
                        href="/projects"
                        className={`font-semibold transition ${pathname === "/projects" ? "text-blue-600" : "text-gray-600 hover:text-gray-900"
                            }`}
                    >
                        Projects & Tasks
                    </Link>
                </nav>
            </div>

            <div className="flex items-center gap-4">
                {agencies.length > 0 && (
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Agency:</span>
                        <select
                            value={activeAgencyId || ""}
                            onChange={(e) => switchAgency(e.target.value)}
                            className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-gray-50 text-gray-900 font-medium outline-none focus:ring-1 focus:ring-blue-500"
                        >
                            {agencies.map((agency) => (
                                <option key={agency.id} value={agency.id}>
                                    {agency.name}
                                </option>
                            ))}
                        </select>
                    </div>
                )}

                {user && (
                    <span className="text-xs bg-blue-50 text-blue-700 font-bold px-2.5 py-1 rounded-full border border-blue-200 uppercase">
                        {user.role}
                    </span>
                )}

                <button
                    onClick={logout}
                    className="text-xs text-red-600 hover:text-red-800 font-semibold transition"
                >
                    Logout
                </button>
            </div>
        </header>
    );
}