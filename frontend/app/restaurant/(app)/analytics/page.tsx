"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { RestaurantAnalytics } from "@/lib/types";
import { cents } from "@/lib/types";
import { Card, StatCard } from "@/components/ui";

export default function AnalyticsPage() {
  const [a, setA] = useState<RestaurantAnalytics | null>(null);

  useEffect(() => {
    api.get<RestaurantAnalytics>("/restaurants/me/analytics").then(setA).catch(() => null);
  }, []);

  if (!a) return <p className="text-ink/50 text-sm">Loading…</p>;

  return (
    <div>
      <h1 className="font-display text-3xl mb-1">Analytics</h1>
      <p className="text-ink/60 text-sm mb-6">
        Demo metrics computed from seeded transactions and claims — labelled where the underlying data is simulated.
      </p>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <StatCard label="Today's revenue" value={cents(a.today_revenue_cents)} hint="Your payout after commission" />
        <StatCard label="Total offer revenue" value={cents(a.offer_revenue_cents)} hint="Diner-paid amount across all offers" />
        <StatCard label="Average transaction" value={cents(a.average_transaction_cents)} />
        <StatCard label="Redemption rate" value={`${a.redemption_rate_pct}%`} hint="Redeemed / claimed" />
        <StatCard label="Unused capacity" value={`${a.unused_capacity_pct}%`} hint="From historical seating data" />
        <StatCard label="Est. incremental revenue" value={cents(a.estimated_incremental_revenue_cents)} hint="From your latest recommendation" />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <p className="text-sm text-ink/50 mb-1">Best performing offer</p>
          <p className="font-display text-xl">{a.best_performing_offer ?? "—"}</p>
        </Card>
        <Card>
          <p className="text-sm text-ink/50 mb-1">Best performing time window</p>
          <p className="font-display text-xl">{a.best_performing_time_window ?? "—"}</p>
        </Card>
      </div>
    </div>
  );
}
