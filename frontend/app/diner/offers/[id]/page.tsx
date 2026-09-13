"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { OfferWithRestaurant, Claim } from "@/lib/types";
import { Button, Card, ErrorBanner } from "@/components/ui";

export default function OfferDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [offer, setOffer] = useState<OfferWithRestaurant | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [claiming, setClaiming] = useState(false);

  useEffect(() => {
    api.get<OfferWithRestaurant>(`/offers/${params.id}`).catch(() => null).then((o) => o && setOffer(o));
  }, [params.id]);

  async function claim() {
    setError(null);
    setClaiming(true);
    try {
      const c = await api.post<Claim>(`/claims/offers/${params.id}`);
      router.push(`/diner/claims?justClaimed=${c.id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't claim this offer");
    } finally {
      setClaiming(false);
    }
  }

  if (!offer) return <p className="text-ink/50 text-sm">Loading…</p>;

  const remaining = offer.max_redemptions - offer.redemptions_used;

  return (
    <div>
      <button onClick={() => router.back()} className="text-sm text-ink/50 mb-4">← Back</button>
      <div className="h-40 bg-teal rounded-2xl mb-4 flex items-end p-5">
        <span className="text-paper font-display text-2xl">{offer.restaurant_name}</span>
      </div>

      <div className="flex items-center gap-2 mb-3 text-sm text-ink/60">
        <span>{offer.restaurant_cuisine}</span>
        <span>·</span>
        <span>{offer.restaurant_rating.toFixed(1)} ★</span>
      </div>

      <h1 className="font-display text-2xl mb-2">{offer.title}</h1>
      {offer.description && <p className="text-ink/70 text-sm mb-4">{offer.description}</p>}

      <Card className="mb-4 flex flex-col gap-2 text-sm">
        <div className="flex justify-between"><span className="text-ink/60">Discount</span><span className="font-semibold">{offer.discount_percent}% off</span></div>
        <div className="flex justify-between"><span className="text-ink/60">Valid</span><span>{offer.start_date} → {offer.end_date}</span></div>
        <div className="flex justify-between"><span className="text-ink/60">Window</span><span>{offer.start_time.slice(0,5)}–{offer.end_time.slice(0,5)}</span></div>
        <div className="flex justify-between"><span className="text-ink/60">Remaining</span><span>{remaining} of {offer.max_redemptions}</span></div>
      </Card>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      <Button onClick={claim} disabled={claiming || remaining <= 0} className="w-full">
        {remaining <= 0 ? "Fully claimed" : claiming ? "Claiming…" : "Claim offer"}
      </Button>
    </div>
  );
}
