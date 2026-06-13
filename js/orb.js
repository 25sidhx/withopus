/**
 * orb.js — Hero orb scroll-fade & Spline interaction
 * 
 * Strategy: Allow pointer events so particles react to mouse,
 * but intercept wheel/touch events to prevent scroll hijacking.
 */
(function () {
  const orb  = document.querySelector('.hero-orb');
  const hero = document.getElementById('hero');
  if (!orb || !hero) return;

  const viewer = orb.querySelector('spline-viewer');
  if (viewer) {
    /* Allow mouse interaction (particles react to cursor) */
    viewer.style.pointerEvents = 'auto';

    /* Block scroll hijacking — let wheel events pass through to the page */
    viewer.addEventListener('wheel', e => {
      e.stopPropagation();
      window.scrollBy(0, e.deltaY);
    }, { passive: false });

    /* Block touch scroll hijacking on mobile */
    viewer.addEventListener('touchmove', e => {
      e.stopPropagation();
    }, { passive: true });

    /* After Spline loads and user interacts, the hint auto-dismisses.
       As a fallback, try to hide it via shadow DOM after a delay. */
    function hideHintText() {
      const shadow = viewer.shadowRoot;
      if (!shadow) return;

      /* Find elements that look like overlays (not canvas ancestors) */
      const canvas = shadow.querySelector('canvas');
      const canvasAncestors = new Set();
      let node = canvas;
      while (node && node !== shadow) {
        canvasAncestors.add(node);
        node = node.parentElement;
      }

      shadow.querySelectorAll('*').forEach(el => {
        if (canvasAncestors.has(el)) return;
        if (el.tagName === 'CANVAS' || el.tagName === 'STYLE' || el.tagName === 'SCRIPT') return;
        /* Only hide if it looks like an overlay (has text or is an image/link) */
        const text = el.textContent?.trim().toLowerCase() || '';
        if (text.includes('move your mouse') || text.includes('spline') ||
            el.tagName === 'A' || el.tagName === 'IMG' ||
            (el.tagName === 'DIV' && el.querySelector('a, img'))) {
          el.style.display = 'none';
        }
      });
    }

    setTimeout(hideHintText, 3000);
    setTimeout(hideHintText, 6000);
    setTimeout(hideHintText, 10000);
  }

  /* Fade the orb out as user scrolls past the hero section */
  window.addEventListener('scroll', function () {
    const bottom   = hero.getBoundingClientRect().bottom;
    const fadeZone = window.innerHeight * 0.55;
    const progress = Math.max(0, Math.min(1, (fadeZone - bottom) / (fadeZone * 0.6)));
    orb.style.opacity = (1 - progress).toFixed(3);
  }, { passive: true });
})();
