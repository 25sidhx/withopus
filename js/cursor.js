/* cursor.js — magnetic custom cursor */
const dot  = document.querySelector('.cursor-dot');
const ring = document.querySelector('.cursor-ring');

let mouse = { x: 0, y: 0 };
let ring_pos = { x: 0, y: 0 };
let isCursorVisible = true;

function checkMobile() {
  const isTouch = window.matchMedia('(hover: none) and (pointer: coarse)').matches || window.innerWidth <= 768;
  if (isTouch) {
    if (dot) dot.style.display = 'none';
    if (ring) ring.style.display = 'none';
    isCursorVisible = false;
  } else {
    if (dot) dot.style.display = '';
    if (ring) ring.style.display = '';
    isCursorVisible = true;
  }
}

// Initial check
checkMobile();
window.addEventListener('resize', checkMobile);

if (dot && ring) {
  document.addEventListener('mousemove', e => {
    if (!isCursorVisible) return;
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    dot.style.transform = `translate(calc(${mouse.x}px - 50%), calc(${mouse.y}px - 50%))`;
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  function animateRing() {
    if (isCursorVisible) {
      ring_pos.x = lerp(ring_pos.x, mouse.x, 0.11);
      ring_pos.y = lerp(ring_pos.y, mouse.y, 0.11);
      ring.style.transform = `translate(calc(${ring_pos.x}px - 50%), calc(${ring_pos.y}px - 50%))`;
    }
    requestAnimationFrame(animateRing);
  }
  animateRing();

  /* Hover expansion on interactive elements */
  const hoverables = 'a, button, [data-target], .price-header, .service-item, .work-card, .hero-cta-primary, .hero-cta-secondary, .pitch-cta';
  document.querySelectorAll(hoverables).forEach(el => {
    el.addEventListener('mouseenter', () => { if (isCursorVisible) ring.classList.add('hovered'); });
    el.addEventListener('mouseleave', () => { if (isCursorVisible) ring.classList.remove('hovered'); });
  });

  /* Hide on leave */
  document.addEventListener('mouseleave', () => {
    if (!isCursorVisible) return;
    dot.style.opacity  = '0';
    ring.style.opacity = '0';
  });
  document.addEventListener('mouseenter', () => {
    if (!isCursorVisible) return;
    dot.style.opacity  = '1';
    ring.style.opacity = '1';
  });
}
