import { ReactNode, ButtonHTMLAttributes } from "react";
import Link from "next/link";

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger" }) {
  const base = "inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-150 ease-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:active:scale-100";
  const variants: Record<string, string> = {
    primary: "bg-teal text-paper hover:bg-teal-soft hover:shadow-[0_0_0_4px_rgba(23,73,74,0.22)]",
    secondary: "bg-saffron text-ink hover:bg-saffron-deep hover:shadow-[0_0_0_4px_rgba(232,163,61,0.35)]",
    ghost: "bg-transparent text-ink border border-line hover:bg-paper-raised hover:border-teal-soft hover:shadow-[0_0_0_4px_rgba(23,73,74,0.12)]",
    danger: "bg-danger text-paper hover:opacity-90 hover:shadow-[0_0_0_4px_rgba(176,67,46,0.25)]",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function LinkButton({
  href, children, variant = "primary", className = "",
}: { href: string; children: ReactNode; variant?: "primary" | "secondary" | "ghost"; className?: string }) {
  const base = "inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-150 ease-out active:scale-95";
  const variants: Record<string, string> = {
    primary: "bg-teal text-paper hover:bg-teal-soft hover:shadow-[0_0_0_4px_rgba(23,73,74,0.22)]",
    secondary: "bg-saffron text-ink hover:bg-saffron-deep hover:shadow-[0_0_0_4px_rgba(232,163,61,0.35)]",
    ghost: "bg-transparent text-ink border border-line hover:bg-paper-raised hover:border-teal-soft hover:shadow-[0_0_0_4px_rgba(23,73,74,0.12)]",
  };
  return (
    <Link href={href} className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </Link>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-paper-raised border border-line rounded-2xl p-5 ${className}`}>
      {children}
    </div>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "danger" | "saffron" }) {
  const tones: Record<string, string> = {
    neutral: "bg-line/60 text-ink",
    success: "bg-success/15 text-success",
    danger: "bg-danger/15 text-danger",
    saffron: "bg-saffron/20 text-saffron-deep",
  };
  return (
    <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card className="flex flex-col gap-1">
      <span className="text-sm text-ink/60">{label}</span>
      <span className="font-display text-3xl">{value}</span>
      {hint && <span className="text-xs text-ink/50">{hint}</span>}
    </Card>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement> & { label?: string }) {
  const { label, id, className = "", ...rest } = props;
  return (
    <label className="flex flex-col gap-1.5 text-sm" htmlFor={id}>
      {label && <span className="text-ink/70">{label}</span>}
      <input
        id={id}
        className={`px-4 py-2.5 rounded-xl border border-line bg-paper focus:bg-paper-raised outline-none ${className}`}
        {...rest}
      />
    </label>
  );
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label?: string }) {
  const { label, id, className = "", ...rest } = props;
  return (
    <label className="flex flex-col gap-1.5 text-sm" htmlFor={id}>
      {label && <span className="text-ink/70">{label}</span>}
      <textarea
        id={id}
        className={`px-4 py-2.5 rounded-xl border border-line bg-paper focus:bg-paper-raised outline-none ${className}`}
        {...rest}
      />
    </label>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="text-center py-16 px-6 border border-dashed border-line rounded-2xl">
      <p className="font-display text-xl mb-2">{title}</p>
      <p className="text-ink/60 text-sm max-w-sm mx-auto">{body}</p>
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="bg-danger/10 border border-danger/30 text-danger rounded-xl px-4 py-3 text-sm">
      {message}
    </div>
  );
}