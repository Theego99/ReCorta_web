"use strict";
document.documentElement.classList.add("js");
const siteLoader = document.querySelector(".site-loader");
const animalAssets = [...new Set((siteLoader?.dataset.animalAssets || "")
  .split(",")
  .filter(Boolean))];

const shuffled = (items) => {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const other = Math.floor(Math.random() * (index + 1));
    [result[index], result[other]] = [result[other], result[index]];
  }
  return result;
};

const setAnimal = (image, name) => {
  image.dataset.animalName = name;
  image.src = `/assets/brand/${name}.svg`;
};

const populateOrbit = (root, shouldCycle = false) => {
  if (!root || !animalAssets.length) return;
  const images = [...root.querySelectorAll(".orbit-animal img")];
  if (!images.length || animalAssets.length < images.length) return;
  const initialAnimals = shuffled(animalAssets).slice(0, images.length);
  images.forEach((image, index) => setAnimal(image, initialAnimals[index]));
  if (!shouldCycle || animalAssets.length <= images.length) return;

  let nextIndex = Math.floor(Math.random() * images.length);
  const scheduleNextAnimal = (delay) => window.setTimeout(() => {
    const image = images[nextIndex];
    const occupied = new Set(images
      .filter((other) => other !== image)
      .map((other) => other.dataset.animalName)
      .filter(Boolean));
    const candidates = animalAssets.filter((name) =>
      name !== image.dataset.animalName && !occupied.has(name));
    if (!candidates.length) {
      nextIndex = (nextIndex + 1) % images.length;
      scheduleNextAnimal(1200);
      return;
    }

    const nextAnimal = candidates[Math.floor(Math.random() * candidates.length)];
    image.classList.add("is-fading");
    window.setTimeout(() => {
      setAnimal(image, nextAnimal);
      nextIndex = (nextIndex + 1) % images.length;
      window.requestAnimationFrame(() => image.classList.remove("is-fading"));
      scheduleNextAnimal(1500 + Math.random() * 900);
    }, 1250);
  }, delay);

  scheduleNextAnimal(2200 + Math.random() * 900);
};

if (siteLoader) {
  populateOrbit(siteLoader);
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

populateOrbit(document.querySelector(".hero-art"), true);

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
