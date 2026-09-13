"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { getRole, getToken, setRole as persistRole, setToken as persistToken } from "@/lib/api";
import type { Role } from "@/lib/types";

interface AuthState {
  token: string | null;
  role: Role | null;
  userId: string | null;
  isLoading: boolean;
  login: (token: string, role: Role, userId: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

function getToken_(): string | null {
  return getToken();
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [role, setRoleState] = useState<Role | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTokenState(getToken_());
    setRoleState((getRole() as Role) || null);
    setUserId(typeof window !== "undefined" ? localStorage.getItem("offpeak_user_id") : null);
    setIsLoading(false);
  }, []);

  function login(newToken: string, newRole: Role, newUserId: string) {
    persistToken(newToken);
    persistRole(newRole);
    if (typeof window !== "undefined") localStorage.setItem("offpeak_user_id", newUserId);
    setTokenState(newToken);
    setRoleState(newRole);
    setUserId(newUserId);
  }

  function logout() {
    persistToken(null);
    persistRole(null);
    if (typeof window !== "undefined") localStorage.removeItem("offpeak_user_id");
    setTokenState(null);
    setRoleState(null);
    setUserId(null);
  }

  return (
    <AuthContext.Provider value={{ token, role, userId, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
