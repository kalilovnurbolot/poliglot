import { apiFetch } from "./api";

export type SwipeDirection = "right" | "left" | "up" | "down";

export type Word = {
  id: number;
  text: string;
  translation: string;
  transcription: string;
  example_sentence: string;
  part_of_speech: string;
  level: string;
};

export type Progress = {
  box_level: number;
  next_review_at: string;
  correct_count: number;
  wrong_count: number;
  last_result: "correct" | "wrong" | null;
  is_favorite: boolean;
};

export type ReviewCard = {
  word: Word;
  progress: Progress | null;
};

export async function fetchReviewQueue(
  language = "en",
  level?: string | null,
  limit = 20,
): Promise<ReviewCard[]> {
  const params = new URLSearchParams({ language, limit: String(limit) });
  if (level) params.set("level", level);
  const res = await apiFetch(`/review/queue/?${params.toString()}`);
  if (!res.ok) throw new Error("Не удалось загрузить слова для повторения");
  return res.json();
}

export async function sendSwipeAnswer(wordId: number, direction: SwipeDirection): Promise<Progress> {
  const res = await apiFetch("/review/answer/", {
    method: "POST",
    body: JSON.stringify({ word: wordId, direction }),
  });
  if (!res.ok) throw new Error("Не удалось сохранить ответ");
  return res.json();
}
