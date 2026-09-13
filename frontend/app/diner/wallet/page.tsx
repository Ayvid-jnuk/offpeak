"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { LoyaltyAccount } from "@/lib/types";
import { cents } from "@/lib/types";
import { Button, Card, ErrorBanner } from "@/components/ui";

const POINTS_PER_CREDIT = 500;

export default function WalletPage() {
  const [account, setAccount] = useState<LoyaltyAccount | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [redeeming, setRedeeming] = useState(false);

  function load() {
    api.get<LoyaltyAccount>("/loyalty").then(setAccount).catch(() => setError("Couldn't load your wallet"));
  }

  useEffect(load, []);

  async function redeem() {
    setError(null);
    setRedeeming(true);
    try {
      await api.post("/loyalty/redeem", { points: POINTS_PER_CREDIT });
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't redeem points");
    } finally {
      setRedeeming(false);
    }
  }

  if (!account) return <p className="text-ink/50 text-sm">Loading…</p>;

  const canRedeem = account.points_balance >= POINTS_PER_CREDIT;
  const progress = Math.min(100, (account.points_balance % POINTS_PER_CREDIT) / POINTS_PER_CREDIT * 100);

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Wallet</h1>

      <Card className="bg-teal text-paper mb-4">
        <p className="text-sm text-paper/60 mb-1">Points balance</p>
        <p className="font-display text-5xl mb-4">{account.points_balance}</p>
        <div className="h-2 rounded-full bg-paper/20 overflow-hidden mb-2">
          <div className="h-full bg-saffron" style={{ width: `${canRedeem ? 100 : progress}%` }} />
        </div>
        <p className="text-xs text-paper/60">
          {canRedeem
            ? "You have enough points for a $10 credit."
            : `${POINTS_PER_CREDIT - (account.points_balance % POINTS_PER_CREDIT)} pts to your next $10 credit`}
        </p>
      </Card>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      <div className="grid grid-cols-2 gap-3 mb-6">
        <Card>
          <p className="text-xs text-ink/50 mb-1">Lifetime earned</p>
          <p className="font-display text-2xl">{account.lifetime_points_earned}</p>
        </Card>
        <Card>
          <p className="text-xs text-ink/50 mb-1">Available credit</p>
          <p className="font-display text-2xl">{cents(account.credits_available_cents)}</p>
        </Card>
      </div>

      <Button onClick={redeem} disabled={!canRedeem || redeeming} className="w-full mb-8">
        {redeeming ? "Redeeming…" : `Redeem ${POINTS_PER_CREDIT} pts for $10 credit`}
      </Button>

      <p className="font-medium text-sm mb-3">Recent activity</p>
      <div className="flex flex-col gap-2">
        {account.recent_activity.map((txn) => (
          <div key={txn.id} className="flex items-center justify-between text-sm bg-paper-raised border border-line rounded-xl px-4 py-3">
            <div>
              <p>{txn.reason}</p>
              <p className="text-xs text-ink/40">{new Date(txn.created_at).toLocaleDateString()}</p>
            </div>
            <span className={txn.points >= 0 ? "text-success font-medium" : "text-danger font-medium"}>
              {txn.points >= 0 ? "+" : ""}{txn.points}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
