import Link from "next/link";
import { LinkButton } from "@/components/ui";

export default function Home() {
  return (
    <main className="flex-1 flex flex-col">
      <header className="max-w-6xl w-full mx-auto flex items-center justify-between px-6 py-6">
        <span className="font-display text-xl">OffPeak</span>
        <nav className="flex items-center gap-3 text-sm">
          <Link href="/restaurant/application" className="text-ink/70 hover:text-ink">
            List your restaurant
          </Link>
          <Link href="/login" className="text-ink/70 hover:text-ink">
            Log in
          </Link>
          <LinkButton href="/signup" variant="primary">Get the app</LinkButton>
        </nav>
      </header>

      <section className="max-w-6xl w-full mx-auto px-6 pt-10 pb-20 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h1 className="font-display text-5xl md:text-6xl leading-[1.05] mb-6">
            Good food.
            <br />
            <span className="italic text-saffron-deep">Better timing.</span>
          </h1>
          <p className="text-ink/70 text-lg max-w-md mb-8">
            Restaurants have quiet tables between the rushes. OffPeak turns that unused
            capacity into real discounts you can claim in a couple of taps — and points
            toward your next meal.
          </p>
          <div className="flex flex-wrap gap-3">
            <LinkButton href="/signup" variant="primary">Find tonight&apos;s offers</LinkButton>
            <LinkButton href="/restaurant/application" variant="ghost">I run a restaurant</LinkButton>
          </div>
        </div>
        <div className="relative">
          <div className="rounded-3xl bg-teal text-paper p-8 rotate-1 shadow-xl">
            <p className="text-sm uppercase tracking-wide text-paper/60 mb-1">Luna Bistro</p>
            <p className="font-display text-2xl mb-4">Afternoon Pasta Special</p>
            <div className="flex items-baseline gap-2 mb-6">
              <span className="font-display text-5xl text-saffron">25%</span>
              <span className="text-paper/70">off, 2:00–4:30 PM today</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-paper/70">1.2 km away · 4.7 ★</span>
              <span className="bg-saffron text-ink px-4 py-2 rounded-full font-medium">
                Save $12
              </span>
            </div>
          </div>
          <div className="absolute -bottom-6 -left-6 rounded-2xl bg-paper-raised border border-line p-5 -rotate-2 shadow-lg w-56">
            <p className="text-xs text-ink/50 mb-1">Loyalty wallet</p>
            <p className="font-display text-3xl">436 pts</p>
            <p className="text-xs text-ink/50">64 pts to your next $10 credit</p>
          </div>
        </div>
      </section>

      <section className="bg-teal text-paper py-16">
        <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-3 gap-8">
          <div>
            <p className="font-display text-2xl mb-2">Discover</p>
            <p className="text-paper/70 text-sm">
              Browse real off-peak discounts near you, sorted by how much you save and
              how soon they end.
            </p>
          </div>
          <div>
            <p className="font-display text-2xl mb-2">Claim & redeem</p>
            <p className="text-paper/70 text-sm">
              Claim an offer, show your code at the restaurant, and pay through the app —
              no surprises at the table.
            </p>
          </div>
          <div>
            <p className="font-display text-2xl mb-2">Earn points</p>
            <p className="text-paper/70 text-sm">
              Every dollar you spend earns a loyalty point. 500 points becomes a $10
              credit toward your next visit.
            </p>
          </div>
        </div>
      </section>

      <footer className="max-w-6xl w-full mx-auto px-6 py-10 flex items-center justify-between text-sm text-ink/50">
        <span>OffPeak — a prototype exploring off-peak revenue for independent restaurants.</span>
        <Link href="/admin/dashboard" className="hover:text-ink">Admin</Link>
      </footer>
    </main>
  );
}
