"use client";

import { useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Textarea } from "@/components/ui";
import { OpeningHoursInput } from "@/components/OpeningHoursInput";

export default function RestaurantApplicationPage() {
  const [form, setForm] = useState({
    name: "", cuisine: "", address: "", description: "", phone: "",
    email: "", opening_hours: "Mon-Sun 11:00-22:00", seating_capacity: "40",
    account_email: "", account_password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function submit() {
    setError(null);
    setLoading(true);
    try {
      await api.post("/restaurants/apply", {
        ...form,
        seating_capacity: parseInt(form.seating_capacity, 10),
      });
      setSubmitted(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't submit application");
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <main className="flex-1 flex items-center justify-center px-6 py-16">
        <div className="max-w-md text-center">
          <h1 className="font-display text-3xl mb-3">Application submitted</h1>
          <p className="text-ink/60 mb-6">
            An OffPeak admin will review {form.name} shortly. Once approved, log in with the
            account email and password you set to start creating offers.
          </p>
          <Link href="/login" className="underline text-sm">Go to login</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-lg">
        <Link href="/" className="font-display text-xl block mb-8">OffPeak</Link>
        <h1 className="font-display text-3xl mb-2">List your restaurant</h1>
        <p className="text-ink/60 text-sm mb-6">
          Tell us about your restaurant. An admin reviews every application before it goes live.
        </p>
        <Card className="flex flex-col gap-4">
          {error && <ErrorBanner message={error} />}
          <Input label="Restaurant name" value={form.name} onChange={(e) => set("name", e.target.value)} />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Cuisine" value={form.cuisine} onChange={(e) => set("cuisine", e.target.value)} />
            <Input label="Seating capacity" type="number" value={form.seating_capacity} onChange={(e) => set("seating_capacity", e.target.value)} />
          </div>
          <Input label="Address" value={form.address} onChange={(e) => set("address", e.target.value)} />
          <Textarea label="Description" rows={3} value={form.description} onChange={(e) => set("description", e.target.value)} />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Phone" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
            <Input label="Public email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} />
          </div>
          <OpeningHoursInput value={form.opening_hours} onChange={(v) => set("opening_hours", v)} />

          <div className="border-t border-line pt-4">
            <p className="text-sm font-medium mb-3">Your login (used once approved)</p>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Account email" type="email" value={form.account_email} onChange={(e) => set("account_email", e.target.value)} />
              <Input label="Account password" type="password" value={form.account_password} onChange={(e) => set("account_password", e.target.value)} />
            </div>
          </div>

          <Button onClick={submit} disabled={loading || !form.name || !form.account_email}>
            {loading ? "Submitting…" : "Submit application"}
          </Button>
        </Card>
      </div>
    </main>
  );
}