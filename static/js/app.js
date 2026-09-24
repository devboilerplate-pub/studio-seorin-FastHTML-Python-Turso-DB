(function () {
  const header = document.getElementById("siteHeader");
  const toggle = document.getElementById("navToggle");
  if (header && toggle) {
    toggle.addEventListener("click", function () {
      header.classList.toggle("is-open");
      toggle.textContent = header.classList.contains("is-open") ? "Close" : "Menu";
    });
  }

  const cards = document.querySelectorAll(".work-card, .svc, .stat");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.transition = "opacity 0.6s ease, transform 0.6s ease";
          entry.target.style.opacity = "1";
          entry.target.style.transform = "none";
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    cards.forEach(function (el, i) {
      el.style.opacity = "0";
      el.style.transform = "translateY(16px)";
      el.style.transitionDelay = (i % 6) * 40 + "ms";
      io.observe(el);
    });
  }
})();
