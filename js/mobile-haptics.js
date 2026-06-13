/* ═══════════════════════════════════════════════════════
   mobile-haptics.js — Opus Tactile System
   Web Vibration API (Android Chrome only — iOS doesn't support it)
   Triggered on touchstart for immediate tactile response
═══════════════════════════════════════════════════════ */

(function () {
  /* Feature detect */
  if (!('vibrate' in navigator)) return;

  /* ─── Patterns ─── */
  const HIT = {
    micro:   [8],
    light:   [15],
    medium:  [25],
    double:  [10, 40, 10],
    success: [12, 40, 20],
  };

  function vibe(pattern) {
    try { navigator.vibrate(pattern); } catch (_) {}
  }

  // Bind to touchstart for immediate feedback
  const bind = (selector, pattern) => {
    document.querySelectorAll(selector).forEach(el => {
      el.addEventListener('touchstart', () => vibe(pattern), { passive: true });
    });
  };

  /* ─── Bind Elements ─── */
  bind('.hero-cta-primary, .pitch-cta, .nav-cta', HIT.medium);
  bind('.hero-cta-secondary, .pitch-cta-secondary, .accent-link, .work-card', HIT.light);
  bind('a[href^="#"], .nav-links a', HIT.micro);
  bind('.price-header', HIT.double);
  bind('.service-item, .philosophy-item', HIT.micro);

  /* ─── Section enter — subtle pulse when scrolling into key sections ─── */
  const pulse_sections = document.querySelectorAll(
    '.services, .work, .pitch, .pricing'
  );
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        vibe(HIT.micro);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.25 });

  pulse_sections.forEach(s => obs.observe(s));

})();
