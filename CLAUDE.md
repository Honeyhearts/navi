# Navi — Project CLAUDE.md

## HQ Locations
- **Code:** `~/Documents/HQ/Projects/Navi/code/` (this repo)
- **Knowledge:** `~/Documents/HQ/Projects/Navi/` — read its `AGENTS.md` first (filing rules, project map, read order)
  - Plans and roadmap source → `~/Documents/HQ/Projects/Navi/Docs/Active Plans/`
  - Decision records → `~/Documents/HQ/Projects/Navi/Docs/decisions/`
  - Research & the architecture PDF → `~/Documents/HQ/Projects/Navi/Reference/`
  - Handoffs and finished plans → `~/Documents/HQ/Projects/Navi/Docs/Archive/`
  - Visual assets → `~/Documents/HQ/Projects/Navi/Assets/`
  - Marketing copy → `~/Documents/HQ/Projects/Navi/Marketing/`
  - Legal docs → `~/Documents/HQ/Projects/Navi/Legal/`
- Read `~/.claude/CLAUDE.md` for full HQ structure and output rules.
- Registry alias: the vault registry lists this project as "Familiar (Navi)".

## Product
Navi is a consumer AI agent platform. "Navigate your life." Pre-configured, personality-rich AI agents for non-technical users.

## Design System
Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.
Always read brand-voice.md when creating copy, marketing, dialogue material for Navi. 
If changes to how written material is produced is requested that has to do with language, vocabulary, tone, remember the shift made so all future material can follow that thread.

## Key Files
- `DESIGN.md` — visual identity and design system (ocean + sage palette, Fraunces + General Sans)
- 'brand-voice.md' - the underlying tone and arrow of intent for language, marketing, and voice of Navi
- `library/` — 36 persona files loaded at runtime by `context_library.py`
- `docs/index.html` — the GitHub Pages landing page
- Status index: `~/Documents/HQ/Projects/Navi/Docs/Archive/Handoffs Mar-Apr 2026/Handoff Apr 2026.md`
- Production architecture: `~/Documents/HQ/Projects/Navi/Docs/Active Plans/Agent Platform Architecture Mar 2026.md`
- Design doc: `~/Documents/HQ/Projects/Navi/Docs/Archive/Conference Test Flight Mar-Apr 2026/Test Flight Design Mar 2026.md`
- CEO plan: `~/Documents/HQ/Projects/Navi/Docs/Archive/Conference Test Flight Mar-Apr 2026/CEO Plan Mar 2026.md`

## Never Into HQ
`.env` (live Telegram token, founder chat id, OpenRouter key), `navi.db` (conference users' PII), `backups/`. All gitignored.
