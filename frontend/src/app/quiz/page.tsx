"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { sendSwipeAnswer } from "@/lib/review";
import { fetchQuizQuestions, speak, type QuizQuestion } from "@/lib/quiz";
import { buttonClass, cardClass, pillClass } from "@/lib/ui";

type Mode = "translation" | "listening";
type Feedback = { selected: string; correct: boolean } | null;

export default function QuizPage() {
  const { user, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const router = useRouter();

  const [mode, setMode] = useState<Mode>("translation");
  const [level, setLevel] = useState<string | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[] | null>(null);
  const [index, setIndex] = useState(0);
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [score, setScore] = useState({ correct: 0, wrong: 0 });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  const loadQuiz = useCallback(async () => {
    setError(null);
    setQuestions(null);
    setIndex(0);
    setFeedback(null);
    setScore({ correct: 0, wrong: 0 });
    try {
      setQuestions(await fetchQuizQuestions(language, level));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить квиз");
    }
  }, [language, level]);

  useEffect(() => {
    if (user) loadQuiz();
  }, [user, loadQuiz]);

  const current = questions?.[index];

  useEffect(() => {
    if (mode === "listening" && current && !feedback) {
      speak(current.word.text, language);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, current, feedback]);

  const handleSelect = (option: string) => {
    if (!current || feedback) return;
    const correct = option === current.word.translation;
    setFeedback({ selected: option, correct });
    setScore((s) => ({
      correct: s.correct + (correct ? 1 : 0),
      wrong: s.wrong + (correct ? 0 : 1),
    }));
    sendSwipeAnswer(current.word.id, correct ? "right" : "left").catch(() => {});

    setTimeout(() => {
      setFeedback(null);
      setIndex((i) => i + 1);
    }, 900);
  };

  if (authLoading || !user) return null;

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col items-center gap-6 px-4 py-10">
      <h1 className="hidden text-2xl font-semibold text-zinc-900 dark:text-zinc-50 sm:block">Квиз</h1>

      <LevelSwitcher value={level} onChange={setLevel} />

      <div className="flex gap-2">
        {(["translation", "listening"] as Mode[]).map((m) => (
          <button key={m} onClick={() => setMode(m)} className={pillClass(mode === m)}>
            {m === "translation" ? "Обычный" : "На слух"}
          </button>
        ))}
      </div>

      {questions && current && (
        <div className="flex w-full items-center justify-between text-sm text-zinc-500">
          <span>
            Вопрос {index + 1} из {questions.length}
          </span>
          <div className="flex gap-3 font-medium">
            <span className="text-emerald-600 dark:text-emerald-400">✅ {score.correct}</span>
            <span className="text-red-600 dark:text-red-400">❌ {score.wrong}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center gap-3 text-center">
          <p className="text-sm text-red-600">{error}</p>
          <Link href="/learn" className="text-sm text-indigo-600 underline dark:text-indigo-400">
            Сначала выучить слова
          </Link>
        </div>
      )}

      {!error && questions === null && <p className="text-zinc-500">Загрузка...</p>}

      {!error && questions !== null && !current && (
        <div className={`${cardClass} flex flex-col items-center gap-4 p-8 text-center`}>
          <p className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">Квиз завершён! 🎉</p>
          <p className="text-zinc-500">
            Правильно: {score.correct} · Неправильно: {score.wrong}
          </p>
          <button onClick={loadQuiz} className={buttonClass("primary")}>
            Пройти ещё раз
          </button>
        </div>
      )}

      {current && (
        <div className={`${cardClass} flex w-full flex-col items-center gap-6 p-6`}>
          {mode === "translation" ? (
            <div className="text-center">
              <p className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
                {current.word.text}
              </p>
              {current.word.transcription && (
                <p className="text-zinc-500">{current.word.transcription}</p>
              )}
            </div>
          ) : (
            <button
              onClick={() => speak(current.word.text, language)}
              className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-600 text-2xl text-white transition-colors hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-400"
              aria-label="Прослушать слово"
            >
              🔊
            </button>
          )}

          <div className="grid w-full grid-cols-1 gap-2">
            {current.options.map((option) => {
              const isSelected = feedback?.selected === option;
              const showCorrect = feedback && option === current.word.translation;
              return (
                <button
                  key={option}
                  onClick={() => handleSelect(option)}
                  disabled={!!feedback}
                  className={`rounded-lg border px-4 py-2 text-left transition-colors ${
                    showCorrect
                      ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10"
                      : isSelected
                        ? "border-red-500 bg-red-50 dark:bg-red-500/10"
                        : "border-zinc-300 hover:border-indigo-400 dark:border-zinc-700 dark:hover:border-indigo-500"
                  }`}
                >
                  {option}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </main>
  );
}
