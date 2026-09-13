"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Offer } from "@/lib/types";
import { Badge, Button, Card, EmptyState, ErrorBanner, LinkButton } from "@/components/ui";

const STATUS_TONE: Record<Offer["status"], "neutral" | "success" | "danger" | "saffron"> = {
  ACTIVE: "success",
  INACTIVE: "neutral",
  EXPIRED: "danger",
};

export default function RestaurantOffersPage() {
  const [offers, setOffers] = useState<Offer[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.get<Offer[]>("/offers/mine/list").then(setOffers).catch(() => setOffers([]));
  }

  useEffect(load, []);

  async function toggleStatus(offer: Offer) {
    setError(null);
    try {
      await api.patch(`/offers/${offer.id}`, {
        status: offer.status === "ACTIVE" ? "INACTIVE" : "ACTIVE",
      });
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't update offer");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-3xl">Offers</h1>
        <LinkButton href="/restaurant/offers/new" variant="primary">New offer</LinkButton>
      </div>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      {offers && offers.length === 0 && (
        <EmptyState title="No offers yet" body="Create an offer manually, or use the recommendation on your dashboard to pre-fill one." />
      )}

      <div className="flex flex-col gap-3">
        {offers?.map((offer) => (
          <Card key={offer.id} className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="font-medium">{offer.title}</p>
                <Badge tone={STATUS_TONE[offer.status]}>{offer.status}</Badge>
              </div>
              <p className="text-sm text-ink/50">
                {offer.discount_percent}% off · {offer.start_date} → {offer.end_date} ·{" "}
                {offer.start_time.slice(0, 5)}–{offer.end_time.slice(0, 5)} ·{" "}
                {offer.redemptions_used}/{offer.max_redemptions} claimed
              </p>
            </div>
            {offer.status !== "EXPIRED" && (
              <Button variant="ghost" onClick={() => toggleStatus(offer)}>
                {offer.status === "ACTIVE" ? "Deactivate" : "Activate"}
              </Button>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
