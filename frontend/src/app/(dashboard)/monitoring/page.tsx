"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import type { MonitoringSummary } from "@/types";
import { Activity, Zap, Coins, Shield, AlertTriangle, Clock, BarChart3 } from "lucide-react";

export default function MonitoringPage() {
  const [summary, setSummary] = useState<MonitoringSummary | null>(null);
  const [costs, setCosts] = useState<any>(null);
  const [errors, setErrors] = useState<any>(null);
  const [guardrails, setGuardrails] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryRes, costsRes, errorsRes, guardrailsRes] = await Promise.allSettled([
        api.get("/monitoring/summary"),
        api.get("/monitoring/costs"),
        api.get("/monitoring/errors"),
        api.get("/monitoring/guardrails"),
      ]);

      if (summaryRes.status === "fulfilled") setSummary(summaryRes.value.data);
      if (costsRes.status === "fulfilled") setCosts(costsRes.value.data);
      if (errorsRes.status === "fulfilled") setErrors(errorsRes.value.data);
      if (guardrailsRes.status === "fulfilled") setGuardrails(guardrailsRes.value.data);
    } catch {}
    setLoading(false);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-full"><p className="text-muted-foreground">Loading monitoring data...</p></div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Monitoring Dashboard</h1>
        <p className="text-muted-foreground">System performance and usage metrics</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard icon={Activity} label="Total Requests" value={summary?.total_requests?.toString() || "0"} color="blue" />
        <KPICard icon={Clock} label="Avg Latency" value={`${summary?.avg_latency_ms?.toFixed(0) || "0"}ms`} color="yellow" />
        <KPICard icon={Zap} label="Total Tokens" value={summary?.total_tokens?.toLocaleString() || "0"} color="purple" />
        <KPICard icon={Coins} label="Total Cost" value={`$${summary?.total_cost_usd?.toFixed(4) || "0"}`} color="green" />
        <KPICard icon={Shield} label="Guardrail Triggers" value={summary?.guardrail_triggers?.toString() || "0"} color="orange" />
        <KPICard icon={AlertTriangle} label="Errors" value={summary?.error_count?.toString() || "0"} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Breakdown */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Coins className="w-5 h-5" /> Cost by Role
          </h2>
          {costs?.cost_by_role && Object.keys(costs.cost_by_role).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(costs.cost_by_role).map(([role, cost]) => (
                <div key={role} className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm text-foreground capitalize">{role}</span>
                  <span className="text-sm font-mono text-muted-foreground">${(cost as number).toFixed(6)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No cost data available</p>
          )}
        </div>

        {/* Guardrail Events */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5" /> Guardrail Events
          </h2>
          {guardrails?.by_type && Object.keys(guardrails.by_type).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(guardrails.by_type).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm text-foreground capitalize">{type}</span>
                  <span className="px-2 py-0.5 text-xs bg-muted rounded text-muted-foreground">{count as number}</span>
                </div>
              ))}
              <div className="pt-2 text-sm font-medium text-foreground">
                Total: {guardrails.total_triggers}
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No guardrail events recorded</p>
          )}
        </div>

        {/* Recent Errors */}
        <div className="bg-card border border-border rounded-xl p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" /> Recent Errors
          </h2>
          {errors?.recent_errors?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground">
                    <th className="pb-2">Endpoint</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2">Error</th>
                    <th className="pb-2">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {errors.recent_errors.slice(0, 10).map((err: any, i: number) => (
                    <tr key={i}>
                      <td className="py-2 text-foreground">{err.endpoint}</td>
                      <td className="py-2"><span className="px-1.5 py-0.5 text-xs bg-destructive/10 text-destructive rounded">{err.status_code}</span></td>
                      <td className="py-2 text-muted-foreground max-w-xs truncate">{err.error || "Unknown"}</td>
                      <td className="py-2 text-muted-foreground">{new Date(err.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No errors recorded</p>
          )}
        </div>
      </div>
    </div>
  );
}

function KPICard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-500/10 text-blue-500",
    yellow: "bg-yellow-500/10 text-yellow-500",
    purple: "bg-purple-500/10 text-purple-500",
    green: "bg-green-500/10 text-green-500",
    orange: "bg-orange-500/10 text-orange-500",
    red: "bg-red-500/10 text-red-500",
  };

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2 ${colorMap[color] || colorMap.blue}`}>
        <Icon className="w-4 h-4" />
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
