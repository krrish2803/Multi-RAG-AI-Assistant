"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

export default function CTA() {
  return (
    <section className="py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-2xl bg-primary px-8 py-16 md:py-20 text-center">
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-3xl" />
          </div>

          <div className="max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 text-white text-sm font-medium rounded-full mb-6">
              <Sparkles className="w-4 h-4" />
              Get Started Today
            </div>

            <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground">
              Ready to transform how your team finds information?
            </h2>

            <p className="mt-4 text-lg text-primary-foreground/80 max-w-lg mx-auto">
              Deploy the Enterprise Knowledge Assistant and give your team instant,
              secure access to company knowledge.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 px-6 py-3 bg-white text-primary rounded-xl font-medium hover:opacity-90 transition-opacity text-base"
              >
                Create Your Account
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-foreground/10 text-primary-foreground border border-primary-foreground/20 rounded-xl font-medium hover:bg-primary-foreground/20 transition-colors text-base"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
