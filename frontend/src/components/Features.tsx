"use client";

import { Shield, Zap, FileText, Users, BarChart3, Lock } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "AI-Powered RAG",
    description:
      "Retrieve answers from your documents using NVIDIA NIM LLMs with advanced retrieval augmented generation. Get precise, context-aware responses instantly.",
  },
  {
    icon: Shield,
    title: "Guardrails & Safety",
    description:
      "PII detection, topic filtering, and jailbreak prevention built into every query. Ensure sensitive data never leaks outside authorized boundaries.",
  },
  {
    icon: FileText,
    title: "Multi-Format Ingestion",
    description:
      "Upload PDFs, DOCX, TXT, and CSV files. Automatic chunking, embedding, and indexing into Qdrant vector storage for fast semantic search.",
  },
  {
    icon: Users,
    title: "Role-Based Access",
    description:
      "Granular RBAC with employee, HR, finance, engineering, executive, and admin roles. Users only see documents their role permits.",
  },
  {
    icon: BarChart3,
    title: "Monitoring & Analytics",
    description:
      "Track request volume, latency, token usage, and cost in real-time. Monitor guardrail triggers and errors with detailed dashboards.",
  },
  {
    icon: Lock,
    title: "Enterprise Security",
    description:
      "JWT-based authentication with token refresh. Full audit trails, encrypted storage, and SOC 2-aligned security practices out of the box.",
  },
];

export default function Features() {
  return (
    <section id="features" className="py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Everything you need to ship enterprise RAG
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Built for security, scale, and ease of use — from document ingestion to
            answer delivery.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group p-6 bg-card border border-border rounded-xl hover:border-primary/50 transition-colors"
            >
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <feature.icon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
