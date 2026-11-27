/* Animal Planet — full-screen menu, reveal on scroll, app links, promo code copy. No dependencies. */
(function () {
  "use strict";

  // full-screen menu
  const nav = document.getElementById("menu");
  const openBtn = document.querySelector("[data-open-nav]");
  if (nav && openBtn) {
    const setOpen = (open) => {
      nav.classList.toggle("open", open);
      nav.setAttribute("aria-hidden", String(!open));
      openBtn.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
      if (open) nav.querySelector("a, button")?.focus();
    };
    openBtn.addEventListener("click", () => setOpen(true));
    nav.querySelector("[data-close-nav]")?.addEventListener("click", () => { setOpen(false); openBtn.focus(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("open")) setOpen(false); });
  }

  // reveal sections as they scroll into view (CSS hides them only under html.js)
  const revealEls = document.querySelectorAll(".reveal, .reveal-group");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    }), { rootMargin: "0px 0px -8% 0px" });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("is-in"));
  }

  // "Get the app" buttons go straight to the right store on phones
  const ua = navigator.userAgent || "";
  const platform = /iPhone|iPad|iPod/.test(ua) ? "ios" : /Android/.test(ua) ? "android" : "";
  document.querySelectorAll("[data-app-link]").forEach((a) => {
    const url = platform && a.dataset[platform];
    if (url) { a.href = url; a.target = "_blank"; a.rel = "noopener"; }
  });

  // copy a promo code
  document.querySelectorAll("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(btn.dataset.copy);
      const label = btn.lastChild.textContent;
      btn.lastChild.textContent = btn.dataset.copied;
      setTimeout(() => { btn.lastChild.textContent = label; }, 1800);
    } catch (e) { /* clipboard blocked: the code is visible anyway */ }
  }));

  // footer giraffe: a fact per click, the promo code after N clicks (core/easter.py)
  const egg = document.querySelector("[data-egg]");
  if (egg) {
    const data = JSON.parse(document.getElementById("egg-data").textContent);
    const bubble = egg.querySelector(".egg-bubble");
    const text = egg.querySelector("[data-egg-text]");
    const prize = egg.querySelector("[data-egg-prize]");
    let clicks = 0, last = -1, found = false, timer = null;
    const hide = () => { bubble.hidden = true; };
    const show = (ms) => { bubble.hidden = false; clearTimeout(timer); if (ms) timer = setTimeout(hide, ms); };
    egg.querySelector(".egg-btn").addEventListener("click", () => {
      clicks++;
      egg.classList.remove("is-stretch");
      void egg.offsetWidth;  // restart the animation
      egg.classList.add("is-stretch");
      if (data.code && (found || clicks >= data.clicks)) {
        text.hidden = true;
        prize.hidden = false;
        show(0);
        if (!found) {
          found = true;
          if (window.ym && data.ym) window.ym(+data.ym, "reachGoal", "giraffe_code");
          if (window.gtag) window.gtag("event", "giraffe_code");
        }
        return;
      }
      let i;
      do { i = Math.floor(Math.random() * data.facts.length); } while (i === last && data.facts.length > 1);
      last = i;
      text.textContent = data.facts[i];
      show(9000);
    });
    egg.querySelector("[data-egg-close]").addEventListener("click", hide);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });
    egg.querySelector("[data-egg-copy]")?.addEventListener("click", async (e) => {
      const btn = e.currentTarget, label = btn.querySelector("span");
      try {
        await navigator.clipboard.writeText(data.code);
        const was = label.textContent;
        label.textContent = btn.dataset.copied;
        setTimeout(() => { label.textContent = was; }, 1800);
      } catch (err) { /* clipboard blocked: the code is on screen */ }
    });
  }
})();
