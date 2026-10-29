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

// <time data-local datetime="..."> is rendered in UTC by the server; show it in the
// viewer's own time zone. data-local="date" shows the date only.
document.querySelectorAll("time[data-local]").forEach((el) => {
  const date = new Date(el.getAttribute("datetime"));
  if (isNaN(date)) return;
  const options = el.dataset.local === "date"
    ? { day: "2-digit", month: "2-digit", year: "numeric" }
    : { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" };
  el.textContent = date.toLocaleString("ru-RU", options);
  el.title = el.getAttribute("datetime");
});

// <button data-copy="#input-id"> copies that field's value and briefly confirms it.
document.addEventListener("click", async (e) => {
  const button = e.target.closest("[data-copy]");
  if (!button) return;
  const field = document.querySelector(button.dataset.copy);
  try {
    await navigator.clipboard.writeText(field.value);
  } catch {
    field.select(); // clipboard blocked (e.g. plain http): leave it selected to copy by hand
    return;
  }
  const label = button.textContent;
  button.textContent = "Скопировано ✓";
  setTimeout(() => (button.textContent = label), 1500);
});

// <details data-sheet> is the tab bar's «Ещё» sheet: tapping the backdrop or Escape
// closes it, and so does coming back to the page with the Back button.
const closeSheets = () => document.querySelectorAll("details[data-sheet][open]").forEach((sheet) => (sheet.open = false));
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-sheet-close]")) closeSheets();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeSheets();
});
window.addEventListener("pageshow", closeSheets);
