"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import type { EvalRun, EvalResult } from "@/types";
import { FlaskConical, Play, CheckCircle, Clock, XCircle, BarChart } from "lucide-react";

export default function EvaluationsPage() {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [results, setResults] = useState<EvalResult[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadRuns();
  }, []);

  useEffect(() => {
    if (selectedRunId) loadResults(selectedRunId);
  }, [selectedRunId]);

  const loadRuns = async () => {
    setLoading(true);
    try {
      const res = await api.get("/evaluation/runs");
      setRuns(res.data || []);
    } catch {}
    setLoading(false);
  };

  const loadResults = async (runId: string) => {
    try {
      const res = await api.get(`/evaluation/results/${runId}`);
      setResults(res.data || []);
    } catch {}
  };

  const handleRunEval = async () => {
    setRunning(true);
    try {
      await api.post("/evaluation/run", { dataset_name: "default" });
      setTimeout(loadRuns, 2000);
    } catch {}
    setRunning(false);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed": return <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded"><CheckCircle className="w-3 h-3" />Completed</span>;
      case "running": return <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 rounded"><Clock className="w-3 h-3" />Running</span>;
      case "failed": return <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded"><XCircle className="w-3 h-3" />Failed</span>;
      default: return <span className="px-2 py-0.5 text-xs bg-muted text-muted-foreground rounded">{status}</span>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Evaluations</h1>
          <p className="text-muted-foreground">RAG quality assessment and regression testing</p>
        </div>
        <button
          onClick={handleRunEval}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 text-sm font-medium"
        >
          <Play className="w-4 h-4" />
          {running ? "Running..." : "Run Evaluation"}
        </button>
      </div>

      {/* Eval Runs */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-muted border-b border-border">
          <h2 className="font-semibold text-foreground text-sm">Evaluation Runs</h2>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs text-muted-foreground">
              <th className="px-4 py-2">Run Name</th>
              <th className="px-4 py-2">Dataset</th>
              <th className="px-4 py-2">Questions</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
            ) : runs.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">No evaluation runs yet. Click &quot;Run Evaluation&quot; to start.</td></tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id} className="hover:bg-accent/50">
                  <td className="px-4 py-3 text-sm font-medium text-foreground">{run.run_name}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{run.dataset_name}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{run.total_questions}</td>
                  <td className="px-4 py-3">{getStatusBadge(run.status)}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(run.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setSelectedRunId(run.id)}
                      className="text-xs text-primary hover:underline"
                    >
                      View Results
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Results */}
      {selectedRunId && results.length > 0 && (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <div className="px-4 py-3 bg-muted border-b border-border flex items-center justify-between">
            <h2 className="font-semibold text-foreground text-sm">Results for selected run</h2>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>Avg Faithfulness: {avg(results.map(r => r.faithfulness))}</span>
              <span>Avg Relevancy: {avg(results.map(r => r.answer_relevancy))}</span>
              <span>Avg Precision: {avg(results.map(r => r.context_precision))}</span>
              <span>Avg Recall: {avg(results.map(r => r.context_recall))}</span>
            </div>
          </div>
          <div className="divide-y divide-border">
            {results.map((result) => (
              <div key={result.id} className="p-4">
                <p className="text-sm font-medium text-foreground mb-1">Q: {result.question}</p>
                <p className="text-xs text-muted-foreground mb-2">Expected: {result.ground_truth}</p>
                <p className="text-xs text-foreground mb-3">Generated: {result.generated_answer}</p>
                <div className="flex gap-3 text-xs">
                  <MetricBadge label="Faithfulness" value={result.faithfulness} />
                  <MetricBadge label="Relevancy" value={result.answer_relevancy} />
                  <MetricBadge label="Precision" value={result.context_precision} />
                  <MetricBadge label="Recall" value={result.context_recall} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function avg(values: (number | undefined | null)[]): string {
  const valid = values.filter((v): v is number => v != null && !isNaN(v));
  if (valid.length === 0) return "N/A";
  return (valid.reduce((a, b) => a + b, 0) / valid.length).toFixed(3);
}

function MetricBadge({ label, value }: { label: string; value?: number | null }) {
  if (value == null) return <span className="px-2 py-0.5 bg-muted rounded text-muted-foreground">{label}: N/A</span>;
  const color = value >= 0.7 ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                value >= 0.4 ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
  return <span className={`px-2 py-0.5 rounded ${color}`}>{label}: {value.toFixed(3)}</span>;
}
