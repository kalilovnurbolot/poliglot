"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { NEW_RULE_TEMPLATE, RuleEditor } from "@/components/RuleEditor";
import { useAuth } from "@/lib/auth-context";
import { createGrammarRule } from "@/lib/grammar";
import { useLanguage } from "@/lib/language-context";

export default function NewGrammarRulePage() {
  const { user, loading: authLoading } = useAuth();
  const { language, languages } = useLanguage();
  const router = useRouter();

  const languageId = languages.find((l) => l.code === language)?.id ?? null;

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  if (authLoading || !user) return null;
  if (!user.is_staff) {
    return (
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-10 text-zinc-500">
        Добавлять правила может только администратор.
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/grammar" className="text-sm text-zinc-500 underline underline-offset-2 hover:text-indigo-600">
        ← Все правила
      </Link>
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Новое правило</h1>
      <RuleEditor
        initial={{ title: "", level: "A1", body: NEW_RULE_TEMPLATE }}
        submitLabel="Добавить правило"
        onSubmit={async (data) => {
          if (!languageId) throw new Error("Язык ещё не загружен");
          const rule = await createGrammarRule({ ...data, language: languageId });
          router.push(`/grammar/${rule.id}`);
        }}
      />
    </main>
  );
}
