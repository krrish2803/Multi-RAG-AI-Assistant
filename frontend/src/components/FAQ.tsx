"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    question: "How does the Knowledge Assistant work?",
    answer:
      "Upload your company documents (PDFs, DOCX, TXT, CSV) and the system automatically chunks, embeds, and indexes them into a vector database. When you ask a question, it retrieves the most relevant document chunks and passes them to an NVIDIA NIM LLM to generate a precise, cited answer.",
  },
  {
    question: "Is my data secure?",
    answer:
      "Yes. All data is encrypted in transit and at rest. We use JWT-based authentication with token refresh, role-based access control (RBAC), and PII detection guardrails. No data leaks outside your organization's authorized boundaries.",
  },
  {
    question: "What file formats are supported?",
    answer:
      "Currently supports PDF, DOCX, TXT, and CSV files. Each document is automatically split into chunks, embedded using NVIDIA's NV-EmbedQA-E5-v5 model, and stored in Qdrant vector database for fast semantic search.",
  },
  {
    question: "Can I control who sees what?",
    answer:
      "Absolutely. The system supports granular RBAC with roles including employee, HR, finance, engineering, marketing, executive, and admin. Each document can be tagged with a department and sensitivity level, and users only see documents their role permits.",
  },
  {
    question: "What LLM powers the answers?",
    answer:
      "We use NVIDIA NIM (NVIDIA Inference Microservices) with Meta's Llama 3.1 70B Instruct model for chat and NVIDIA's NV-EmbedQA-E5-v5 for embeddings. This provides enterprise-grade accuracy and performance.",
  },
  {
    question: "How is usage monitored?",
    answer:
      "The monitoring dashboard tracks request volume, average latency, token usage, and cost in real-time. You can also view guardrail triggers, error logs, and cost breakdowns by role.",
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section id="faq" className="py-20 md:py-28 bg-muted/50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know about the Enterprise Knowledge Assistant.
          </p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-card border border-border rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-center justify-between px-6 py-4 text-left"
              >
                <span className="text-sm font-medium text-foreground">{faq.question}</span>
                <ChevronDown
                  className={`w-4 h-4 text-muted-foreground flex-shrink-0 transition-transform ${
                    openIndex === index ? "rotate-180" : ""
                  }`}
                />
              </button>
              {openIndex === index && (
                <div className="px-6 pb-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
