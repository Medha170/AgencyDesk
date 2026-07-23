"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import Navbar from "@/components/Navbar";

interface Project {
    id: string;
    name: string;
    description?: string;
    status?: string;
}

interface Task {
    id: string;
    title: string;
    description?: string;
    status: "todo" | "in_progress" | "completed";
    is_internal: boolean;
}

interface TaskFile {
    id: string;
    file_name: string;
    file_url: string;
    approval_status: "pending" | "approved" | "needs_changes";
    is_internal: boolean;
}

interface TaskComment {
    id: string;
    content: string;
    is_internal: boolean;
    created_at: string;
}

export default function ProjectsPage() {
    const { activeAgencyId, user } = useAuth();

    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);

    const [taskFiles, setTaskFiles] = useState<TaskFile[]>([]);
    const [taskComments, setTaskComments] = useState<TaskComment[]>([]);

    const [loggedHours, setLoggedHours] = useState<number>(0);
    const [newComment, setNewComment] = useState("");
    const [isInternalComment, setIsInternalComment] = useState(false);
    const [timeMinutes, setTimeMinutes] = useState("");
    const [timeNote, setTimeNote] = useState("");

    const isClientUser = user?.role === "client_user";

    // 1. Fetch Projects when Active Agency changes
    useEffect(() => {
        if (activeAgencyId) {
            fetchProjects();
        }
    }, [activeAgencyId]);

    // 2. Fetch Tasks & Hours when Selected Project changes
    useEffect(() => {
        if (selectedProjectId) {
            fetchTasks(selectedProjectId);
            fetchProjectHours(selectedProjectId);
        }
    }, [selectedProjectId]);

    // 3. Fetch Files & Comments when Selected Task changes
    useEffect(() => {
        if (selectedTask) {
            fetchTaskDetails(selectedTask.id);
        }
    }, [selectedTask]);

    const fetchProjects = async () => {
        try {
            const res = await api.get("/projects");
            setProjects(res.data);
            if (res.data.length > 0) {
                setSelectedProjectId(res.data[0].id);
            } else {
                setTasks([]);
                setSelectedTask(null);
            }
        } catch (err) {
            console.error("Failed to load projects", err);
        }
    };

    const fetchTasks = async (projectId: string) => {
        try {
            const res = await api.get(`/projects/${projectId}/tasks`);
            setTasks(res.data);
            setSelectedTask(res.data.length > 0 ? res.data[0] : null);
        } catch (err) {
            console.error("Failed to load tasks", err);
        }
    };

    const fetchProjectHours = async (projectId: string) => {
        try {
            const res = await api.get(`/tracking/projects/${projectId}/hours`);
            setLoggedHours(res.data.total_hours);
        } catch (err) {
            console.error("Failed to load hours", err);
        }
    };

    const fetchTaskDetails = async (taskId: string) => {
        try {
            const [filesRes, commentsRes] = await Promise.all([
                api.get(`/content/tasks/${taskId}/files`),
                api.get(`/content/tasks/${taskId}/comments`),
            ]);
            setTaskFiles(filesRes.data);
            setTaskComments(commentsRes.data);
        } catch (err) {
            console.error("Failed to load task deliverables or comments", err);
        }
    };

    const handlePostComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedTask || !newComment.trim()) return;

        try {
            await api.post(`/content/tasks/${selectedTask.id}/comments`, {
                content: newComment,
                is_internal: isInternalComment,
            });
            setNewComment("");
            fetchTaskDetails(selectedTask.id);
        } catch (err) {
            console.error("Failed to post comment", err);
        }
    };

    const handleLogTime = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedTask || !timeMinutes) return;

        try {
            await api.post(`/tracking/tasks/${selectedTask.id}/time`, {
                duration_minutes: parseInt(timeMinutes, 10),
                note: timeNote,
            });
            setTimeMinutes("");
            setTimeNote("");
            if (selectedProjectId) fetchProjectHours(selectedProjectId);
        } catch (err) {
            console.error("Failed to log time", err);
        }
    };

    const handleUpdateFileStatus = async (fileId: string, status: string) => {
        try {
            await api.patch(`/content/files/${fileId}/status`, {
                approval_status: status,
            });
            if (selectedTask) fetchTaskDetails(selectedTask.id);
        } catch (err) {
            console.error("Failed to update status", err);
        }
    };

    return (
        <div className="flex h-[calc(100vh-53px)] bg-gray-50 text-gray-800 overflow-hidden">
            {/* LEFT SIDEBAR: Projects List */}
            <div className="w-1/4 border-r bg-white p-4 overflow-y-auto">
                <h2 className="text-xl font-bold mb-4">Projects</h2>
                <div className="space-y-2">
                    {projects.map((proj) => (
                        <button
                            key={proj.id}
                            onClick={() => setSelectedProjectId(proj.id)}
                            className={`w-full text-left p-3 rounded-lg border transition ${selectedProjectId === proj.id
                                    ? "border-blue-600 bg-blue-50 text-blue-700 font-semibold"
                                    : "hover:bg-gray-100"
                                }`}
                        >
                            <div className="text-sm font-medium">{proj.name}</div>
                            {proj.description && (
                                <div className="text-xs text-gray-500 truncate">{proj.description}</div>
                            )}
                        </button>
                    ))}
                    {projects.length === 0 && (
                        <div className="text-sm text-gray-400">No projects found.</div>
                    )}
                </div>
            </div>

            {/* MIDDLE COLUMN: Task List Board */}
            <div className="w-2/4 border-r bg-white p-4 overflow-y-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Tasks</h2>
                    <div className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full font-semibold">
                        Logged: {loggedHours} hrs
                    </div>
                </div>

                <div className="space-y-3">
                    {tasks.map((task) => (
                        <div
                            key={task.id}
                            onClick={() => setSelectedTask(task)}
                            className={`p-4 rounded-lg border cursor-pointer transition ${selectedTask?.id === task.id ? "border-blue-500 ring-2 ring-blue-100" : "hover:border-gray-300"
                                }`}
                        >
                            <div className="flex justify-between items-start">
                                <h3 className="font-semibold">{task.title}</h3>
                                <div className="flex gap-1">
                                    {task.is_internal && (
                                        <span className="bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded uppercase font-bold">
                                            Internal
                                        </span>
                                    )}
                                    <span className="bg-gray-100 text-gray-700 text-[10px] px-2 py-0.5 rounded uppercase font-semibold">
                                        {task.status}
                                    </span>
                                </div>
                            </div>
                            {task.description && (
                                <p className="text-xs text-gray-500 mt-1">{task.description}</p>
                            )}
                        </div>
                    ))}
                    {tasks.length === 0 && (
                        <div className="text-sm text-gray-400">No tasks in this project.</div>
                    )}
                </div>
            </div>

            {/* RIGHT COLUMN: Selected Task Inspector (Deliverables, Comments & Time) */}
            <div className="w-1/4 bg-gray-50 p-4 overflow-y-auto">
                {selectedTask ? (
                    <div>
                        <div className="mb-4 border-b pb-3">
                            <h3 className="text-lg font-bold">{selectedTask.title}</h3>
                            <p className="text-xs text-gray-500 mt-1">{selectedTask.description || "No description provided."}</p>
                        </div>

                        {/* DELIVERABLE FILES SECTION */}
                        <div className="mb-6">
                            <h4 className="text-xs font-bold uppercase text-gray-500 mb-2">Deliverables</h4>
                            <div className="space-y-2">
                                {taskFiles.map((file) => (
                                    <div key={file.id} className="p-2 border rounded bg-white text-xs">
                                        <div className="flex justify-between items-center mb-1">
                                            <a href={file.file_url} target="_blank" rel="noreferrer" className="text-blue-600 font-medium hover:underline truncate">
                                                {file.file_name}
                                            </a>
                                            {file.is_internal && (
                                                <span className="text-[9px] bg-amber-100 text-amber-800 px-1 rounded">Internal</span>
                                            )}
                                        </div>
                                        <div className="flex justify-between items-center mt-2">
                                            <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${file.approval_status === "approved" ? "bg-green-100 text-green-800" :
                                                    file.approval_status === "needs_changes" ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-800"
                                                }`}>
                                                {file.approval_status}
                                            </span>
                                            <div className="flex gap-1">
                                                <button
                                                    onClick={() => handleUpdateFileStatus(file.id, "approved")}
                                                    className="px-1.5 py-0.5 bg-green-600 text-white text-[10px] rounded hover:bg-green-700"
                                                >
                                                    Approve
                                                </button>
                                                <button
                                                    onClick={() => handleUpdateFileStatus(file.id, "needs_changes")}
                                                    className="px-1.5 py-0.5 bg-red-600 text-white text-[10px] rounded hover:bg-red-700"
                                                >
                                                    Changes
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {taskFiles.length === 0 && <div className="text-xs text-gray-400">No deliverables attached.</div>}
                            </div>
                        </div>

                        {/* TIME TRACKING LOG FORM (Agency Only) */}
                        {!isClientUser && (
                            <div className="mb-6 p-3 bg-white border rounded">
                                <h4 className="text-xs font-bold uppercase text-gray-500 mb-2">Log Time</h4>
                                <form onSubmit={handleLogTime} className="space-y-2">
                                    <input
                                        type="number"
                                        placeholder="Duration (minutes)"
                                        value={timeMinutes}
                                        onChange={(e) => setTimeMinutes(e.target.value)}
                                        className="w-full text-xs p-2 border rounded"
                                    />
                                    <input
                                        type="text"
                                        placeholder="Note (optional)"
                                        value={timeNote}
                                        onChange={(e) => setTimeNote(e.target.value)}
                                        className="w-full text-xs p-2 border rounded"
                                    />
                                    <button type="submit" className="w-full py-1.5 bg-blue-600 text-white text-xs font-semibold rounded hover:bg-blue-700">
                                        Log Time Entry
                                    </button>
                                </form>
                            </div>
                        )}

                        {/* COMMENTS THREAD */}
                        <div>
                            <h4 className="text-xs font-bold uppercase text-gray-500 mb-2">Comments</h4>
                            <div className="space-y-2 mb-3 max-h-48 overflow-y-auto">
                                {taskComments.map((comment) => (
                                    <div key={comment.id} className="p-2 border rounded bg-white text-xs">
                                        <div className="flex justify-between items-center text-[10px] text-gray-400 mb-1">
                                            <span>{new Date(comment.created_at).toLocaleTimeString()}</span>
                                            {comment.is_internal && (
                                                <span className="bg-amber-100 text-amber-800 text-[9px] px-1 rounded">Internal</span>
                                            )}
                                        </div>
                                        <p className="text-gray-700">{comment.content}</p>
                                    </div>
                                ))}
                                {taskComments.length === 0 && <div className="text-xs text-gray-400">No comments yet.</div>}
                            </div>

                            {/* POST COMMENT FORM */}
                            <form onSubmit={handlePostComment} className="space-y-2">
                                <textarea
                                    placeholder="Write a comment..."
                                    value={newComment}
                                    onChange={(e) => setNewComment(e.target.value)}
                                    className="w-full text-xs p-2 border rounded h-16 resize-none"
                                />
                                {!isClientUser && (
                                    <label className="flex items-center gap-1.5 text-xs text-gray-600">
                                        <input
                                            type="checkbox"
                                            checked={isInternalComment}
                                            onChange={(e) => setIsInternalComment(e.target.checked)}
                                        />
                                        Mark as internal note (hidden from client)
                                    </label>
                                )}
                                <button type="submit" className="w-full py-1.5 bg-gray-800 text-white text-xs font-semibold rounded hover:bg-gray-900">
                                    Post Comment
                                </button>
                            </form>
                        </div>
                    </div>
                ) : (
                    <div className="text-xs text-gray-400 text-center mt-10">Select a task to inspect details</div>
                )}
            </div>
        </div>
    );
}