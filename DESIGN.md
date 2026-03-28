# Design System — Navi

## Product Context
- **What this is:** Consumer AI agent platform. Pre-configured, personality-rich agents for non-technical users.
- **Who it's for:** Motivated, productive people who want an AI companion without the setup wall.
- **Space/industry:** Consumer AI / personal productivity. Competes on curation and personality, not infrastructure.
- **Project type:** Landing page + Telegram bot (conference test flight), then mobile app.

## Aesthetic Direction
- **Direction:** Organic Warmth — grounded, personal, crafted. Not a tech product. A companion.
- **Decoration level:** Intentional — subtle grain texture, colored card accents, tag pills. Enough to signal care, not enough to distract.
- **Mood:** Morning light through a coastal forest. Warm but clear. Calm but alive. The feeling of someone thoughtful already handling what you forgot.
- **Key differentiators:** Serif display font (uncommon in AI products), two-hue organic palette (ocean + sage), editorial layout with bento grid.

## Typography
- **Display/Hero:** Fraunces (variable, opsz 9-144, weight 300-600) — warm, slightly quirky serif with optical sizing. Beautiful at large sizes. Says "I have soul" in a space full of geometric sans.
- **Body:** General Sans (weight 400-700) — clean, geometric, warm. Excellent readability.
- **UI/Labels:** General Sans 600, uppercase with 0.06-0.1em letter-spacing for tags/labels.
- **Data/Tables:** General Sans (tabular-nums) or JetBrains Mono for monospaced data.
- **Code:** JetBrains Mono 400/500.
- **Loading:** Google Fonts CDN — `family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300;1,9..144,400&family=General+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500`
- **Scale:**
  - Display hero: clamp(48px, 7vw, 88px) / weight 300 / letter-spacing -0.03em
  - Display section: clamp(32px, 4vw, 52px) / weight 300 / letter-spacing -0.02em
  - Heading card: 22px / weight 400
  - Body large: 19px / weight 400
  - Body: 16px / weight 400
  - Body small: 14px / weight 400
  - UI label: 13px / weight 600 / uppercase / letter-spacing 0.02em
  - Tag: 11px / mono / uppercase / letter-spacing 0.1em
  - Mono data: 12px / weight 400

## Color
- **Approach:** Two-hue organic system. Ocean = action, navigation. Sage = status, grounding. Two colors from nature that breathe together.
- **Light mode:**
  - Background: `#F6F8F9`
  - Elevated: `#EDF1F3`
  - Surface: `#FFFFFF`
  - Primary text: `#1A2028`
  - Muted text: `#6A7280`
  - Border: `#DEE2E6`
  - Border light: `#ECF0F2`
  - Ocean (primary accent): `#4E96BD`
  - Ocean hover: `#3D82A6`
  - Ocean deep: `#3A7294`
  - Ocean light: `#E8F2F8`
  - Ocean glow: `#4E96BD22`
  - Sage (secondary): `#6B8F71`
  - Sage hover: `#5A7D60`
  - Sage light: `#EDF4EF`
  - Sage muted: `#8AAD8F`
  - Success: `#5A9B6B`
  - Warning: `#C4A03A`
  - Error: `#C45B4A`
  - Info: `#4E96BD` (same as ocean)
- **Dark mode:**
  - Background: `#0F1316`
  - Elevated: `#161B20`
  - Surface: `#1C2228`
  - Primary text: `#E4E8EC`
  - Muted text: `#8A9098`
  - Border: `#262E34`
  - Border light: `#1E262A`
  - Ocean: `#5EA8D0`
  - Ocean hover: `#74B8DC`
  - Ocean deep: `#4A8CB2`
  - Ocean light: `#162230`
  - Ocean glow: `#5EA8D033`
  - Sage: `#7EA884`
  - Sage hover: `#92BC98`
  - Sage light: `#1A261C`
  - Success: `#6EAE7E`
  - Warning: `#D4B44E`
  - Error: `#D47060`
  - Info: `#5EA8D0`

## Spacing
- **Base unit:** 8px
- **Density:** Spacious — the product creates time and space in your life, the design should feel that way.
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64)
- **Section padding:** 96px vertical (desktop), 64px (mobile)
- **Card padding:** 36px (desktop), 24px (mobile)
- **Bento grid gap:** 16px

## Layout
- **Approach:** Creative-editorial with bento grid.
- **Grid:** Bento (mixed 1fr/2fr spans), 3-column desktop, 1-column mobile.
- **Max content width:** 1400px
- **Border radius:** sm: 6px, md: 10px, lg: 16px, full: 9999px (pills/tags)
- **Card accent:** 3px colored top border (ocean or sage) on bento cards for visual hierarchy.
- **Grain texture:** SVG noise overlay at 2% opacity. Adds tangible, physical quality.

## Motion
- **Approach:** Intentional — subtle, guiding. Nothing bounces or spins.
- **Easing:** enter(ease-out) exit(ease-in) move(ease-in-out)
- **Duration:** micro(50-100ms) short(150-250ms) medium(250-400ms) long(400-700ms)
- **Hover:** Cards lift 1px with shadow expansion. Buttons translate -1px with glow increase. 250ms ease.
- **Online indicator:** Gentle pulse animation, 2.5s ease-in-out infinite.

## Component Patterns
- **Primary CTA:** Ocean background, white text, 2px glow shadow, lifts on hover.
- **Secondary CTA:** Sage-light background, sage text, transparent border that appears on hover.
- **Tertiary/Ghost:** White background, text-primary, 1px border, border goes ocean on hover.
- **Tags/Pills:** Mono font, 11px uppercase, 1px border, rounded-full. Ocean or sage colored.
- **Badges:** Rounded-full, 12px font-weight-600. Color-coded: ocean (active), sage (online), warning, error.
- **Inputs:** 1px border, radius-md. Focus: ocean border + ocean glow ring (3px box-shadow).
- **Chat bubbles:** Agent = ocean-light bg + 3px ocean left border. User = sage-light bg.
- **Cards:** Surface bg, 1px border, radius-lg. Hover: ocean border + subtle ocean glow shadow.
- **Links:** Ocean color, underline, 3px underline-offset. Darker on hover.

## Logo
- **Wordmark:** "navi" in Fraunces, weight 400, 24px. Followed by a period "." in ocean color.
- **No icon/symbol yet.** Wordmark only for conference launch.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Initial design system | Created by /design-consultation. Organic warmth aesthetic with ocean + sage two-hue system. |
| 2026-03-28 | Fraunces serif for display | Deliberate differentiation from geometric sans-serif AI products. Serif says "soul." |
| 2026-03-28 | Ocean blue primary accent | Warm Pacific blue, not corporate. Navigator = ocean. Replaces copper from earlier iteration. |
| 2026-03-28 | Sage secondary hue | Growth, grounding, calm. The "land" to ocean's "water." Status and secondary elements. |
| 2026-03-28 | Grain texture overlay | 2% opacity SVG noise. Adds physical, tangible quality. Feels crafted, not generated. |
| 2026-03-28 | Bento grid layout | Asymmetric card sizes create visual interest. Avoids generic 3-column SaaS template feel. |
