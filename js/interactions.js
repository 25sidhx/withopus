/* ──────────────────────────────────────────────────────────
   INTERACTIONS — Premium Editorial OPUS (v2.0)
   Full rewrite: scroll stagger, magnetic cursor, parallax,
   electric glow trails, section-aware nav theming.
   ───────────────────────────────────────────────────────── */

(function () {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  /* ═══════════════════════════════════════════════════════
     1. CUSTOM CURSOR - Removed to restore default browser cursor
     ═══════════════════════════════════════════════════════ */

  /* ═══════════════════════════════════════════════════════
     2. NAVBAR — Scroll-direction hide/show + frosted glass + dark-mode aware
     ═══════════════════════════════════════════════════════ */
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

    // Dark section awareness — invert nav colors when over dark sections
    const darkSections = $$('.process, .cta-banner, .footer');
    let overDark = false;
    darkSections.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top < 80 && rect.bottom > 80) overDark = true;
    });
    navbar.classList.toggle('nav-dark-mode', overDark);

    lastScroll = y;
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });

  // Mobile toggle
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

  /* ═══════════════════════════════════════════════════════
     3. HERO — Cinematic Entry Sequence
     ═══════════════════════════════════════════════════════ */
  function animateHero() {
    const displayRows = $$('.hero-display-text .hero-row');
    if (!displayRows.length || typeof anime === 'undefined') return;

    // Split each display row into letter spans to preserve line breaks
    displayRows.forEach(row => {
      const text = row.textContent.trim();
      if (row.classList.contains('text-glitch')) {
        row.innerHTML = `<span class="letter" style="display:inline-block;opacity:0;transform:translateY(80px) rotateX(-40deg);will-change:transform,opacity;transform-origin:bottom center;">${text}</span>`;
      } else {
        row.innerHTML = text.split('').map(letter => {
          if (letter === ' ') return '&nbsp;';
          return `<span class="letter" style="display:inline-block;opacity:0;transform:translateY(80px) rotateX(-40deg);will-change:transform,opacity;transform-origin:bottom center;">${letter}</span>`;
        }).join('');
      }
    });

    const tl = anime.timeline({
      easing: 'cubicBezier(0.16, 1, 0.3, 1)'
    });

    tl.add({
      targets: '.hero-display-text .letter',
      opacity: [0, 1],
      translateY: [80, 0],
      rotateX: [-40, 0],
      delay: anime.stagger(35, { start: 200 }),
      duration: 1100
    })
    .add({
      targets: '.hero-label-badge',
      opacity: [0, 1],
      translateY: [-20, 0],
      scale: [0.9, 1],
      duration: 800,
      easing: 'cubicBezier(0.34, 1.56, 0.64, 1)'
    }, '-=800')
    .add({
      targets: '.hero-card-wrap',
      opacity: [0, 1],
      scale: [0.88, 1],
      translateY: [40, 0],
      duration: 1400,
      easing: 'cubicBezier(0.34, 1.56, 0.64, 1)'
    }, '-=700')
    .add({
      targets: ['.hero-editorial-desc', '.hero-editorial-cta-wrap'],
      opacity: [0, 1],
      translateY: [30, 0],
      delay: anime.stagger(120),
      duration: 900
    }, '-=700')
    .add({
      targets: '.hero-scroll',
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 600
    }, '-=400');
  }

  /* ═══════════════════════════════════════════════════════
     4. PARALLAX — Hero elements respond to scroll & mouse
     ═══════════════════════════════════════════════════════ */
  function initParallax() {
    const hero = $('.hero');
    const heroCardWrap = $('.hero-card-wrap');
    const heroCard = $('.hero-card');
    const heroText = $('.hero-display-text');
    const heroScroll = $('.hero-scroll');
    if (!hero) return;

    // 1. Scroll Parallax translation on outer elements
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      const heroH = hero.offsetHeight;
      if (y > heroH) return;

      const ratio = y / heroH;
      if (heroCardWrap) heroCardWrap.style.transform = `translateY(${y * 0.15}px) scale(${1 - ratio * 0.05})`;
      if (heroText) heroText.style.transform = `translateY(${y * 0.08}px)`;
      if (heroScroll) heroScroll.style.opacity = Math.max(0, 1 - ratio * 3);
    }, { passive: true });

    // 2. Interactive 3D Mouse Parallax Tilt on inner card element
    if (heroCard) {
      let isMoving = false;

      hero.addEventListener('mousemove', (e) => {
        if (isMoving) return;
        isMoving = true;

        requestAnimationFrame(() => {
          const rect = hero.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;

          const percentX = (x / rect.width) * 2 - 1; // scale to [-1, 1]
          const percentY = (y / rect.height) * 2 - 1; // scale to [-1, 1]

          // Max tilt angle of 12deg for premium, non-jarring Framer look
          const rotateY = percentX * 12;
          const rotateX = -percentY * 12;

          heroCard.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
          isMoving = false;
        });
      });

      hero.addEventListener('mouseleave', () => {
        requestAnimationFrame(() => {
          heroCard.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
        });
      });
    }
  }

  /* ═══════════════════════════════════════════════════════
     5. SCROLL REVEAL — Staggered, Directional, Section-Aware
     ═══════════════════════════════════════════════════════ */
  function initScrollReveal() {
    const reveals = $$('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');

            // Stagger children within revealed sections
            const staggerChildren = entry.target.querySelectorAll(
              '.stat-item, .process-card, .testimonial-item, .project-item, .pricing-tier, .faq-item, .service-accordion-item'
            );
            if (staggerChildren.length && typeof anime !== 'undefined') {
              anime({
                targets: staggerChildren,
                opacity: [0, 1],
                translateY: [50, 0],
                delay: anime.stagger(100, { start: 100 }),
                duration: 800,
                easing: 'cubicBezier(0.16, 1, 0.3, 1)',
              });
            }

            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.06, rootMargin: '0px 0px -60px 0px' }
    );

    reveals.forEach((el) => observer.observe(el));
  }

  /* ═══════════════════════════════════════════════════════
     6. STATS COUNTER — Elastic snap with suffix
     ═══════════════════════════════════════════════════════ */
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

            // Animate the stat item scale for visual punch
            const statItem = el.closest('.stat-item');
            if (statItem && typeof anime !== 'undefined') {
              anime({
                targets: statItem,
                scale: [0.85, 1],
                opacity: [0, 1],
                duration: 800,
                easing: 'cubicBezier(0.34, 1.56, 0.64, 1)',
                delay: Array.from(statItem.parentNode.children).indexOf(statItem) * 150
              });
            }

            const counter = { val: 0 };
            anime({
              targets: counter,
              val: target,
              easing: 'easeOutExpo',
              duration: 2200,
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

  /* ═══════════════════════════════════════════════════════
     7. SERVICES ACCORDION — Spring physics
     ═══════════════════════════════════════════════════════ */
  function initServicesAccordion() {
    const headers = $$('.service-accordion-header');

    headers.forEach((header) => {
      header.addEventListener('click', () => {
        const item = header.closest('.service-accordion-item');
        const content = item.querySelector('.service-accordion-content');
        const isActive = item.classList.contains('active');

        $$('.service-accordion-item.active').forEach((activeItem) => {
          if (activeItem !== item) {
            activeItem.classList.remove('active');
            activeItem.querySelector('.service-accordion-content').style.maxHeight = '0';
          }
        });

        if (isActive) {
          item.classList.remove('active');
          content.style.maxHeight = '0';
        } else {
          item.classList.add('active');
          content.style.maxHeight = content.scrollHeight + 'px';

          // Animate deliverables in
          if (typeof anime !== 'undefined') {
            const delivItems = content.querySelectorAll('.service-deliverables li');
            if (delivItems.length) {
              anime({
                targets: delivItems,
                opacity: [0, 1],
                translateX: [-20, 0],
                delay: anime.stagger(60, { start: 200 }),
                duration: 500,
                easing: 'cubicBezier(0.16, 1, 0.3, 1)'
              });
            }
          }
        }
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     8. PROCESS CARDS — Enhanced hover with glow
     ═══════════════════════════════════════════════════════ */
  function initProcessHovers() {
    const cards = $$('.process-card');
    cards.forEach((card) => {
      const dot = card.querySelector('.process-dot');
      const isOriginallyActive = dot && dot.classList.contains('active');

      card.addEventListener('mouseenter', () => {
        if (dot) dot.classList.add('active');
      });

      card.addEventListener('mouseleave', () => {
        if (dot && !isOriginallyActive) dot.classList.remove('active');
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     9. PROJECTS — Tilt + glow on hover
     ═══════════════════════════════════════════════════════ */
  function initProjectHovers() {
    const projects = $$('.project-item');
    projects.forEach((item) => {
      item.addEventListener('mousemove', (e) => {
        const rect = item.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;

        item.style.transform = `perspective(800px) rotateY(${x * 8}deg) rotateX(${-y * 6}deg) translateY(-5px) scale(1.02)`;

        // Move glow overlay position
        const glowX = ((e.clientX - rect.left) / rect.width) * 100;
        const glowY = ((e.clientY - rect.top) / rect.height) * 100;
        item.style.setProperty('--glow-x', glowX + '%');
        item.style.setProperty('--glow-y', glowY + '%');
      });

      item.addEventListener('mouseleave', () => {
        item.style.transform = '';
        if (typeof anime !== 'undefined') {
          anime({
            targets: item,
            rotateY: 0,
            rotateX: 0,
            translateY: 0,
            scale: 1,
            duration: 600,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)'
          });
        }
      });

      // Background parallax on hover
      item.addEventListener('mouseenter', () => {
        if (typeof anime !== 'undefined') {
          anime({
            targets: item.querySelector('.project-bg'),
            scale: 1.08,
            duration: 800,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)'
          });
        }
      });
      item.addEventListener('mouseleave', () => {
        if (typeof anime !== 'undefined') {
          anime({
            targets: item.querySelector('.project-bg'),
            scale: 1,
            duration: 600,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)'
          });
        }
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     10. PRICING TIERS — Spotlight hover
     ═══════════════════════════════════════════════════════ */
  function initPricingHovers() {
    const tiers = $$('.pricing-tier');
    tiers.forEach(tier => {
      tier.addEventListener('mousemove', (e) => {
        const rect = tier.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        tier.style.setProperty('--spotlight-x', x + '%');
        tier.style.setProperty('--spotlight-y', y + '%');
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     11. TESTIMONIALS — Hover lift
     ═══════════════════════════════════════════════════════ */
  function initTestimonialHovers() {
    // Handled entirely by high-performance GPU CSS transition selectors to avoid dual animation jank.
  }

  /* ═══════════════════════════════════════════════════════
     12. FAQ ACCORDION
     ═══════════════════════════════════════════════════════ */
  function initFAQ() {
    const questions = $$('.faq-question');

    questions.forEach((btn) => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        const answer = item.querySelector('.faq-answer');
        const isOpen = item.classList.contains('open');

        $$('.faq-item.open').forEach((openItem) => {
          if (openItem !== item) {
            openItem.classList.remove('open');
            openItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
            openItem.querySelector('.faq-answer').style.maxHeight = '0';
          }
        });

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

  /* ═══════════════════════════════════════════════════════
     13. SMOOTH SCROLL
     ═══════════════════════════════════════════════════════ */
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

  /* ═══════════════════════════════════════════════════════
     14. ACTIVE NAV HIGHLIGHT
     ═══════════════════════════════════════════════════════ */
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

  /* ═══════════════════════════════════════════════════════
     15. CONTACT FORM
     ═══════════════════════════════════════════════════════ */
  function initContactForm() {
    const form = $('#contact-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('.form-submit');
      const originalText = btn.textContent;

      btn.textContent = 'Sending...';
      btn.disabled = true;

      setTimeout(() => {
        btn.textContent = 'Sent! ✓';
        btn.style.background = '#10b981';
        form.reset();
        setTimeout(() => {
          btn.textContent = originalText;
          btn.style.background = '';
          btn.disabled = false;
        }, 2500);
      }, 1200);
    });
  }

  /* ═══════════════════════════════════════════════════════
     16. SCROLL PROGRESS BAR
     ═══════════════════════════════════════════════════════ */
  function initScrollProgress() {
    const bar = document.createElement('div');
    bar.className = 'scroll-progress';
    document.body.appendChild(bar);

    window.addEventListener('scroll', () => {
      const scrolled = window.scrollY;
      const total = document.documentElement.scrollHeight - window.innerHeight;
      const pct = (scrolled / total) * 100;
      bar.style.width = pct + '%';
    }, { passive: true });
  }

  /* ═══════════════════════════════════════════════════════
     17. SECTION LABEL ANIMATION — Typewriter for labels
     ═══════════════════════════════════════════════════════ */
  function initSectionLabels() {
    const labels = $$('.section-label');
    if (!labels.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('label-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    labels.forEach(label => observer.observe(label));
  }

  /* ═══════════════════════════════════════════════════════
     18. BIO SCROLL REVEAL — Staggered Word Blur & Fade (Framer style)
     ═══════════════════════════════════════════════════════ */
  function initBioScrollReveal() {
    const triggers = $$('.scroll-reveal-word-trigger');
    if (!triggers.length) return;

    triggers.forEach(el => {
      // Split text content into words
      const text = el.textContent.trim();
      const words = text.split(/\s+/);
      
      // Wrap each word in a span with staggered transition delay
      el.innerHTML = words.map((word, i) => {
        if (!word) return '';
        return `<span class="scroll-reveal-word" style="transition-delay: ${i * 0.03}s;">${word}</span>`;
      }).join(' ');

      // Set up IntersectionObserver
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const spans = $$('.scroll-reveal-word', entry.target);
              spans.forEach(span => {
                span.classList.add('in-view');
              });
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.1, rootMargin: '0px 0px -5% 0px' }
      );

      observer.observe(el);
    });
  }

  /* ═══════════════════════════════════════════════════════
     19. BIO CARD 3D SCROLL — Perspective Rotation on Scroll
     ═══════════════════════════════════════════════════════ */
  function initBioCard3DScroll() {
    const card = $('#intro-card');
    const introSection = $('#intro');
    if (!card || !introSection) return;

    function updateCard3D() {
      const rect = introSection.getBoundingClientRect();
      const viewHeight = window.innerHeight;
      
      // Calculate scroll progress (0 when section top is at screen bottom, 1 when section bottom is at screen top)
      const progress = Math.max(0, Math.min(1, (viewHeight - rect.top) / (viewHeight + rect.height)));
      
      // Map progress to 3D rotation variables
      // Initial state: rotateY = -18deg, rotateX = 12deg, scale = 0.92
      // Ease fast so it aligns perfectly flat when fully in view
      const easeProgress = Math.min(1, progress * 1.45);
      
      const rotY = -18 * (1 - easeProgress);
      const rotX = 12 * (1 - easeProgress);
      const scale = 0.92 + 0.08 * easeProgress;
      
      card.style.transform = `perspective(1200px) rotateY(${rotY}deg) rotateX(${rotX}deg) scale(${scale})`;
    }

    window.addEventListener('scroll', updateCard3D, { passive: true });
    updateCard3D();
  }

  /* ═══════════════════════════════════════════════════════
     20. MANIFESTO SCROLL DRAW — Highlighting words on scroll progress
     ═══════════════════════════════════════════════════════ */
  function initScrollDrawingManifesto() {
    const textEl = $('#scroll-draw-text');
    const section = $('#manifesto');
    if (!textEl || !section) return;

    // Split text into individual words wrapped in spans
    const text = textEl.textContent.trim();
    const words = text.split(/\s+/);
    textEl.innerHTML = words.map(word => 
      `<span class="scroll-draw-word">${word}</span>`
    ).join(' ');

    const spans = $$('.scroll-draw-word', textEl);

    function updateHighlight() {
      const rect = section.getBoundingClientRect();
      const viewHeight = window.innerHeight;
      
      // Scroll progress tracking inside the viewport middle range
      const startTrigger = viewHeight * 0.85;
      const endTrigger = viewHeight * 0.15;
      const totalRange = startTrigger - endTrigger + rect.height;
      const progress = Math.max(0, Math.min(1, (startTrigger - rect.top) / totalRange));
      
      // Calculate how many words should be highlighted
      const totalWords = spans.length;
      const highlightedCount = Math.floor(progress * totalWords * 1.05); // boost slightly to guarantee full highlight at end

      spans.forEach((span, idx) => {
        if (idx < highlightedCount) {
          span.classList.add('highlighted');
        } else {
          span.classList.remove('highlighted');
        }
      });
    }

    window.addEventListener('scroll', updateHighlight, { passive: true });
    updateHighlight();
  }

  /* ═══════════════════════════════════════════════════════
     21. PROJECTS 3D SPIRAL HELIX — Kinetic Floating Showcase
     ═══════════════════════════════════════════════════════ */
  /* ═══════════════════════════════════════════════════════
     21. PROJECTS HORIZONTAL KINETIC SCROLL — Side-by-side Showcase
     ═══════════════════════════════════════════════════════ */
  function initProjectsHorizontalScroll() {
    const projectsSection = $('#projects');
    const track = $('#horizontal-track');
    if (!projectsSection || !track) return;

    // Define projects with their premium assets
    const projects = [
      { img: 'portfolio_kolm.jpg', category: 'Industrial Design & Packaging', title: 'KOLM Coffee / Specialty Canister' },
      { img: 'portfolio_lunare.jpg', category: 'Haute Couture & E-Commerce', title: 'LUNARE Maison / Fashion House' },
      { img: 'portfolio_kiro.jpg', category: 'Creative Direction & Apparel', title: 'KIRO / Brand Identity Packaging' },
      { img: 'portfolio_veda.jpg', category: 'Spatial Design & Architecture', title: 'Veda Restaurant / Atmosphere' },
      { img: 'portfolio_chai.jpg', category: 'Identity & Tactile Cardstock', title: 'Chai Thadi / Streetways Brew' },
      { img: 'portfolio_dakshin.jpg', category: 'Branding & Eco Takeaway', title: 'Dakshin Canteen / Takeaway Packaging' },
      { img: 'portfolio_sinua.jpg', category: 'Luxury Cosmetics & Foil Stamping', title: 'Sinua / Foil-Stamped Cardstock' },
      { img: 'portfolio_crumb.jpg', category: 'Visual Identity & Luxury Packaging', title: 'Crumb Club / Artisan Patisserie' }
    ];

    // Shuffle the photos randomly on load to keep it dynamic and fresh!
    function shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    }
    const shuffledProjects = shuffleArray([...projects]);

    // Static array of premium organic tilts to distribute among cards
    const tilts = [-3, 2, -1.5, 3, -2, 1, -2.5, 2];

    // Build card elements dynamically side-by-side with individual custom tilts
    track.innerHTML = shuffledProjects.map((project, index) => {
      const tilt = tilts[index % tilts.length];
      return `
        <div class="project-horizontal-card" data-index="${index}" style="--card-tilt: ${tilt}deg; transform: rotate(${tilt}deg);">
          <img src="${project.img}" alt="${project.title}" class="card-img">
          <div class="card-overlay">
            <div class="card-overlay-body">
              <span class="card-category">${project.category}</span>
              <h3 class="card-title">${project.title}</h3>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Scroll calculations with LERP momentum
    let targetProgress = 0;
    let currentProgress = 0;
    let rafId = null;

    function renderScroll(progress) {
      // Calculate scroll limits based on scrollWidth and window.innerWidth
      const maxTranslate = Math.max(0, track.scrollWidth - window.innerWidth);
      const translateVal = -progress * maxTranslate;

      // Translate the entire track horizontally
      track.style.transform = `translate3d(${translateVal}px, 0, 0)`;
    }

    function renderLoop() {
      const diff = targetProgress - currentProgress;
      if (Math.abs(diff) < 0.0001) {
        currentProgress = targetProgress;
        renderScroll(currentProgress);
        rafId = null;
        return;
      }

      // Smooth LERP easing (0.08) for premium fluid feel
      currentProgress += diff * 0.08;
      renderScroll(currentProgress);
      rafId = requestAnimationFrame(renderLoop);
    }

    function updateScrollTarget() {
      const rect = projectsSection.getBoundingClientRect();
      const sectionHeight = rect.height;
      const viewHeight = window.innerHeight;

      // Calculate how far we've scrolled inside the sticky container
      const scrolledPast = -rect.top;
      const scrollableDist = sectionHeight - viewHeight;
      targetProgress = Math.max(0, Math.min(1, scrolledPast / scrollableDist));

      if (!rafId) {
        rafId = requestAnimationFrame(renderLoop);
      }
    }

    window.addEventListener('scroll', updateScrollTarget, { passive: true });
    window.addEventListener('resize', () => {
      // Trigger instant recalculation on resize
      updateScrollTarget();
      currentProgress = targetProgress;
      renderScroll(currentProgress);
    }, { passive: true });

    // Initial positioning
    updateScrollTarget();
    currentProgress = targetProgress;
    renderScroll(currentProgress);
  }

  /* ═══════════════════════════════════════════════════════
     22. OS HUD REAL-TIME CLOCK - Removed
     ═══════════════════════════════════════════════════════ */

  /* ═══════════════════════════════════════════════════════
     23. DYNAMIC KEYBOARD DIAGNOSTICS TERMINAL EASTER EGG
     ═══════════════════════════════════════════════════════ */
  function initDiagnosticsTerminal() {
    const termOverlay = $('#terminal-overlay');
    const closeBtn = $('#terminal-close-btn');
    const logStream = $('#terminal-log-stream');
    if (!termOverlay || !closeBtn || !logStream) return;

    let keysPressed = [];
    const secretCode = 'opus';

    window.addEventListener('keydown', (e) => {
      // Prevent key caching issues if user is writing in inputs
      if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;

      keysPressed.push(e.key.toLowerCase());
      keysPressed = keysPressed.slice(-secretCode.length);

      if (keysPressed.join('') === secretCode) {
        openTerminal();
      }
    });

    closeBtn.addEventListener('click', closeTerminal);
    termOverlay.addEventListener('click', (e) => {
      if (e.target === termOverlay) closeTerminal();
    });

    function openTerminal() {
      termOverlay.classList.add('open');
      keysPressed = []; // Clear sequence cache
      
      // Simulate live system compilation logs!
      logStream.innerHTML = `
        <div class="log-line text-accent">&gt;&gt; INITIALIZING OPUS_OS CORE ARCHIVE PANEL...</div>
        <div class="log-line">&gt;&gt; LOADING VOLUMETRIC GLASS ORBIT PARTICLES... [OK]</div>
        <div class="log-line">&gt;&gt; LAT_LNG TARGET: Nagpur, Maharashtra (21.14N 79.08E)</div>
        <div class="log-line">&gt;&gt; ACTIVE STACK: 8 Shuffled AI Portfolio Files Loaded</div>
        <div class="log-line">&gt;&gt; GRAPH FACTOR: Hardware Accelerated rAF 3D Perspective</div>
        <div class="log-line">&gt;&gt; LERP MOMENTUM: Active (Diff factor 0.08, inertia enabled)</div>
        <div class="log-line">&gt;&gt; ACTIVE LIMIT: 3 Client Sprint Milestones Engaged</div>
        <div class="log-line text-accent">&gt;&gt; SYSTEMS STATUS: COGNITIVE TEMPERATURE NOMINAL.</div>
      `;

      // Tick dynamic telemetry pulse lines to make it feel alive!
      let counter = 0;
      const interval = setInterval(() => {
        if (!termOverlay.classList.contains('open')) {
          clearInterval(interval);
          return;
        }
        counter++;
        const line = document.createElement('div');
        line.className = 'log-line';
        line.textContent = `>> telemetry_pulse_tick_${counter} latency: ${(Math.random() * 6 + 2).toFixed(1)}ms [system_call: operative]`;
        logStream.appendChild(line);
        logStream.scrollTop = logStream.scrollHeight;
      }, 1200);
    }

    function closeTerminal() {
      termOverlay.classList.remove('open');
    }
  }

  /* ═══════════════════════════════════════════════════════
     24. TACTILE MAGNETIC BUTTONS — Proximity Attraction Spell
     ═══════════════════════════════════════════════════════ */
  function initMagneticButtons() {
    const magneticBtns = $$('.hero-cta-btn, .nav-cta-desktop, .cta-banner-btn, .form-submit');
    if (!magneticBtns.length) return;

    magneticBtns.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        // Pull the button towards cursor, but limit the translation to max 12px
        const pullX = x * 0.35;
        const pullY = y * 0.35;

        btn.style.transform = `translate3d(${pullX}px, ${pullY}px, 0) scale(1.02)`;
        const arrow = btn.querySelector('.arrow');
        if (arrow) {
          arrow.style.transform = 'translate(3px, -3px) scale(1.1)';
        }
      });

      btn.addEventListener('mouseleave', () => {
        // Smoothly return back to baseline using a spring easing
        if (typeof anime !== 'undefined') {
          anime({
            targets: btn,
            translateX: 0,
            translateY: 0,
            scale: 1,
            duration: 650,
            easing: 'cubicBezier(0.34, 1.56, 0.64, 1)'
          });
          const arrow = btn.querySelector('.arrow');
          if (arrow) {
            anime({
              targets: arrow,
              translateX: 0,
              translateY: 0,
              scale: 1,
              duration: 500,
              easing: 'easeOutQuad'
            });
          }
        } else {
          btn.style.transform = '';
        }
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     25. HUD CLOCK — Real-Time Systems Telemetry
     ═══════════════════════════════════════════════════════ */
  function initHUDClock() {
    const clockEl = $('#hud-clock');
    if (!clockEl) return;

    function updateClock() {
      const now = new Date();
      const hrs = String(now.getUTCHours()).padStart(2, '0');
      const mins = String(now.getUTCMinutes()).padStart(2, '0');
      const secs = String(now.getUTCSeconds()).padStart(2, '0');
      clockEl.textContent = `${hrs}:${mins}:${secs} UTC`;
    }

    setInterval(updateClock, 1000);
    updateClock();
  }

  /* ═══════════════════════════════════════════════════════
     INIT
     ═══════════════════════════════════════════════════════ */
  document.addEventListener('DOMContentLoaded', () => {
    animateHero();
    initParallax();
    initScrollReveal();
    initStatsCounter();
    initServicesAccordion();
    initProcessHovers();
    initProjectHovers();
    initPricingHovers();
    initTestimonialHovers();
    initFAQ();
    initSmoothScroll();
    initActiveNavHighlight();
    initContactForm();
    initScrollProgress();
    initSectionLabels();
    initBioScrollReveal();
    initBioCard3DScroll();
    initScrollDrawingManifesto();
    initProjectsHorizontalScroll();
    initDiagnosticsTerminal();
    initMagneticButtons();
    initHUDClock();
  });
})();


