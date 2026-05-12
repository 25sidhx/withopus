/* ═══════════════════════════════════════════════════════
   haptics.js — Opus Feel System
   Magnetic · Text scramble · Word reveal · Cursor parallax
   Scroll tilt · Ambient glow · Cinematic loader
   (NO inertia scroll, NO particle trails)
═══════════════════════════════════════════════════════ */


/* ─────────────────────────────────────────────────────
   1. CINEMATIC PAGE INTRO LOADER
───────────────────────────────────────────────────── */
(function () {
  const loader  = document.getElementById('opus-loader');
  if (!loader) return;

  const lineEl  = loader.querySelector('.loader-line');
  const countEl = loader.querySelector('.loader-count');

  let count = 0;
  const interval = setInterval(() => {
    count += Math.floor(Math.random() * 14) + 6;
    if (count >= 100) { count = 100; clearInterval(interval); }
    if (countEl) countEl.textContent = count + '%';
    if (lineEl)  lineEl.style.width  = count + '%';
    if (count === 100) {
      setTimeout(() => {
        loader.style.transition = 'opacity 0.9s cubic-bezier(0.7,0,0.84,0), transform 0.9s cubic-bezier(0.7,0,0.84,0)';
        loader.style.opacity    = '0';
        loader.style.transform  = 'translateY(-10px)';
        setTimeout(() => { loader.style.display = 'none'; }, 950);
      }, 250);
    }
  }, 30);
})();


/* ─────────────────────────────────────────────────────
   2. AMBIENT GLOW FOLLOWS CURSOR
   PERF-02 FIX: Pause rAF loop when tab is not visible
───────────────────────────────────────────────────── */
(function () {
  const glow = document.getElementById('ambient-glow');
  if (!glow) return;

  let gx = window.innerWidth / 2, gy = window.innerHeight / 2;
  let cx = gx, cy = gy;
  let running = true;

  document.addEventListener('mousemove', (e) => { gx = e.clientX; gy = e.clientY; }, { passive: true });

  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) tick();
  });

  function tick() {
    if (!running) return;
    cx += (gx - cx) * 0.045;
    cy += (gy - cy) * 0.045;
    const xp = (cx / window.innerWidth  * 100).toFixed(1);
    const yp = (cy / window.innerHeight * 100).toFixed(1);
    glow.style.background = `
      radial-gradient(ellipse 50% 40% at ${xp}% ${yp}%,
        rgba(232,160,52,0.065) 0%,
        rgba(212,67,26,0.035)  40%,
        transparent            70%)
    `;
    requestAnimationFrame(tick);
  }
  tick();
})();


/* ─────────────────────────────────────────────────────
   3. MAGNETIC BUTTONS
   Elements with class .magnetic gently attract to cursor
───────────────────────────────────────────────────── */
(function () {
  document.querySelectorAll('.magnetic').forEach(el => {
    let bounds, active = false;
    let tx = 0, ty = 0, cx = 0, cy = 0;

    el.addEventListener('mouseenter', () => {
      bounds = el.getBoundingClientRect();
      active = true;
      loop();
    });

    el.addEventListener('mousemove', (e) => {
      if (!bounds) return;
      tx = (e.clientX - bounds.left - bounds.width  / 2) * 0.32;
      ty = (e.clientY - bounds.top  - bounds.height / 2) * 0.32;
    });

    el.addEventListener('mouseleave', () => {
      active = false;
      tx = 0; ty = 0;
      const spring = () => {
        cx += (0 - cx) * 0.13;
        cy += (0 - cy) * 0.13;
        el.style.transform = `translate(${cx}px, ${cy}px)`;
        if (Math.abs(cx) > 0.05 || Math.abs(cy) > 0.05) requestAnimationFrame(spring);
        else el.style.transform = '';
      };
      spring();
    });

    function loop() {
      if (!active) return;
      cx += (tx - cx) * 0.13;
      cy += (ty - cy) * 0.13;
      el.style.transform = `translate(${cx}px, ${cy}px)`;
      requestAnimationFrame(loop);
    }
  });
})();


/* ─────────────────────────────────────────────────────
   4. TEXT SCRAMBLE REVEAL
   Applies to .scramble elements on scroll-enter
───────────────────────────────────────────────────── */
(function () {
  const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$';

  class TextScramble {
    constructor(el) {
      this.el       = el;
      this.original = el.textContent.trim();
      this.rafId    = null;
    }
    scramble() {
      const text  = this.original;
      const len   = text.length;
      let   iter  = 0;
      const total = len * 2.2;
      cancelAnimationFrame(this.rafId);

      const update = () => {
        let out = '';
        for (let i = 0; i < len; i++) {
          if (text[i] === ' ') { out += ' '; continue; }
          if (i < iter / 2.2) out += text[i];
          else out += CHARS[Math.floor(Math.random() * CHARS.length)];
        }
        this.el.textContent = out;
        iter++;
        if (iter < total + 3) this.rafId = requestAnimationFrame(update);
        else this.el.textContent = this.original;
      };
      update();
    }
  }

  const targets   = document.querySelectorAll('.scramble');
  const instances = new Map();
  targets.forEach(el => instances.set(el, new TextScramble(el)));

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        instances.get(e.target)?.scramble();
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.7 });

  targets.forEach(el => obs.observe(el));
})();


/* ─────────────────────────────────────────────────────
   5. WORD-BY-WORD REVEAL
   Wraps .word-reveal text in spans, rises on scroll
───────────────────────────────────────────────────── */
(function () {
  document.querySelectorAll('.word-reveal').forEach(el => {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map((w, i) =>
      `<span style="display:inline-block;overflow:hidden;vertical-align:bottom"><span class="wr-inner" style="display:inline-block;transform:translateY(108%);transition:transform ${0.6 + i * 0.045}s cubic-bezier(0.16,1,0.3,1) ${i * 0.055}s">${w}</span></span>${i < words.length - 1 ? ' ' : ''}`
    ).join('');
  });

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.querySelectorAll('.wr-inner').forEach(s => { s.style.transform = 'translateY(0)'; });
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.word-reveal').forEach(el => obs.observe(el));
})();


/* ─────────────────────────────────────────────────────
   6. CURSOR PARALLAX IN HERO
   data-depth elements drift gently with mouse
   PERF-02 FIX: pause when tab hidden
───────────────────────────────────────────────────── */
(function () {
  const layers = document.querySelectorAll('[data-depth]');
  if (!layers.length) return;

  let mx = 0, my = 0, cx = 0, cy = 0;
  let running = true;

  document.addEventListener('mousemove', (e) => {
    mx = (e.clientX / window.innerWidth  - 0.5);
    my = (e.clientY / window.innerHeight - 0.5);
  }, { passive: true });

  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) tick();
  });

  function tick() {
    if (!running) return;
    cx += (mx - cx) * 0.055;
    cy += (my - cy) * 0.055;
    layers.forEach(el => {
      const d = parseFloat(el.dataset.depth) || 0.1;
      el.style.transform = `translate(${cx * d * 55}px, ${cy * d * 35}px)`;
    });
    requestAnimationFrame(tick);
  }
  tick();
})();


/* ─────────────────────────────────────────────────────
   7. SCROLL VELOCITY TILT ON HEADINGS
   BUG-02 FIX: Exclude .word-reveal elements — their
   children have pending transform transitions. Tilting
   the parent mid-reveal corrupts the translateY animation.
   PERF-02 FIX: pause when tab hidden
───────────────────────────────────────────────────── */
(function () {
  let lastY = window.scrollY, vel = 0;
  let running = true;

  window.addEventListener('scroll', () => {
    vel   = window.scrollY - lastY;
    lastY = window.scrollY;
  }, { passive: true });

  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) tick();
  });

  // BUG-02 FIX: only target titles that are NOT word-reveal
  // (word-reveal manages its own transform on child spans)
  const titles = document.querySelectorAll('.section-title:not(.word-reveal)');

  function tick() {
    if (!running) return;
    const tilt = Math.max(-3.5, Math.min(3.5, vel * 0.07));
    titles.forEach(el => {
      el.style.transform  = `skewY(${tilt}deg)`;
      el.style.transition = 'transform 0.55s cubic-bezier(0.16,1,0.3,1)';
    });
    vel *= 0.82;
    requestAnimationFrame(tick);
  }
  tick();
})();
