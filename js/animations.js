/* animations.js — scroll reveal & parallax */

/* ── Intersection Observer reveal ── */
const revealEls = document.querySelectorAll('.reveal:not(.philosophy-item)'); // Exclude philosophy items as they are staggered using Anime.js

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
const nav = document.querySelector('.nav-pill');
if (nav) {
  let isNavScrolled = false;
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY > 120;
    if (scrolled !== isNavScrolled) {
      isNavScrolled = scrolled;
      anime({
        targets: '.nav-pill',
        padding: isNavScrolled ? '10px 20px' : '14px 28px',
        backgroundColor: isNavScrolled ? 'rgba(13,11,20,0.92)' : 'rgba(13,11,20,0.72)',
        borderColor: isNavScrolled ? 'rgba(245,240,232,0.04)' : 'rgba(245,240,232,0.06)',
        duration: 450,
        easing: 'easeOutQuad'
      });
    }
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

/* ── Scroll Progress & Section Indicators ── */
const progressBar = document.querySelector('.scroll-progress-bar');
const indicatorDots = document.querySelectorAll('.indicator-dot');
const sections = document.querySelectorAll('section[id], div#manifesto-band');

window.addEventListener('scroll', () => {
  if (progressBar) {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight > 0) {
      const progress = window.scrollY / totalHeight;
      progressBar.style.transform = `scaleX(${progress})`;
    }
  }
}, { passive: true });

// Section highlighting observer
if (indicatorDots.length) {
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        indicatorDots.forEach(dot => {
          const target = dot.getAttribute('data-target') || dot.getAttribute('href');
          if (target === `#${id}`) {
            dot.classList.add('active');
          } else {
            dot.classList.remove('active');
          }
        });
      }
    });
  }, { threshold: 0.35, rootMargin: '-10% 0px -40% 0px' });

  sections.forEach(sec => sectionObserver.observe(sec));
}

/* ── Philosophy Staggered Reveals & Count-up ── */
const philGrid = document.querySelector('.philosophy-grid');
if (philGrid) {
  const philObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        philObserver.unobserve(entry.target);
        const items = entry.target.querySelectorAll('.philosophy-item');
        
        items.forEach(item => {
          item.style.transition = 'none';
        });

        anime({
          targets: items,
          opacity: [0, 1],
          translateY: [40, 0],
          delay: anime.stagger(140),
          duration: 1200,
          easing: 'spring(1, 85, 13, 0)',
          complete: () => {
            items.forEach(item => {
              const numEl = item.querySelector('.philosophy-number');
              if (numEl) {
                const targetVal = parseInt(numEl.textContent, 10);
                if (!isNaN(targetVal)) {
                  const counter = { val: 0 };
                  anime({
                    targets: counter,
                    val: targetVal,
                    round: 1,
                    duration: 1000,
                    easing: 'easeOutQuad',
                    update: () => {
                      numEl.textContent = String(counter.val).padStart(2, '0');
                    }
                  });
                }
              }
            });
          }
        });
      }
    });
  }, { threshold: 0.15 });

  philObserver.observe(philGrid);
}

/* ── Process steps connecting timeline SVG ── */
const processGrid = document.querySelector('.process-grid');
const processSteps = document.querySelectorAll('.process-step');
const processPath = document.querySelector('.process-svg-path');

if (processGrid && processSteps.length && processPath) {
  const updateTimeline = () => {
    const gridRect = processGrid.getBoundingClientRect();
    const pts = Array.from(processSteps).map(step => {
      const r = step.getBoundingClientRect();
      return {
        x: r.left - gridRect.left + r.width / 2,
        y: r.top - gridRect.top + r.height / 2
      };
    });

    let d = '';
    if (window.innerWidth <= 640) {
      // Straight vertical connecting line on mobile
      d = `M ${pts[0].x} ${pts[0].y}`;
      for (let i = 1; i < pts.length; i++) {
        d += ` L ${pts[i].x} ${pts[i].y}`;
      }
    } else {
      // Elegant Bezier curves on desktop 2x2 grid
      d = `M ${pts[0].x} ${pts[0].y} `;
      // Step 1 -> Step 2
      d += `C ${pts[0].x + (pts[1].x - pts[0].x) * 0.5} ${pts[0].y}, ${pts[0].x + (pts[1].x - pts[0].x) * 0.5} ${pts[1].y}, ${pts[1].x} ${pts[1].y} `;
      // Step 2 -> Step 3
      d += `C ${pts[1].x} ${pts[1].y + (pts[2].y - pts[1].y) * 0.5}, ${pts[2].x} ${pts[1].y + (pts[2].y - pts[1].y) * 0.5}, ${pts[2].x} ${pts[2].y} `;
      // Step 3 -> Step 4
      d += `C ${pts[2].x + (pts[3].x - pts[2].x) * 0.5} ${pts[2].y}, ${pts[2].x + (pts[3].x - pts[2].x) * 0.5} ${pts[3].y}, ${pts[3].x} ${pts[3].y}`;
    }

    processPath.setAttribute('d', d);
    const len = processPath.getTotalLength();
    processPath.style.strokeDasharray = len;
    processPath.style.strokeDashoffset = len;

    const animateLine = () => {
      const rect = processGrid.getBoundingClientRect();
      const viewHeight = window.innerHeight;
      const start = viewHeight * 0.82;
      const end = viewHeight * 0.18;
      const totalDist = start - end + rect.height;
      const progress = Math.max(0, Math.min(1, (start - rect.top) / totalDist));
      processPath.style.strokeDashoffset = len * (1 - progress);
    };

    window.removeEventListener('scroll', animateLine);
    window.addEventListener('scroll', animateLine, { passive: true });
    animateLine();
  };

  updateTimeline();
  window.addEventListener('resize', updateTimeline);
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
