"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AdminDashboard } from "@/lib/types";
import { cents } from "@/lib/types";
import { StatCard } from "@/components/ui";

export default function AdminDashboardPage() {
  const [d, setD] = useState<AdminDashboard | null>(null);

  useEffect(() => {
    api.get<AdminDashboard>("/admin/dashboard").then(setD).catch(() => null);
  }, []);

  if (!d) return <p className="text-paper/50 text-sm">Loading…</p>;

  return (
    <div>
      <h1 className="font-display text-3xl mb-1">Operations dashboard</h1>
      <p className="text-ink/60 text-sm mb-6">Platform-wide activity across all restaurants and diners.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Restaurants" value={String(d.restaurants)} />
        <StatCard label="Pending applications" value={String(d.pending_applications)} />
        <StatCard label="Active offers" value={String(d.active_offers)} />
        <StatCard label="Active diners" value={String(d.active_diners)} />
        <StatCard label="Total claims" value={String(d.claims)} />
        <StatCard label="Completed transactions" value={String(d.transactions)} />
        <StatCard label="Gross transaction value" value={cents(d.gross_transaction_value_cents)} />
        <StatCard label="Platform commission" value={cents(d.platform_commission_cents)} />
      </div>
    </div>
  );
}
