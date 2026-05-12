# 001: 3D Card CSS + Cursor Lerp Validation

## Question
Given our Opus design requiring 4 floating 3D cards with perspective transforms and a custom cursor with lerp-based ring expansion, can we implement these with pure CSS and vanilla JS that perform smoothly?

## Risk
- 3D transforms may cause z-fighting or odd stacking contexts
- Cursor lerp with `requestAnimationFrame` may feel sluggish or jittery
- Mobile cursor should be disabled
- Performance on low-end devices

## Approach

### 3D Cards
- `perspective: 1400px` on container
- `transform-style: preserve-3d` on cards
- Individual cards: `rotateY`, `rotateX`, `translateZ` with distinct values
- `@keyframes float` animation: `translateY` from 0 to -18px, ease-in-out, 6s infinite, staggered delays
- Box shadows with amber gradient glow

### Custom Cursor
- Hide default: `html { cursor: none; }`
- Amber dot: 6px fixed position, follows mouse exactly
- Ring: 32px base, lerp factor 0.12 (12%) using `requestAnimationFrame`
- On hover over `<a>` or `<button>`: ring expands to 52px
- Disable on mobile via `@media (hover: none)` detection

## Build
Simple HTML file with inline CSS/JS to demonstrate both working together.

## Expected Behavior
- 3D cards float smoothly, no jitter
- Cursor dot tracks mouse instantly
- Cursor ring lerps smoothly behind dot (12% smoothing)
- Ring expands on interactive elements
- Animations at 60fps

## Verdict: VALIDATED

### What worked
- 3D cards: using outer `.card` for transforms and inner `.card-inner` for float animation prevents transform override. Works smoothly at 60fps in test.
- Cursor lerp: 12% factor produces smooth trailing; instant dot feels responsive.
- Hover expansion: class toggle on body works, transitions smooth.
- Mobile detection: `@media (hover: none)` correctly hides custom cursor.

### What didn't
None.

### Surprises
None.

### Recommendation for the real build
- Use the same wrapper pattern for 3D cards (outer: rotate/translateZ; inner: float translateY).
- Cursor: keep separate dot and ring elements; use rAF; disable on mobile.
- Add `will-change: transform` for optimization (optional).
- Ensure cursor dot and ring are centered by subtracting half dimensions.
