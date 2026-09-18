"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { FlashCard, type FlashCardHandle } from "@/components/FlashCard";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import {
  fetchReviewQueue,
  sendSwipeAnswer,
  type ReviewCard,
  type SwipeDirection,
} from "@/lib/review";
import { buttonClass, cardClass } from "@/lib/ui";

const KEY_TO_DIRECTION: Record<string, SwipeDirection> = {
  ArrowRight: "right",
  ArrowLeft: "left",
  ArrowUp: "up",
  ArrowDown: "down",
};

export default function LearnPage() {
  const { user, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const router = useRouter();

  const [level, setLevel] = useState<string | null>(null);
  const [queue, setQueue] = useState<ReviewCard[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ known: 0, unknown: 0, favorited: 0 });
  const cardRef = useRef<FlashCardHandle>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  const loadQueue = useCallback(async () => {
    setError(null);
    setQueue(null);
    setStats({ known: 0, unknown: 0, favorited: 0 });
    try {
      setQueue(await fetchReviewQueue(language, level));
    } catch {
      setError("Не удалось загрузить слова. Попробуйте ещё раз.");
    }
  }, [language, level]);

  useEffect(() => {
    if (user) loadQueue();
  }, [user, loadQueue]);

  const handleSwipe = (direction: SwipeDirection) => {
    if (!queue || queue.length === 0) return;
    const [current, ...rest] = queue;

    if (direction === "down") {
      setQueue([...rest, current]);
      return;
    }

    sendSwipeAnswer(current.word.id, direction).catch(() => {
      setError("Ответ не сохранился — проверьте соединение.");
    });

    setStats((s) => ({
      known: s.known + (direction === "right" ? 1 : 0),
      unknown: s.unknown + (direction === "left" ? 1 : 0),
      favorited: s.favorited + (direction === "up" ? 1 : 0),
    }));
    setQueue(rest);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const direction = KEY_TO_DIRECTION[e.key];
      if (direction) {
        e.preventDefault();
        cardRef.current?.swipe(direction);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (authLoading || !user) return null;

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center gap-6 px-4 py-10">
      <LevelSwitcher value={level} onChange={setLevel} />

      <div className="flex gap-3 text-sm font-medium">
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400">
          ✅ {stats.known}
        </span>
        <span className="rounded-full bg-red-50 px-3 py-1 text-red-700 dark:bg-red-500/10 dark:text-red-400">
          ❌ {stats.unknown}
        </span>
        <span className="rounded-full bg-amber-50 px-3 py-1 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
          ⭐ {stats.favorited}
        </span>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {queue === null && !error && <p className="text-zinc-500">Загрузка слов...</p>}

      {queue !== null && queue.length === 0 && (
        <div className={`${cardClass} flex flex-col items-center gap-4 p-8 text-center`}>
          <p className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
            На сегодня всё! 🎉
          </p>
          <p className="text-zinc-500">
            Знаю: {stats.known} · Не знаю: {stats.unknown} · Избранное: {stats.favorited}
          </p>
          <button onClick={loadQueue} className={buttonClass("primary")}>
            Проверить ещё раз
          </button>
        </div>
      )}

      {queue !== null && queue.length > 0 && (
        <FlashCard key={queue[0].word.id} ref={cardRef} card={queue[0]} onSwipe={handleSwipe} />
      )}

      <p className="hidden max-w-xs text-center text-xs text-zinc-400 sm:block">
        Свайп вправо — знаю, влево — не знаю, вверх — в избранное, вниз — пропустить.
        Можно и стрелками на клавиатуре.
      </p>
    </main>
  );
}
