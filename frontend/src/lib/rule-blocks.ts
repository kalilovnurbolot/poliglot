// Parsers for the special fenced blocks in a grammar rule body.
//
// Word roles inside blocks are written as [s: She] [v: is] [o: a student] [m: now] [f: ?]
//   s — подлежащее, v — глагол, o — дополнение/complement, m — уточнение/модификатор, f — служебное слово.
// Text outside brackets is shown as is (in a formula it is a «+», «→» etc., in an example — a plain word).

export type Role = "s" | "v" | "o" | "m" | "f";

export const ROLES: Record<Role, string> = {
  s: "подлежащее",
  v: "глагол",
  o: "дополнение",
  m: "уточнение",
  f: "служебное слово",
};

export type Token = { role: Role | null; text: string };

const TOKEN_RE = /\[([svomf]):\s*([^\]]*)\]/g;

export function parseTokens(line: string): Token[] {
  const tokens: Token[] = [];
  let last = 0;
  for (const match of line.matchAll(TOKEN_RE)) {
    const before = line.slice(last, match.index).trim();
    if (before) tokens.push({ role: null, text: before });
    tokens.push({ role: match[1] as Role, text: match[2].trim() });
    last = match.index + match[0].length;
  }
  const rest = line.slice(last).trim();
  if (rest) tokens.push({ role: null, text: rest });
  return tokens;
}

function lines(source: string) {
  return source.split("\n").map((l) => l.trim()).filter(Boolean);
}

// "label | content" → { label, content }; without " | " the label is empty.
function splitLabel(line: string, fallback = "") {
  const i = line.indexOf(" | ");
  if (i === -1) return { label: fallback, content: line };
  return { label: line.slice(0, i).trim(), content: line.slice(i + 3).trim() };
}

export type FormulaRow = { label: string; tokens: Token[] };

export function parseFormula(source: string): FormulaRow[] {
  return lines(source).map((line) => {
    const { label, content } = splitLabel(line);
    return { label, tokens: parseTokens(content) };
  });
}

export type Example = { tokens: Token[]; translation: string };

export function parseExample(source: string): Example {
  const words: Token[] = [];
  const translation: string[] = [];
  for (const line of lines(source)) {
    if (line.startsWith("=")) translation.push(line.slice(1).trim());
    else words.push(...parseTokens(line));
  }
  return { tokens: words, translation: translation.join(" ") };
}

export function parseNote(source: string) {
  const [first = "", ...restLines] = source.trim().split("\n");
  const { label, content } = splitLabel(first.trim(), "!");
  return { mark: label, text: [content, ...restLines].join("\n").trim() };
}

export function parseLegend(source: string): { role: Role; label: string }[] {
  return lines(source).flatMap((line) => {
    const m = line.match(/^([svomf])\s*[:—-]\s*(.+)$/);
    return m ? [{ role: m[1] as Role, label: m[2] }] : [];
  });
}

export function parsePills(source: string) {
  return lines(source).map((line) => {
    const [term, ...meaning] = line.split(" — ");
    return { term: term.trim(), meaning: meaning.join(" — ").trim() };
  });
}

export function parseCards(source: string) {
  return lines(source).map((line) => {
    const [kicker = "", big = "", hint = "", text = ""] = line.split("|").map((p) => p.trim());
    return { kicker, big, hint, text };
  });
}

export const BLOCK_TYPES = ["formula", "example", "note", "legend", "pills", "cards"] as const;
