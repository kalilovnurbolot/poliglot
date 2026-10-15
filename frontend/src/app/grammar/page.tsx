"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { extractLede } from "@/components/RuleBody";
import { useAuth } from "@/lib/auth-context";
import { fetchGrammarRules, type GrammarRule } from "@/lib/grammar";
import { useLanguage } from "@/lib/language-context";
import { buttonClass, cardClass } from "@/lib/ui";

export default function GrammarListPage() {
  const { language } = useLanguage();
  const { user } = useAuth();
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
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-4 py-10">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="min-w-0">
          <p className="mb-1.5 font-mono text-xs font-semibold tracking-wide text-indigo-600 dark:text-indigo-400">
            {language.toUpperCase()} · справочник
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">Грамматика</h1>
          <p className="mt-1.5 max-w-[52ch] text-[15px] leading-relaxed text-zinc-500 dark:text-zinc-400">
            Формулы предложений с разбором по членам, примеры и частые ошибки.
          </p>
        </div>
        {user?.is_staff && (
          <Link href="/grammar/new" className={buttonClass("primary")}>
            + Добавить правило
          </Link>
        )}
      </header>

      <div className="flex flex-col gap-4 border-y border-zinc-200 py-4 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
        <LevelSwitcher value={level} onChange={(l) => setLevel(l ?? "A1")} allowAll={false} />
        {rules !== null && rules.length > 0 && (
          <div className="flex items-center gap-3 sm:w-56">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all"
                style={{ width: `${(learnedCount / rules.length) * 100}%` }}
              />
            </div>
            <span className="shrink-0 font-mono text-xs text-zinc-500">
              {learnedCount}/{rules.length} изучено
            </span>
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {rules === null && !error && (
        <div className="flex flex-col gap-2">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-[76px] animate-pulse rounded-xl bg-zinc-200/60 dark:bg-zinc-900" />
          ))}
        </div>
      )}
      {rules !== null && rules.length === 0 && (
        <p className="rounded-xl border border-dashed border-zinc-300 px-4 py-10 text-center text-zinc-500 dark:border-zinc-700">
          Для уровня {level} пока нет правил.
        </p>
      )}

      <ol className="flex flex-col gap-2">
        {rules?.map((rule, i) => {
          const lede = extractLede(rule.body);
          return (
            <li key={rule.id}>
              <Link
                href={`/grammar/${rule.id}`}
                className={`${cardClass} group grid grid-cols-[2.25rem_minmax(0,1fr)_auto] items-start gap-3 px-4 py-3.5 transition-colors hover:border-indigo-400 dark:hover:border-indigo-500`}
              >
                <span
                  className={`pt-0.5 font-mono text-sm font-semibold ${
                    rule.is_learned ? "text-emerald-600 dark:text-emerald-400" : "text-indigo-600 dark:text-indigo-400"
                  }`}
                >
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="min-w-0">
                  <span className="block font-semibold text-zinc-900 dark:text-zinc-50">{rule.title}</span>
                  {lede && (
                    <span className="mt-0.5 line-clamp-2 block text-sm leading-snug text-zinc-500 dark:text-zinc-400">
                      {lede}
                    </span>
                  )}
                </span>
                {rule.is_learned ? (
                  <span
                    className="mt-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
                    title="Изучено"
                  >
                    ✓
                  </span>
                ) : (
                  <span className="mt-0.5 text-zinc-400 transition-transform group-hover:translate-x-0.5 group-hover:text-indigo-500">
                    →
                  </span>
                )}
              </Link>
            </li>
          );
        })}
      </ol>
    </main>
  );
}
