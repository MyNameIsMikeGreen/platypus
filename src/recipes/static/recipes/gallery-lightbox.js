const galleries = document.querySelectorAll("[data-gallery]");

for (const gallery of galleries) {
  const section = gallery.closest(".gallery");
  const lightbox = section?.querySelector("[data-lightbox]");
  if (!lightbox) {
    continue;
  }

  const triggers = [...gallery.querySelectorAll("[data-gallery-trigger]")];
  const images = triggers.map((trigger) => trigger.querySelector("img"));
  const lightboxImage = lightbox.querySelector("[data-lightbox-image]");
  const counter = lightbox.querySelector("[data-lightbox-counter]");
  const prevButton = lightbox.querySelector("[data-lightbox-prev]");
  const nextButton = lightbox.querySelector("[data-lightbox-next]");
  const closeButton = lightbox.querySelector("[data-lightbox-close]");
  const dismissElements = [...lightbox.querySelectorAll("[data-lightbox-close], [data-lightbox-dismiss]")];

  if (triggers.length === 0 || !lightboxImage || !prevButton || !nextButton || !closeButton) {
    continue;
  }

  let currentIndex = 0;
  let triggerToRestoreFocus = null;

  const showImage = (index) => {
    currentIndex = index;
    const image = images[index];
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    if (counter) {
      counter.textContent = `Photo ${index + 1} of ${images.length}`;
    }
    prevButton.hidden = images.length <= 1;
    nextButton.hidden = images.length <= 1;
  };

  const openLightbox = (index, trigger) => {
    triggerToRestoreFocus = trigger;
    showImage(index);
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    closeButton.focus();
  };

  const closeLightbox = () => {
    if (lightbox.hidden) {
      return;
    }
    lightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
    triggerToRestoreFocus?.focus();
    triggerToRestoreFocus = null;
  };

  const showPrevious = () => {
    showImage((currentIndex - 1 + images.length) % images.length);
  };

  const showNext = () => {
    showImage((currentIndex + 1) % images.length);
  };

  triggers.forEach((trigger, index) => {
    trigger.addEventListener("click", () => openLightbox(index, trigger));
  });

  prevButton.addEventListener("click", showPrevious);
  nextButton.addEventListener("click", showNext);
  for (const element of dismissElements) {
    element.addEventListener("click", closeLightbox);
  }

  lightbox.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeLightbox();
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      showPrevious();
      return;
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      showNext();
      return;
    }
    if (event.key !== "Tab") {
      return;
    }
    const focusable = [closeButton, prevButton, nextButton].filter(
      (element) => element && !element.hidden,
    );
    if (focusable.length === 0) {
      return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
}
