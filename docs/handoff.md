# Handoff
Generated: 2026-04-03
Branch: feature/conference-test-flight
Directory: /Users/maitreya/Desktop/Navi

## Active Task
Building Navi — a consumer AI agent platform for solo operators (barbers, tattoo artists, attorneys, contractors). Current branch is the conference test-flight bot. We just completed a full `/plan-eng-review` pass and applied 4 code fixes directly to the codebase. The plan doc is updated, test plan artifact is written, and Eng Review is cleared. We are at the transition point between the conference bot (SQLite, single-file Python) and Phase 0 of the production Navi stack (Hermes Agent + Modal serverless + SOUL.md persona system).

## Current State
**Done this session:**
- `context_library.py` — module-level `_CACHE` added, disk reads only once at startup
- `dashboard.py` — rebound from `0.0.0.0` to `127.0.0.1` (security fix)
- `db.py` — empty kwargs guard added to `update_user()` (prevents SQL syntax error)
- `referrals.py` — `extract_referral_from_start("ref_")` now returns `None` not `""`
- `followup.py` — domain updated from `heynavi.com` → `naviagents.io`
- `docs/open-source-integration-strategy.md` — created, logs PDF framework decisions (pages 12-21)
- Design doc updated: pause/resume semantics, SOUL.md checksum spec, Phase 0 Modal checklist, CrewAI deferred to Phase 2, conference re-engagement blast message
- Test plan artifact written: `~/.gstack/projects/honeyhearts-navi/maitreya-feature-conference-test-flight-eng-review-test-plan-20260330-194619.md`

**In progress / not started:**
- 8 pytest tests from the test plan — NOT written yet
- Phase 0 build: SOUL.md templates (barber, tattoo, attorney archetypes), seed skills in agentskills.io format, manual provisioning script
- Modal account setup on Mac mini

## Key Decisions This Session
- **CrewAI deferred to Phase 2** — Phase 1 is single-agent-per-user; no multi-agent orchestration needed yet. Gate: 10% of attorney sessions need multi-step handoff.
- **`kill()` renamed to `pause()`/`resume()`** — Modal functions are stateless; no process to kill. Gate is routing layer only.
- **SOUL.md checksum in Navi DB** — SHA-256 stored in `profiles.soul_checksum`, verified once per conversation session. Mismatch → log + alert + pause agent.
- **Web form = lead capture, bot = trial onboarding** — `web_leads` table bridges form data into bot, pre-seeding profile so no duplicate questions.
- **Conference users: clean break** — they re-onboard in Phase 1. Blast re-engagement message when Phase 1 launches.
- **naviagents.io** — confirmed production domain. All placeholder URLs updated.
- **Mac mini is the server** — all terminal commands, installs, and bot-related tasks run on the Mac mini. Label explicitly in all instructions.

## Immediate Next Steps
1. **[Mac mini]** Install test infrastructure: `pip install pytest pytest-asyncio` + create `tests/` directory
2. **[Mac mini]** Write the 8 pytest tests from test plan (see test plan artifact above)
3. **[Mac mini]** `pip install modal && modal setup` — auth Modal account (needs browser, April 5 deadline)
4. **[Mac mini]** `pip install hermes-agent` (verify package name — may be `nous-hermes` or similar)
5. **[Either]** Write Phase 0 SOUL.md templates: barber, tattoo artist, attorney archetypes
6. **[Either]** Seed skills in agentskills.io format (appointment_reminder, intake_form, morning_briefing)
7. **[Either]** Write manual provisioning script (ProfileProvisioner stub)

## Open Questions / Blockers
- Hermes Agent exact pip package name — needs verification before install
- Modal account: does Matt have one already, or needs signup? (April 5 deadline for conference)
- Conference bot: still running live? If yes, the 5 code fixes on this branch need to be merged/deployed before the conference

## Changed Files
 context_library.py | 10 ++++++++--
 dashboard.py       |  2 +-
 db.py              |  2 ++
 followup.py        |  2 +-
 referrals.py       |  3 ++-
 5 files changed, 14 insertions(+), 5 deletions(-)

## DO NOT MODIFY
- `bot.py` — core Telegram message handler, working in production
- `morning.py` — cron job, working in production
- `schema.sql` — conference schema, clean break planned but not executed yet
