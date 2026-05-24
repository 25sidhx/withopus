# Opus Design System: Warm Cinematic Minimalism

## 1. Brand Design Philosophy
Our visual philosophy is **Warm Cinematic Minimalism**. We reject the sterile, overly bright, and generic aesthetic of modern SaaS and agency templates. Every interaction with Opus should feel like a carefully graded film—intentional, moody, and premium. Space is our primary luxury. We do not fill corners just to occupy them; we allow elements to breathe within a vast, dark canvas. The brand relies on three pillars: **Warmth** (an amber-to-violet signature gradient), **Texture** (film-like grain adding organic depth), and **Space** (massive intentional voids).

## 2. Emotional Experience Goals
The user should feel they have entered a curated gallery. The interface must evoke:
- **Quiet Confidence:** We state things; we do not hedge or over-explain. The design should feel authoritative yet deeply human.
- **Cinematic Depth:** Users should feel immersed, as if viewing a masterpiece in a dimly lit room where only the art is illuminated.
- **Premium Restraint:** The experience must scream quality not through abundance, but through deliberate omission. If an element does not add, it subtracts.

## 3. Typography System
Our typography creates tension between confident display and highly functional utility. 
- **Primary Font (Headings & Display): Satoshi.** Used exclusively for headlines, wordmarks, and hero copy. It provides a clean, geometric, and modern feel.
  - *Weights:* 300 (Light) for massive display headers; 400 (Regular) for section titles; 500 (Medium) for sub-headings.
  - *Rule:* Never use heavy weights (700+) for headings. Heavy feels aggressive; light feels premium.
- **Secondary Font (Body & Utility): Inter.** Used for all long-form reading, UI text, and functional data.
  - *Weights:* 400 (Regular), 500 (Medium) for active states.
  - *Labels:* All-caps, tracked out (+0.15em) for metadata and tags.

## 4. Color System
Our palette is rooted in the absence of light, pierced by organic warmth.
- **Void Black (`#0D0B14`):** The primary canvas. All content lives in this deep, rhythmic darkness.
- **Warm Cream (`#F5F0E8`):** The primary text color. Never use pure white (`#FFFFFF`).
- **The Opus Gradient (Signature):** A linear left-to-right gradient moving through Amber (`#E8A034`) → Burnt Orange (`#D4431A`) → Crimson (`#7A1530`) → Deep Violet (`#3D1155`). This is not a decoration; it is the brand's lifeblood. It must always be overlaid with a 5–8% noise/grain texture.
- **Surface Dark (`#13101E`) & Surface Mid (`#2A2535`):** Used for subtle card backgrounds and interaction states.

## 5. Layout/Grid System
The layout feels breathable, cinematic, and controlled.
- **The Asymmetric Grid:** Do not default to centered content. Use a 12-column grid but allow text to anchor to the left while imagery or empty space dominates the right. 
- **The 80px Rule:** A mandatory minimum safe zone of 80px around core content containers. 
- **Focal Singularity:** Only one primary focal point per viewport. Never force the user to decide where to look first.

## 6. Spacing Rules
Whitespace is an active design element, not an empty container.
- **Micro (4px/8px):** For strict grouping of icon and label.
- **Component (16px/24px):** Inside buttons, cards, and input fields.
- **Section (80px/120px+):** Between major content blocks. If a section transition feels too close, double the space. 

## 7. Component Standards
- **Buttons:** Sharp, intentional geometry. No playful rounded corners (`0px` or max `2px` radius). Primary buttons use the Opus Gradient (with grain) and Warm Cream text. Hover states shift the gradient angle slightly.
- **Cards:** Background `Surface Dark` (`#13101E`). No borders. Separation is achieved purely through the tonal shift from `Void Black`. 
- **Inputs & Forms:** Minimalist. A single bottom border in `Surface Mid` (`#2A2535`) that glows Amber (`#E8A034`) on focus. Labels sit inside the void.
- **Dividers:** Prohibited. Do not use 1px lines to separate content. Use whitespace.

## 8. Motion & Interaction Guidelines
Motion must feel smooth, deliberate, and cinematic—never bouncy or hyperactive.
- **Easing:** `cubic-bezier(0.25, 0.1, 0.25, 1.0)` for a slow-start, smooth-finish cinematic glide.
- **Durations:** 300ms for micro-interactions; 600ms–800ms for page or section transitions.
- **Hover States:** Instead of drop shadows, buttons and cards should slightly lift in tonal brightness or experience a subtle gradient shift. Text reveals should fade up from below, mimicking a slow cinematic reveal.

## 9. Responsive Behavior Rules
- **Mobile-First Intentionality:** On small screens, the cinematic feel is maintained by ensuring text does not touch the edges (minimum 24px padding). The gradient bloom should shift to accommodate vertical scrolling.
- **Adaptive Typography:** `display-lg` scales down drastically on mobile to maintain the generous white space. 

## 10. Accessibility Standards
- **Contrast:** `Warm Cream` on `Void Black` guarantees a ~14:1 contrast ratio.
- **Focus States:** A clear `Amber` 2px outline for keyboard navigation. We do not compromise accessibility for aesthetics.
- **Legibility:** Body text is strictly `Inter` with a minimum 1.6 line-height for effortless reading. 

## 11. Design Tokens
- `color-bg-primary`: `#0D0B14`
- `color-text-primary`: `#F5F0E8`
- `color-text-muted`: `#6B6478`
- `color-surface-1`: `#13101E`
- `color-surface-2`: `#2A2535`
- `color-accent-amber`: `#E8A034`
- `gradient-opus`: `linear-gradient(90deg, #E8A034, #D4431A, #7A1530, #3D1155)`
- `font-display`: `'Satoshi', sans-serif`
- `font-body`: `'Inter', sans-serif`
- `spacing-safe`: `80px`

## 12. Implementation Recommendations
- **CSS Architecture:** Map all colors and typography to CSS custom properties (variables) at the `:root` level. 
- **Tailwind Extension:** Extend the Tailwind theme config to include `void`, `cream`, `amber`, `crimson`, and `violet`. Create a custom utility plugin for the `.bg-opus-gradient` that automatically applies the SVG noise filter.
- **Grain Filter:** Use an SVG filter overlay `mix-blend-mode: overlay` at 5-8% opacity fixed over the viewport or gradient containers.

## 13. Visual Consistency Rules
- **One Rule to Rule Them All:** If a component looks like it belongs in a generic SaaS dashboard, delete it. 
- Every image must be color-graded to match the warm, lifted-black aesthetic.
- Never place gradient text on a gradient background. 

## 14. Common Mistakes To Avoid
- ❌ Using pure `#FFFFFF` white or `#000000` black.
- ❌ Applying heavy drop shadows to create depth.
- ❌ Center-aligning long paragraphs of text.
- ❌ Using the Opus Gradient without the accompanying noise/grain texture.
- ❌ Using bold (700+) weights for Satoshi headlines.

## 15. Final Design System Philosophy
The Opus Design System is not just a collection of Hex codes and fonts. It is an operating system for brand perception. It requires discipline to execute properly—the discipline to leave a section empty, the discipline to use a light font weight when everyone else is shouting in bold, and the discipline to let the work speak for itself. We are building an atelier, not a factory.
