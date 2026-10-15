"use client";

import type { ReactNode } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  parseCards,
  parseExample,
  parseFormula,
  parseLegend,
  parseNote,
  parsePills,
  type Token,
} from "@/lib/rule-blocks";

export function slugify(text: string) {
  return text
    .toLowerCase()
    .replace(/[*_`]/g, "")
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "");
}

// Section list for the side navigation: every "## Heading" outside fenced blocks.
export function extractSections(body: string) {
  const withoutFences = body.replace(/```[\s\S]*?```/g, "");
  return [...withoutFences.matchAll(/^## +(.+)$/gm)].map((m) => {
    const title = m[1].replace(/[*_`]/g, "").trim();
    return { id: slugify(title), title };
  });
}

// First plain paragraph of the body, without Markdown markup — the rule's one-line summary.
export function extractLede(body: string) {
  const withoutFences = body.replace(/```[\s\S]*?```/g, "");
  const paragraph = withoutFences
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .find((p) => p && !/^(#|\||-|\d+\.|>)/.test(p));
  return paragraph?.replace(/[*_`]/g, "").replace(/\s+/g, " ") ?? "";
}

type HastNode = { type: string; value?: string; tagName?: string; properties?: Record<string, unknown>; children?: HastNode[] };

function textOf(node: HastNode | undefined): string {
  if (!node) return "";
  if (node.type === "text") return node.value ?? "";
  return (node.children ?? []).map(textOf).join("");
}

function InlineMarkdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <span className="rule-inline-p">{children}</span>,
        code: ({ children }) => <code className="rule-mono">{children}</code>,
      }}
    >
      {children}
    </ReactMarkdown>
  );
}

function Chips({ tokens }: { tokens: Token[] }) {
  return tokens.map((t, i) =>
    t.role ? (
      <span key={i} className={`rule-chip rule-chip-${t.role}`}>
        {t.text}
      </span>
    ) : (
      <span key={i} className="rule-plus">
        {t.text}
      </span>
    ),
  );
}

function Words({ tokens }: { tokens: Token[] }) {
  return tokens.map((t, i) => (
    <span key={i} className={`rule-w rule-w-${t.role ?? "plain"}`}>
      {t.text}
    </span>
  ));
}

function renderBlock(lang: string, source: string): ReactNode | null {
  switch (lang) {
    case "formula":
      return (
        <div className="rule-formula">
          {parseFormula(source).map((row, i) => (
            <div key={i} className="rule-f-row">
              {row.label && <span className="rule-f-label">{row.label}</span>}
              <Chips tokens={row.tokens} />
            </div>
          ))}
        </div>
      );
    case "example": {
      const { tokens, translation } = parseExample(source);
      return (
        <div className="rule-example">
          <Words tokens={tokens} />
          {translation && <span className="rule-tr">{translation}</span>}
        </div>
      );
    }
    case "note": {
      const { mark, text } = parseNote(source);
      return (
        <div className={`rule-note ${mark === "×" ? "rule-note-error" : ""}`}>
          <span className="rule-note-mark">{mark}</span>
          <span>
            <InlineMarkdown>{text}</InlineMarkdown>
          </span>
        </div>
      );
    }
    case "legend":
      return (
        <div className="rule-legend">
          {parseLegend(source).map((item, i) => (
            <span key={i}>
              <i className={`rule-dot-${item.role}`} />
              {item.label}
            </span>
          ))}
        </div>
      );
    case "pills":
      return (
        <div className="rule-pills">
          {parsePills(source).map((p, i) => (
            <span key={i} className="rule-pill">
              <span className="rule-mono">{p.term}</span>
              {p.meaning && <>— {p.meaning}</>}
            </span>
          ))}
        </div>
      );
    case "cards":
      return (
        <div className="rule-cards">
          {parseCards(source).map((c, i) => (
            <div key={i} className="rule-card">
              {c.kicker && <div className="rule-card-k">{c.kicker}</div>}
              <div className="rule-card-big">
                {c.big} {c.hint && <small>— {c.hint}</small>}
              </div>
              {c.text && <p>{c.text}</p>}
            </div>
          ))}
        </div>
      );
    default:
      return null;
  }
}

const components: Components = {
  pre: ({ node, children }) => {
    const code = (node as HastNode | undefined)?.children?.[0];
    const classes = (code?.properties?.className as string[] | undefined) ?? [];
    const lang = classes.find((c) => c.startsWith("language-"))?.slice("language-".length);
    const block = lang ? renderBlock(lang, textOf(code).replace(/\n$/, "")) : null;
    return block ?? <pre className="rule-pre">{children}</pre>;
  },
  code: ({ className, children }) =>
    className ? <code className={className}>{children}</code> : <code className="rule-mono">{children}</code>,
  h2: ({ node, children }) => (
    <h2 id={slugify(textOf(node as HastNode))} className="rule-h2">
      {children}
    </h2>
  ),
  table: ({ children }) => (
    <div className="rule-table-wrap">
      <table>{children}</table>
    </div>
  ),
  blockquote: ({ children }) => (
    <div className="rule-note">
      <span className="rule-note-mark">!</span>
      <div>{children}</div>
    </div>
  ),
};

export function RuleBody({ body }: { body: string }) {
  return (
    <div className="rule">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {body}
      </ReactMarkdown>
    </div>
  );
}
