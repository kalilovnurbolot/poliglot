// «Времена»: a video game for the front camera. A horizontal escalator carries each word
// (its picture) past three barriers, one per tense; a barrier opens only when that form is
// said right (I eat / I am eating / I will eat). After the last one the word rides off the
// end of the escalator and the next one comes. Camera, escalator and captions are drawn
// on one canvas, which is recorded with the microphone and offered for saving at the end.
// Speech goes to the voice service when it is on (voice.js), otherwise to the browser's
// own recognition. Nothing is saved as progress. The irregular verbs game (verbs_play.html)
// runs the same escalator with a barrier per form: be -> was / were -> been.
(() => {
  const W = 720;
  const H = 1280;
  const BELT_Y = H * 0.7; // top surface of the escalator
  const BELT_HEIGHT = 70;
  const GATES = [0.38, 0.62, 0.86].map((f) => f * W);
  const ARM_LENGTH = 90;
  const STOP_BEFORE = ARM_LENGTH + 70; // the word waits clear of the closed arm
  const ITEM_SPEED = 160; // px per second
  const STEP_WIDTH = 44;
  const ITEM_SIZE = 130;
  const FEEDBACK_MS = 2500;
  const HINT_MS = 4000;
  const END_SCREEN_MS = 1800;
  // Recognition may drop or swap a letter ("im eating"), so close enough counts.
  const ANSWER_SIMILARITY = 0.8;
  const SPEECH_TAIL = 300;
  const SPEECH_LANG = { en: "en-US", de: "de-DE", ru: "ru-RU" };
  const VIDEO_TYPES = [["video/mp4;codecs=avc1", "mp4"], ["video/mp4", "mp4"], ["video/webm;codecs=vp9,opus", "webm"], ["video/webm", "webm"]];

  const $ = (id) => document.getElementById(id);
  const verbs = JSON.parse($("verbs-data").textContent);
  if (!verbs.length) return;
  const language = window.poliglotLanguage;
  const canvas = $("game");
  const ctx = canvas.getContext("2d");
  const status = $("game-status");
  const camera = document.createElement("video");
  camera.muted = true;
  camera.playsInline = true;

  let index = 0;
  let step = 0; // barriers passed by the current word
  let itemX = -ITEM_SIZE;
  let running = false;
  let finishedAt = 0;
  let mistakes = 0;
  let gateOpen = [0, 0, 0];
  let feedback = null; // { text, ok, until }
  let hintUntil = 0;
  let particles = [];
  let media = null; // camera + microphone
  let session = null; // speech recognition
  let recorder = null;
  let recordStart = 0;
  let wakeLock = null;
  let speaking = 0;

  const current = () => verbs[index]?.forms[step];

  // ---- speech ----

  // The microphone also hears the page's own speech, so it is muted while the page talks.
  // Variants ("was / were") are read with a pause instead of "slash".
  function say(text, lang) {
    speaking++;
    session?.setMuted(true);
    return poliglot
      .speak(text.replace(/\s*\/\s*/g, ", "), lang)
      .then(() => new Promise((resolve) => setTimeout(resolve, SPEECH_TAIL)))
      .finally(() => {
        speaking--;
        session?.setMuted(speaking > 0);
      });
  }

  // "I'm eating" and "I'll eat" count as "I am eating" and "I will eat".
  const normalize = (text) =>
    text.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim()
      .replace(/\bi m\b/g, "i am").replace(/\bi ll\b/g, "i will");

  function similarity(a, b) {
    let previous = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i++) {
      const row = [i];
      for (let j = 1; j <= b.length; j++) {
        row[j] = Math.min(previous[j] + 1, row[j - 1] + 1, previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      }
      previous = row;
    }
    return 1 - previous[b.length] / Math.max(a.length, b.length, 1);
  }

  // A form may have variants: "was / were", "learnt / learned"; any of them counts.
  const variants = (expected) => expected.split("/").map(normalize).filter(Boolean);

  function isCorrect(text, expected) {
    const said = normalize(text);
    return variants(expected).some((target) =>
      ` ${said} `.includes(` ${target} `) || similarity(said, target) >= ANSWER_SIMILARITY);
  }

  function burst(x, y) {
    const colors = [palette.accent, palette.success, "#facc15", "#ffffff"];
    for (let i = 0; i < 40; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 150 + Math.random() * 350;
      particles.push({
        x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - 200,
        life: 1, color: colors[i % colors.length],
      });
    }
  }

  function onText(text, { alternative, alternatives = [] } = {}) {
    if (!running || !current()) return;
    const form = current();
    const heard = [text, alternative, ...alternatives].find((candidate) => candidate && isCorrect(candidate, form.text));
    if (heard) {
      navigator.vibrate?.(30);
      feedback = { text: `✓ ${form.text}`, ok: true, until: performance.now() + FEEDBACK_MS };
      burst(GATES[step], BELT_Y - 160);
      step++;
      status.textContent = current() ? `Скажите: ${current().tense}` : "Отлично!";
      return;
    }
    if (!text) return;
    mistakes++;
    navigator.vibrate?.([40, 60, 40]);
    feedback = { text: `✗ «${text}» → ${form.text}`, ok: false, until: performance.now() + FEEDBACK_MS };
    say(form.text, language);
  }

  // ---- microphone: the voice service, or the browser's speech recognition ----
  const voiceConfigEl = $("voice-config");
  const BrowserRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function voiceUrl(base) {
    const params = new URLSearchParams({ language });
    verbs[index]?.forms.flatMap((form) => variants(form.text)).forEach((hint) => params.append("hint", hint));
    return `${base}?${params}`;
  }

  // Same shape as poliglot.voice.start(): { stop(), setMuted(muted) }.
  function startBrowserRecognition({ onStop }) {
    const recognition = new BrowserRecognition();
    recognition.lang = SPEECH_LANG[language] ?? "en-US";
    recognition.continuous = true;
    recognition.maxAlternatives = 3;
    let stopped = false;
    let muted = false;
    const stop = (error = null) => {
      if (stopped) return;
      stopped = true;
      recognition.abort();
      onStop(error);
    };
    recognition.onresult = (e) => {
      const result = e.results[e.results.length - 1];
      if (muted || !result.isFinal) return;
      const [first, ...rest] = Array.from(result, (alternative) => alternative.transcript);
      onText(first, { alternatives: rest });
    };
    recognition.onerror = (e) => {
      if (e.error === "not-allowed") stop(new Error("Нет доступа к микрофону — разрешите его в настройках браузера."));
    };
    // Chrome ends recognition after a pause; keep listening until stopped.
    recognition.onend = () => { if (!stopped) recognition.start(); };
    recognition.start();
    return { stop: () => stop(), setMuted: (value) => (muted = value) };
  }

  function startListening(onStop) {
    if (voiceConfigEl && poliglot.voice?.supported()) {
      const config = JSON.parse(voiceConfigEl.textContent);
      return poliglot.voice.start({ url: () => voiceUrl(config.url), onText, onStop });
    }
    if (BrowserRecognition) return Promise.resolve(startBrowserRecognition({ onStop }));
    return Promise.reject(new Error("Распознавание речи недоступно в этом браузере — откройте сайт в Chrome."));
  }

  // ---- drawing: in the site's palette (accent, zinc neutrals, light or dark theme) ----

  const FONT = '"Geist", ui-sans-serif, system-ui, sans-serif';
  const font = (weight, size) => `${weight} ${size}px ${FONT}`;
  let palette = {};

  // Theme colors as the page resolves them: the accent may be the learner's own color
  // (theme.js), which canvas cannot read from the CSS variable directly.
  function readPalette() {
    const root = document.documentElement;
    const dark = root.dataset.theme === "dark"
      || (root.dataset.theme !== "light" && matchMedia("(prefers-color-scheme: dark)").matches);
    const probe = document.createElement("span");
    document.body.append(probe);
    const color = (name, fallback) => {
      probe.style.color = "";
      probe.style.color = `var(--${name}, ${fallback})`;
      return getComputedStyle(probe).color;
    };
    palette = {
      dark,
      background: color("background", dark ? "#09090b" : "#fafafa"),
      surface: dark ? color("color-zinc-900", "#18181b") : "#ffffff",
      line: dark ? color("color-zinc-800", "#27272a") : color("color-zinc-200", "#e4e4e7"),
      text: dark ? color("color-zinc-50", "#fafafa") : color("color-zinc-900", "#18181b"),
      muted: color("color-zinc-500", "#71717a"),
      accent: dark ? color("color-indigo-500", "#6366f1") : color("color-indigo-600", "#4f46e5"),
      success: color("color-emerald-600", "#059669"),
      danger: color("color-red-600", "#dc2626"),
      belt: [color("color-zinc-300", "#d4d4d8"), color("color-zinc-400", "#a1a1aa"), color("color-zinc-600", "#52525b")],
      rail: color("color-zinc-800", "#27272a"),
      post: color("color-zinc-400", "#a1a1aa"),
    };
    probe.remove();
  }
  readPalette();
  new MutationObserver(readPalette).observe(document.documentElement, { attributes: true });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", readPalette);

  function card(x, y, width, height, radius, { fill = palette.surface, stroke = palette.line, alpha = 1 } = {}) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.shadowColor = "rgba(0, 0, 0, 0.12)";
    ctx.shadowBlur = 24;
    ctx.shadowOffsetY = 6;
    ctx.fillStyle = fill;
    ctx.beginPath();
    ctx.roundRect(x, y, width, height, radius);
    ctx.fill();
    ctx.shadowColor = "transparent";
    if (stroke) {
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.restore();
  }

  function pill(text, x, y, { size = 26, weight = 600, fill = palette.surface, color = palette.text, stroke = palette.line } = {}) {
    ctx.font = font(weight, size);
    const padding = size * 0.7;
    const width = ctx.measureText(text).width + padding * 2;
    const height = size + padding;
    card(x - width / 2, y - height / 2, width, height, height / 2, { fill, stroke });
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x, y + 1);
  }

  function drawBackground() {
    if (camera.readyState >= 2) {
      // Cover the canvas, mirrored like a selfie.
      const scale = Math.max(W / camera.videoWidth, H / camera.videoHeight);
      const w = camera.videoWidth * scale;
      const h = camera.videoHeight * scale;
      ctx.save();
      ctx.translate(W, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(camera, (W - w) / 2, (H - h) / 2, w, h);
      ctx.restore();
      return;
    }
    ctx.fillStyle = palette.background;
    ctx.fillRect(0, 0, W, H);
    // A soft accent glow, like the hover tint of the site's cards.
    const glow = ctx.createRadialGradient(W / 2, BELT_Y - 150, 0, W / 2, BELT_Y - 150, W);
    glow.addColorStop(0, palette.accent);
    glow.addColorStop(1, "transparent");
    ctx.save();
    ctx.globalAlpha = palette.dark ? 0.18 : 0.1;
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }

  function drawEscalator(time) {
    // Glass side panel and handrail behind the word.
    ctx.save();
    ctx.globalAlpha = 0.1;
    ctx.fillStyle = palette.accent;
    ctx.fillRect(0, BELT_Y - 110, W, 110);
    ctx.restore();
    ctx.strokeStyle = palette.rail;
    ctx.lineWidth = 12;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(0, BELT_Y - 110);
    ctx.lineTo(W, BELT_Y - 110);
    ctx.stroke();

    // Body with moving steps; the edge is in the accent color.
    const [top, middle, bottom] = palette.belt;
    const body = ctx.createLinearGradient(0, BELT_Y, 0, BELT_Y + BELT_HEIGHT);
    body.addColorStop(0, top);
    body.addColorStop(0.3, middle);
    body.addColorStop(1, bottom);
    ctx.fillStyle = body;
    ctx.fillRect(0, BELT_Y, W, BELT_HEIGHT);
    const offset = ((time / 1000) * ITEM_SPEED) % STEP_WIDTH;
    ctx.strokeStyle = bottom;
    ctx.lineWidth = 3;
    for (let x = offset - STEP_WIDTH; x < W; x += STEP_WIDTH) {
      ctx.beginPath();
      ctx.moveTo(x, BELT_Y + 8);
      ctx.lineTo(x, BELT_Y + BELT_HEIGHT);
      ctx.stroke();
    }
    ctx.fillStyle = palette.accent;
    ctx.fillRect(0, BELT_Y, W, 6);
  }

  function drawGates(time) {
    GATES.forEach((x, i) => {
      gateOpen[i] += ((i < step ? 1 : 0) - gateOpen[i]) * 0.15;
      const passed = i < step;
      const active = i === step && running;
      ctx.fillStyle = passed ? palette.success : palette.post;
      ctx.beginPath();
      ctx.roundRect(x - 7, BELT_Y - 150, 14, 150, 7);
      ctx.fill();
      // Arm swings up as it opens.
      ctx.save();
      ctx.translate(x, BELT_Y - 130);
      ctx.rotate((gateOpen[i] * Math.PI) / 2);
      ctx.beginPath();
      ctx.roundRect(-ARM_LENGTH, -9, ARM_LENGTH, 18, 9);
      ctx.save();
      ctx.clip();
      for (let s = 0; s < ARM_LENGTH; s += 30) {
        ctx.fillStyle = passed ? palette.success : (s / 30) % 2 ? "#ffffff" : palette.accent;
        ctx.fillRect(-s - 30, -9, 30, 18);
      }
      ctx.restore();
      ctx.restore();
      // Tense name above the barrier.
      const { short } = verbs[index]?.forms[i] ?? verbs[0].forms[i];
      const pulse = active ? 1 + Math.sin(time / 200) * 0.04 : 1;
      ctx.save();
      ctx.translate(x, BELT_Y - (i % 2 ? 235 : 190)); // staggered so neighbours never overlap
      ctx.scale(pulse, pulse);
      pill(passed ? `✓ ${short}` : short, 0, 0, {
        size: 22,
        weight: 600,
        fill: passed ? palette.success : active ? palette.accent : palette.surface,
        color: passed || active ? "#ffffff" : palette.muted,
        stroke: passed || active ? null : palette.line,
      });
      ctx.restore();
    });
  }

  function drawItem(time) {
    const verb = verbs[index];
    if (!verb) return;
    // The word fades out as it rides off the end of the escalator.
    const alpha = Math.max(0, Math.min(1, (W + ITEM_SIZE / 2 - itemX) / (ITEM_SIZE * 1.5)));
    const waiting = step < 3 && itemX >= GATES[step] - STOP_BEFORE;
    const bob = waiting ? Math.sin(time / 150) * 4 : Math.sin(time / 300) * 2;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.font = `${ITEM_SIZE}px "Apple Color Emoji", "Segoe UI Emoji", ${FONT}`;
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText(verb.emoji, itemX, BELT_Y + 18 + bob);
    ctx.restore();
  }

  function drawCaptions(time) {
    const verb = verbs[index];
    ctx.textAlign = "center";
    ctx.textBaseline = "alphabetic";
    pill("Полиглот", W / 2, 56, { size: 20, color: palette.accent });

    // Top: the word being learned, on a card like the listen page's.
    if (verb) {
      card(48, 100, W - 96, 200, 32, { alpha: 0.95 });
      ctx.textAlign = "center";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = palette.muted;
      ctx.font = font(500, 22);
      ctx.fillText(`${index + 1} / ${verbs.length}`, W / 2, 145);
      ctx.fillStyle = palette.text;
      ctx.font = font(600, 56);
      ctx.fillText(verb.text, W / 2, 212);
      ctx.fillStyle = palette.accent;
      ctx.font = font(500, 32);
      ctx.fillText(verb.translation, W / 2, 265);
    }

    // What to say now, or the hint.
    if (running && current()) {
      const { tense, hint, text } = current();
      const showHint = time < hintUntil;
      pill(showHint ? text : `Скажите: ${tense} · ${hint}`, W / 2, BELT_Y - 330, {
        size: 26, color: showHint ? palette.accent : palette.text,
      });
    }
    if (feedback && time < feedback.until) {
      pill(feedback.text, W / 2, BELT_Y + BELT_HEIGHT + 70, {
        size: 28, fill: feedback.ok ? palette.success : palette.danger, color: "#ffffff", stroke: null,
      });
    }

    if (recorder?.state === "recording") {
      const seconds = Math.floor((time - recordStart) / 1000);
      card(W - 150, 34, 112, 44, 22);
      ctx.fillStyle = Math.floor(time / 500) % 2 ? palette.danger : palette.line;
      ctx.beginPath();
      ctx.arc(W - 124, 56, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = palette.text;
      ctx.font = font(600, 22);
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(`${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`, W - 108, 57);
    }

    if (finishedAt) {
      ctx.save();
      ctx.globalAlpha = 0.7;
      ctx.fillStyle = palette.background;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
      card(60, H / 2 - 200, W - 120, 360, 32);
      ctx.textAlign = "center";
      ctx.textBaseline = "alphabetic";
      ctx.font = `120px "Apple Color Emoji", "Segoe UI Emoji", ${FONT}`;
      ctx.fillText("🏆", W / 2, H / 2 - 40);
      ctx.fillStyle = palette.text;
      ctx.font = font(600, 44);
      ctx.fillText("Все шлагбаумы пройдены!", W / 2, H / 2 + 50);
      ctx.fillStyle = palette.muted;
      ctx.font = font(500, 28);
      ctx.fillText(`Слов: ${verbs.length} · ошибок: ${mistakes}`, W / 2, H / 2 + 105);
    }
  }

  function drawParticles(dt) {
    particles = particles.filter((p) => (p.life -= dt * 1.2) > 0);
    for (const p of particles) {
      p.vy += 900 * dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x - 5, p.y - 5, 10, 10);
    }
    ctx.globalAlpha = 1;
  }

  function update(dt) {
    if (!running || !verbs[index]) return;
    const target = step < 3 ? GATES[step] - STOP_BEFORE : W + ITEM_SIZE;
    itemX = Math.min(target, itemX + ITEM_SPEED * dt);
    if (step === 3 && itemX >= W + ITEM_SIZE) {
      index++;
      step = 0;
      itemX = -ITEM_SIZE;
      gateOpen = [0, 0, 0];
      hintUntil = 0;
      if (verbs[index]) {
        status.textContent = `Скажите: ${current().tense}`;
        say(verbs[index].text, language);
      } else {
        finish();
      }
    }
  }

  let last = performance.now();
  function frame(time) {
    const dt = Math.min(0.05, (time - last) / 1000);
    last = time;
    update(dt);
    drawBackground();
    drawEscalator(running ? time : 0);
    drawGates(time);
    drawItem(time);
    drawParticles(dt);
    drawCaptions(time);
    requestAnimationFrame(frame);
  }

  // ---- recording ----

  function startRecording() {
    if (!window.MediaRecorder || !canvas.captureStream) return;
    const stream = canvas.captureStream(30);
    media?.getAudioTracks().forEach((track) => stream.addTrack(track));
    const [mimeType, extension] = VIDEO_TYPES.find(([type]) => MediaRecorder.isTypeSupported(type)) ?? ["", "webm"];
    const chunks = [];
    recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
    recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    recorder.onstop = () => showVideo(new Blob(chunks, { type: recorder.mimeType || mimeType }), extension);
    recorder.start(1000);
    recordStart = performance.now();
  }

  function showVideo(blob, extension) {
    const url = URL.createObjectURL(blob);
    const name = `poliglot-${new Date().toISOString().slice(0, 10)}.${extension}`;
    $("game-video").src = url;
    $("game-save").href = url;
    $("game-save").download = name;
    $("game-summary").textContent = `Слов: ${index} из ${verbs.length} · ошибок: ${mistakes}`;
    const file = new File([blob], name, { type: blob.type });
    if (navigator.canShare?.({ files: [file] })) {
      const share = $("game-share");
      share.classList.remove("hidden");
      share.addEventListener("click", () => navigator.share({ files: [file] }).catch(() => {}));
    }
    $("game-result").classList.replace("hidden", "flex");
  }

  function setRecording(recording) {
    const button = $("game-record");
    button.classList.toggle("btn-primary", !recording);
    button.classList.toggle("btn-secondary", recording);
    $("game-record-label").textContent = recording ? "Остановить запись" : "Начать запись";
    $("game-mode").classList.toggle("invisible", recording);
  }

  function stopAll() {
    running = false;
    session?.stop();
    media?.getTracks().forEach((track) => track.stop());
    wakeLock?.release().catch(() => {});
    wakeLock = null;
    setRecording(false);
    $("game-record").disabled = true; // one recording per page; «Ещё раз» starts over
    if (recorder?.state === "recording") recorder.stop();
  }

  // The end screen is drawn for a moment first, so it is in the video too.
  function finish() {
    running = false;
    finishedAt = performance.now();
    status.textContent = "";
    say("Отлично! Все шлагбаумы пройдены.", "ru");
    setTimeout(stopAll, END_SCREEN_MS);
  }

  // The camera is the video's background when there is one; without it the game is
  // recorded on the plain background. Returns { stream, note }, never throws.
  async function openCamera() {
    if (!navigator.mediaDevices?.getUserMedia) return { stream: null, note: "Камера недоступна в этом браузере — запись без неё." };
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: true })
      .catch(() => navigator.mediaDevices.getUserMedia({ audio: true }))
      .catch(() => null);
    const [track] = stream?.getVideoTracks() ?? [];
    if (!track) return { stream, note: "Камера не найдена — запись без неё." };
    // Unplugged or taken by another app mid-game: go on with the plain background.
    track.addEventListener("ended", () => (camera.srcObject = null));
    camera.srcObject = stream;
    await camera.play().catch(() => {});
    return { stream, note: "" };
  }

  async function start() {
    const button = $("game-record");
    button.disabled = true;
    // Spoken inside the click: mobile browsers only allow speech that starts from a gesture.
    const intro = say(verbs[index].text, language);
    try {
      const { stream, note } = await openCamera();
      media = stream;
      session = await startListening((error) => {
        session = null;
        if (error && running) {
          status.textContent = error.message;
          stopAll();
        }
      });
      session.setMuted(speaking > 0);
      startRecording();
      running = true;
      setRecording(true);
      status.textContent = `${note ? `${note} ` : ""}Скажите: ${current().tense}`;
      // A locked phone stops the camera and the microphone.
      wakeLock = await navigator.wakeLock?.request("screen").catch(() => null);
      await intro;
    } catch (e) {
      window.speechSynthesis?.cancel();
      media?.getTracks().forEach((track) => track.stop());
      media = null;
      camera.srcObject = null;
      session?.stop();
      session = null;
      status.textContent = e.name === "NotAllowedError"
        ? "Нет доступа к микрофону — разрешите его в настройках браузера."
        : e.message || "Не удалось включить микрофон.";
    } finally {
      button.disabled = false;
    }
  }

  $("game-record").addEventListener("click", () => {
    if (running) return stopAll();
    if (!finishedAt && !recorder) start();
  });
  $("game-listen").addEventListener("click", () => current() && say(current().text, language));
  $("game-hint").addEventListener("click", () => (hintUntil = performance.now() + HINT_MS));

  document.addEventListener("visibilitychange", async () => {
    if (running && !document.hidden && !wakeLock) {
      wakeLock = await navigator.wakeLock?.request("screen").catch(() => null);
    }
  });

  status.textContent = "Нажмите запись и произнесите каждую форму у шлагбаума, чтобы он открылся";
  requestAnimationFrame(frame);
})();
