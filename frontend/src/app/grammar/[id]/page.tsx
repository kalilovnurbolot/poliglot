"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { extractSections, RuleBody } from "@/components/RuleBody";
import { useAuth } from "@/lib/auth-context";
import {
  deleteGrammarRule,
  fetchGrammarRule,
  fetchGrammarRules,
  toggleGrammarRuleLearned,
  type GrammarRule,
} from "@/lib/grammar";
import { useLanguage } from "@/lib/language-context";
import { buttonClass } from "@/lib/ui";

const navCardClass =
  "group flex flex-col gap-1 rounded-xl border border-zinc-200 bg-white px-4 py-3 transition-colors hover:border-indigo-400 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-500";

export default function GrammarRulePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { language } = useLanguage();
  const { user } = useAuth();

  const [rule, setRule] = useState<GrammarRule | null>(null);
  const [siblings, setSiblings] = useState<GrammarRule[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchGrammarRule(params.id)
      .then(setRule)
      .catch(() => setError("Не удалось загрузить правило"));
  }, [params.id]);

  useEffect(() => {
    if (!rule) return;
    fetchGrammarRules(language, rule.level)
      .then(setSiblings)
      .catch(() => {});
  }, [rule, language]);

  const handleToggleLearned = async () => {
    if (!rule) return;
    setSaving(true);
    try {
      const { is_learned } = await toggleGrammarRuleLearned(rule.id);
      setRule((r) => (r ? { ...r, is_learned } : r));
    } catch {
      setError("Не удалось сохранить прогресс");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!rule || !confirm(`Удалить правило «${rule.title}»?`)) return;
    try {
      await deleteGrammarRule(rule.id);
      router.push("/grammar");
    } catch {
      setError("Не удалось удалить правило");
    }
  };

  const sections = useMemo(() => (rule ? extractSections(rule.body) : []), [rule]);
  const [activeSection, setActiveSection] = useState<string | null>(null);

  useEffect(() => {
    if (sections.length < 2) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.find((e) => e.isIntersecting);
        if (visible) setActiveSection(visible.target.id);
      },
      { rootMargin: "-10% 0px -70% 0px" },
    );
    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [sections]);

  const isAdmin = !!user?.is_staff;
  const index = siblings.findIndex((s) => s.id === rule?.id);
  const prev = index > 0 ? siblings[index - 1] : null;
  const next = index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null;

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/grammar" className="self-start text-sm text-zinc-500 transition-colors hover:text-indigo-600 dark:hover:text-indigo-400">
        ← Все правила
      </Link>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {!rule && !error && <p className="text-zinc-500">Загрузка...</p>}

      {rule && (
        <>
          <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4 border-b border-zinc-200 pb-5 dark:border-zinc-800">
            <div className="min-w-0">
              <p className="mb-2 flex flex-wrap items-center gap-2 font-mono text-xs font-semibold tracking-wide">
                <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                  {language.toUpperCase()} → {rule.level}
                </span>
                {index >= 0 && (
                  <span className="text-zinc-500">
                    правило {index + 1} из {siblings.length}
                  </span>
                )}
                {rule.is_learned && <span className="text-emerald-600 dark:text-emerald-400">✓ изучено</span>}
              </p>
              <h1 className="text-2xl font-bold tracking-tight text-balance text-zinc-900 dark:text-zinc-50 sm:text-3xl">
                {rule.title}
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {isAdmin && (
                <>
                  <Link href={`/grammar/${rule.id}/edit`} className={buttonClass("secondary")}>
                    Изменить
                  </Link>
                  <button onClick={handleDelete} className={buttonClass("danger")}>
                    Удалить
                  </button>
                </>
              )}
              <button
                onClick={handleToggleLearned}
                disabled={saving}
                className={buttonClass(rule.is_learned ? "secondary" : "primary")}
              >
                {rule.is_learned ? "✓ Изучено" : "Отметить как изученное"}
              </button>
            </div>
          </header>

          <div
            className={
              sections.length >= 2 ? "grid grid-cols-1 gap-6 lg:grid-cols-[200px_minmax(0,1fr)] lg:gap-12" : ""
            }
          >
            {sections.length >= 2 && (
              <nav
                aria-label="Разделы"
                className="flex flex-wrap gap-1.5 text-[13.5px] lg:sticky lg:top-24 lg:flex-col lg:flex-nowrap lg:gap-0.5 lg:self-start"
              >
                <div className="hidden px-2.5 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-zinc-500 lg:block">
                  Разделы
                </div>
                {sections.map((s) => {
                  const active = (activeSection ?? sections[0].id) === s.id;
                  return (
                    <a
                      key={s.id}
                      href={`#${s.id}`}
                      onClick={(e) => {
                        e.preventDefault();
                        document.getElementById(s.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
                      }}
                      className={`rounded-lg border px-2.5 py-1.5 transition-colors lg:rounded-md lg:border-0 lg:border-l-2 ${
                        active
                          ? "border-indigo-500 bg-indigo-50 font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                          : "border-zinc-200 bg-white text-zinc-500 hover:text-zinc-900 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:text-zinc-100 lg:border-transparent lg:bg-transparent lg:dark:bg-transparent"
                      }`}
                    >
                      {s.title}
                    </a>
                  );
                })}
              </nav>
            )}

            <article className="min-w-0 max-w-3xl">
              <RuleBody body={rule.body} />

              {(prev || next) && (
                <div className="mt-12 grid grid-cols-1 gap-3 border-t border-zinc-200 pt-6 dark:border-zinc-800 sm:grid-cols-2">
                  {prev ? (
                    <button onClick={() => router.push(`/grammar/${prev.id}`)} className={`${navCardClass} text-left`}>
                      <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                        ← Предыдущее
                      </span>
                      <span className="font-semibold text-zinc-900 group-hover:text-indigo-600 dark:text-zinc-50 dark:group-hover:text-indigo-400">
                        {prev.title}
                      </span>
                    </button>
                  ) : (
                    <span className="hidden sm:block" />
                  )}
                  {next && (
                    <button
                      onClick={() => router.push(`/grammar/${next.id}`)}
                      className={`${navCardClass} text-left sm:items-end sm:text-right`}
                    >
                      <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                        Следующее →
                      </span>
                      <span className="font-semibold text-zinc-900 group-hover:text-indigo-600 dark:text-zinc-50 dark:group-hover:text-indigo-400">
                        {next.title}
                      </span>
                    </button>
                  )}
                </div>
              )}
            </article>
          </div>
        </>
      )}
    </main>
  );
}
