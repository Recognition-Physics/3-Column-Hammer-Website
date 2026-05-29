---
name: frontend-design
description: Create production-grade frontend that matches the VibeVoice Hammer demos — light futuristic glass UI, red-forward accents, Outfit + Plus Jakarta Sans. Use for web components, landing sections, dashboards, or styling/beautifying UI in this repo.
license: Complete terms in LICENSE.txt
---

This skill guides distinctive, production-grade interfaces aligned with **this repository’s Hammer / VibeVoice realtime and voice demos**: modern, slightly futuristic, **light glass surfaces** with **Hammer red** as the primary accent (not blue or purple as the hero color).

The user may ask for a component, page, layout, or polish pass. Implement real working code with strong aesthetic consistency to the existing site.

## Default direction for this repo

Unless the user explicitly requests something else (e.g. dark mode only, print, third-party embed):

- **Tone**: Light, confident, “product demo” futurism — **glass panels**, soft depth, crisp type, restrained motion. Think precision instrument, not gamer RGB.
- **Accent hierarchy**: **Red first** (`#c91e1e` → `#e03030`, glow `rgba(201, 30, 30, 0.2–0.45)`). Use **cool blue** only as a **sparse atmospheric secondary** (mesh highlights, subtle conic accents) — never let blue compete with red for CTAs, focus rings, or key labels.
- **Surfaces**: Off-white / cool gray bases (`#f2f4f9`, `#ffffff`, faint ink `rgba(12, 15, 20, 0.08)` borders). Frosted glass: `backdrop-filter` + white semi-transparent fills + **inset top highlight**.
- **CTAs**: Red gradient pills, white label, inset highlight, red-tinted shadow — match `.landing-cta` / primary chrome patterns in `demo/realtime-sales-demo/web/src/landing-hero.css` and `style.css`.
- **Typography**: **Outfit** (display / headlines / UI emphasis) + **Plus Jakarta Sans** (body). Weights 600–800 for display moments; avoid Inter, Roboto, Arial as primary pairings.
- **Motion**: Purposeful only — hover lift on controls, staggered reveal if it earns its keep, **respect `prefers-reduced-motion`**. Avoid gratuitous parallax or novelty cursors unless requested.
- **Composition**: Clean grid, generous radius (`14–22px` cards, `999px` pills), optional **asymmetric hero** or mesh underlay that echoes existing `hero-scene` / underlay patterns — don’t invent a unrelated visual language.

## Hammer-aligned token crib (reference)

Reuse CSS variables where they already exist on `.app-shell--landing` / `:root` in this repo:

| Role | Typical values |
|------|----------------|
| Ink | `#0c0f14` / `--landing-ink` |
| Muted | `rgba(12, 15, 20, 0.58)` |
| Red core | `#c91e1e`, vivid `#e03030`, dark `#8f1010` |
| Red glow | `rgba(201, 30, 30, 0.22)` |
| CTA gradient | warm red linear (see `--landing-cta-gradient`) |
| Atmosphere | Optional **small** blue radial (`rgba(43, 127, 212, 0.05–0.08)`) — background only |

When adding new UI, **extend** these tokens rather than introducing a second palette.

## Design thinking (still apply)

Before coding, briefly anchor:

- **Purpose**: Who uses this screen and what’s the one outcome?
- **Constraints**: Framework (here: often Vite + vanilla or existing patterns), a11y, `prefers reduced motion`.
- **Differentiation**: Within brand — what makes *this* view memorable without breaking the Hammer look?

**CRITICAL**: In this repo, **intentionality beats novelty**. A bold direction should still read as the **same product family** as `landing-hero.css` / `style.css`.

## Implementation quality bar

- Production-grade, accessible focus states (visible outline; red or ink — consistent with existing `:focus-visible` patterns).
- Cohesive **glass + red accent** language; no clashing neon blues or default Material blues on primary actions.
- Atmosphere via **layered gradients and soft shadow**, not flat `#fff` boxes with harsh borders.
- **Do not** default to generic “AI slop”: purple-to-blue hero gradients, Inter-only stacks, cookie-cutter card grids with no depth.

Match implementation depth to scope: a small fix needs surgical CSS; a new section can borrow underlay/shine/grid motifs from the landing nav panel and hero glass.

Remember: aim for interfaces that feel **designed for Hammer’s voice demos** — modern, trustworthy, and futuristic with **red** as the signal color.
