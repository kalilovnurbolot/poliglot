"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { useAuth } from "@/lib/auth-context";

export default function LearnPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  if (authLoading || !user) return null;

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-6 px-4 py-10 text-center">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Учить слова</h1>
        <p className="mt-1 text-zinc-500">Выберите уровень, чтобы начать</p>
      </div>

      <LevelSwitcher value={null} onChange={(level) => router.push(`/learn/${level ?? "all"}`)} />
    </main>
  );
}
