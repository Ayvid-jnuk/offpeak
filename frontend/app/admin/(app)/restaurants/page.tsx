"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Restaurant } from "@/lib/types";
import { Card } from "@/components/ui";

export default function AdminRestaurantsPage() {
  const [restaurants, setRestaurants] = useState<Restaurant[] | null>(null);

  useEffect(() => {
    api.get<Restaurant[]>("/admin/restaurants").then(setRestaurants).catch(() => setRestaurants([]));
  }, []);

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Restaurants</h1>
      <div className="grid md:grid-cols-2 gap-3">
        {restaurants?.map((r) => (
          <Card key={r.id}>
            <p className="font-medium mb-1">{r.name}</p>
            <p className="text-sm text-ink/50">{r.cuisine} · {r.seating_capacity} seats · {r.rating.toFixed(1)} ★</p>
            <p className="text-xs text-ink/40 mt-1">{r.address}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
