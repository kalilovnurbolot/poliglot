// Small helpers shared by every page.
window.poliglot = {
  csrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  },

  postJSON(url, data) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": this.csrfToken() },
      body: JSON.stringify(data),
    });
  },

  // Resolves when the phrase has been spoken (or was interrupted by the next one).
  speak(text, language) {
    return new Promise((resolve) => {
      if (!window.speechSynthesis) return resolve();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = { en: "en-US", de: "de-DE", ru: "ru-RU" }[language] ?? "en-US";
      utterance.onend = utterance.onerror = () => resolve();
      // Some browsers occasionally never fire onend; don't wait forever.
      setTimeout(resolve, 2000 + text.length * 120);
      this.currentUtterance = utterance; // Chrome drops events of garbage-collected utterances
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    });
  },
};

// <form data-confirm="..."> asks before submitting; data-submitting-label disables
// the submit button and swaps its text while the request is in flight.
document.addEventListener("submit", (e) => {
  const form = e.target;
  if (form.dataset.confirm && !confirm(form.dataset.confirm)) {
    e.preventDefault();
    return;
  }
  const button = form.querySelector('button[type="submit"]');
  if (button && form.dataset.submittingLabel) {
    button.textContent = form.dataset.submittingLabel;
    setTimeout(() => (button.disabled = true));
  }
});

if ("serviceWorker" in navigator && location.hostname !== "localhost" && location.hostname !== "127.0.0.1") {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
