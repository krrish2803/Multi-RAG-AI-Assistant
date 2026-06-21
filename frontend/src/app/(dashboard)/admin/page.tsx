"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import type { User } from "@/types";
import { useAuthStore } from "@/stores/authStore";
import { Users, Shield, Edit, Trash2 } from "lucide-react";

const ROLES = ["employee", "hr", "finance", "marketing", "engineering", "executive", "admin"];

export default function AdminPage() {
  const { user: currentUser } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get("/users");
      setUsers(res.data || []);
    } catch {}
    setLoading(false);
  };

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await api.put(`/users/${userId}/role`, { role });
      loadUsers();
    } catch {}
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      executive: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
      engineering: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
      hr: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
      finance: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
      marketing: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400",
      employee: "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400",
    };
    return colors[role] || colors.employee;
  };

  const isAdmin = currentUser?.role === "admin" || currentUser?.role === "executive";

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Access Restricted</h2>
          <p className="text-muted-foreground">Admin or Executive role required to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Admin Panel</h1>
        <p className="text-muted-foreground">User management and system administration</p>
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-muted border-b border-border flex items-center gap-2">
          <Users className="w-4 h-4" />
          <h2 className="font-semibold text-foreground text-sm">Users ({users.length})</h2>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs text-muted-foreground bg-muted/50">
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Departments</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
            ) : users.map((u) => (
              <tr key={u.id} className="hover:bg-accent/50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium">{u.full_name.charAt(0)}</span>
                    </div>
                    <span className="text-sm font-medium text-foreground">{u.full_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{u.email}</td>
                <td className="px-4 py-3">
                  <select
                    value={u.role}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                    className={`px-2 py-0.5 text-xs rounded border-0 cursor-pointer ${getRoleBadgeColor(u.role)}`}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-1 flex-wrap">
                    {u.departments.map((d) => (
                      <span key={d} className="px-1.5 py-0.5 text-xs bg-muted rounded text-muted-foreground">{d}</span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 text-xs rounded ${u.is_active ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>
                    {u.is_active ? "Active" : "Disabled"}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
