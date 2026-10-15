"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RuleEditor } from "@/components/RuleEditor";
import { useAuth } from "@/lib/auth-context";
import { fetchGrammarRule, updateGrammarRule, type GrammarRule } from "@/lib/grammar";

export default function EditGrammarRulePage() {
  const params = useParams<{ id: string }>();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [rule, setRule] = useState<GrammarRule | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user?.is_staff) return;
    fetchGrammarRule(params.id)
      .then(setRule)
      .catch(() => setError("Не удалось загрузить правило"));
  }, [user, params.id]);

  if (authLoading || !user) return null;

  const canEdit = user.is_staff;

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-10">
      <Link
        href={`/grammar/${params.id}`}
        className="text-sm text-zinc-500 underline underline-offset-2 hover:text-indigo-600"
      >
        ← К правилу
      </Link>
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Редактирование правила</h1>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {canEdit && !rule && !error && <p className="text-zinc-500">Загрузка...</p>}
      {!canEdit && <p className="text-zinc-500">Редактировать правила может только администратор.</p>}

      {rule && canEdit && (
        <RuleEditor
          initial={{ title: rule.title, level: rule.level, body: rule.body }}
          submitLabel="Сохранить"
          onSubmit={async (data) => {
            await updateGrammarRule(rule.id, data);
            router.push(`/grammar/${rule.id}`);
          }}
        />
      )}
    </main>
  );
}
