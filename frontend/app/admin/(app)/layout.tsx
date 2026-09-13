"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useRequireRole } from "@/lib/useRequireRole";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/admin/dashboard", label: "Dashboard" },
  { href: "/admin/applications", label: "Applications" },
  { href: "/admin/restaurants", label: "Restaurants" },
  { href: "/admin/activity", label: "Activity" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { ready } = useRequireRole("ADMIN");
  const pathname = usePathname();
  const { logout } = useAuth();
  const router = useRouter();

  if (!ready) return null;

  return (
    <div className="flex-1 flex min-h-screen">
      <aside className="w-56 border-r border-line bg-ink text-paper flex flex-col px-4 py-6 gap-1">
        <Link href="/admin/dashboard" className="font-display text-xl mb-6 px-2">OffPeak Ops</Link>
        {NAV.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${active ? "bg-saffron text-ink shadow-[0_0_0_3px_rgba(232,163,61,0.3)]" : "text-paper/70 hover:bg-paper/10"}`}
            >
              {item.label}
            </Link>
          );
        })}
        <button
          onClick={() => { logout(); router.push("/"); }}
          className="mt-auto px-3 py-2 text-sm text-paper/40 text-left hover:text-paper"
        >
          Log out
        </button>
      </aside>
      <main className="flex-1 px-8 py-8 max-w-5xl">{children}</main>
    </div>
  );
}
