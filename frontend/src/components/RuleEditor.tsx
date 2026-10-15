"use client";

import { useRef, useState, type FormEvent } from "react";
import { RuleBody } from "@/components/RuleBody";
import type { GrammarRuleInput } from "@/lib/grammar";
import { LEVELS } from "@/lib/levels";
import { buttonClass, cardClass, inputClass, pillClass } from "@/lib/ui";

const FENCE = "```";

const SNIPPETS: { label: string; text: string }[] = [
  { label: "Раздел", text: "## Название раздела\n\nКороткое объяснение, когда это используется.\n" },
  {
    label: "Формула",
    text: `${FENCE}formula\n+ | [s: Subject] + [v: Verb] + [o: Object]\n− | [s: Subject] + [f: don't] + [v: Verb]\n? | [f: Do] + [s: Subject] + [v: Verb] [f: ?]\n${FENCE}\n`,
  },
  { label: "Пример", text: `${FENCE}example\n[s: She] [v: reads] [o: a book] [m: every day]\n= Она читает книгу каждый день.\n${FENCE}\n` },
  { label: "Заметка", text: `${FENCE}note\n! | Важное замечание, можно с \`кодом\` и **жирным**.\n${FENCE}\n` },
  { label: "Легенда", text: `${FENCE}legend\ns: подлежащее\nv: глагол\no: дополнение\nm: время / место\n${FENCE}\n` },
  { label: "Таблица", text: "| Лицо | Форма | Пример |\n|---|---|---|\n| I | **am** | I am ready. |\n" },
  { label: "Плашки", text: `${FENCE}pills\nWhat — что\nWhere — где\n${FENCE}\n` },
  { label: "Карточки", text: `${FENCE}cards\nБлизко · один | this | этот | this book\nДалеко · один | that | тот | that house\n${FENCE}\n` },
];

export const NEW_RULE_TEMPLATE = `${FENCE}legend
s: подлежащее
v: глагол
o: дополнение
m: время / место
${FENCE}

Коротко: когда и зачем используется это правило.

## Формула

${FENCE}formula
+ | [s: Subject] + [v: Verb] + [o: Object]
${FENCE}

${FENCE}example
[s: I] [v: like] [o: coffee]
= Я люблю кофе.
${FENCE}

${FENCE}note
! | Частая ошибка и как её избежать.
${FENCE}
`;

type Props = {
  initial: Omit<GrammarRuleInput, "language">;
  submitLabel: string;
  onSubmit: (data: Omit<GrammarRuleInput, "language">) => Promise<void>;
};

export function RuleEditor({ initial, submitLabel, onSubmit }: Props) {
  const [form, setForm] = useState(initial);
  const [tab, setTab] = useState<"edit" | "preview">("edit");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insert = (snippet: string) => {
    const el = textareaRef.current;
    const start = el?.selectionStart ?? form.body.length;
    const end = el?.selectionEnd ?? form.body.length;
    const before = form.body.slice(0, start);
    const prefix = before && !before.endsWith("\n\n") ? (before.endsWith("\n") ? "\n" : "\n\n") : "";
    const body = before + prefix + snippet + form.body.slice(end);
    setForm((f) => ({ ...f, body }));
    setTab("edit");
    requestAnimationFrame(() => {
      const pos = start + prefix.length + snippet.length;
      el?.focus();
      el?.setSelectionRange(pos, pos);
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({ ...form, title: form.title.trim() });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сохранить правило");
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className={`${cardClass} flex flex-col gap-3 p-4 sm:flex-row`}>
        <input
          required
          placeholder="Название правила"
          value={form.title}
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          className={`flex-1 ${inputClass}`}
        />
        <select
          value={form.level}
          onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))}
          className={inputClass}
        >
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              Уровень {l}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap gap-2">
        {SNIPPETS.map((s) => (
          <button key={s.label} type="button" onClick={() => insert(s.text)} className={pillClass(false)}>
            + {s.label}
          </button>
        ))}
      </div>

      <div className="flex gap-2 lg:hidden">
        <button type="button" onClick={() => setTab("edit")} className={pillClass(tab === "edit")}>
          Текст
        </button>
        <button type="button" onClick={() => setTab("preview")} className={pillClass(tab === "preview")}>
          Превью
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <textarea
          ref={textareaRef}
          required
          value={form.body}
          onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
          spellCheck={false}
          className={`${inputClass} min-h-[480px] font-mono text-[13px] leading-relaxed ${tab === "preview" ? "hidden lg:block" : ""}`}
        />
        <div className={`${cardClass} min-h-[480px] p-5 ${tab === "edit" ? "hidden lg:block" : ""}`}>
          <RuleBody body={form.body} />
        </div>
      </div>

      <details className="text-sm text-zinc-600 dark:text-zinc-400">
        <summary className="cursor-pointer select-none font-medium text-zinc-800 dark:text-zinc-200">
          Как размечать правило
        </summary>
        <div className="mt-2 flex flex-col gap-1.5 leading-relaxed">
          <p>
            Обычный Markdown: <code>## Раздел</code> (попадает в оглавление), <code>**жирный**</code>, списки,
            таблицы.
          </p>
          <p>
            Роли слов в формулах и примерах: <code>[s: …]</code> подлежащее, <code>[v: …]</code> глагол,{" "}
            <code>[o: …]</code> дополнение, <code>[m: …]</code> время/место/уточнение, <code>[f: …]</code>{" "}
            служебное слово. Текст вне скобок показывается как есть.
          </p>
          <p>
            <code>formula</code> — строка на каждую форму, подпись слева через <code>+ | </code>. <code>example</code> —
            строка, начинающаяся с <code>=</code>, это перевод. <code>note</code> — значок слева через{" "}
            <code>× | </code>.
          </p>
        </div>
      </details>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button type="submit" disabled={submitting} className={buttonClass("primary", "self-start")}>
        {submitting ? "Сохранение..." : submitLabel}
      </button>
    </form>
  );
}
