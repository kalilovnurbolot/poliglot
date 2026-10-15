// Voice control: streams the microphone to the voice service (voice/server.py)
// and calls onText with every phrase it recognizes.
(() => {
  const WORKLET_URL = document.currentScript.dataset.worklet;

  function socketUrl(url, token) {
    const result = new URL(url, location.href);
    if (result.protocol === "https:") result.protocol = "wss:";
    if (result.protocol === "http:") result.protocol = "ws:";
    result.searchParams.set("token", token);
    return result;
  }

  window.poliglot.voice = {
    supported() {
      return Boolean(navigator.mediaDevices?.getUserMedia && window.AudioWorkletNode && window.WebSocket);
    },

    // Resolves with { stop(), setMuted(muted) } once the microphone is on. While muted,
    // silence is sent instead of the microphone, e.g. so the page's own speech is not heard.
    // onStop(error) fires when listening ends: error is null after a normal stop().
    async start({ url, token, grammar, onText, onStop }) {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
      });
      const context = new AudioContext();
      let socket;
      let stopped = false;
      let opened = false;
      let muted = false;

      function stop(error = null) {
        if (stopped) return;
        stopped = true;
        stream.getTracks().forEach((track) => track.stop());
        context.close();
        if (socket && socket.readyState <= WebSocket.OPEN) socket.close();
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

      socket = new WebSocket(socketUrl(url, token));
      socket.addEventListener("open", () => {
        opened = true;
        socket.send(JSON.stringify({ grammar }));
      });
      socket.addEventListener("message", (e) => {
        const { text } = JSON.parse(e.data);
        if (text) onText(text);
      });
      // Our own stop() is already done by now, so any close seen here is unexpected.
      socket.addEventListener("close", (e) => {
        if (e.code === 4401) return stop(new Error("Сессия устарела — обновите страницу."));
        stop(new Error(opened ? "Связь с сервисом распознавания прервалась." : "Сервис распознавания речи недоступен."));
      });
      node.port.onmessage = (e) => {
        if (socket.readyState === WebSocket.OPEN) socket.send(muted ? new ArrayBuffer(e.data.byteLength) : e.data);
      };

      return {
        stop: () => stop(),
        setMuted: (value) => (muted = value),
      };
    },
  };
})();
