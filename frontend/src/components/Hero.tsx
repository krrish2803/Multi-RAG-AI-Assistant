"use client";

import Link from "next/link";
import { ArrowRight, Sparkles, Shield, Zap } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-sm font-medium rounded-full mb-6">
            <Sparkles className="w-4 h-4" />
            Enterprise-Grade RAG Platform
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-foreground tracking-tight leading-tight">
            Your Company Knowledge,
            <span className="text-primary"> Instantly Answered</span>
          </h1>

          <p className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Securely query your internal documents, policies, and data with AI-powered
            retrieval augmented generation. Role-based access, guardrails, and full audit
            trails built in.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-opacity text-base"
            >
              Get Started Free
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-6 py-3 bg-card border border-border text-foreground rounded-xl font-medium hover:bg-accent transition-colors text-base"
            >
              Sign In
            </Link>
          </div>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          <div className="flex items-center gap-3 px-4 py-3 bg-card border border-border rounded-xl">
            <Shield className="w-5 h-5 text-primary flex-shrink-0" />
            <span className="text-sm text-foreground">RBAC & Guardrails</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 bg-card border border-border rounded-xl">
            <Zap className="w-5 h-5 text-primary flex-shrink-0" />
            <span className="text-sm text-foreground">NVIDIA-Powered LLMs</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 bg-card border border-border rounded-xl md:col-span-1">
            <svg className="w-5 h-5 text-primary flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-sm text-foreground">Multi-Format Support</span>
          </div>
        </div>
      </div>
    </section>
  );
}
