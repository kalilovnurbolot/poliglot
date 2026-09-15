import { apiFetch } from "./api";
import type { Word } from "./review";

export type QuizQuestion = {
  word: Word;
  options: string[];
};

export async function fetchQuizQuestions(
  language = "en",
  level?: string | null,
  limit = 10,
): Promise<QuizQuestion[]> {
  const params = new URLSearchParams({ language, limit: String(limit) });
  if (level) params.set("level", level);
  const res = await apiFetch(`/quiz/questions/?${params.toString()}`);
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.detail ?? "Не удалось загрузить квиз");
  }
  return res.json();
}

const SPEECH_LOCALES: Record<string, string> = {
  en: "en-US",
  de: "de-DE",
};

export function speak(text: string, language = "en") {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = SPEECH_LOCALES[language] ?? "en-US";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}
