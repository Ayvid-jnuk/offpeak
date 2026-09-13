"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button, Card, ErrorBanner, Input } from "@/components/ui";
import type { Role } from "@/lib/types";

function roleHome(role: Role): string {
  if (role === "DINER") return "/diner/discover";
  if (role === "RESTAURANT") return "/restaurant/dashboard";
  return "/admin/dashboard";
}

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [mode, setMode] = useState<"phone" | "email">("phone");

  const [phone, setPhone] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [code, setCode] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function sendOtp() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<{ message: string; dev_otp: string | null }>("/auth/send-otp", {
        phone_number: phone,
      });
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
        phone_number: phone,
        code,
      });
      login(res.access_token, res.role, res.user_id);
      router.push(roleHome(res.role));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Invalid code");
    } finally {
      setLoading(false);
    }
  }

  async function emailLogin() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<{ access_token: string; role: Role; user_id: string }>("/auth/login", {
        email, password,
      });
      login(res.access_token, res.role, res.user_id);
      router.push(roleHome(res.role));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Invalid email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm">
        <Link href="/" className="font-display text-xl block mb-8">OffPeak</Link>
        <h1 className="font-display text-3xl mb-2">Welcome back</h1>
        <p className="text-ink/60 text-sm mb-6">
          Diners sign in with a phone number. Restaurants and admins use email.
        </p>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => { setMode("phone"); setError(null); }}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-150 active:scale-95 ${mode === "phone" ? "bg-teal text-paper shadow-[0_0_0_4px_rgba(23,73,74,0.22)]" : "bg-paper-raised border border-line hover:border-teal-soft"}`}
          >
            Diner (phone)
          </button>
          <button
            onClick={() => { setMode("email"); setError(null); }}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-150 active:scale-95 ${mode === "email" ? "bg-teal text-paper shadow-[0_0_0_4px_rgba(23,73,74,0.22)]" : "bg-paper-raised border border-line hover:border-teal-soft"}`}
          >
            Restaurant / Admin
          </button>
        </div>

        <Card className="flex flex-col gap-4">
          {error && <ErrorBanner message={error} />}

          {mode === "phone" && !otpSent && (
            <>
              <Input
                label="Phone number"
                placeholder="+61 4XX XXX XXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <Button onClick={sendOtp} disabled={loading || phone.length < 6}>
                Send verification code
              </Button>
              <p className="text-xs text-ink/50">
                Demo diner: +61400000000
              </p>
            </>
          )}

          {mode === "phone" && otpSent && (
            <>
              <p className="text-sm text-ink/70">
                Enter the 6-digit code sent to {phone}.
                {devOtp && <span className="block mt-1 text-saffron-deep font-medium">Dev mode code: {devOtp}</span>}
              </p>
              <Input
                label="Verification code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                maxLength={6}
              />
              <Button onClick={verifyOtp} disabled={loading || code.length < 4}>
                Verify & continue
              </Button>
              <button className="text-xs text-ink/50 underline self-start" onClick={() => setOtpSent(false)}>
                Use a different number
              </button>
            </>
          )}

          {mode === "email" && (
            <>
              <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button onClick={emailLogin} disabled={loading || !email || !password}>
                Log in
              </Button>
              <p className="text-xs text-ink/50">
                Demo restaurant: luna@offpeak.app · Demo admin: admin@offpeak.app · password: demo1234
              </p>
            </>
          )}
        </Card>
      </div>
    </main>
  );
}
