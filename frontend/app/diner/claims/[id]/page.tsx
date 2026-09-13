"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { QRCodeSVG } from "qrcode.react";
import { api, ApiError } from "@/lib/api";
import type { Claim, Offer, Transaction } from "@/lib/types";
import { cents } from "@/lib/types";
import { Badge, Button, Card, ErrorBanner, Input } from "@/components/ui";

export default function ClaimDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [claim, setClaim] = useState<Claim | null>(null);
  const [offer, setOffer] = useState<Offer | null>(null);
  const [billAmount, setBillAmount] = useState("120.00");
  const [txn, setTxn] = useState<Transaction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    const c = await api.get<Claim>(`/claims/${params.id}`);
    setClaim(c);
    const o = await api.get<Offer>(`/offers/${c.offer_id}`);
    setOffer(o);
  }

  useEffect(() => {
    refresh().catch(() => setError("Couldn't load this claim"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function checkout() {
    if (!claim) return;
    setError(null);
    setLoading(true);
    try {
      const original_amount_cents = Math.round(parseFloat(billAmount) * 100);
      const result = await api.post<Transaction>("/transactions", {
        claim_id: claim.id,
        original_amount_cents,
      });
      setTxn(result);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Checkout failed");
    } finally {
      setLoading(false);
    }
  }

  if (!claim || !offer) return <p className="text-ink/50 text-sm">Loading…</p>;

  return (
    <div>
      <button onClick={() => router.back()} className="text-sm text-ink/50 mb-4">← Back</button>
      <h1 className="font-display text-2xl mb-1">{offer.title}</h1>
      <div className="mb-4"><Badge tone={claim.status === "REDEEMED" ? "success" : "saffron"}>{claim.status}</Badge></div>

      <Card className="flex flex-col items-center gap-4 mb-6">
        <QRCodeSVG value={claim.redemption_code} size={160} />
        <p className="font-mono text-lg tracking-wide">{claim.redemption_code}</p>
        <p className="text-xs text-ink/50 text-center">
          Show this code to restaurant staff to redeem your {offer.discount_percent}% discount.
        </p>
      </Card>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      {txn ? (
        <Card className="flex flex-col gap-2 text-sm">
          <p className="font-display text-xl mb-2">Payment complete</p>
          <div className="flex justify-between"><span className="text-ink/60">Original bill</span><span>{cents(txn.original_amount_cents)}</span></div>
          <div className="flex justify-between"><span className="text-ink/60">Discount</span><span>-{cents(txn.discount_amount_cents)}</span></div>
          <div className="flex justify-between font-semibold"><span>You paid</span><span>{cents(txn.final_amount_cents)}</span></div>
          <div className="border-t border-line my-2" />
          <div className="flex justify-between text-ink/50"><span>Platform commission</span><span>{cents(txn.platform_commission_cents)}</span></div>
          <div className="flex justify-between text-ink/50"><span>Restaurant receives</span><span>{cents(txn.restaurant_payout_cents)}</span></div>
        </Card>
      ) : claim.status === "REDEEMED" ? (
        <Card className="flex flex-col gap-3">
          <p className="font-medium text-sm">Complete your payment</p>
          <Input
            label="Bill total before discount"
            type="number"
            step="0.01"
            value={billAmount}
            onChange={(e) => setBillAmount(e.target.value)}
          />
          <Button onClick={checkout} disabled={loading}>
            {loading ? "Processing…" : `Pay ${offer.discount_percent}% off`}
          </Button>
        </Card>
      ) : (
        <p className="text-sm text-ink/60 text-center">
          Waiting for the restaurant to redeem this code at your table.
        </p>
      )}
    </div>
  );
}
