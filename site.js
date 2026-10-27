"use strict";
document.documentElement.classList.add("js");
const siteLoader = document.querySelector(".site-loader");
if (siteLoader) {
  siteLoader.hidden = false;
  const startedAt = performance.now();
  let hideScheduled = false;
  const hideSiteLoader = () => {
    if (hideScheduled) return;
    hideScheduled = true;
    const minimumTimeLeft = Math.max(0, 520 - (performance.now() - startedAt));
    window.setTimeout(() => {
      siteLoader.classList.add("is-done");
      window.setTimeout(() => { siteLoader.hidden = true; }, 420);
    }, minimumTimeLeft);
  };
  if (document.readyState === "complete") {
    hideSiteLoader();
  } else {
    window.addEventListener("load", hideSiteLoader, { once: true });
  }
  window.setTimeout(hideSiteLoader, 2200);
}

const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector("#navigation");
if (toggle && nav) {
  toggle.hidden = false;
  const closeMenu = () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
  };
  toggle.addEventListener("click", () => {
    const opened = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(opened));
  });
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("open")) {
      closeMenu();
      toggle.focus();
    }
  });
  window
    .matchMedia("(min-width: 1001px)")
    .addEventListener("change", closeMenu);
}
