// Highlights the section currently in view in the side navigation and scrolls smoothly on click.
(() => {
  const nav = document.querySelector("[data-section-nav]");
  if (!nav) return;
  const links = [...nav.querySelectorAll("[data-section]")];

  const setActive = (id) => links.forEach((a) => a.classList.toggle("is-active", a.dataset.section === id));

  links.forEach((a) =>
    a.addEventListener("click", (e) => {
      e.preventDefault();
      document.getElementById(a.dataset.section)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }),
  );

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.find((e) => e.isIntersecting);
      if (visible) setActive(visible.target.id);
    },
    { rootMargin: "-10% 0px -70% 0px" },
  );
  links.forEach((a) => {
    const el = document.getElementById(a.dataset.section);
    if (el) observer.observe(el);
  });
})();
