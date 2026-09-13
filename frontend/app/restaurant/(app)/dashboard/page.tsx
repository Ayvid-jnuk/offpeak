"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Recommendation, RestaurantAnalytics, Claim } from "@/lib/types";
import { DAY_NAMES, cents } from "@/lib/types";
import { Button, Card, ErrorBanner, Input, StatCard } from "@/components/ui";

export default function RestaurantDashboard() {
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [analytics, setAnalytics] = useState<RestaurantAnalytics | null>(null);
  const [loadingRec, setLoadingRec] = useState(false);
  const [creatingOffer, setCreatingOffer] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offerCreated, setOfferCreated] = useState(false);

  const [redemptionCode, setRedemptionCode] = useState("");
  const [redeemResult, setRedeemResult] = useState<Claim | null>(null);
  const [redeemError, setRedeemError] = useState<string | null>(null);

  function loadAnalytics() {
    api.get<RestaurantAnalytics>("/restaurants/me/analytics").then(setAnalytics).catch(() => null);
  }

  useEffect(() => {
    api.get<Recommendation | null>("/restaurants/me/recommendations/latest").then(setRec).catch(() => null);
    loadAnalytics();
  }, []);

  async function generateRecommendation() {
    setError(null);
    setLoadingRec(true);
    try {
      const r = await api.post<Recommendation>("/restaurants/me/recommendations/generate");
      setRec(r);
      setOfferCreated(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Not enough historical data yet");
    } finally {
      setLoadingRec(false);
    }
  }

  async function createOfferFromRec() {
    if (!rec) return;
    setError(null);
    setCreatingOffer(true);
    try {
      await api.post(`/restaurants/me/recommendations/${rec.id}/create-offer`, {
        recommendation_id: rec.id,
        max_redemptions: 20,
      });
      setOfferCreated(true);
      loadAnalytics();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't create offer");
    } finally {
      setCreatingOffer(false);
    }
  }

  async function redeem() {
    setRedeemError(null);
    setRedeemResult(null);
    try {
      const claim = await api.post<Claim>("/claims/redeem", { redemption_code: redemptionCode });
      setRedeemResult(claim);
      setRedemptionCode("");
      loadAnalytics();
    } catch (e) {
      setRedeemError(e instanceof ApiError ? e.message : "Couldn't redeem this code");
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-display text-3xl mb-1">Dashboard</h1>
        <p className="text-ink/60 text-sm">A quick read on today, and where your next off-peak window is.</p>
      </div>

      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard label="Today's revenue" value={cents(analytics.today_revenue_cents)} />
          <StatCard label="Redemption rate" value={`${analytics.redemption_rate_pct}%`} />
          <StatCard label="Unused capacity" value={`${analytics.unused_capacity_pct}%`} />
          <StatCard label="Total claims" value={String(analytics.total_claims)} />
        </div>
      )}

      <Card className="border-saffron/40">
        <div className="flex items-center justify-between mb-4">
          <p className="font-display text-xl">Today&apos;s Opportunity</p>
          <button onClick={generateRecommendation} disabled={loadingRec} className="text-xs text-teal underline">
            {loadingRec ? "Analyzing…" : "Re-run analysis"}
          </button>
        </div>

        {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

        {!rec && !error && (
          <p className="text-sm text-ink/60">
            No recommendation yet. Click &quot;Re-run analysis&quot; to scan your historical occupancy data.
          </p>
        )}

        {rec && rec.recommended_discount_percent === 0 && (
          <p className="text-sm text-ink/70">{rec.rationale}</p>
        )}

        {rec && rec.recommended_discount_percent > 0 && (
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-ink/50 mb-1">Quiet window detected</p>
              <p className="font-display text-2xl mb-1">
                {DAY_NAMES[rec.day_of_week]} {rec.window_start_hour}:00–{rec.window_end_hour}:00
              </p>
              <p className="text-sm text-ink/60">{rec.rationale}</p>
            </div>
            <div className="grid grid-cols-2 gap-3 content-start">
              <div>
                <p className="text-xs text-ink/50">Historical occupancy</p>
                <p className="font-display text-xl">{rec.historical_occupancy_pct}%</p>
              </div>
              <div>
                <p className="text-xs text-ink/50">Available capacity</p>
                <p className="font-display text-xl">{rec.available_capacity} seats</p>
              </div>
              <div>
                <p className="text-xs text-ink/50">Recommended discount</p>
                <p className="font-display text-xl text-saffron-deep">{rec.recommended_discount_percent}%</p>
              </div>
              <div>
                <p className="text-xs text-ink/50">Est. incremental revenue</p>
                <p className="font-display text-xl">+{cents(rec.estimated_incremental_revenue_cents)}</p>
              </div>
            </div>
          </div>
        )}

        {rec && rec.recommended_discount_percent > 0 && (
          <div className="mt-5">
            {offerCreated || rec.was_used_for_offer ? (
              <p className="text-sm text-success font-medium">Offer created from this recommendation.</p>
            ) : (
              <Button onClick={createOfferFromRec} disabled={creatingOffer} variant="secondary">
                {creatingOffer ? "Creating…" : "Create recommended offer"}
              </Button>
            )}
          </div>
        )}
      </Card>

      <Card>
        <p className="font-display text-xl mb-4">Redeem a claim</p>
        <div className="flex gap-3 items-end mb-3">
          <Input
            label="Redemption code"
            placeholder="OFFPEAK-XXXXXX"
            value={redemptionCode}
            onChange={(e) => setRedemptionCode(e.target.value.toUpperCase())}
            className="font-mono"
          />
          <Button onClick={redeem} disabled={!redemptionCode}>Redeem</Button>
        </div>
        {redeemError && <ErrorBanner message={redeemError} />}
        {redeemResult && (
          <p className="text-sm text-success">
            Redeemed! The diner can now complete checkout in their app.
          </p>
        )}
      </Card>
    </div>
  );
}
