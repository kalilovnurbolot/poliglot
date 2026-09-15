import { apiFetch } from "./api";
import type { Word } from "./review";

export type Language = {
  id: number;
  code: string;
  name: string;
};

export type PartOfSpeech = "noun" | "verb" | "adjective" | "adverb" | "phrase" | "other";

export const PART_OF_SPEECH_LABELS: Record<PartOfSpeech, string> = {
  noun: "существительное",
  verb: "глагол",
  adjective: "прилагательное",
  adverb: "наречие",
  phrase: "фраза",
  other: "другое",
};

export type NewWord = {
  language: number;
  text: string;
  translation: string;
  transcription?: string;
  example_sentence?: string;
  part_of_speech: PartOfSpeech;
  level: string;
};

export async function fetchLanguages(): Promise<Language[]> {
  const res = await apiFetch("/languages/");
  if (!res.ok) throw new Error("Не удалось загрузить список языков");
  return res.json();
}

export async function fetchMyWords(language = "en", level?: string | null): Promise<Word[]> {
  const params = new URLSearchParams({ language, mine: "true" });
  if (level) params.set("level", level);
  const res = await apiFetch(`/words/?${params.toString()}`);
  if (!res.ok) throw new Error("Не удалось загрузить ваши слова");
  return res.json();
}

export async function createWord(data: NewWord): Promise<Word> {
  const res = await apiFetch("/words/", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const firstValue = body ? Object.values(body)[0] : null;
    const message = Array.isArray(firstValue) ? String(firstValue[0]) : "Не удалось добавить слово";
    throw new Error(message);
  }
  return res.json();
}

export async function deleteWord(id: number): Promise<void> {
  const res = await apiFetch(`/words/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error("Не удалось удалить слово");
}
