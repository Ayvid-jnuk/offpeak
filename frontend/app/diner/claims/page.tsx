"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Claim } from "@/lib/types";
import { Badge, EmptyState } from "@/components/ui";

const STATUS_TONE: Record<Claim["status"], "neutral" | "success" | "danger" | "saffron"> = {
  CLAIMED: "saffron",
  REDEEMED: "success",
  EXPIRED: "danger",
  CANCELLED: "neutral",
};

export default function ClaimsPage() {
  const [claims, setClaims] = useState<Claim[] | null>(null);

  useEffect(() => {
    api.get<Claim[]>("/claims").then(setClaims).catch(() => setClaims([]));
  }, []);

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">My claims</h1>

      {claims && claims.length === 0 && (
        <EmptyState title="No claims yet" body="Claim an off-peak offer from Discover and it'll show up here with your redemption code." />
      )}

      <div className="flex flex-col gap-3">
        {claims?.map((claim) => (
          <Link
            key={claim.id}
            href={`/diner/claims/${claim.id}`}
            className="flex items-center justify-between bg-paper-raised border border-line rounded-xl px-4 py-3"
          >
            <div>
              <p className="font-mono text-sm">{claim.redemption_code}</p>
              <p className="text-xs text-ink/50">{new Date(claim.claimed_at).toLocaleDateString()}</p>
            </div>
            <Badge tone={STATUS_TONE[claim.status]}>{claim.status}</Badge>
          </Link>
        ))}
      </div>
    </div>
  );
}
