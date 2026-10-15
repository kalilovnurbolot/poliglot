// Multiple-choice quiz. Each answer is reported to /api/review/answer/
// (right = correct, left = wrong), so it feeds the same SRS progress as flashcards.
(() => {
  const dataEl = document.getElementById("quiz-data");
  if (!dataEl) return;

  const config = window.poliglotQuiz;
  const questions = JSON.parse(dataEl.textContent);
  let mode = config.mode;
  let index = 0;
  let answered = false;
  const score = { correct: 0, wrong: 0 };

  const q = (name) => document.querySelectorAll(`[data-quiz="${name}"]`);
  const setText = (name, value) => q(name).forEach((el) => (el.textContent = value));
  const optionsEl = document.getElementById("quiz-options");
  const speakButton = document.getElementById("quiz-speak");
  const wordEl = document.getElementById("quiz-word");

  const speak = (text) => poliglot.speak(text, config.language);

  const OPTION_BASE = "rounded-lg border px-4 py-2 text-left transition-colors";
  const OPTION_IDLE = "border-zinc-300 hover:border-indigo-400 dark:border-zinc-700 dark:hover:border-indigo-500";
  const OPTION_CORRECT = "border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10";
  const OPTION_WRONG = "border-red-500 bg-red-50 dark:bg-red-500/10";

  function applyMode() {
    const listening = mode === "listening";
    wordEl.classList.toggle("hidden", listening);
    speakButton.classList.toggle("hidden", !listening);
    speakButton.classList.toggle("flex", listening);
    document.querySelectorAll("[data-mode]").forEach((b) => b.classList.toggle("pill-active", b.dataset.mode === mode));
    // Keep the mode in the URL so level links and «ещё раз» remember it.
    const url = new URL(location.href);
    url.searchParams.set("mode", mode);
    history.replaceState(null, "", url);
    document.getElementById("quiz-restart").href = url.pathname + url.search;
    document.querySelectorAll("a.pill").forEach((a) => {
      const link = new URL(a.href);
      link.searchParams.set("mode", mode);
      a.href = link.pathname + link.search;
    });
  }

  function render() {
    const current = questions[index];
    if (!current) {
      document.getElementById("quiz-card").classList.add("hidden");
      document.getElementById("quiz-progress").classList.add("hidden");
      const done = document.getElementById("quiz-done");
      done.classList.remove("hidden");
      done.classList.add("flex");
      return;
    }

    answered = false;
    setText("index", index + 1);
    setText("text", current.word.text);
    setText("transcription", current.word.transcription);

    optionsEl.replaceChildren(
      ...current.options.map((option) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `${OPTION_BASE} ${OPTION_IDLE}`;
        button.textContent = option;
        button.addEventListener("click", () => select(button, option));
        return button;
      }),
    );

    if (mode === "listening") speak(current.word.text);
  }

  function select(button, option) {
    if (answered) return;
    answered = true;
    const current = questions[index];
    const correct = option === current.word.translation;

    for (const b of optionsEl.children) {
      b.disabled = true;
      if (b.textContent === current.word.translation) b.className = `${OPTION_BASE} ${OPTION_CORRECT}`;
    }
    if (!correct) button.className = `${OPTION_BASE} ${OPTION_WRONG}`;

    score[correct ? "correct" : "wrong"]++;
    setText("correct", score.correct);
    setText("wrong", score.wrong);
    poliglot.postJSON(config.answerUrl, { word: current.word.id, direction: correct ? "right" : "left" }).catch(() => {});

    setTimeout(() => {
      index++;
      render();
    }, 900);
  }

  document.querySelectorAll("[data-mode]").forEach((b) =>
    b.addEventListener("click", () => {
      mode = b.dataset.mode;
      applyMode();
      if (mode === "listening" && questions[index] && !answered) speak(questions[index].word.text);
    }),
  );
  speakButton.addEventListener("click", () => questions[index] && speak(questions[index].word.text));

  applyMode();
  render();
})();
