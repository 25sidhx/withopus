/* animations.js — scroll reveal & parallax */

/* ── Intersection Observer reveal ── */
const revealEls = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -48px 0px' });

revealEls.forEach(el => observer.observe(el));

/* ── Nav pill scroll state ── */
// BUG-08 FIX: null-guard nav before adding scroll listener
const nav = document.querySelector('.nav-pill');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
}

/* ── Horizontal scroll drag (work filmstrip) ── */
const scrollContainer = document.querySelector('.work-scroll-container');
if (scrollContainer) {
  let isDown = false;
  let startX, scrollLeft;

  scrollContainer.addEventListener('mousedown', e => {
    isDown = true;
    scrollContainer.classList.add('grabbing');
    startX = e.pageX - scrollContainer.offsetLeft;
    scrollLeft = scrollContainer.scrollLeft;
  });

  window.addEventListener('mouseup', () => {
    isDown = false;
    scrollContainer.classList.remove('grabbing');
  });

  scrollContainer.addEventListener('mousemove', e => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - scrollContainer.offsetLeft;
    const walk = (x - startX) * 1.4;
    scrollContainer.scrollLeft = scrollLeft - walk;
  });
}

/* ── Parallax bloom on hero ── */
const heroBg = document.querySelector('.hero-bg');
window.addEventListener('scroll', () => {
  if (!heroBg) return;
  const y = window.scrollY;
  heroBg.style.transform = `translateY(${y * 0.25}px)`;
}, { passive: true });

/* ── Count-up numbers (if added later) ── */
function countUp(el, target, duration = 1800) {
  let start = 0;
  const step = timestamp => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    el.textContent = Math.floor(progress * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
}

/* ── Text split char reveal ── */
function splitReveal(selector) {
  document.querySelectorAll(selector).forEach(el => {
    const text = el.textContent;
    el.innerHTML = text.split('').map((char, i) =>
      `<span style="display:inline-block;opacity:0;transform:translateY(12px);
        transition:opacity 0.5s ${i * 0.02}s var(--ease-out),
                   transform 0.5s ${i * 0.02}s var(--ease-out)">${char === ' ' ? '&nbsp;' : char}</span>`
    ).join('');

    const charObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('span').forEach(span => {
            span.style.opacity = '1';
            span.style.transform = 'translateY(0)';
          });
          charObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    charObserver.observe(el);
  });
}

splitReveal('.manifesto-text');
