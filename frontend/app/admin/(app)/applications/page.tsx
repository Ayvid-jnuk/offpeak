"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { RestaurantApplication } from "@/lib/types";
import { Badge, Button, Card, EmptyState, ErrorBanner } from "@/components/ui";

const STATUS_TONE: Record<RestaurantApplication["status"], "neutral" | "success" | "danger" | "saffron"> = {
  PENDING: "saffron",
  APPROVED: "success",
  REJECTED: "danger",
};

export default function ApplicationsPage() {
  const [apps, setApps] = useState<RestaurantApplication[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  function load() {
    api.get<RestaurantApplication[]>("/admin/applications").then(setApps).catch(() => setApps([]));
  }

  useEffect(load, []);

  async function review(id: string, action: "approve" | "reject") {
    setError(null);
    setBusyId(id);
    try {
      await api.post(`/admin/applications/${id}/${action}`, { notes: null });
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't update application");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Applications</h1>
      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      {apps && apps.length === 0 && (
        <EmptyState title="No applications" body="Restaurant applications will appear here as they come in." />
      )}

      <div className="flex flex-col gap-3">
        {apps?.map((app) => (
          <Card key={app.id} className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="font-medium">{app.name}</p>
                <Badge tone={STATUS_TONE[app.status]}>{app.status}</Badge>
              </div>
              <p className="text-sm text-ink/50">
                {app.cuisine} · {app.address} · {app.seating_capacity} seats
              </p>
            </div>
            {app.status === "PENDING" && (
              <div className="flex gap-2">
                <Button variant="ghost" disabled={busyId === app.id} onClick={() => review(app.id, "reject")}>
                  Reject
                </Button>
                <Button disabled={busyId === app.id} onClick={() => review(app.id, "approve")}>
                  Approve
                </Button>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
