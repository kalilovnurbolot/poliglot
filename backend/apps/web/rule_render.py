"""Server-side rendering of a grammar rule body: Markdown (GFM tables) plus the
special fenced blocks formula / example / note / legend / pills / cards.

Word roles inside blocks are written as [s: She] [v: is] [o: a student] [m: now] [f: ?]
  s — подлежащее, v — глагол, o — дополнение/complement, m — уточнение/модификатор, f — служебное слово.
Text outside brackets is shown as is (in a formula it is a «+», «→» etc., in an example — a plain word).
"""
import re
from html import escape

from markdown_it import MarkdownIt

TOKEN_RE = re.compile(r'\[([svomf]):\s*([^\]]*)\]')
FENCE_RE = re.compile(r'```[\s\S]*?```')


def parse_tokens(line):
    tokens = []
    last = 0
    for match in TOKEN_RE.finditer(line):
        before = line[last:match.start()].strip()
        if before:
            tokens.append((None, before))
        tokens.append((match.group(1), match.group(2).strip()))
        last = match.end()
    rest = line[last:].strip()
    if rest:
        tokens.append((None, rest))
    return tokens


def _lines(source):
    return [line.strip() for line in source.split('\n') if line.strip()]


def _split_label(line, fallback=''):
    """'label | content' → (label, content); without ' | ' the label is the fallback."""
    i = line.find(' | ')
    if i == -1:
        return fallback, line
    return line[:i].strip(), line[i + 3:].strip()


def parse_formula(source):
    rows = []
    for line in _lines(source):
        label, content = _split_label(line)
        rows.append((label, parse_tokens(content)))
    return rows


def parse_example(source):
    words, translation = [], []
    for line in _lines(source):
        if line.startswith('='):
            translation.append(line[1:].strip())
        else:
            words.extend(parse_tokens(line))
    return words, ' '.join(translation)


def parse_note(source):
    first, *rest = source.strip().split('\n')
    mark, content = _split_label(first.strip(), '!')
    return mark, '\n'.join([content, *rest]).strip()


def parse_legend(source):
    items = []
    for line in _lines(source):
        m = re.match(r'^([svomf])\s*[:—-]\s*(.+)$', line)
        if m:
            items.append((m.group(1), m.group(2)))
    return items


def parse_pills(source):
    pills = []
    for line in _lines(source):
        term, *meaning = line.split(' — ')
        pills.append((term.strip(), ' — '.join(meaning).strip()))
    return pills


def parse_cards(source):
    cards = []
    for line in _lines(source):
        parts = [p.strip() for p in line.split('|')] + ['', '', '', '']
        cards.append(tuple(parts[:4]))
    return cards


def slugify(text):
    text = re.sub(r'[*_`]', '', text.lower())
    return re.sub(r'[\W_]+', '-', text).strip('-')


def extract_sections(body):
    """Section list for the side navigation: every '## Heading' outside fenced blocks."""
    without_fences = FENCE_RE.sub('', body)
    sections = []
    for m in re.finditer(r'^## +(.+)$', without_fences, re.M):
        title = re.sub(r'[*_`]', '', m.group(1)).strip()
        sections.append({'id': slugify(title), 'title': title})
    return sections


def extract_lede(body):
    """First plain paragraph of the body, without Markdown markup — the rule's one-line summary."""
    without_fences = FENCE_RE.sub('', body)
    for paragraph in re.split(r'\n\s*\n', without_fences):
        paragraph = paragraph.strip()
        if paragraph and not re.match(r'^(#|\||-|\d+\.|>)', paragraph):
            return re.sub(r'\s+', ' ', re.sub(r'[*_`]', '', paragraph))
    return ''


# ---------- HTML ----------

def _chips(tokens):
    return ''.join(
        f'<span class="rule-chip rule-chip-{role}">{escape(text)}</span>' if role
        else f'<span class="rule-plus">{escape(text)}</span>'
        for role, text in tokens
    )


def _words(tokens):
    return ''.join(
        f'<span class="rule-w rule-w-{role or "plain"}">{escape(text)}</span>' for role, text in tokens
    )


def _inline_markdown(text):
    html = md.render(text).strip()
    return html.replace('<p>', '<span class="rule-inline-p">').replace('</p>', '</span>')


def render_block(lang, source):
    if lang == 'formula':
        rows = ''.join(
            '<div class="rule-f-row">'
            + (f'<span class="rule-f-label">{escape(label)}</span>' if label else '')
            + _chips(tokens) + '</div>'
            for label, tokens in parse_formula(source)
        )
        return f'<div class="rule-formula">{rows}</div>'
    if lang == 'example':
        tokens, translation = parse_example(source)
        tr = f'<span class="rule-tr">{escape(translation)}</span>' if translation else ''
        return f'<div class="rule-example">{_words(tokens)}{tr}</div>'
    if lang == 'note':
        mark, text = parse_note(source)
        error = ' rule-note-error' if mark == '×' else ''
        return (
            f'<div class="rule-note{error}"><span class="rule-note-mark">{escape(mark)}</span>'
            f'<span>{_inline_markdown(text)}</span></div>'
        )
    if lang == 'legend':
        items = ''.join(
            f'<span><i class="rule-dot-{role}"></i>{escape(label)}</span>' for role, label in parse_legend(source)
        )
        return f'<div class="rule-legend">{items}</div>'
    if lang == 'pills':
        pills = ''.join(
            f'<span class="rule-pill"><span class="rule-mono">{escape(term)}</span>'
            + (f'— {escape(meaning)}' if meaning else '') + '</span>'
            for term, meaning in parse_pills(source)
        )
        return f'<div class="rule-pills">{pills}</div>'
    if lang == 'cards':
        cards = []
        for kicker, big, hint, text in parse_cards(source):
            cards.append(
                '<div class="rule-card">'
                + (f'<div class="rule-card-k">{escape(kicker)}</div>' if kicker else '')
                + f'<div class="rule-card-big">{escape(big)} '
                + (f'<small>— {escape(hint)}</small>' if hint else '') + '</div>'
                + (f'<p>{escape(text)}</p>' if text else '')
                + '</div>'
            )
        return f'<div class="rule-cards">{"".join(cards)}</div>'
    return None


def _fence(self, tokens, idx, options, env):
    token = tokens[idx]
    lang = token.info.strip().split(' ')[0] if token.info else ''
    source = token.content[:-1] if token.content.endswith('\n') else token.content
    block = render_block(lang, source) if lang else None
    return block or f'<pre class="rule-pre"><code>{escape(token.content)}</code></pre>'


def _code_block(self, tokens, idx, options, env):
    return f'<pre class="rule-pre"><code>{escape(tokens[idx].content)}</code></pre>'


def _code_inline(self, tokens, idx, options, env):
    return f'<code class="rule-mono">{escape(tokens[idx].content)}</code>'


def _heading_open(self, tokens, idx, options, env):
    token = tokens[idx]
    if token.tag == 'h2':
        return f'<h2 id="{escape(slugify(tokens[idx + 1].content))}" class="rule-h2">'
    return f'<{token.tag}>'


md = MarkdownIt('commonmark', {'html': False}).enable(['table', 'strikethrough'])
md.add_render_rule('fence', _fence)
md.add_render_rule('code_block', _code_block)
md.add_render_rule('code_inline', _code_inline)
md.add_render_rule('heading_open', _heading_open)
md.add_render_rule('table_open', lambda *a: '<div class="rule-table-wrap"><table>')
md.add_render_rule('table_close', lambda *a: '</table></div>')
md.add_render_rule(
    'blockquote_open', lambda *a: '<div class="rule-note"><span class="rule-note-mark">!</span><div>'
)
md.add_render_rule('blockquote_close', lambda *a: '</div></div>')


def render_rule(body):
    return f'<div class="rule">{md.render(body)}</div>'
