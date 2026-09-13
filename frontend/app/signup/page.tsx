"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button, Card, ErrorBanner, Input } from "@/components/ui";
import type { Role } from "@/lib/types";

export default function SignupPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function sendOtp() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<{ dev_otp: string | null }>("/auth/send-otp", { phone_number: phone });
      setOtpSent(true);
      setDevOtp(res.dev_otp);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not send code");
    } finally {
      setLoading(false);
    }
  }

  async function verifyOtp() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<{ access_token: string; role: Role; user_id: string }>("/auth/verify-otp", {
        phone_number: phone, code, full_name: name || undefined,
      });
      login(res.access_token, res.role, res.user_id);
      router.push("/diner/discover");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Invalid code");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm">
        <Link href="/" className="font-display text-xl block mb-8">OffPeak</Link>
        <h1 className="font-display text-3xl mb-2">Find tonight&apos;s offers</h1>
        <p className="text-ink/60 text-sm mb-6">Sign up with your phone number — no password needed.</p>

        <Card className="flex flex-col gap-4">
          {error && <ErrorBanner message={error} />}
          {!otpSent && (
            <>
              <Input label="Your name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input label="Phone number" placeholder="+61 4XX XXX XXX" value={phone} onChange={(e) => setPhone(e.target.value)} />
              <Button onClick={sendOtp} disabled={loading || phone.length < 6}>Send verification code</Button>
            </>
          )}
          {otpSent && (
            <>
              <p className="text-sm text-ink/70">
                Enter the 6-digit code sent to {phone}.
                {devOtp && <span className="block mt-1 text-saffron-deep font-medium">Dev mode code: {devOtp}</span>}
              </p>
              <Input label="Verification code" value={code} onChange={(e) => setCode(e.target.value)} maxLength={6} />
              <Button onClick={verifyOtp} disabled={loading || code.length < 4}>Verify & continue</Button>
            </>
          )}
        </Card>
        <p className="text-sm text-ink/50 mt-4">
          Already have an account? <Link href="/login" className="underline">Log in</Link>
        </p>
      </div>
    </main>
  );
}
