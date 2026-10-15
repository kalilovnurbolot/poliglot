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

export type GrammarRuleInput = {
  language: number;
  title: string;
  level: string;
  body: string;
};

async function errorMessage(res: Response, fallback: string) {
  const body = await res.json().catch(() => null);
  const firstValue = body ? Object.values(body)[0] : null;
  return Array.isArray(firstValue) ? String(firstValue[0]) : fallback;
}

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

export async function createGrammarRule(data: GrammarRuleInput): Promise<GrammarRule> {
  const res = await apiFetch("/grammar-rules/", { method: "POST", body: JSON.stringify(data) });
  if (!res.ok) throw new Error(await errorMessage(res, "Не удалось добавить правило"));
  return res.json();
}

export async function updateGrammarRule(id: number | string, data: Partial<GrammarRuleInput>): Promise<GrammarRule> {
  const res = await apiFetch(`/grammar-rules/${id}/`, { method: "PATCH", body: JSON.stringify(data) });
  if (!res.ok) throw new Error(await errorMessage(res, "Не удалось сохранить правило"));
  return res.json();
}

export async function deleteGrammarRule(id: number | string): Promise<void> {
  const res = await apiFetch(`/grammar-rules/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error("Не удалось удалить правило");
}
