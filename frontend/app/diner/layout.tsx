"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRequireRole } from "@/lib/useRequireRole";

const TABS = [
  { href: "/diner/discover", label: "Discover" },
  { href: "/diner/claims", label: "My claims" },
  { href: "/diner/wallet", label: "Wallet" },
  { href: "/diner/profile", label: "Profile" },
];

export default function DinerLayout({ children }: { children: React.ReactNode }) {
  const { ready } = useRequireRole("DINER");
  const pathname = usePathname();

  if (!ready) return null;

  return (
    <div className="flex-1 flex flex-col max-w-md mx-auto w-full min-h-screen bg-paper">
      <main className="flex-1 pb-24 px-4 pt-6">{children}</main>
      <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-paper-raised border-t border-line flex justify-around py-3">
        {TABS.map((tab) => {
          const active = pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`text-xs font-medium px-3 py-1 rounded-full transition-all duration-150 ${active ? "text-teal bg-teal/10 shadow-[0_0_0_2px_rgba(23,73,74,0.15)]" : "text-ink/50 hover:text-ink/70"}`}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
