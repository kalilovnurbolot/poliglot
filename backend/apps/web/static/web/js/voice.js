// Voice control: listens to the microphone, cuts it into phrases by loudness and posts
// each phrase to Django (apps/web/voice.py), which recognizes it via the voice service.
// Plain same-origin requests, so it works wherever the site works (HTTP or HTTPS).
(() => {
  const WORKLET_URL = document.currentScript.dataset.worklet;
  const CHUNK_MS = 100; // voice-worklet.js posts 100 ms chunks
  const PRE_ROLL_CHUNKS = 3; // keep the start of a word that began before the level rose
  const END_SILENCE_MS = 700; // this much quiet ends a phrase
  const MAX_PHRASE_MS = 8000;
  const MIN_VOICED_MS = 200; // shorter bursts (a click, a cough) are ignored
  const MIN_LEVEL = 0.015;

  function level(chunk) {
    let sum = 0;
    for (const sample of chunk) sum += sample * sample;
    return Math.sqrt(sum / chunk.length) / 0x8000;
  }

  function concat(chunks) {
    const result = new Int16Array(chunks.reduce((n, c) => n + c.length, 0));
    let offset = 0;
    for (const chunk of chunks) {
      result.set(chunk, offset);
      offset += chunk.length;
    }
    return result;
  }

  window.poliglot.voice = {
    supported() {
      return Boolean(navigator.mediaDevices?.getUserMedia && window.AudioWorkletNode);
    },

    // Resolves with { stop(), setMuted(muted) } once the microphone is on. While muted
    // the microphone is ignored, e.g. so the page's own speech is not heard.
    // onStop(error) fires when listening ends: error is null after a normal stop().
    async start({ url, onText, onStop }) {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
      });
      const context = new AudioContext();
      let stopped = false;
      let muted = false;

      function stop(error = null) {
        if (stopped) return;
        stopped = true;
        stream.getTracks().forEach((track) => track.stop());
        context.close();
        onStop?.(error);
      }

      try {
        await context.audioWorklet.addModule(WORKLET_URL);
      } catch (e) {
        stop(e);
        throw e;
      }
      const node = new AudioWorkletNode(context, "pcm-downsampler");
      context.createMediaStreamSource(stream).connect(node);

      async function send(pcm) {
        try {
          const res = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/octet-stream", "X-CSRFToken": poliglot.csrfToken() },
            body: pcm,
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok) throw new Error(data.detail || "Не удалось распознать речь.");
          if (data.text && !stopped && !muted) onText(data.text);
        } catch (e) {
          stop(e instanceof TypeError ? new Error("Нет связи с сервером.") : e);
        }
      }

      // Phrase detection: the noise floor follows the quiet level of the room, and a
      // phrase lasts from the first loud chunk until END_SILENCE_MS of quiet.
      let noise = MIN_LEVEL / 2;
      let preRoll = [];
      let phrase = null;

      node.port.onmessage = (e) => {
        if (stopped) return;
        if (muted) {
          phrase = null;
          preRoll = [];
          return;
        }
        const chunk = new Int16Array(e.data);
        const value = level(chunk);
        const loud = value > Math.max(noise * 3, MIN_LEVEL);

        if (!phrase) {
          if (!loud) noise = noise * 0.95 + value * 0.05;
          preRoll.push(chunk);
          if (preRoll.length > PRE_ROLL_CHUNKS) preRoll.shift();
          if (loud) {
            phrase = { chunks: preRoll, voicedMs: CHUNK_MS, silentMs: 0 };
            preRoll = [];
          }
          return;
        }

        phrase.chunks.push(chunk);
        if (loud) {
          phrase.voicedMs += CHUNK_MS;
          phrase.silentMs = 0;
        } else {
          phrase.silentMs += CHUNK_MS;
        }
        if (phrase.silentMs >= END_SILENCE_MS || phrase.chunks.length * CHUNK_MS >= MAX_PHRASE_MS) {
          const { chunks, voicedMs } = phrase;
          phrase = null;
          if (voicedMs >= MIN_VOICED_MS) send(concat(chunks));
        }
      };

      return {
        stop: () => stop(),
        setMuted: (value) => (muted = value),
      };
    },
  };
})();
