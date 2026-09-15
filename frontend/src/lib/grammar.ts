import { apiFetch } from "./api";

export { LEVELS } from "./levels";

export type GrammarRule = {
  id: number;
  language: number;
  title: string;
  level: string;
  body: string;
  order: number;
  is_learned: boolean;
};

export async function fetchGrammarRules(language = "en", level?: string): Promise<GrammarRule[]> {
  const params = new URLSearchParams({ language });
  if (level) params.set("level", level);
  const res = await apiFetch(`/grammar-rules/?${params.toString()}`);
  if (!res.ok) throw new Error("Не удалось загрузить правила");
  return res.json();
}

export async function fetchGrammarRule(id: string): Promise<GrammarRule> {
  const res = await apiFetch(`/grammar-rules/${id}/`);
  if (!res.ok) throw new Error("Правило не найдено");
  return res.json();
}

export async function toggleGrammarRuleLearned(id: string | number): Promise<{ is_learned: boolean }> {
  const res = await apiFetch(`/grammar-rules/${id}/toggle-learned/`, { method: "POST" });
  if (!res.ok) throw new Error("Не удалось сохранить прогресс");
  return res.json();
}
