/* interactions.js — pricing accordion, nav, micro-interactions */

/* ── Pricing accordion ── */
function activatePriceItem(item) {
  const header = item.querySelector('.price-header');
  item.classList.add('open');
  if (header) header.setAttribute('aria-expanded', 'true');
}
function deactivatePriceItem(item) {
  const header = item.querySelector('.price-header');
  item.classList.remove('open');
  if (header) header.setAttribute('aria-expanded', 'false');
}

document.querySelectorAll('.price-header').forEach(header => {
  // BUG-07 FIX: keyboard support — Enter and Space activate accordion
  function handleToggle() {
    const item = header.closest('.price-item');
    const isOpen = item.classList.contains('open');

    // Close all
    document.querySelectorAll('.price-item').forEach(i => deactivatePriceItem(i));

    // BUG-04 FIX: toggle aria-expanded in sync with visual state
    if (!isOpen) activatePriceItem(item);
  }

  header.addEventListener('click', handleToggle);

  header.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  });
});

/* Open first by default */
const firstPriceItem = document.querySelector('.price-item');
if (firstPriceItem) activatePriceItem(firstPriceItem);

/* ── Smooth anchor scroll (override native) ── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

/* ── Hero CTA hover tilt effect ── */
const primaryCta = document.querySelector('.hero-cta-primary');
if (primaryCta) {
  primaryCta.addEventListener('mousemove', e => {
    if (window.innerWidth <= 768) return;
    const rect = primaryCta.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / (rect.width / 2);
    const dy = (e.clientY - cy) / (rect.height / 2);
    primaryCta.style.transform = `scale(1.02) rotateX(${-dy * 4}deg) rotateY(${dx * 4}deg)`;
  });
  primaryCta.addEventListener('mouseleave', () => {
    if (window.innerWidth <= 768) return;
    primaryCta.style.transform = '';
  });
}

/* ── Work card tilt ── */
document.querySelectorAll('.work-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    if (window.innerWidth <= 768) return;
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `perspective(600px) rotateY(${x * 8}deg) rotateX(${-y * 6}deg) scale(0.98)`;
  });
  card.addEventListener('mouseleave', () => {
    if (window.innerWidth <= 768) return;
    card.style.transform = '';
  });
});

/* ── Philosophy item hover sound (visual pulse) ── */
document.querySelectorAll('.philosophy-item').forEach(item => {
  item.addEventListener('mouseenter', () => {
    item.style.transition = 'background 0.5s var(--ease-out)';
  });
});

/* ── Ambient gradient mouse follow on hero ── */
const hero = document.querySelector('.hero');
if (hero) {
  hero.addEventListener('mousemove', e => {
    if (window.innerWidth <= 768) return;
    const rect = hero.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    const heroBg = hero.querySelector('.hero-bg');
    if (heroBg) {
      heroBg.style.background = `
        radial-gradient(ellipse 60% 50% at ${x}% ${y + 20}%,
          rgba(232,160,52,0.16) 0%,
          rgba(212,67,26,0.1) 35%,
          rgba(122,21,48,0.06) 60%,
          transparent 80%)
      `;
    }
  });
}

/* ── Spline UI Overrides (Shadow DOM) ── */
// Forcefully remove the interaction prompt from the spline-viewer shadow DOM 
// by injecting a <style> tag directly into it.
const splineViewer = document.querySelector('spline-viewer');
if (splineViewer) {
  const injectStyle = () => {
    if (splineViewer.shadowRoot && !splineViewer.shadowRoot.querySelector('#opus-spline-override')) {
      const style = document.createElement('style');
      style.id = 'opus-spline-override';
      style.textContent = `
        #interaction-prompt, .interaction-prompt, #hint, .hint { 
          display: none !important; 
          opacity: 0 !important; 
          pointer-events: none !important; 
          visibility: hidden !important;
        }
      `;
      splineViewer.shadowRoot.appendChild(style);
    }
  };

  // The shadow root might not be immediately ready or might be rebuilt
  injectStyle();
  const uiInterval = setInterval(injectStyle, 500);
  setTimeout(() => clearInterval(uiInterval), 10000);
}
