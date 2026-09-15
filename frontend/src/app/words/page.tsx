"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { LevelSwitcher } from "@/components/LevelSwitcher";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { LEVELS } from "@/lib/levels";
import type { Word } from "@/lib/review";
import { buttonClass, cardClass, inputClass } from "@/lib/ui";
import {
  createWord,
  deleteWord,
  fetchMyWords,
  PART_OF_SPEECH_LABELS,
  type PartOfSpeech,
} from "@/lib/words";

const PARTS_OF_SPEECH = Object.keys(PART_OF_SPEECH_LABELS) as PartOfSpeech[];

const emptyForm = {
  text: "",
  translation: "",
  transcription: "",
  example_sentence: "",
  part_of_speech: "other" as PartOfSpeech,
  level: "A1",
};

export default function MyWordsPage() {
  const { user, loading: authLoading } = useAuth();
  const { language, languages } = useLanguage();
  const router = useRouter();

  const [filterLevel, setFilterLevel] = useState<string | null>(null);
  const [words, setWords] = useState<Word[] | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const languageId = languages.find((l) => l.code === language)?.id ?? null;

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    setWords(null);
    fetchMyWords(language, filterLevel)
      .then(setWords)
      .catch(() => setError("Не удалось загрузить слова"));
  }, [user, language, filterLevel]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!languageId) return;
    setError(null);
    setSubmitting(true);
    try {
      const word = await createWord({
        language: languageId,
        text: form.text.trim(),
        translation: form.translation.trim(),
        transcription: form.transcription.trim(),
        example_sentence: form.example_sentence.trim(),
        part_of_speech: form.part_of_speech,
        level: form.level,
      });
      setWords((prev) => [word, ...(prev ?? [])]);
      setForm(emptyForm);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка добавления слова");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    setWords((prev) => prev?.filter((w) => w.id !== id) ?? null);
    try {
      await deleteWord(id);
    } catch {
      setError("Не удалось удалить слово");
      fetchMyWords(language, filterLevel).then(setWords).catch(() => {});
    }
  };

  if (authLoading || !user) return null;

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col gap-6 px-4 py-10">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Мои слова</h1>

      <form onSubmit={handleSubmit} className={`${cardClass} flex flex-col gap-3 p-4`}>
        <div className="grid grid-cols-2 gap-3">
          <input
            required
            placeholder="Слово"
            value={form.text}
            onChange={(e) => setForm((f) => ({ ...f, text: e.target.value }))}
            className={inputClass}
          />
          <input
            required
            placeholder="Перевод"
            value={form.translation}
            onChange={(e) => setForm((f) => ({ ...f, translation: e.target.value }))}
            className={inputClass}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <input
            placeholder="Транскрипция (необязательно)"
            value={form.transcription}
            onChange={(e) => setForm((f) => ({ ...f, transcription: e.target.value }))}
            className={inputClass}
          />
          <select
            value={form.part_of_speech}
            onChange={(e) =>
              setForm((f) => ({ ...f, part_of_speech: e.target.value as PartOfSpeech }))
            }
            className={inputClass}
          >
            {PARTS_OF_SPEECH.map((p) => (
              <option key={p} value={p}>
                {PART_OF_SPEECH_LABELS[p]}
              </option>
            ))}
          </select>
        </div>
        <select
          value={form.level}
          onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))}
          className={`self-start ${inputClass}`}
        >
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              Уровень {l}
            </option>
          ))}
        </select>
        <textarea
          placeholder="Пример предложения (необязательно)"
          value={form.example_sentence}
          onChange={(e) => setForm((f) => ({ ...f, example_sentence: e.target.value }))}
          className={inputClass}
          rows={2}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting || !languageId}
          className={buttonClass("primary", "self-start")}
        >
          {submitting ? "Добавляем..." : "Добавить слово"}
        </button>
      </form>

      <LevelSwitcher value={filterLevel} onChange={setFilterLevel} />

      {words === null && <p className="text-zinc-500">Загрузка...</p>}
      {words !== null && words.length === 0 && (
        <p className="text-zinc-500">У вас пока нет своих слов на этом уровне — добавьте выше.</p>
      )}

      <ul className="flex flex-col gap-2">
        {words?.map((word) => (
          <li key={word.id} className={`${cardClass} flex items-center justify-between px-4 py-3`}>
            <div>
              <span className="mr-2 rounded-full border border-zinc-300 px-2 py-0.5 text-xs text-zinc-500 dark:border-zinc-700">
                {word.level}
              </span>
              <span className="font-medium text-zinc-900 dark:text-zinc-50">{word.text}</span>
              <span className="text-zinc-500"> — {word.translation}</span>
              {word.transcription && (
                <span className="ml-2 text-sm text-zinc-400">{word.transcription}</span>
              )}
            </div>
            <button onClick={() => handleDelete(word.id)} className={buttonClass("danger", "!px-0")}>
              Удалить
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
