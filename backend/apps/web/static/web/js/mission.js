// Mission: a spoken role-play with a character (apps/web/mission_views.py).
// The character speaks its line (browser speech, mouth animated meanwhile), the player
// answers by voice (voice.js, with per-word confidence) or text, and the server checks
// the answer against the step and replies with the next one, or the result page at the end.
(() => {
  const configEl = document.getElementById("mission-config");
  if (!configEl) return;

  const config = JSON.parse(configEl.textContent);
  const $ = (id) => document.getElementById(id);
  const scene = $("scene");
  const mouth = $("npc-mouth");
  const micButton = $("mic");
  const micStatus = $("mic-status");
  const textForm = $("text-form");
  const textInput = $("text-answer");

  const MOUTH = {
    closed: "M189 145Q200 150 211 145Q200 147 189 145Z",
    half: "M191 143Q200 154 209 143Q200 146 191 143Z",
    open: "M190 142Q200 160 210 142Q200 145 190 142Z",
    round: "M195 144Q200 156 205 144Q200 140 195 144Z",
    smile: "M185 141Q200 157 215 141Q200 148 185 141Z",
    unsure: "M192 148Q200 144 208 148Q200 147 192 148Z",
  };
  const TALKING = ["half", "open", "round", "half", "closed", "open"];

  let busy = false; // the character speaks or an answer is being checked
  let listening = null; // voice.js session while the microphone is on
  let restingMouth = "closed";

  function setMood(mood) {
    scene.classList.remove("npc-nod", "npc-confused");
    restingMouth = { happy: "smile", confused: "unsure" }[mood] ?? "closed";
    mouth.setAttribute("d", MOUTH[restingMouth]);
    if (mood === "happy") {
      void scene.getBoundingClientRect(); // restart the nod animation
      scene.classList.add("npc-nod");
    }
    if (mood === "confused") scene.classList.add("npc-confused");
  }

  function addLine(who, text, extra = "") {
    const li = document.createElement("li");
    const npc = who === "npc";
    li.className = `max-w-[85%] rounded-xl px-3 py-2 ${npc
      ? "self-start bg-white text-zinc-900 shadow-sm dark:bg-zinc-900 dark:text-zinc-50"
      : "self-end bg-indigo-600 text-white dark:bg-indigo-500"} ${extra}`;
    li.textContent = text;
    $("dialog").append(li);
    li.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  // The character says `text`; the mouth moves until the speech ends.
  async function npcSay(text, translation = "") {
    $("subtitle").classList.remove("hidden");
    $("subtitle-text").textContent = text;
    $("subtitle-ru").textContent = translation;
    addLine("npc", text);
    listening?.setMuted(true);
    let frame = 0;
    const timer = setInterval(() => mouth.setAttribute("d", MOUTH[TALKING[frame++ % TALKING.length]]), 110);
    try {
      await poliglot.speak(text, config.language);
    } finally {
      clearInterval(timer);
      mouth.setAttribute("d", MOUTH[restingMouth]);
      listening?.setMuted(false);
    }
  }

  function setBusy(value) {
    busy = value;
    textForm.querySelectorAll("input, button").forEach((el) => (el.disabled = value));
    if (micButton) micButton.disabled = value;
  }

  function showFeedback(text, ok) {
    const el = $("feedback");
    el.textContent = text;
    el.className = `text-sm ${ok ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`;
  }

  function tickWords(used) {
    document.querySelectorAll("[data-target-word]").forEach((pill) => {
      const done = used.includes(pill.dataset.targetWord);
      pill.classList.toggle("pill-active", done);
      pill.querySelector("[data-tick]").classList.toggle("hidden", !done);
    });
  }

  async function showStep(step) {
    $("goal").textContent = step.goal;
    $("step-index").textContent = step.order;
    $("hint").classList.replace("flex", "hidden");
    setBusy(true);
    await npcSay(step.npc_line, step.npc_line_ru);
    setBusy(false);
    if (!micButton) textInput.focus();
  }

  async function handleReply(reply, answered) {
    tickWords(reply.usedWords ?? []);
    if (reply.passed) document.querySelectorAll(`[data-item="${answered}"]`).forEach((el) => el.classList.remove("is-hidden"));

    if (reply.done) {
      setMood("happy");
      await npcSay(reply.farewell);
      location.href = reply.resultUrl;
      return;
    }
    if (reply.next) {
      if (reply.passed) {
        setMood("happy");
        showFeedback("Понял вас!", true);
      } else {
        setMood(null);
        $("feedback").classList.add("hidden");
      }
      await showStep(reply.next);
      return;
    }

    setMood("confused");
    showFeedback(reply.missing?.length ? "Не совсем то, что нужно. Попробуйте ещё раз." : "Попробуйте сказать это по-другому.", false);
    if (reply.hint !== undefined) {
      $("hint-text").textContent = reply.hint;
      $("hint").classList.replace("hidden", "flex");
    }
    await npcSay(config.retryLine);
    setBusy(false);
  }

  let currentOrder = config.firstStep?.order;

  async function send(body) {
    setBusy(true);
    try {
      const res = await poliglot.postJSON(config.stepUrl, body);
      const reply = await res.json();
      if (!res.ok) throw new Error(reply.detail || "Ошибка сервера.");
      const answered = currentOrder;
      if (reply.next) currentOrder = reply.next.order;
      await handleReply(reply, answered);
    } catch (e) {
      showFeedback(e.message === "Failed to fetch" ? "Нет связи с сервером." : e.message, false);
      setBusy(false);
    }
  }

  function answer(text, words = [], pronunciation = null) {
    if (busy || !text.trim()) return;
    addLine("player", text);
    send({ text, words, pronunciation });
  }

  textForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = textInput.value;
    textInput.value = "";
    answer(text);
  });

  $("skip").addEventListener("click", () => {
    if (busy) return;
    addLine("player", "(шаг пропущен)", "opacity-60");
    send({ skip: true });
  });

  // ---- voice: the microphone listens for one phrase per press ----
  function stopListening() {
    listening?.stop();
  }

  if (micButton) {
    if (!poliglot.voice?.supported()) {
      micButton.disabled = true;
      micStatus.textContent = "Микрофон не поддерживается в этом браузере — отвечайте текстом.";
    }
    micButton.addEventListener("click", async () => {
      if (listening) return stopListening();
      if (busy) return;
      micStatus.textContent = "Слушаю…";
      micButton.setAttribute("aria-pressed", "true");
      try {
        listening = await poliglot.voice.start({
          url: config.voice.url,
          // Learners pause inside a sentence while they look for a word.
          endSilenceMs: 1200,
          onText(text, data) {
            if (!text) return; // only a hint was heard, and it did not reach the goal
            stopListening();
            answer(text, data.words ?? [], data.pronunciation ?? null);
          },
          onStop(error) {
            listening = null;
            micButton.setAttribute("aria-pressed", "false");
            micStatus.textContent = error ? error.message : "Нажмите и скажите ответ";
          },
        });
      } catch (e) {
        listening = null;
        micButton.setAttribute("aria-pressed", "false");
        micStatus.textContent = e.name === "NotAllowedError"
          ? "Нет доступа к микрофону. Разрешите его в настройках браузера."
          : "Не удалось включить микрофон.";
      }
    });
  }

  $("start").addEventListener("click", () => {
    $("start-overlay").remove();
    $("controls").classList.replace("hidden", "flex");
    if (config.firstStep) showStep(config.firstStep);
  });
})();
