"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { apiFetch, clearTokens, getTokens, setTokens } from "./api";

type User = {
  id: number;
  email: string;
  first_name: string;
};

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName: string) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function parseErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    const firstValue = Object.values(data)[0];
    return Array.isArray(firstValue) ? String(firstValue[0]) : String(firstValue ?? "Ошибка");
  } catch {
    return "Ошибка";
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = async () => {
    if (!getTokens()) {
      setUser(null);
      setLoading(false);
      return;
    }
    const res = await apiFetch("/auth/me/");
    if (res.ok) {
      setUser(await res.json());
    } else {
      clearTokens();
      setUser(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadUser();
  }, []);

  const handleAuthResponse = async (res: Response) => {
    if (!res.ok) {
      throw new Error(await parseErrorMessage(res));
    }
    const data = await res.json();
    setTokens(data.access, data.refresh);
    setUser(data.user);
  };

  const login = async (email: string, password: string) => {
    const res = await apiFetch("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Неверный email или пароль");
    const data = await res.json();
    setTokens(data.access, data.refresh);
    const me = await apiFetch("/auth/me/");
    setUser(await me.json());
  };

  const register = async (email: string, password: string, firstName: string) => {
    const res = await apiFetch("/auth/register/", {
      method: "POST",
      body: JSON.stringify({ email, password, first_name: firstName }),
    });
    await handleAuthResponse(res);
  };

  const loginWithGoogle = async (idToken: string) => {
    const res = await apiFetch("/auth/google/", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });
    await handleAuthResponse(res);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
