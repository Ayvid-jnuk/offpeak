"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DinerRoot() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/diner/discover");
  }, [router]);
  return null;
}
