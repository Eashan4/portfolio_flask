/* === animations.js ===
   Features:
   - Scroll reveal (fade/slide/zoom with stagger)
   - 3D tilt on hover for .hover-tilt
   - Button ripple for .btn
   - Back-to-top button
   - Optional typing effect if #hero-typing exists
   - Respects prefers-reduced-motion
*/

(function () {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Auto-tag common elements for reveal (so you don’t edit all templates) ----
  const autoMap = [
    [".card", "fade-up"],
    [".timeline-item", "fade-up"],
    ["section", "fade-in"],
    [".hover-card", "zoom-in"]
  ];
  autoMap.forEach(([sel, anim]) => {
    document.querySelectorAll(sel).forEach((el, i) => {
      if (!el.hasAttribute("data-animate")) el.setAttribute("data-animate", anim);
      if (!el.hasAttribute("data-delay")) el.setAttribute("data-delay", `${(i % 10) * 60}ms`);
    });
  });

  // ---- Scroll reveal with IntersectionObserver ----
  if (!prefersReduced && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            const el = e.target;
            const delay = el.dataset.delay || "0ms";
            el.style.transitionDelay = delay;
            el.classList.add("animate");
            io.unobserve(el);
          }
        });
      },
      { threshold: 0.15 }
    );

    document.querySelectorAll("[data-animate]").forEach((el) => io.observe(el));
  } else {
    // If reduced motion, show everything immediately
    document.querySelectorAll("[data-animate]").forEach((el) => el.classList.add("animate"));
  }

  // ---- 3D tilt on hover for .hover-tilt ----
  const tilts = document.querySelectorAll(".hover-tilt, .hover-card");
  tilts.forEach((card) => {
    let rect;
    const reset = () => (card.style.transform = "");
    const onMove = (e) => {
      rect = rect || card.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = (e.clientX - cx) / (rect.width / 2);
      const dy = (e.clientY - cy) / (rect.height / 2);
      card.style.transform = `perspective(900px) rotateX(${-dy * 6}deg) rotateY(${dx * 8}deg) translateZ(0)`;
    };
    card.addEventListener("mousemove", onMove);
    card.addEventListener("mouseleave", () => {
      rect = null;
      reset();
    });
  });

  // ---- Button ripple for .btn ----
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn");
    if (!btn) return;
    const ripple = document.createElement("span");
    ripple.className = "ripple";
    const r = Math.max(btn.clientWidth, btn.clientHeight);
    const rect = btn.getBoundingClientRect();
    ripple.style.width = ripple.style.height = r + "px";
    ripple.style.left = e.clientX - rect.left - r / 2 + "px";
    ripple.style.top = e.clientY - rect.top - r / 2 + "px";
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });

  // ---- Back to top ----
  const back = document.getElementById("backToTop");
  if (back) {
    const toggle = () => {
      if (window.scrollY > 400) back.classList.add("show");
      else back.classList.remove("show");
    };
    window.addEventListener("scroll", toggle, { passive: true });
    back.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    toggle();
  }

  // ---- Optional typing effect (add <span id="hero-typing"></span> in your hero) ----
  const target = document.getElementById("hero-typing");
  if (target && !prefersReduced) {
    const lines = [
      "IoT Developer",
      "Python Programmer",
      "Arduino Enthusiast",
      "AI/ML Learner"
    ];
    let i = 0, j = 0, deleting = false;

    const tick = () => {
      const word = lines[i];
      target.textContent = deleting ? word.slice(0, j--) : word.slice(0, j++);
      if (!deleting && j === word.length + 3) deleting = true;
      if (deleting && j === 0) { deleting = false; i = (i + 1) % lines.length; }
      setTimeout(tick, deleting ? 45 : 85);
    };
    tick();
  }
})();
