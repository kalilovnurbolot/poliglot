"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { fetchGrammarRules, type GrammarRule } from "@/lib/grammar";
import { useLanguage } from "@/lib/language-context";
import { cardClass } from "@/lib/ui";

export default function GrammarListPage() {
  const { language } = useLanguage();
  const [level, setLevel] = useState<string>("A1");
  const [rules, setRules] = useState<GrammarRule[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setRules(null);
    setError(null);
    fetchGrammarRules(language, level)
      .then(setRules)
      .catch(() => setError("Не удалось загрузить правила"));
  }, [language, level]);

  const learnedCount = rules?.filter((r) => r.is_learned).length ?? 0;

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Грамматика</h1>

      <LevelSwitcher value={level} onChange={(l) => setLevel(l ?? "A1")} allowAll={false} />

      {error && <p className="text-sm text-red-600">{error}</p>}
      {rules === null && !error && <p className="text-zinc-500">Загрузка...</p>}
      {rules !== null && rules.length === 0 && (
        <p className="text-zinc-500">Для уровня {level} пока нет правил.</p>
      )}

      {rules !== null && rules.length > 0 && (
        <div className="flex items-center gap-3">
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
            <div
              className="h-full rounded-full bg-indigo-600 transition-all dark:bg-indigo-500"
              style={{ width: `${(learnedCount / rules.length) * 100}%` }}
            />
          </div>
          <span className="shrink-0 text-sm text-zinc-500">
            {learnedCount} из {rules.length} изучено
          </span>
        </div>
      )}

      <ul className="flex flex-col gap-2">
        {rules?.map((rule) => (
          <li key={rule.id}>
            <Link
              href={`/grammar/${rule.id}`}
              className={`${cardClass} flex items-center justify-between px-4 py-3 transition-colors hover:border-indigo-400 dark:hover:border-indigo-500`}
            >
              <span className="text-zinc-900 dark:text-zinc-50">{rule.title}</span>
              {rule.is_learned && (
                <span className="text-sm text-emerald-600 dark:text-emerald-400">✓ изучено</span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
