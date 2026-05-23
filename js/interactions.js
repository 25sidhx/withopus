/* ──────────────────────────────────────────────────────────
   INTERACTIONS — Premium Editorial OPUS
   Applying: animejs-animation, design-spells, magic-animator
   ───────────────────────────────────────────────────────── */

(function () {
  'use strict';

  // ── UTILITIES ──
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  // ── NAV: Scroll-direction hide/show + frosted glass ──
  const navbar = $('#navbar');
  const navToggle = $('#nav-toggle');
  const navLinks = $('#nav-links');
  let lastScroll = 0;

  function handleNavScroll() {
    const y = window.scrollY;
    if (y > 80) {
      navbar.classList.add('scrolled');
      if (y > lastScroll + 5 && y > 200) {
        navbar.classList.add('hidden');
      } else if (y < lastScroll - 5) {
        navbar.classList.remove('hidden');
      }
    } else {
      navbar.classList.remove('scrolled');
      navbar.classList.remove('hidden');
    }
    lastScroll = y;
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });

  // ── NAV: Mobile toggle ──
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('open');
      navLinks.classList.toggle('open');
      document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    $$('.nav-link', navLinks).forEach(link => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('open');
        navLinks.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // ── HERO: Premium Asymmetric Typography Stagger (anime.js) ──
  function animateHero() {
    const displayTexts = $$('.hero-display-text');
    if (!displayTexts.length || typeof anime === 'undefined') return;

    // Split text into wrapped letter spans for high-end cinematic entry
    displayTexts.forEach(headline => {
      const text = headline.textContent.trim();
      headline.innerHTML = text.split('').map(letter => {
        return `<span class="letter" style="display:inline-block;opacity:0;transform:translateY(60px);will-change:transform,opacity;">${letter}</span>`;
      }).join('');
    });

    // Master timelines with custom cubic-bezier curves
    const tl = anime.timeline({
      easing: 'cubicBezier(0.16, 1, 0.3, 1)'
    });

    tl.add({
      targets: '.hero-display-text[data-anime="studio"] .letter',
      opacity: [0, 1],
      translateY: [60, 0],
      delay: anime.stagger(45),
      duration: 900
    })
    .add({
      targets: '.hero-display-text[data-anime="opus"] .letter',
      opacity: [0, 1],
      translateY: [60, 0],
      delay: anime.stagger(45),
      duration: 900
    }, '-=700')
    .add({
      targets: '.hero-wavy-card',
      opacity: [0, 1],
      scale: [0.85, 1],
      rotate: [-3, 0],
      duration: 1200,
      easing: 'cubicBezier(0.34, 1.56, 0.64, 1)' // Custom elastic spring feel
    }, '-=750')
    .add({
      targets: ['.hero-label', '.hero-nav-links a'],
      opacity: [0, 1],
      translateY: [15, 0],
      delay: anime.stagger(80),
      duration: 600
    }, '-=900')
    .add({
      targets: ['.hero-editorial-desc', '.hero-editorial-cta-wrap', '.hero-scroll'],
      opacity: [0, 1],
      translateY: [20, 0],
      delay: anime.stagger(100),
      duration: 700
    }, '-=600');
  }

  // ── SERVICES: Collapsible Division Accordions ──
  function initServicesAccordion() {
    const headers = $$('.service-accordion-header');

    headers.forEach((header) => {
      header.addEventListener('click', () => {
        const item = header.closest('.service-accordion-item');
        const content = item.querySelector('.service-accordion-content');
        const isActive = item.classList.contains('active');

        // Close all other open panels first
        $$('.service-accordion-item.active').forEach((activeItem) => {
          if (activeItem !== item) {
            activeItem.classList.remove('active');
            activeItem.querySelector('.service-accordion-content').style.maxHeight = '0';
          }
        });

        // Toggle state of current panel
        if (isActive) {
          item.classList.remove('active');
          content.style.maxHeight = '0';
        } else {
          item.classList.add('active');
          content.style.maxHeight = content.scrollHeight + 'px';
        }
      });
    });
  }

  // ── PROCESS: Bento Hover Interactions & Glows ──
  function initProcessHovers() {
    const cards = $$('.process-card');
    cards.forEach((card) => {
      const dot = card.querySelector('.process-dot');
      const isOriginallyActive = dot && dot.classList.contains('active');

      card.addEventListener('mouseenter', () => {
        if (dot) dot.classList.add('active');
        anime({
          targets: card,
          translateY: -8,
          scale: 1.015,
          borderColor: 'rgba(255, 255, 255, 0.28)',
          backgroundColor: '#1b1b1b',
          duration: 350,
          easing: 'cubicBezier(0.16, 1, 0.3, 1)'
        });
      });

      card.addEventListener('mouseleave', () => {
        if (dot && !isOriginallyActive) {
          dot.classList.remove('active');
        }
        anime({
          targets: card,
          translateY: 0,
          scale: 1,
          borderColor: 'rgba(255, 255, 255, 0.12)',
          backgroundColor: '#161616',
          duration: 350,
          easing: 'cubicBezier(0.16, 1, 0.3, 1)'
        });
      });
    });
  }

  // ── SCROLL REVEAL (IntersectionObserver) ──
  function initScrollReveal() {
    const reveals = $$('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );

    reveals.forEach((el) => observer.observe(el));
  }

  // ── STATS COUNTER (anime.js) ──
  function initStatsCounter() {
    const statNumbers = $$('.stat-number[data-target]');
    if (!statNumbers.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseFloat(el.dataset.target);
            const suffix = el.dataset.suffix || '';
            const decimals = parseInt(el.dataset.decimals || '0', 10);

            const counter = { val: 0 };
            anime({
              targets: counter,
              val: target,
              easing: 'easeOutExpo',
              duration: 2000,
              round: decimals === 0 ? 1 : false,
              update: () => {
                el.textContent = decimals > 0
                  ? counter.val.toFixed(decimals) + suffix
                  : Math.round(counter.val) + suffix;
              },
            });

            observer.unobserve(el);
          }
        });
      },
      { threshold: 0.3 }
    );

    statNumbers.forEach((el) => observer.observe(el));
  }

  // ── FAQ ACCORDION ──
  function initFAQ() {
    const questions = $$('.faq-question');

    questions.forEach((btn) => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        const answer = item.querySelector('.faq-answer');
        const isOpen = item.classList.contains('open');

        // Close all others
        $$('.faq-item.open').forEach((openItem) => {
          if (openItem !== item) {
            openItem.classList.remove('open');
            openItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
            openItem.querySelector('.faq-answer').style.maxHeight = '0';
          }
        });

        // Toggle current
        if (isOpen) {
          item.classList.remove('open');
          btn.setAttribute('aria-expanded', 'false');
          answer.style.maxHeight = '0';
        } else {
          item.classList.add('open');
          btn.setAttribute('aria-expanded', 'true');
          answer.style.maxHeight = answer.scrollHeight + 'px';
        }
      });
    });
  }

  // ── PROJECT HOVER: Scale + Overlay ──
  function initProjectHovers() {
    const projects = $$('.project-item');
    projects.forEach((item) => {
      item.addEventListener('mouseenter', () => {
        if (typeof anime !== 'undefined') {
          anime({
            targets: item.querySelector('.project-bg'),
            scale: 1.04,
            duration: 500,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)'
          });
        }
      });
      item.addEventListener('mouseleave', () => {
        if (typeof anime !== 'undefined') {
          anime({
            targets: item.querySelector('.project-bg'),
            scale: 1,
            duration: 500,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)'
          });
        }
      });
    });
  }

  // ── SMOOTH SCROLL for anchor links ──
  function initSmoothScroll() {
    $$('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const targetStr = a.getAttribute('href');
        if (targetStr === '#') return;
        const target = document.querySelector(targetStr);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ── ACTIVE NAV LINK HIGHLIGHT ──
  function initActiveNavHighlight() {
    const sections = $$('section[id]');
    const navLinkEls = $$('.nav-link');

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            navLinkEls.forEach((link) => {
              link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
            });
          }
        });
      },
      { threshold: 0.25 }
    );

    sections.forEach((section) => observer.observe(section));
  }

  // ── CONTACT FORM HANDLER ──
  function initContactForm() {
    const form = $('#contact-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('.form-submit');
      const originalText = btn.textContent;

      btn.textContent = 'Sending...';
      btn.disabled = true;

      // Simulate send
      setTimeout(() => {
        btn.textContent = 'Sent! ✓';
        form.reset();
        setTimeout(() => {
          btn.textContent = originalText;
          btn.disabled = false;
        }, 2000);
      }, 1200);
    });
  }

  // ── INIT ──
  document.addEventListener('DOMContentLoaded', () => {
    animateHero();
    initScrollReveal();
    initStatsCounter();
    initServicesAccordion();
    initProcessHovers();
    initFAQ();
    initProjectHovers();
    initSmoothScroll();
    initActiveNavHighlight();
    initContactForm();
  });
})();
