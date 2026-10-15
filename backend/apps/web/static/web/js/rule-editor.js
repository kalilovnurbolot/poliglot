// Grammar rule editor: snippet buttons, text/preview tabs on mobile and a live
// server-rendered preview (same renderer as the rule page).
(() => {
  const form = document.querySelector("[data-rule-editor]");
  if (!form) return;

  const FENCE = "```";
  const SNIPPETS = [
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

  const textarea = form.querySelector("[data-rule-body]");
  const preview = form.querySelector("[data-preview]");
  const panes = { edit: form.querySelector('[data-pane="edit"]'), preview: form.querySelector('[data-pane="preview"]') };

  function setTab(tab) {
    form.querySelectorAll("[data-tab]").forEach((b) => b.classList.toggle("pill-active", b.dataset.tab === tab));
    panes.edit.classList.toggle("hidden", tab !== "edit");
    panes.edit.classList.toggle("lg:block", tab !== "edit");
    panes.preview.classList.toggle("hidden", tab !== "preview");
  }
  form.querySelectorAll("[data-tab]").forEach((b) => b.addEventListener("click", () => setTab(b.dataset.tab)));

  let timer = null;
  let requestId = 0;
  function refreshPreview() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const id = ++requestId;
      const body = new FormData();
      body.append("body", textarea.value);
      const res = await fetch(form.dataset.previewUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": poliglot.csrfToken() },
        body,
      }).catch(() => null);
      if (res?.ok && id === requestId) preview.innerHTML = await res.text();
    }, 250);
  }
  textarea.addEventListener("input", refreshPreview);

  const snippetBox = form.querySelector("[data-snippets]");
  for (const snippet of SNIPPETS) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "pill";
    button.textContent = `+ ${snippet.label}`;
    button.addEventListener("click", () => {
      const { selectionStart: start, selectionEnd: end, value } = textarea;
      const before = value.slice(0, start);
      const prefix = before && !before.endsWith("\n\n") ? (before.endsWith("\n") ? "\n" : "\n\n") : "";
      textarea.value = before + prefix + snippet.text + value.slice(end);
      setTab("edit");
      const pos = start + prefix.length + snippet.text.length;
      textarea.focus();
      textarea.setSelectionRange(pos, pos);
      refreshPreview();
    });
    snippetBox.appendChild(button);
  }
})();
