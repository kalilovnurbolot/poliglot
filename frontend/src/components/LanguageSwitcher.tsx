"use client";

import { useLanguage } from "@/lib/language-context";
import { inputClass } from "@/lib/ui";

export function LanguageSwitcher() {
  const { language, languages, setLanguage } = useLanguage();

  if (languages.length < 2) return null;

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
      className={inputClass + " cursor-pointer py-1.5"}
      aria-label="Изучаемый язык"
    >
      {languages.map((l) => (
        <option key={l.code} value={l.code}>
          {l.name}
        </option>
      ))}
    </select>
  );
}
