"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";

export function useRequireRole(role: Role) {
  const { role: currentRole, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (currentRole !== role) {
      router.replace("/login");
    }
  }, [isLoading, currentRole, role, router]);

  return { ready: !isLoading && currentRole === role };
}
