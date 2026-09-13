"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Textarea } from "@/components/ui";

const todayISO = () => new Date().toISOString().slice(0, 10);
const inWeekISO = () => new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);

export default function NewOfferPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [discount, setDiscount] = useState("20");
  const [startDate, setStartDate] = useState(todayISO());
  const [endDate, setEndDate] = useState(inWeekISO());
  const [startTime, setStartTime] = useState("14:00");
  const [endTime, setEndTime] = useState("16:00");
  const [maxRedemptions, setMaxRedemptions] = useState("20");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError(null);
    setLoading(true);
    try {
      await api.post("/offers", {
        title,
        description: description || undefined,
        discount_percent: parseInt(discount, 10),
        start_date: startDate,
        end_date: endDate,
        start_time: `${startTime}:00`,
        end_time: `${endTime}:00`,
        max_redemptions: parseInt(maxRedemptions, 10),
      });
      router.push("/restaurant/offers");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't create offer");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg">
      <h1 className="font-display text-3xl mb-6">New offer</h1>
      <Card className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} />}
        <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Afternoon Pasta Special" />
        <Textarea label="Description (optional)" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
        <div className="grid grid-cols-2 gap-4">
          <Input label="Discount %" type="number" min={1} max={100} value={discount} onChange={(e) => setDiscount(e.target.value)} />
          <Input label="Max redemptions" type="number" min={1} value={maxRedemptions} onChange={(e) => setMaxRedemptions(e.target.value)} />
          <Input label="Start date" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <Input label="End date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          <Input label="Start time" type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          <Input label="End time" type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
        </div>
        <Button onClick={submit} disabled={loading || !title}>
          {loading ? "Publishing…" : "Publish offer"}
        </Button>
      </Card>
    </div>
  );
}
