// Listening before learning: each picked word is read aloud with its translation, as many
// times as picked in "Повторять", and the player moves on by itself. Nothing is saved as progress.
// The list below the player has every word of the level or group; the checked ones are
// played. The choice is remembered in this browser per level or group.
// «Мини-плеер» takes the card with its controls out: into an always-on-top window where the
// browser can (Document Picture-in-Picture, desktop Chrome/Edge), else to a corner of the page.
(() => {
  const AFTER_WORD = 700;
  const AFTER_CARD = 1500;
  const EXAMPLE_KEY = "poliglot-listen-example";
  const REPEAT_KEY = "poliglot-listen-repeat";
  const PICKED_KEY = `poliglot-listen-picked:${location.pathname}`;
  const PIP_TIMEOUT = 2000;

  const $ = (id) => document.getElementById(id);
  const words = JSON.parse($("words-data").textContent);
  if (!words.length) return;
  // Looked up once: in the mini player the card lives in another window's document,
  // where document.getElementById() of this page no longer finds it.
  const ui = {
    card: $("listen-card"), mini: $("listen-mini"), position: $("listen-position"), total: $("listen-total"),
    nothing: $("listen-nothing"), text: $("listen-text"), transcription: $("listen-transcription"),
    translation: $("listen-translation"), example: $("listen-example"), play: $("listen-play"),
    playLabel: $("listen-play-label"), prev: $("listen-prev"), next: $("listen-next"), done: $("listen-done"),
    picked: $("listen-picked"), searchEmpty: $("listen-search-empty"),
  };
  const language = window.poliglotLanguage;
  const rows = document.querySelectorAll("#listen-list > li");
  const items = document.querySelectorAll("#listen-list [data-index]");
  const boxes = document.querySelectorAll("#listen-list [data-pick]");
  const exampleToggle = $("listen-example-toggle");
  const repeatButtons = document.querySelectorAll("#listen-repeat [data-repeat]");
  let repeat = 2;
  try {
    exampleToggle.checked = localStorage.getItem(EXAMPLE_KEY) === "1";
    repeat = Number(localStorage.getItem(REPEAT_KEY)) || repeat;
  } catch {}

  // ---- the list: which words are played ----
  const defaultIds = new Set(JSON.parse($("picked-data").textContent));
  let pickedIds = defaultIds;
  try {
    const saved = JSON.parse(localStorage.getItem(PICKED_KEY));
    if (Array.isArray(saved)) pickedIds = new Set(saved);
  } catch {}
  const isPicked = (i) => boxes[i].checked;
  const pickedIndexes = () => words.map((_, i) => i).filter(isPicked);

  function savePicked() {
    try {
      localStorage.setItem(PICKED_KEY, JSON.stringify(words.filter((_, i) => isPicked(i)).map((word) => word.id)));
    } catch {}
  }

  let index = 0;
  let playing = false;
  // Bumped on every pause or jump, so a loop still waiting on old speech stops.
  let run = 0;
  let wakeLock = null;

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function showCount() {
    const picked = pickedIndexes();
    ui.picked.textContent = picked.length;
    ui.total.textContent = picked.length;
    ui.position.textContent = Math.max(1, picked.filter((i) => i <= index).length);
    ui.nothing.classList.toggle("hidden", picked.length > 0);
    for (const button of [ui.play, ui.prev, ui.next]) button.disabled = !picked.length;
  }

  function show(i) {
    index = i;
    const word = words[i];
    ui.text.textContent = word.text;
    ui.transcription.textContent = word.transcription;
    ui.translation.textContent = word.translation;
    ui.example.textContent = word.example_sentence ? `«${word.example_sentence}»` : "";
    rows.forEach((row, n) => {
      row.classList.toggle("bg-indigo-50", n === i);
      row.classList.toggle("dark:bg-indigo-500/10", n === i);
    });
    if (!rows[i].classList.contains("hidden")) rows[i].scrollIntoView({ block: "nearest", behavior: "smooth" });
    showCount();
  }

  function setPlaying(value) {
    playing = value;
    ui.playLabel.textContent = playing ? "Пауза" : "Слушать";
    if (playing) {
      navigator.wakeLock?.request("screen").then((lock) => (wakeLock = lock)).catch(() => {});
    } else {
      wakeLock?.release().catch(() => {});
      wakeLock = null;
    }
  }

  // The nearest picked word from `from` in direction `step` (+1 / -1), or -1.
  function nearestPicked(from, step) {
    for (let i = from; i >= 0 && i < words.length; i += step) if (isPicked(i)) return i;
    return -1;
  }

  async function play(from) {
    const current = ++run;
    setPlaying(true);
    ui.done.classList.replace("flex", "hidden");
    // Checked each time, so a word picked or unpicked while playing counts from the next one.
    for (let i = nearestPicked(from, 1); i !== -1; i = nearestPicked(i + 1, 1)) {
      show(i);
      const word = words[i];
      // Read at the time of each word, so a change applies from the next one.
      const steps = [];
      for (let n = 0; n < repeat; n++) {
        if (n) steps.push(() => wait(AFTER_WORD));
        steps.push(
          () => poliglot.speak(word.text, language), () => wait(AFTER_WORD),
          () => poliglot.speak(word.translation, "ru"),
        );
      }
      if (exampleToggle.checked && word.example_sentence) {
        steps.push(() => wait(AFTER_WORD), () => poliglot.speak(word.example_sentence, language));
      }
      steps.push(() => wait(AFTER_CARD));
      for (const step of steps) {
        await step();
        if (current !== run) return;
      }
    }
    setPlaying(false);
    if (pickedIndexes().length) ui.done.classList.replace("hidden", "flex");
  }

  function pause() {
    run++;
    window.speechSynthesis?.cancel();
    setPlaying(false);
  }

  function jump(step) {
    const i = nearestPicked(index + step, step);
    if (i === -1) return;
    if (playing) return play(i);
    show(i);
  }

  ui.play.addEventListener("click", () => (playing ? pause() : play(index)));
  ui.prev.addEventListener("click", () => jump(-1));
  ui.next.addEventListener("click", () => jump(1));
  // Playing a word from the list puts it in the list.
  items.forEach((item) => item.addEventListener("click", () => {
    const i = Number(item.dataset.index);
    if (!isPicked(i)) {
      boxes[i].checked = true;
      savePicked();
    }
    play(i);
  }));

  boxes.forEach((box) => box.addEventListener("change", () => {
    savePicked();
    showCount();
  }));

  // «Все» and «Ничего» apply to the words the search shows.
  function pickVisible(value) {
    rows.forEach((row, i) => { if (!row.classList.contains("hidden")) boxes[i].checked = value; });
    savePicked();
    showCount();
  }
  $("listen-pick-all").addEventListener("click", () => pickVisible(true));
  $("listen-pick-none").addEventListener("click", () => pickVisible(false));
  $("listen-pick-default").addEventListener("click", () => {
    words.forEach((word, i) => (boxes[i].checked = defaultIds.has(word.id)));
    try { localStorage.removeItem(PICKED_KEY); } catch {}
    showCount();
  });

  $("listen-search")?.addEventListener("input", (e) => {
    const query = e.target.value.trim().toLowerCase();
    let found = 0;
    rows.forEach((row) => {
      const match = row.dataset.search.includes(query);
      row.classList.toggle("hidden", !match);
      if (match) found++;
    });
    ui.searchEmpty.classList.toggle("hidden", found > 0);
  });

  function showRepeat() {
    repeatButtons.forEach((button) => {
      const active = Number(button.dataset.repeat) === repeat;
      button.classList.toggle("pill-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }
  repeatButtons.forEach((button) => button.addEventListener("click", () => {
    repeat = Number(button.dataset.repeat);
    try { localStorage.setItem(REPEAT_KEY, String(repeat)); } catch {}
    showRepeat();
  }));
  exampleToggle.addEventListener("change", () => {
    try { localStorage.setItem(EXAMPLE_KEY, exampleToggle.checked ? "1" : "0"); } catch {}
  });

  function onKey(e) {
    // Typing in the search box is not a player command.
    if (e.target.closest("input[type=search]")) return;
    if (e.key === " ") {
      // A focused button or checkbox handles Space itself.
      if (e.target.closest("input, button, a")) return;
      e.preventDefault();
      playing ? pause() : play(index);
    }
    if (e.key === "ArrowLeft") jump(-1);
    if (e.key === "ArrowRight") jump(1);
  }
  window.addEventListener("keydown", onKey);

  // ---- mini player ----
  const { card } = ui;
  const main = card.closest("main");
  const spot = document.createComment("listen-card");
  let pipWindow = null;

  function setMini(mode) {
    if (mode) card.dataset.mini = mode;
    else delete card.dataset.mini;
    const label = mode ? "Развернуть" : "Мини-плеер";
    ui.mini.setAttribute("aria-label", label);
    ui.mini.title = label;
    // Room below the list, so the pinned card never covers its last words.
    main.classList.toggle("pb-72", mode === "float");
  }

  // The window starts empty: it gets the page's styles and theme (palette, dark mode).
  function dressWindow(win) {
    for (const sheet of document.styleSheets) {
      if (sheet.href) {
        const link = win.document.createElement("link");
        link.rel = "stylesheet";
        link.href = sheet.href;
        win.document.head.append(link);
      } else if (sheet.ownerNode) {
        win.document.head.append(sheet.ownerNode.cloneNode(true));
      }
    }
    for (const { name, value } of document.documentElement.attributes) win.document.documentElement.setAttribute(name, value);
    win.document.body.className = document.body.className;
  }

  // Back exactly where it was, as it was.
  function restoreCard() {
    if (spot.isConnected) spot.replaceWith(card);
    pipWindow = null;
    setMini(null);
    card.scrollIntoView({ block: "nearest" });
  }

  // Some browsers leave the request hanging instead of refusing it (window blocked, no
  // window system): after PIP_TIMEOUT the card is pinned to the page instead, and a window
  // that still turns up later is closed.
  async function requestPipWindow() {
    const request = window.documentPictureInPicture.requestWindow({ width: 340, height: 260 });
    let timedOut = false;
    const timeout = new Promise((_, reject) => setTimeout(() => {
      timedOut = true;
      reject(new Error("Окно мини-плеера не открылось."));
    }, PIP_TIMEOUT));
    request.then((win) => timedOut && win.close(), () => {});
    return Promise.race([request, timeout]);
  }

  async function openPip() {
    const win = await requestPipWindow();
    try {
      dressWindow(win);
      card.before(spot);
      win.document.body.append(card);
    } catch (e) {
      restoreCard();
      win.close();
      throw e;
    }
    pipWindow = win;
    win.addEventListener("keydown", onKey);
    setMini("pip");
    // Closed from its own button or the window's ×: the card goes back where it was.
    win.addEventListener("pagehide", restoreCard, { once: true });
  }

  ui.mini.addEventListener("click", async () => {
    if (pipWindow) return pipWindow.close();
    if (card.dataset.mini) return setMini(null);
    if (window.documentPictureInPicture) {
      try {
        return await openPip();
      } catch {} // refused (e.g. not from a click): pin it to the page instead
    }
    setMini("float");
  });

  document.addEventListener("visibilitychange", () => {
    if (playing && !document.hidden && !wakeLock) {
      navigator.wakeLock?.request("screen").then((lock) => (wakeLock = lock)).catch(() => {});
    }
  });

  words.forEach((word, i) => (boxes[i].checked = pickedIds.has(word.id)));
  showRepeat();
  show(Math.max(0, nearestPicked(0, 1)));
})();
