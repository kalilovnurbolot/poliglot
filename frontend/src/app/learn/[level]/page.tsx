"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { FlashCard, type FlashCardHandle } from "@/components/FlashCard";
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

export default function LearnSessionPage() {
  const { user, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const router = useRouter();
  const params = useParams<{ level: string }>();
  const level = params.level === "all" ? null : params.level;

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
    <main className="relative flex min-h-dvh w-full flex-1 flex-col items-center justify-center gap-6 px-4 py-10">
      <button
        onClick={() => router.push("/learn")}
        aria-label="Закрыть"
        className="absolute top-4 left-4 flex h-9 w-9 items-center justify-center rounded-full bg-zinc-900/5 text-lg text-zinc-500 hover:bg-zinc-900/10 hover:text-zinc-900 dark:bg-white/5 dark:text-zinc-400 dark:hover:bg-white/10 dark:hover:text-zinc-50"
      >
        ✕
      </button>

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
          <div className="flex gap-3">
            <button onClick={loadQueue} className={buttonClass("primary")}>
              Проверить ещё раз
            </button>
            <button onClick={() => router.push("/learn")} className={buttonClass("secondary")}>
              К выбору уровня
            </button>
          </div>
        </div>
      )}

      {queue !== null && queue.length > 0 && (
        <FlashCard key={queue[0].word.id} ref={cardRef} card={queue[0]} onSwipe={handleSwipe} />
      )}
    </main>
  );
}
