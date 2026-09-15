"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { fetchLanguages, type Language } from "./words";

const STORAGE_KEY = "poliglot_language";
const DEFAULT_LANGUAGE = "en";

type LanguageContextValue = {
  language: string;
  languages: Language[];
  loading: boolean;
  setLanguage: (code: string) => void;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState(DEFAULT_LANGUAGE);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) setLanguageState(stored);

    fetchLanguages()
      .then(setLanguages)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const setLanguage = (code: string) => {
    setLanguageState(code);
    localStorage.setItem(STORAGE_KEY, code);
  };

  return (
    <LanguageContext.Provider value={{ language, languages, loading, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
