"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useRequireRole } from "@/lib/useRequireRole";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/restaurant/dashboard", label: "Dashboard" },
  { href: "/restaurant/offers", label: "Offers" },
  { href: "/restaurant/analytics", label: "Analytics" },
];

export default function RestaurantLayout({ children }: { children: React.ReactNode }) {
  const { ready } = useRequireRole("RESTAURANT");
  const pathname = usePathname();
  const { logout } = useAuth();
  const router = useRouter();

  if (!ready) return null;

  return (
    <div className="flex-1 flex min-h-screen">
      <aside className="w-56 border-r border-line bg-paper-raised flex flex-col px-4 py-6 gap-1">
        <Link href="/restaurant/dashboard" className="font-display text-xl mb-6 px-2">OffPeak</Link>
        {NAV.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${active ? "bg-teal text-paper shadow-[0_0_0_3px_rgba(23,73,74,0.2)]" : "text-ink/70 hover:bg-paper"}`}
            >
              {item.label}
            </Link>
          );
        })}
        <button
          onClick={() => { logout(); router.push("/"); }}
          className="mt-auto px-3 py-2 text-sm text-ink/40 text-left hover:text-ink"
        >
          Log out
        </button>
      </aside>
      <main className="flex-1 px-8 py-8 max-w-5xl">{children}</main>
    </div>
  );
}
