// «Словарь»: the speaker button reads a word aloud; the search box hides words that
// don't match, and with them letters that are left empty.
(() => {
  document.addEventListener("click", (e) => {
    const button = e.target.closest("[data-speak]");
    if (button) poliglot.speak(button.dataset.speak, window.poliglotLanguage);
  });

  const search = document.getElementById("dictionary-search");
  if (!search) return;
  const sections = document.querySelectorAll("[data-letter]");

  search.addEventListener("input", () => {
    const query = search.value.trim().toLowerCase();
    let found = 0;
    for (const section of sections) {
      let visible = 0;
      for (const item of section.querySelectorAll("[data-search]")) {
        const match = item.dataset.search.includes(query);
        item.classList.toggle("hidden", !match);
        if (match) visible++;
      }
      section.classList.toggle("hidden", !visible);
      document.querySelector(`[data-letter-link="${section.dataset.letter}"]`).classList.toggle("hidden", !visible);
      found += visible;
    }
    document.getElementById("dictionary-empty").classList.toggle("hidden", found > 0);
  });
})();
