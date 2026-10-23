// Listening before learning: each word is read aloud with its translation, as many times
// as picked in "Повторять", and the player moves on by itself. Nothing is saved as progress.
(() => {
  const AFTER_WORD = 700;
  const AFTER_CARD = 1500;
  const EXAMPLE_KEY = "poliglot-listen-example";
  const REPEAT_KEY = "poliglot-listen-repeat";

  const $ = (id) => document.getElementById(id);
  const cards = JSON.parse($("cards-data").textContent);
  if (!cards.length) return;
  const language = window.poliglotLanguage;
  const items = document.querySelectorAll("#listen-list [data-index]");
  const exampleToggle = $("listen-example-toggle");
  const repeatButtons = document.querySelectorAll("#listen-repeat [data-repeat]");
  let repeat = 2;
  try {
    exampleToggle.checked = localStorage.getItem(EXAMPLE_KEY) === "1";
    repeat = Number(localStorage.getItem(REPEAT_KEY)) || repeat;
  } catch {}

  let index = 0;
  let playing = false;
  // Bumped on every pause or jump, so a loop still waiting on old speech stops.
  let run = 0;
  let wakeLock = null;

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function show(i) {
    index = i;
    const { word } = cards[i];
    $("listen-position").textContent = i + 1;
    $("listen-text").textContent = word.text;
    $("listen-transcription").textContent = word.transcription;
    $("listen-translation").textContent = word.translation;
    $("listen-example").textContent = word.example_sentence ? `«${word.example_sentence}»` : "";
    items.forEach((item, n) => {
      item.classList.toggle("bg-indigo-50", n === i);
      item.classList.toggle("dark:bg-indigo-500/10", n === i);
    });
    items[i].scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function setPlaying(value) {
    playing = value;
    $("listen-play-label").textContent = playing ? "Пауза" : "Слушать";
    if (playing) {
      navigator.wakeLock?.request("screen").then((lock) => (wakeLock = lock)).catch(() => {});
    } else {
      wakeLock?.release().catch(() => {});
      wakeLock = null;
    }
  }

  async function play(from) {
    const current = ++run;
    setPlaying(true);
    $("listen-done").classList.replace("flex", "hidden");
    for (let i = from; i < cards.length; i++) {
      show(i);
      const { word } = cards[i];
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
    $("listen-done").classList.replace("hidden", "flex");
  }

  function pause() {
    run++;
    window.speechSynthesis?.cancel();
    setPlaying(false);
  }

  function jump(i) {
    if (i < 0 || i >= cards.length) return;
    if (playing) return play(i);
    show(i);
  }

  $("listen-play").addEventListener("click", () => (playing ? pause() : play(index)));
  $("listen-prev").addEventListener("click", () => jump(index - 1));
  $("listen-next").addEventListener("click", () => jump(index + 1));
  items.forEach((item) => item.addEventListener("click", () => play(Number(item.dataset.index))));
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

  window.addEventListener("keydown", (e) => {
    if (e.key === " ") {
      // A focused button or checkbox handles Space itself.
      if (e.target.closest("input, button, a")) return;
      e.preventDefault();
      playing ? pause() : play(index);
    }
    if (e.key === "ArrowLeft") jump(index - 1);
    if (e.key === "ArrowRight") jump(index + 1);
  });

  document.addEventListener("visibilitychange", () => {
    if (playing && !document.hidden && !wakeLock) {
      navigator.wakeLock?.request("screen").then((lock) => (wakeLock = lock)).catch(() => {});
    }
  });

  showRepeat();
  show(0);
})();
