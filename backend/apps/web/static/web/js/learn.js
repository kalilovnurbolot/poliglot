// Flashcard session: drag (or arrow keys) right = знаю, left = не знаю,
// up = в избранное, down = пропустить (card goes to the back of the queue).
// With the voice service on, the same actions can be spoken (see VOICE_COMMANDS),
// or the learner just says the translation and it is checked (see isCorrectAnswer).
// Everything is also spoken aloud, so a session can be done in headphones without
// looking at the screen.
(() => {
  const EXIT_DISTANCE = 600;
  const SWIPE_THRESHOLD = 100;
  const DRAG_ELASTIC = 0.6;

  const EXIT_OFFSET = {
    right: { x: EXIT_DISTANCE, y: 0, rotate: 20 },
    left: { x: -EXIT_DISTANCE, y: 0, rotate: -20 },
    up: { x: 0, y: -EXIT_DISTANCE, rotate: 0 },
    down: { x: 0, y: EXIT_DISTANCE, rotate: 0 },
  };
  const DIRECTION_LABEL = { right: "Знаю", left: "Не знаю", up: "В избранное", down: "Пропустить" };
  const DIRECTION_COLOR = { right: "bg-emerald-600", left: "bg-red-600", up: "bg-amber-500", down: "bg-zinc-600" };
  const KEY_TO_DIRECTION = { ArrowRight: "right", ArrowLeft: "left", ArrowUp: "up", ArrowDown: "down" };
  // Checked in order, so longer phrases come first ("не знаю" before "знаю",
  // "озвучь перевод" before "озвучь").
  const VOICE_COMMANDS = [
    ["не знаю", "left"],
    ["знаю", "right"],
    ["в избранное", "up"],
    ["избранное", "up"],
    ["дальше", "down"],
    ["пропусти", "down"],
    ["пропустить", "down"],
    ["скажи перевод", "speak-translation"],
    ["озвучь перевод", "speak-translation"],
    ["прочитай перевод", "speak-translation"],
    ["переверни", "flip"],
    ["перевод", "flip"],
    ["повтори", "speak"],
    ["озвучь", "speak"],
  ];
  // Spoken translations may differ from the stored one by an ending ("доверия" for
  // "доверие") or a misheard letter, so close enough counts as correct.
  const ANSWER_SIMILARITY = 0.75;
  // Extra pause after the page stops talking before the microphone is heard again.
  const SPEECH_TAIL = 300;

  const $ = (id) => document.getElementById(id);
  const card = $("flashcard");
  const hint = $("card-hint");
  const front = $("card-front");
  const back = $("card-back");

  let queue = JSON.parse($("cards-data").textContent);
  const stats = { known: 0, unknown: 0, favorited: 0 };
  let flipped = false;
  let animating = false;

  function setTransform(x, y, rotate, transition) {
    card.style.transition = transition || "none";
    card.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg)`;
  }

  function showHint(direction) {
    hint.className = "absolute top-3 rounded-full px-3 py-1 text-xs font-medium text-white";
    if (!direction) return hint.classList.add("hidden");
    hint.classList.add(DIRECTION_COLOR[direction]);
    hint.textContent = DIRECTION_LABEL[direction];
  }

  function setFlipped(value) {
    flipped = value;
    front.classList.toggle("hidden", flipped);
    front.classList.toggle("flex", !flipped);
    back.classList.toggle("hidden", !flipped);
    back.classList.toggle("flex", flipped);
  }

  function sizeClass(length, steps) {
    return steps.find(([limit]) => length > limit)?.[1] ?? steps[steps.length - 1][1];
  }

  function render() {
    if (queue.length === 0) {
      if (voiceSession) say("На сегодня всё. Отличная работа!", "ru").then(() => voiceSession?.stop());
      $("voice-panel").classList.replace("flex", "hidden");
      $("learn-stage").classList.add("hidden");
      const done = $("learn-done");
      done.classList.remove("hidden");
      done.classList.add("flex");
      for (const [key, value] of Object.entries(stats)) {
        done.querySelector(`[data-stat="${key}"]`).textContent = value;
      }
      return;
    }

    const { word } = queue[0];
    const text = $("card-text");
    text.textContent = word.text;
    text.classList.remove("text-lg", "text-2xl", "text-3xl");
    text.classList.add(sizeClass(word.text.length, [[40, "text-lg"], [20, "text-2xl"], [-1, "text-3xl"]]));

    $("card-transcription").textContent = word.transcription;
    $("card-transcription").classList.toggle("hidden", !word.transcription);
    $("card-pos").textContent = word.part_of_speech;
    $("card-level").textContent = word.level;

    const translation = $("card-translation");
    translation.textContent = word.translation;
    translation.classList.remove("text-lg", "text-2xl");
    translation.classList.add(word.translation.length > 30 ? "text-lg" : "text-2xl");
    $("card-example").textContent = word.example_sentence ? `«${word.example_sentence}»` : "";

    setFlipped(false);
    showHint(null);
    card.style.opacity = "1";
    setTransform(0, 0, 0);
    if (voiceSession) say(word.text, window.poliglotLanguage);
  }

  function showError(message) {
    const el = $("learn-error");
    el.textContent = message;
    el.classList.remove("hidden");
  }

  function handleSwipe(direction) {
    const [current, ...rest] = queue;
    if (direction === "down") {
      queue = [...rest, current];
    } else {
      poliglot
        .postJSON(window.poliglotAnswerUrl, { word: current.word.id, direction })
        .then((res) => { if (!res.ok) throw new Error(); })
        .catch(() => showError("Ответ не сохранился — проверьте соединение."));
      if (direction === "right") stats.known++;
      if (direction === "left") stats.unknown++;
      if (direction === "up") stats.favorited++;
      queue = rest;
    }
    render();
  }

  function swipe(direction) {
    if (animating || queue.length === 0) return;
    animating = true;
    showHint(direction);
    const { x, y, rotate } = EXIT_OFFSET[direction];
    card.style.opacity = "0";
    setTransform(x, y, rotate, "transform 0.25s ease-in, opacity 0.25s ease-in");
    setTimeout(() => {
      animating = false;
      handleSwipe(direction);
    }, 250);
  }

  function directionOf(dx, dy, threshold) {
    if (Math.abs(dx) > Math.abs(dy)) {
      if (dx > threshold) return "right";
      if (dx < -threshold) return "left";
    } else {
      if (dy < -threshold) return "up";
      if (dy > threshold) return "down";
    }
    return null;
  }

  // ---- drag ----
  let start = null;
  let moved = false;

  card.addEventListener("pointerdown", (e) => {
    if (animating) return;
    start = { x: e.clientX, y: e.clientY };
    moved = false;
    card.setPointerCapture(e.pointerId);
    card.classList.replace("cursor-grab", "cursor-grabbing");
  });

  card.addEventListener("pointermove", (e) => {
    if (!start) return;
    const dx = e.clientX - start.x;
    const dy = e.clientY - start.y;
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) moved = true;
    setTransform(dx * DRAG_ELASTIC, dy * DRAG_ELASTIC, (dx * DRAG_ELASTIC) / 20);
    showHint(Math.abs(dx) < 20 && Math.abs(dy) < 20 ? null : directionOf(dx, dy, 0));
  });

  function endDrag(e) {
    if (!start) return;
    const dx = e.clientX - start.x;
    const dy = e.clientY - start.y;
    start = null;
    card.classList.replace("cursor-grabbing", "cursor-grab");

    if (!moved) {
      setTransform(0, 0, 0);
      return setFlipped(!flipped);
    }
    const direction = directionOf(dx, dy, SWIPE_THRESHOLD);
    if (direction) return swipe(direction);
    showHint(null);
    setTransform(0, 0, 0, "transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)");
  }

  card.addEventListener("pointerup", endDrag);
  card.addEventListener("pointercancel", endDrag);

  window.addEventListener("keydown", (e) => {
    const direction = KEY_TO_DIRECTION[e.key];
    if (direction) {
      e.preventDefault();
      swipe(direction);
    }
  });

  // ---- voice ----
  const voiceConfigEl = $("voice-config");
  const micButton = $("voice-toggle");
  const voiceStatus = $("voice-status");
  let voiceSession = null;
  let wakeLock = null;
  let speaking = 0;

  // The microphone also hears the page's own speech (without headphones), so audio is
  // muted while it talks — otherwise "Правильно: коза" would count as the learner's answer.
  function say(text, language) {
    speaking++;
    voiceSession?.setMuted(true);
    return poliglot
      .speak(text, language)
      .then(() => new Promise((resolve) => setTimeout(resolve, SPEECH_TAIL)))
      .finally(() => {
        speaking--;
        voiceSession?.setMuted(speaking > 0);
      });
  }

  const normalize = (text) =>
    text.toLowerCase().replace(/ё/g, "е").replace(/[^\p{L}\p{N}]+/gu, " ").trim();

  // Each comma-separated variant counts ("тот, та, то"). Brackets mark optional parts:
  // "(Нас) зовут ..." -> full "нас зовут" or short "зовут"; "прятать(ся)" -> "прятаться"/"прятать".
  function answerVariants(translation) {
    return translation
      .split(/[,;/]/)
      .map((part) => ({ full: normalize(part.replace(/[()]/g, "")), short: normalize(part.replace(/\([^)]*\)/g, " ")) }))
      .filter(({ full }) => full);
  }

  function similarity(a, b) {
    let previous = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i++) {
      const current = [i];
      for (let j = 1; j <= b.length; j++) {
        current[j] = Math.min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      }
      previous = current;
    }
    return 1 - previous[b.length] / Math.max(a.length, b.length, 1);
  }

  // A longer phrase may contain the answer ("это коза"), but only the full form: otherwise
  // "меня зовут" would pass for "(Нас) зовут" through its short form "зовут".
  function isCorrectAnswer(text, translation) {
    const said = normalize(text);
    return answerVariants(translation).some(({ full, short }) =>
      ` ${said} `.includes(` ${full} `) ||
      [full, short].some((variant) => variant && similarity(said, variant) >= ANSWER_SIMILARITY));
  }

  // Say something about the current card, then swipe it — unless it was already
  // swiped some other way in the meantime.
  let revealing = false;
  async function sayThenSwipe(text, direction) {
    const current = queue[0];
    revealing = true;
    setFlipped(true);
    await say(text, "ru");
    revealing = false;
    if (queue[0] === current) swipe(direction);
  }

  function runVoiceCommand(text) {
    if (queue.length === 0 || revealing) return;
    const { word } = queue[0];
    if (isCorrectAnswer(text, word.translation)) {
      voiceStatus.textContent = `✓ Верно: «${text}»`;
      return sayThenSwipe("Верно!", "right");
    }

    const match = VOICE_COMMANDS.find(([phrase]) => ` ${normalize(text)} `.includes(` ${phrase} `));
    if (!match) {
      voiceStatus.textContent = `✗ Вы сказали «${text}». Попробуйте ещё раз или скажите «не знаю»`;
      return say(`Нет, вы сказали: ${text}. Попробуйте ещё раз.`, "ru").then(() => {
        if (queue[0]?.word === word) say(word.text, window.poliglotLanguage);
      });
    }
    voiceStatus.textContent = `«${text}»`;
    const action = match[1];
    if (action === "left") return sayThenSwipe(`Перевод: ${word.translation}`, "left");
    if (action === "speak") return say(word.text, window.poliglotLanguage);
    if (action === "speak-translation" || (action === "flip" && !flipped)) {
      setFlipped(true);
      return say(word.translation, "ru");
    }
    if (action === "flip") {
      setFlipped(false);
      return say(word.text, window.poliglotLanguage);
    }
    swipe(action);
  }

  function setListening(listening) {
    micButton.classList.toggle("btn-primary", listening);
    micButton.classList.toggle("btn-secondary", !listening);
    micButton.setAttribute("aria-pressed", String(listening));
    micButton.textContent = listening ? "🎙 Слушаю… (выключить)" : "🎤 Голосовое управление";
  }

  if (voiceConfigEl && poliglot.voice?.supported()) {
    const config = JSON.parse(voiceConfigEl.textContent);
    $("voice-panel").classList.replace("hidden", "flex");

    micButton.addEventListener("click", async () => {
      if (voiceSession) return voiceSession.stop();
      micButton.disabled = true;
      voiceStatus.textContent = "Назовите перевод или скажите «не знаю». Ещё: «знаю», «в избранное», «дальше», «переверни», «повтори», «скажи перевод»";
      // Spoken right away, inside the click: mobile browsers only allow speech that
      // starts from a user gesture.
      const intro = say("Назовите перевод слова.", "ru");
      try {
        voiceSession = await poliglot.voice.start({
          url: config.url,
          token: config.token,
          grammar: null,
          onText: runVoiceCommand,
          onStop: (error) => {
            voiceSession = null;
            wakeLock?.release().catch(() => {});
            wakeLock = null;
            setListening(false);
            voiceStatus.textContent = error ? error.message : "";
            if (error) say(error.message, "ru");
          },
        });
        voiceSession.setMuted(speaking > 0);
        setListening(true);
        // Keep the phone screen on: a locked phone stops the microphone.
        wakeLock = await navigator.wakeLock?.request("screen").catch(() => null);
        await intro;
        if (voiceSession && queue.length) say(queue[0].word.text, window.poliglotLanguage);
      } catch (e) {
        voiceStatus.textContent = e.name === "NotAllowedError"
          ? "Нет доступа к микрофону — разрешите его в настройках браузера."
          : e.message || "Не удалось включить микрофон.";
      } finally {
        micButton.disabled = false;
      }
    });

    // The screen lock is dropped whenever the tab is hidden; take it again on return.
    document.addEventListener("visibilitychange", async () => {
      if (voiceSession && !document.hidden && !wakeLock) {
        wakeLock = await navigator.wakeLock?.request("screen").catch(() => null);
      }
    });
  }

  render();
})();
