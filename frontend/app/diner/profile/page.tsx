"use client";

import { useAuth } from "@/lib/auth";
import { Button, Card } from "@/components/ui";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const { userId, logout } = useAuth();
  const router = useRouter();

  return (
    <div>
      <h1 className="font-display text-3xl mb-6">Profile</h1>
      <Card className="mb-6 flex flex-col gap-2 text-sm">
        <div className="flex justify-between"><span className="text-ink/60">Account</span><span>Diner</span></div>
        <div className="flex justify-between"><span className="text-ink/60">User ID</span><span className="font-mono text-xs">{userId}</span></div>
      </Card>
      <Button
        variant="ghost"
        onClick={() => {
          logout();
          router.push("/");
        }}
        className="w-full"
      >
        Log out
      </Button>
    </div>
  );
}
