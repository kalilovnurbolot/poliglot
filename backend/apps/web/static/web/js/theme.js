// Appearance: mode ("system" follows the OS, "light", "dark"), accent color (any hex,
// "" = default indigo) and tinted background. The palette itself is built in CSS from
// --accent (see tailwind/input.css). Loaded in <head>, so a saved choice is applied
// before the page is painted and never flashes the default first.
//
// Signed-in users keep it in their account (apps/web/appearance.py): base.html renders
// it and passes it here as #appearance-data, and changes are saved back to the server.
// Guests keep it in localStorage; a guest's choice moves to the account on sign-in.
(() => {
  const KEY = "appearance";
  const HINT_KEY = "appearance-hint-seen";
  const MODES = ["system", "light", "dark"];
  const ACTIVE_SWATCH = ["ring-2", "ring-zinc-900", "dark:ring-zinc-100"];
  const DEFAULTS = { mode: "system", accent: "", tint: false };
  const SAVE_DELAY = 400; // the color picker fires many events while dragging

  const accountEl = document.getElementById("appearance-data");
  const account = accountEl ? JSON.parse(accountEl.textContent) : null;

  function normalize(saved) {
    return {
      mode: MODES.includes(saved.mode) ? saved.mode : DEFAULTS.mode,
      accent: /^#[0-9a-f]{6}$/i.test(saved.accent) ? saved.accent : DEFAULTS.accent,
      tint: saved.tint === true,
    };
  }

  // The guest's choice in this browser, or null if there is none.
  function loadLocal() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY));
      return saved ? normalize(saved) : null;
    } catch {
      return null;
    }
  }

  let state = account?.saved ? normalize(account) : loadLocal() ?? { ...DEFAULTS };

  let saveTimer = null;
  let pending = null;
  function flushSave() {
    clearTimeout(saveTimer);
    if (!pending) return;
    // keepalive: the request survives leaving the page right after picking a color.
    fetch(account.url, {
      method: "POST",
      credentials: "same-origin",
      keepalive: true,
      headers: { "Content-Type": "application/json", "X-CSRFToken": poliglot.csrfToken() },
      body: JSON.stringify(pending),
    }).catch(() => {});
    pending = null;
  }
  function saveToAccount(data, delay = SAVE_DELAY) {
    pending = data;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flushSave, delay);
  }
  addEventListener("pagehide", () => account && flushSave());

  function apply() {
    const root = document.documentElement;
    if (state.mode === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", state.mode);
    if (state.accent) {
      root.setAttribute("data-accent", "");
      root.style.setProperty("--accent", state.accent);
    } else {
      root.removeAttribute("data-accent");
      root.style.removeProperty("--accent");
    }
    root.toggleAttribute("data-tint", state.tint);
    if (document.body) syncControls();
  }

  // Panel state and the browser/status bar color, which follows the page background.
  function syncControls() {
    const background = getComputedStyle(document.body).backgroundColor;
    document.querySelectorAll('meta[name="theme-color"]').forEach((meta) => (meta.content = background));
    document.querySelectorAll("[data-theme-mode]").forEach((button) => {
      const active = button.dataset.themeMode === state.mode;
      button.classList.toggle("pill-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    const presets = [...document.querySelectorAll("[data-theme-accent]")];
    const isPreset = presets.some((button) => button.dataset.themeAccent === state.accent);
    presets.forEach((button) => {
      const active = button.dataset.themeAccent === state.accent;
      ACTIVE_SWATCH.forEach((cls) => button.classList.toggle(cls, active));
      button.setAttribute("aria-pressed", String(active));
    });
    document.querySelectorAll("[data-theme-custom-swatch]").forEach((label) => {
      ACTIVE_SWATCH.forEach((cls) => label.classList.toggle(cls, !isPreset));
      if (!isPreset) label.style.background = state.accent;
    });
    document.querySelectorAll("[data-theme-custom]").forEach((input) => (input.value = state.accent || "#4f46e5"));
    document.querySelectorAll("[data-theme-tint]").forEach((input) => (input.checked = state.tint));
  }

  // The "new: appearance" hint is shown until the learner has used the panel once.
  function hintSeen() {
    if (account) return account.hint_seen || account.saved;
    try {
      return localStorage.getItem(KEY) !== null || localStorage.getItem(HINT_KEY) !== null;
    } catch {
      return true; // can't remember a dismissal, so don't show it on every page
    }
  }

  function dismissHint() {
    document.querySelectorAll("[data-theme-hint]").forEach((hint) => (hint.hidden = true));
    if (hintSeen()) return;
    if (account) {
      account.hint_seen = true;
      poliglot.postJSON(account.url, { hint_seen: true }).catch(() => {});
      return;
    }
    try {
      localStorage.setItem(HINT_KEY, "1");
    } catch {
      // ignore, see hintSeen()
    }
  }

  function update(changes) {
    state = { ...state, ...changes };
    apply();
    document.querySelectorAll("[data-theme-hint]").forEach((hint) => (hint.hidden = true));
    if (account) {
      account.saved = true; // the server marks the hint as seen too
      return saveToAccount(state);
    }
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch {
      // Storage blocked (private mode): the look still changes until the page reloads.
    }
  }

  apply();
  document.addEventListener("DOMContentLoaded", () => {
    // First visit after signing in: keep the look chosen as a guest in this browser.
    if (account && !account.saved && loadLocal()) {
      account.saved = true;
      saveToAccount(state, 0);
    }
    syncControls();
    if (!hintSeen()) document.querySelectorAll("[data-theme-hint]").forEach((hint) => (hint.hidden = false));
  });

  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-theme-hint-close], [data-theme-panel] summary")) dismissHint();
    if (e.target.closest("[data-theme-hint-close]")) return;
    if (e.target.closest("[data-theme-hint-open]")) {
      dismissHint();
      document.querySelectorAll("[data-theme-panel]").forEach((panel) => (panel.open = true));
      return;
    }
    const mode = e.target.closest("[data-theme-mode]");
    if (mode) return update({ mode: mode.dataset.themeMode });
    const accent = e.target.closest("[data-theme-accent]");
    if (accent) return update({ accent: accent.dataset.themeAccent });
    // Clicking outside closes the panel.
    document.querySelectorAll("[data-theme-panel][open]").forEach((panel) => {
      if (!panel.contains(e.target)) panel.open = false;
    });
  });

  document.addEventListener("input", (e) => {
    if (e.target.matches("[data-theme-custom]")) update({ accent: e.target.value });
  });

  document.addEventListener("change", (e) => {
    if (e.target.matches("[data-theme-tint]")) update({ tint: e.target.checked });
  });

  // In "system" mode the background changes with the OS setting.
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => document.body && syncControls());
})();
