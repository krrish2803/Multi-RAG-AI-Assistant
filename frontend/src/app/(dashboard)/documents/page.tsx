"use client";

import { useState, useEffect, useRef } from "react";
import api from "@/lib/api";
import type { DocumentItem } from "@/types";
import { useRouter } from "next/navigation";
import { Upload, FileText, Trash2, CheckCircle, XCircle, Clock, Filter, MessageSquare } from "lucide-react";

const DEPARTMENTS = ["company-wide", "hr", "finance", "marketing", "engineering"];
const SENSITIVITY_LEVELS = ["public", "internal", "confidential", "restricted"];

export default function DocumentsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [department, setDepartment] = useState("company-wide");
  const [sensitivity, setSensitivity] = useState("internal");
  const [filterDept, setFilterDept] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const MAX_SIZE = 100 * 1024 * 1024; // 100 MB

  useEffect(() => {
    loadDocuments();
  }, [filterDept]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const params = filterDept ? `?department=${filterDept}` : "";
      const res = await api.get(`/documents${params}`);
      setDocuments(res.data.documents || []);
    } catch {}
    setLoading(false);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError("");
    if (file.size > MAX_SIZE) {
      setUploadError(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum allowed: 100 MB`);
      if (fileRef.current) fileRef.current.value = "";
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("department", department);
    formData.append("sensitivity", sensitivity);

    try {
      await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      loadDocuments();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Upload failed");
    }
    setUploading(false);
    if (fileRef.current) fileRef.current.value = "";
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document and all its embeddings?")) return;
    try {
      await api.delete(`/documents/${id}`);
      loadDocuments();
    } catch {}
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ready": return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "processing": return <Clock className="w-4 h-4 text-yellow-500" />;
      case "failed": return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Documents</h1>
          <p className="text-muted-foreground">Manage company documents and knowledge base</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Upload Document</h2>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-sm text-muted-foreground block mb-1">Department</label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-input rounded-lg text-foreground text-sm"
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">Sensitivity</label>
            <select
              value={sensitivity}
              onChange={(e) => setSensitivity(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-input rounded-lg text-foreground text-sm"
            >
              {SENSITIVITY_LEVELS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <label className="w-full cursor-pointer">
              <div className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity text-sm font-medium">
                <Upload className="w-4 h-4" />
                {uploading ? "Uploading..." : "Choose File"}
              </div>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf,.docx,.txt,.csv,.xlsx,.xls"
                onChange={handleUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>
        </div>
        {uploadError && (
          <p className="text-xs text-destructive mb-2">{uploadError}</p>
        )}
        <p className="text-xs text-muted-foreground">Supported: PDF, DOCX, TXT, CSV, XLSX &bull; Max: 100 MB</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <select
          value={filterDept}
          onChange={(e) => setFilterDept(e.target.value)}
          className="px-3 py-1.5 bg-background border border-input rounded-lg text-sm text-foreground"
        >
          <option value="">All Departments</option>
          {DEPARTMENTS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <span className="text-sm text-muted-foreground">{documents.length} documents</span>
      </div>

      {/* Documents Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">File</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Department</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Sensitivity</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Chunks</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Uploaded</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
            ) : documents.length === 0 ? (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">No documents found</td></tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-accent/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium text-foreground">{doc.filename}</p>
                        <p className="text-xs text-muted-foreground">{doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 text-xs bg-muted rounded text-muted-foreground">{doc.department}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 text-xs rounded ${
                      doc.sensitivity === "restricted" ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                      doc.sensitivity === "confidential" ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400" :
                      "bg-muted text-muted-foreground"
                    }`}>{doc.sensitivity}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(doc.status)}
                      <span className="text-xs text-muted-foreground capitalize">{doc.status}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{doc.chunk_count}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      {doc.status === "ready" && (
                        <button
                          onClick={() => router.push(`/chat?document_id=${doc.id}`)}
                          className="p-1.5 text-primary hover:bg-primary/10 rounded transition-colors"
                          title="Ask AI about this document"
                        >
                          <MessageSquare className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1.5 text-destructive hover:bg-destructive/10 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
