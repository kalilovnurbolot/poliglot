"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  fetchGrammarRule,
  fetchGrammarRules,
  toggleGrammarRuleLearned,
  type GrammarRule,
} from "@/lib/grammar";
import { useLanguage } from "@/lib/language-context";
import { buttonClass, cardClass } from "@/lib/ui";

export default function GrammarRulePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { language } = useLanguage();

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

  const index = siblings.findIndex((s) => s.id === rule?.id);
  const prev = index > 0 ? siblings[index - 1] : null;
  const next = index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null;

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/grammar" className="text-sm text-zinc-500 underline underline-offset-2 hover:text-indigo-600">
        ← Все правила
      </Link>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {!rule && !error && <p className="text-zinc-500">Загрузка...</p>}

      {rule && (
        <article className={`${cardClass} p-6 sm:p-8`}>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="rounded-full border border-zinc-300 px-2 py-0.5 text-xs text-zinc-500 dark:border-zinc-700">
                {rule.level}
              </span>
              <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{rule.title}</h1>
            </div>
            <button
              onClick={handleToggleLearned}
              disabled={saving}
              className={buttonClass(rule.is_learned ? "secondary" : "primary")}
            >
              {rule.is_learned ? "✓ Изучено" : "Отметить как изученное"}
            </button>
          </div>

          <div className="prose prose-zinc dark:prose-invert max-w-none prose-table:text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{rule.body}</ReactMarkdown>
          </div>

          {(prev || next) && (
            <div className="mt-8 flex items-center justify-between border-t border-zinc-200 pt-4 dark:border-zinc-800">
              {prev ? (
                <button
                  onClick={() => router.push(`/grammar/${prev.id}`)}
                  className="text-left text-sm text-zinc-500 hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                  ← {prev.title}
                </button>
              ) : (
                <span />
              )}
              {next && (
                <button
                  onClick={() => router.push(`/grammar/${next.id}`)}
                  className="text-right text-sm text-zinc-500 hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                  {next.title} →
                </button>
              )}
            </div>
          )}
        </article>
      )}
    </main>
  );
}
