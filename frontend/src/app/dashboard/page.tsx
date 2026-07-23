"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface Metrics {
    total_clients: number;
    total_projects: number;
    active_projects: number;
    tasks: {
        total_tasks: number;
        pending_tasks: number;
        in_progress_tasks: number;
        completed_tasks: number;
    };
    deliverables: {
        total_files: number;
        pending_approval: number;
        approved: number;
        needs_changes: number;
    };
}

export default function DashboardPage() {
    const { activeAgencyId } = useAuth();
    const [metrics, setMetrics] = useState<Metrics | null>(null);

    useEffect(() => {
        if (activeAgencyId) {
            api.get("/analytics/overview")
                .then((res) => setMetrics(res.data))
                .catch((err) => console.error("Failed to load analytics", err));
        }
    }, [activeAgencyId]);

    if (!metrics) {
        return <div className="p-8 text-sm text-gray-500">Loading overview metrics...</div>;
    }

    return (
        <div className="p-8 max-w-6xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Agency Overview Dashboard</h1>

            {/* TOP STAT CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-5 bg-white border rounded-xl shadow-sm">
                    <div className="text-xs font-semibold text-gray-400 uppercase">Clients</div>
                    <div className="text-3xl font-bold text-gray-900 mt-1">{metrics.total_clients}</div>
                </div>
                <div className="p-5 bg-white border rounded-xl shadow-sm">
                    <div className="text-xs font-semibold text-gray-400 uppercase">Active Projects</div>
                    <div className="text-3xl font-bold text-blue-600 mt-1">{metrics.active_projects} / {metrics.total_projects}</div>
                </div>
                <div className="p-5 bg-white border rounded-xl shadow-sm">
                    <div className="text-xs font-semibold text-gray-400 uppercase">Total Tasks</div>
                    <div className="text-3xl font-bold text-gray-900 mt-1">{metrics.tasks.total_tasks}</div>
                </div>
            </div>

            {/* BREAKDOWN SECTIONS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* TASK STATUS BREAKDOWN */}
                <div className="p-5 bg-white border rounded-xl shadow-sm">
                    <h2 className="text-sm font-bold text-gray-700 uppercase mb-4">Task Status Breakdown</h2>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between items-center pb-2 border-b">
                            <span className="text-gray-600">To Do</span>
                            <span className="font-bold text-yellow-600">{metrics.tasks.pending_tasks}</span>
                        </div>
                        <div className="flex justify-between items-center pb-2 border-b">
                            <span className="text-gray-600">In Progress</span>
                            <span className="font-bold text-blue-600">{metrics.tasks.in_progress_tasks}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">Completed</span>
                            <span className="font-bold text-green-600">{metrics.tasks.completed_tasks}</span>
                        </div>
                    </div>
                </div>

                {/* DELIVERABLES & APPROVALS */}
                <div className="p-5 bg-white border rounded-xl shadow-sm">
                    <h2 className="text-sm font-bold text-gray-700 uppercase mb-4">Deliverables & Approvals</h2>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between items-center pb-2 border-b">
                            <span className="text-gray-600">Pending Review</span>
                            <span className="font-bold text-yellow-600">{metrics.deliverables.pending_approval}</span>
                        </div>
                        <div className="flex justify-between items-center pb-2 border-b">
                            <span className="text-gray-600">Approved</span>
                            <span className="font-bold text-green-600">{metrics.deliverables.approved}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">Needs Changes</span>
                            <span className="font-bold text-red-600">{metrics.deliverables.needs_changes}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}