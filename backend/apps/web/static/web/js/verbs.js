// «Глаголы»: the speaker button reads the three forms aloud ("was / were" as "was, were");
// the search box hides verbs where no form or translation matches.
(() => {
  document.addEventListener("click", (e) => {
    const button = e.target.closest("[data-speak]");
    if (button) poliglot.speak(button.dataset.speak.replace(/\s*\/\s*/g, ", "), window.poliglotLanguage);
  });

  const search = document.getElementById("verbs-search");
  if (!search) return;
  const rows = document.querySelectorAll("[data-search]");
  search.addEventListener("input", () => {
    const query = search.value.trim().toLowerCase();
    let found = 0;
    for (const row of rows) {
      const match = row.dataset.search.includes(query);
      row.classList.toggle("hidden", !match);
      if (match) found++;
    }
    document.getElementById("verbs-empty").classList.toggle("hidden", found > 0);
  });
})();
