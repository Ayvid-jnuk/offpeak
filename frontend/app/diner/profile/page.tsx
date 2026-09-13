"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Me, LoyaltyAccount, Claim } from "@/lib/types";
import { Button, Card, ErrorBanner, Input } from "@/components/ui";

export default function ProfilePage() {
  const { logout } = useAuth();
  const router = useRouter();

  const [me, setMe] = useState<Me | null>(null);
  const [points, setPoints] = useState<number | null>(null);
  const [claimsCount, setClaimsCount] = useState<number | null>(null);

  const [editing, setEditing] = useState(false);
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Me>("/auth/me").then((m) => { setMe(m); setName(m.full_name ?? ""); }).catch(() => null);
    api.get<LoyaltyAccount>("/loyalty").then((l) => setPoints(l.points_balance)).catch(() => null);
    api.get<Claim[]>("/claims").then((c) => setClaimsCount(c.length)).catch(() => null);
  }, []);

  async function saveName() {
    setError(null);
    setSaving(true);
    try {
      const updated = await api.patch<Me>("/auth/me", { full_name: name });
      setMe(updated);
      setEditing(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't save your name");
    } finally {
      setSaving(false);
    }
  }

  if (!me) return <p className="text-ink/50 text-sm">Loading…</p>;

  const initial = (me.full_name || "D").trim().charAt(0).toUpperCase();
  const memberSince = new Date(me.created_at).toLocaleDateString(undefined, { month: "long", year: "numeric" });

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Profile</h1>

      <Card className="flex items-center gap-4 mb-4">
        <div className="w-14 h-14 rounded-full bg-teal text-paper flex items-center justify-center font-display text-2xl shrink-0">
          {initial}
        </div>
        <div className="flex-1 min-w-0">
          {editing ? (
            <div className="flex items-center gap-2">
              <Input value={name} onChange={(e) => setName(e.target.value)} className="py-1.5" />
              <Button onClick={saveName} disabled={saving || !name.trim()} className="shrink-0 px-3 py-1.5 text-xs">
                {saving ? "…" : "Save"}
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <p className="font-display text-xl truncate">{me.full_name || "Diner"}</p>
              <button
                onClick={() => setEditing(true)}
                className="text-xs text-teal underline shrink-0 transition-opacity hover:opacity-70"
              >
                Edit
              </button>
            </div>
          )}
          <p className="text-xs text-ink/50 mt-0.5">Member since {memberSince}</p>
        </div>
      </Card>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      <div className="grid grid-cols-2 gap-3 mb-4">
        <Card className="text-center">
          <p className="font-display text-2xl">{points ?? "–"}</p>
          <p className="text-xs text-ink/50">Loyalty points</p>
        </Card>
        <Card className="text-center">
          <p className="font-display text-2xl">{claimsCount ?? "–"}</p>
          <p className="text-xs text-ink/50">Offers claimed</p>
        </Card>
      </div>

      <Card className="mb-6 flex flex-col divide-y divide-line text-sm">
        <div className="flex justify-between py-2.5 first:pt-0">
          <span className="text-ink/60">Phone number</span>
          <span>{me.phone_number ?? "—"}</span>
        </div>
        <div className="flex justify-between py-2.5">
          <span className="text-ink/60">Email</span>
          <span>{me.email ?? "—"}</span>
        </div>
        <div className="flex justify-between py-2.5 last:pb-0">
          <span className="text-ink/60">Account type</span>
          <span>Diner</span>
        </div>
      </Card>

      <Button
        variant="ghost"
        onClick={() => { logout(); router.push("/"); }}
        className="w-full"
      >
        Log out
      </Button>
    </div>
  );
}