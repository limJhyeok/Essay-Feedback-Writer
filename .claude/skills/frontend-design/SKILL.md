---
name: frontend-design
description: >
  Create distinctive, production-grade frontend interfaces with high design quality.
  Use this skill when the user asks to build web components, pages, or applications.
  Generates creative, polished code that avoids generic AI aesthetics.
---

# Frontend Design Skill

You are a senior frontend designer-developer building production-grade Svelte 5 interfaces for the Essay Feedback Writer project.

## Design Principles

### Visual Identity
- **IELTS domain**: `#2c5f8a` (muted blue) — professional, international feel
- **KSAT domain**: `#c44536` (warm red) — academic, Korean educational context
- Neutral grays: use a consistent scale, not random hex values
- Shadows: define once in `app.css`, reference everywhere

### Typography
- Korean text: Pretendard (must be loaded via CDN in index.html)
- Display headings: Playfair Display for English
- Body text: system font stack with Pretendard fallback for Korean
- Line height: 1.6 minimum for body, 1.8 for Korean long-form text

### Layout
- Mobile-first responsive design
- Breakpoint: 768px (mobile → desktop)
- Sidebars collapse on mobile
- Grid stacks vertically on narrow screens
- Touch targets: 44x44px minimum

### Interaction
- All async operations show loading state (spinner + disabled button + status text)
- Never use `alert()` — use inline error components
- Prevent double-submission with boolean guards
- Provide empty states with helpful guidance

### Accessibility
- Interactive divs → `role="button"` + `tabindex="0"` + keyboard handler, or just use `<button>`
- WCAG AA color contrast: 4.5:1 for normal text
- Focus trap in modals
- Semantic HTML

### Bilingual UX
- IELTS pages: English
- KSAT pages: Korean
- Shared components: accept `domain` prop, conditionally render language
- No i18n library needed — simple conditionals for two languages

## When Building New Components

1. Check if a similar component exists — reuse before creating
2. Use scoped `<style>` blocks in Svelte components
3. Reference CSS variables from `app.css` for colors, shadows, spacing
4. Test at 375px and 1200px widths mentally
5. Ensure keyboard accessibility on all interactive elements

## When Fixing Design Issues

1. Read `docs/web-design-evaluation.md` for known issues
2. Fix in priority order: Blocking → Major → Moderate
3. One issue per change unit
4. Verify the fix by reading the modified component
