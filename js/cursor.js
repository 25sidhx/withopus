/* cursor.js — magnetic custom cursor */
const dot  = document.querySelector('.cursor-dot');
const ring = document.querySelector('.cursor-ring');

// BUG-01 FIX: Guard — custom cursor may not exist (mobile / DOM change)
if (!dot || !ring) {
  // Nothing to do on touch-only devices
} else {
  let mouse = { x: 0, y: 0 };
  let ring_pos = { x: 0, y: 0 };

  document.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    dot.style.transform = `translate(calc(${mouse.x}px - 50%), calc(${mouse.y}px - 50%))`;
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  function animateRing() {
    ring_pos.x = lerp(ring_pos.x, mouse.x, 0.11);
    ring_pos.y = lerp(ring_pos.y, mouse.y, 0.11);
    ring.style.transform = `translate(calc(${ring_pos.x}px - 50%), calc(${ring_pos.y}px - 50%))`;
    requestAnimationFrame(animateRing);
  }
  animateRing();

  /* Hover expansion on interactive elements */
  const hoverables = 'a, button, [data-target], .price-header, .service-item, .work-card, .hero-cta-primary, .hero-cta-secondary, .pitch-cta';
  document.querySelectorAll(hoverables).forEach(el => {
    el.addEventListener('mouseenter', () => ring.classList.add('hovered'));
    el.addEventListener('mouseleave', () => ring.classList.remove('hovered'));
  });

  /* Hide on leave */
  document.addEventListener('mouseleave', () => {
    dot.style.opacity  = '0';
    ring.style.opacity = '0';
  });
  document.addEventListener('mouseenter', () => {
    dot.style.opacity  = '1';
    ring.style.opacity = '1';
  });
}
