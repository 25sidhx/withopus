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

  /* ── Cursor Trail Particles (Hero Section Only) ── */
  const heroSection = document.getElementById('hero');
  const particles = [];
  const maxParticles = 8;
  let lastSpawn = 0;
  let particleIndex = 0;

  // Create particle pool container
  const poolContainer = document.createElement('div');
  poolContainer.className = 'cursor-particle-pool';
  poolContainer.style.pointerEvents = 'none';
  poolContainer.style.position = 'fixed';
  poolContainer.style.inset = 0;
  poolContainer.style.zIndex = '9997';
  document.body.appendChild(poolContainer);

  for (let i = 0; i < maxParticles; i++) {
    const p = document.createElement('div');
    p.className = 'cursor-particle';
    p.style.opacity = '0';
    poolContainer.appendChild(p);
    particles.push({
      el: p,
      active: false
    });
  }

  function spawnParticle(x, y) {
    if (typeof anime === 'undefined') return;
    const now = performance.now();
    if (now - lastSpawn < 30) return; // spawn throttle for buttery performance
    lastSpawn = now;

    const p = particles[particleIndex];
    p.active = true;
    p.el.style.transform = `translate(calc(${x}px - 50%), calc(${y}px - 50%)) scale(1)`;
    p.el.style.opacity = '0.6';

    // Cancel active animations on this element
    anime.remove(p.el);
    anime({
      targets: p.el,
      scale: [1, 0.15],
      opacity: [0.6, 0],
      translateX: anime.random(-15, 15),
      translateY: anime.random(-15, 15),
      duration: 750,
      easing: 'easeOutQuad',
      complete: () => {
        p.active = false;
      }
    });

    particleIndex = (particleIndex + 1) % maxParticles;
  }

  if (heroSection) {
    heroSection.addEventListener('mousemove', e => {
      if (!isCursorVisible) return;
      spawnParticle(e.clientX, e.clientY);
    }, { passive: true });
  }
}
