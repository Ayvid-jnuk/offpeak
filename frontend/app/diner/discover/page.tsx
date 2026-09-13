"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { OfferWithRestaurant } from "@/lib/types";
import { EmptyState } from "@/components/ui";

function formatTime(t: string) {
  const [h, m] = t.split(":");
  const hour = parseInt(h, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  const h12 = hour % 12 === 0 ? 12 : hour % 12;
  return `${h12}:${m} ${ampm}`;
}

export default function DiscoverPage() {
  const { logout } = useAuth();
  const [offers, setOffers] = useState<OfferWithRestaurant[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<OfferWithRestaurant[]>("/offers")
      .then(setOffers)
      .catch(() => setError("Couldn't load offers right now."));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-display text-3xl">Good food.</h1>
        <button onClick={logout} className="text-xs text-ink/40 underline">Log out</button>
      </div>
      <p className="font-display text-3xl italic text-saffron-deep mb-6">Better timing.</p>

      {error && <p className="text-danger text-sm">{error}</p>}

      {offers && offers.length === 0 && (
        <EmptyState title="No offers right now" body="Check back soon — restaurants post new off-peak windows throughout the week." />
      )}

      <div className="flex flex-col gap-4">
        {offers?.map((offer) => {
          const savings = Math.round((offer.discount_percent / 100) * 4000) / 100; // rough illustrative estimate
          return (
            <Link
              key={offer.id}
              href={`/diner/offers/${offer.id}`}
              className="block rounded-2xl overflow-hidden border border-line bg-paper-raised hover:shadow-md transition-shadow"
            >
              <div className="h-32 bg-teal relative flex items-end p-4">
                <span className="absolute top-3 right-3 bg-saffron text-ink text-sm font-semibold px-3 py-1 rounded-full">
                  {offer.discount_percent}% OFF
                </span>
                <span className="text-paper font-display text-xl">{offer.restaurant_name}</span>
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between text-sm text-ink/60 mb-2">
                  <span>{offer.restaurant_cuisine} · {offer.restaurant_rating.toFixed(1)} ★</span>
                  <span>{formatTime(offer.start_time)}–{formatTime(offer.end_time)}</span>
                </div>
                <p className="font-medium mb-2">{offer.title}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-ink/50">
                    {offer.max_redemptions - offer.redemptions_used} left today
                  </span>
                  <span className="text-sm font-semibold text-teal">Save ~${savings.toFixed(0)}</span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
