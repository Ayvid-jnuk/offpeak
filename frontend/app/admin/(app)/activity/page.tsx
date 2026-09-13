"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { cents } from "@/lib/types";
import { Card } from "@/components/ui";

interface ActivityResponse {
  recent_claims: { id: string; offer_id: string; status: string; claimed_at: string }[];
  recent_transactions: { id: string; final_amount_cents: number; platform_commission_cents: number; status: string; created_at: string }[];
}

export default function ActivityPage() {
  const [data, setData] = useState<ActivityResponse | null>(null);

  useEffect(() => {
    api.get<ActivityResponse>("/admin/activity").then(setData).catch(() => null);
  }, []);

  if (!data) return <p className="text-ink/50 text-sm">Loading…</p>;

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Platform activity</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <p className="font-medium text-sm mb-3">Recent claims</p>
          <div className="flex flex-col gap-2">
            {data.recent_claims.map((c) => (
              <Card key={c.id} className="text-sm flex justify-between">
                <span className="font-mono text-xs">{c.id.slice(0, 8)}</span>
                <span>{c.status}</span>
              </Card>
            ))}
          </div>
        </div>
        <div>
          <p className="font-medium text-sm mb-3">Recent transactions</p>
          <div className="flex flex-col gap-2">
            {data.recent_transactions.map((t) => (
              <Card key={t.id} className="text-sm flex justify-between">
                <span>{cents(t.final_amount_cents)}</span>
                <span className="text-ink/50">commission {cents(t.platform_commission_cents)}</span>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
