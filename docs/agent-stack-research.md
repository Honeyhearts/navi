# Navi Agent Stack Research
## OpenClaw vs Hermes — Capabilities, Persona Fit, and Security Architecture

**Status:** Research complete. Ready for planning.
**Date:** 2026-03-30
**Branch:** feature/conference-test-flight

**Related docs:**
- `docs/open-source-integration-strategy.md` — Framework evaluation (CrewAI, LangGraph, LangChain, Dify, etc.), phased roadmap, 5 architecture principles. Source: Navi_Agent_Architecture.pdf pages 12-21.
- `~/.gstack/projects/honeyhearts-navi/maitreya-feature/conference-test-flight-design-20260330-154753.md` — Full architecture design doc (office-hours output)

---

## Executive Summary

Navi's backend should be built on **Hermes Agent** (NousResearch, MIT license). The decision is driven by one architectural fact: Hermes Profiles create fully isolated agent instances per user — each with its own personality (SOUL.md), memory, skills, credentials, and Telegram bot token. That maps exactly to Navi's product model.

Navi's real engineering task is not "build an AI agent." It's **build the provisioning and configuration layer on top of Hermes** — the onboarding UI, the SOUL.md generator, the archetype skill library, the profile spawner — that makes a technically complex system feel like magic to a barber in Detroit.

---

## Part 1: What OpenClaw Is

OpenClaw is a local-first, open-source autonomous agent (originally "Clawdbot", Nov 2025, then briefly "Moltbot", then "OpenClaw"). It connects LLMs to real software via a central Gateway process. Messaging platforms — Telegram, WhatsApp, Discord, iMessage, Slack, Signal — are its primary user interface.

**GitHub:** 250,000 stars in 60 days (record, surpassing React's previous milestone). As of Feb 2026.

### What OpenClaw Can Actually Do

**Confirmed real-world uses (community-documented):**

- **Morning briefings** — Aggregates weather, calendar, emails, reminders, trending topics. Delivered to Telegram before work. Setup: ~30 minutes. Most common entry point for new users.
- **Multi-channel client communication inbox** — Unifies WhatsApp, Instagram, Email, Google Reviews into one AI-powered inbox with 24/7 auto-responses.
- **Client onboarding automation** — CRM webhook detects new client → reads data → executes multi-platform sequence: welcome email, folder creation, calendar invite, follow-up reminder.
- **Personal CRM + follow-up reminders** — Scans Gmail and Google Calendar, builds contact profiles, flags stale relationships with follow-up prompts.
- **Appointment detection from messages** — Detects "Your appointment is confirmed for..." patterns, auto-creates calendar events with buffers.
- **Overnight lead outreach** — "Every night at 1am, go through today's new Twitter followers with a business in their bio, write a personalized DM, and send it before I wake up."
- **Receipt → expense log** — Send photo to Telegram bot → reads vendor, date, amount, category → logs to accounting software.
- **Voice call guest confirmation** (SuperCall plugin) — Calls guests one-by-one to confirm attendance, collects notes, compiles summary. Fully automated.
- **Email triage in DRAFT-ONLY mode** — Composes responses for user review, never auto-sends. Includes injection protection.
- **3x daily habit/follow-up reminders with snooze** — Proactive check-ins at configurable times.

### OpenClaw Limitations for Navi

- **No per-user profile isolation.** One Gateway, one operator. Not designed for a platform where each user gets their own agent.
- **Skills are static.** 52 built-in skills; no self-authoring from behavior.
- **ClawJacked vulnerability (2026).** Local WebSocket allows attackers to hijack the agent and access device data. Still unpatched in some versions.
- **Memory is per-assistant, not layered.** No episodic + semantic + procedural memory stack.
- **Requires persistent machine.** Gateway needs a running host.

### OpenClaw Verdict for Navi

Viable for single-operator personal use. The Gateway architecture is strong for multi-channel coverage (especially Instagram/WhatsApp DMs). But the ClawJacked security exposure, static skills, and absence of per-user profile isolation disqualify it as Navi's backend for a consumer-facing multi-user platform.

---

## Part 2: What Hermes Agent Is

Hermes Agent is a self-improving autonomous agent framework by NousResearch. Released February 26, 2026. Latest version: v2026.3.28 ("hardening release"). MIT license.

It is both a model fine-tuning lineage (Hermes 2/3 — fine-tuned on Llama 3.1 using the Atropos RL framework for tool-calling accuracy) and a full agent runtime with memory, skills, scheduling, and multi-platform messaging.

**Install:** `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`

### What Hermes Can Actually Do

**Confirmed real-world uses:**

- **Scheduled intelligence delivery to Telegram** — "Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram." Natural language triggers create cron jobs. Results auto-deliver to the originating chat. (Documented in cron docs.)
- **Automated triage with self-correction** — Daily GitHub issue triage, summarized by severity, posted to Slack. Episodic memory corrects its own logic: "if it makes a mistake on day one, it learns and adjusts by day three." (Reviewed by real users.)
- **Trending topic reports** — Automated report for top 5 trending topics across Reddit and X. Real user: took ~1 hour to set up. (@0xsachi on X.)
- **Server monitoring via SSH** — "Check disk usage across three VPS instances, alert if partitions exceed 80%, compress largest log files." Manages SSH sessions autonomously.
- **Parallel research with subagents** — Multi-step research: find papers → extract findings → write summaries. Subagent spawning handles sequential tool chains.
- **Standup prep (documented example)** — Cron at 8:45am weekdays, reviews git logs, drafts standup update, delivers to Telegram.
- **Code generation + test execution** — FastAPI boilerplate with parameters, unit tests, execution. Quality scales with LLM backend (GPT-4o / Claude Sonnet = solid; local 70B = inconsistent).

### Hermes Core Architecture

**Profiles — the key feature for Navi:**
Each Hermes profile is a fully isolated agent instance with its own directory:
```
~/.hermes/profiles/<name>/
  config.yaml     — model, gateway, platform tokens
  .env            — API credentials (scoped per profile)
  SOUL.md         — agent identity and personality
  memories/       — persistent user model and session history
  sessions/       — conversation history (FTS5 indexed)
  skills/         — procedural memory, custom skill documents
```
> "Profiles let you run separate agents for different purposes — a coding assistant, a personal bot, a research agent."

**SOUL.md — persona definition:**
Slot #1 in the system prompt. Fully editable. Defines voice, role, personality, default behaviors. Seeded automatically; operator customizes. Can be overridden per-session via `/personality`.

**Skills System:**
- 40+ built-in tools
- Custom skills written as SKILL.md markdown files
- Agent auto-creates skills after complex tasks (5+ tool calls), errors it solved, non-trivial workflows
- Skills as procedural memory: agent saves approach for future reuse
- External skill directories configurable (shared team skills repo)
- Compatible with agentskills.io open standard
- Installable from ClawHub, LobeHub, GitHub repos

**Memory Architecture (3 layers):**
1. Session memory — current conversation context
2. Persistent memory — facts, preferences, user model across all sessions (FTS5 full-text search + LLM summarization)
3. Skill memory — solution patterns the agent learned and filed

**Scheduling:**
- Natural language: "Every morning at 9am, run X and send to Telegram"
- Standard cron: `/cron add "0 9 * * *" "Morning briefing"`
- One-shot: "30m" (run once in 30 minutes)
- Results auto-deliver to originating chat
- Output archived to `~/.hermes/cron/output/<job-id>/<timestamp>.md`

**Deployment:**
- Local machine, Docker, SSH, Daytona, Singularity, Modal
- Serverless (Modal/Daytona): near-$0 idle cost; hibernates when inactive
- $5 VPS minimum for persistent deployment
- MIT license; you only pay LLM API costs

### Hermes Limitations

- **Not plug-and-play.** Requires Python config, CLI comfort, source-code debugging. Setup: 1+ hour for technical users.
- **Self-improving memory requires volume.** Patterns emerge after 20–30 repeated interactions. One-off tasks gain no benefit.
- **LLM quality determines output quality.** GPT-4o and Claude Sonnet: solid. Local 70B models: struggle with tool selection and multi-step planning.
- **No native Windows.** WSL2 required.
- **No built-in consumer provisioning UI.** Each profile is manually configured. Navi must build this layer.
- **Documentation sparse post-launch.** Some features require reading source code.
- **Natural language cron is flexible but less deterministic** than interval-based scheduling for precise business workflows.

---

## Part 3: Persona-to-Capability Map

### Pain Theme 1: Scheduling Chaos
*Barber, Dog Groomer, Hair Salon, Massage Therapist, Personal Trainer, Fitness Studio*

| Capability | OpenClaw | Hermes |
|---|---|---|
| Morning "who's coming in today" briefing | ✅ Documented | ✅ Documented (cron + Telegram) |
| Appointment reminder sent to client | ✅ Via messaging channels | ✅ Via cron + skill |
| Detect no-reply → send follow-up | ✅ CRM follow-up logic | ✅ Multi-step workflow via skill |
| Reactivation ("haven't seen you in 6 weeks") | ✅ CRM health scores | ✅ Persistent memory + cron |
| Instagram/WhatsApp DM triage | ✅ Multi-channel inbox | ❌ Not documented |

**Edge: OpenClaw** for Instagram/WhatsApp DM handling. Hermes covers Telegram natively; multi-channel social is OpenClaw's strength.

---

### Pain Theme 2: Inquiry Overwhelm
*Tattoo Artist, Photographer, Life Coach, Freelance Copywriter, Social Media Manager*

| Capability | OpenClaw | Hermes |
|---|---|---|
| 24/7 first-response to inbound DMs | ✅ "24/7 auto-responses" documented | ✅ Telegram gateway always-on |
| Draft response for review (not auto-send) | ✅ DRAFT-ONLY mode documented | ✅ Configurable via SOUL.md |
| Triage complex vs standard inquiries | ✅ Routes by message type | ✅ Classification skill + flag |
| Pre/post appointment message sequences | ✅ Client onboarding automation | ✅ Cron-based sequence |
| Waitlist management | ❌ Not documented | ❌ Not documented |

**Edge: OpenClaw** for multi-platform inbound simultaneously. Hermes matches on Telegram-only contexts.

---

### Pain Theme 3: Admin Debt
*Attorney, Bookkeeper, Insurance Agent, Care Agency, SEN Consultant*

| Capability | OpenClaw | Hermes |
|---|---|---|
| Track outstanding documents per client | ✅ Personal CRM + health score | ✅ Persistent memory + morning flag |
| Draft follow-up for missing items | ✅ Email triage → draft | ✅ Natural language draft → send |
| Morning briefing: what's outstanding | ✅ Morning brief | ✅ Cron + memory query |
| Deadline flagging | ✅ Calendar + reminders | ✅ Persistent memory + cron alarm |
| Multi-step intake sequence | ✅ Client onboarding automation | ✅ Skills-based workflow |

**Edge: Hermes** for persistent per-client memory that deepens over time. OpenClaw's CRM requires explicit setup per contact; Hermes builds memory from conversations automatically.

---

### Pain Theme 4: Revenue Leakage
*Roofer, HVAC, Auto Detailer, Real Estate, Plumber, Events Company*

| Capability | OpenClaw | Hermes |
|---|---|---|
| Lead re-engagement | ✅ Overnight outreach documented | ✅ Cron + memory flag |
| Follow-up after estimate not converted | ✅ CRM health score + prompt | ✅ Memory + scheduled follow-up |
| After-job upsell / referral request | ✅ Sequence automation | ✅ Multi-step skill |
| New inquiry → immediate acknowledgment | ✅ 24/7 auto-response | ✅ Telegram always-on |
| Weekly revenue pipeline report | ✅ KPI snapshots documented | ✅ Cron + reporting skill |

**Even.** Both handle this well. OpenClaw has documented overnight outreach across more channels. Hermes knows *why* a lead went cold.

---

### Pain Theme 5: Compliance / Deadline Pressure
*Attorney, Care Agency, SEN Consultant*

| Capability | OpenClaw | Hermes |
|---|---|---|
| Morning flag: deadlines in next 48h | ✅ Calendar + daily briefing | ✅ Cron + persistent memory query |
| Alert when deadline < X days away | ✅ Background health checks | ✅ Cron + conditional alert |
| Track regulatory filing status | ❓ Requires custom skill | ✅ Persistent memory + skill |
| Cross-case deadline overview | ❓ Requires structured data source | ✅ Memory indexes across sessions |

**Edge: Hermes** — persistent cross-session memory is the deciding factor. Compliance tracking requires remembering context across many separate client conversations over weeks.

---

## Part 4: Backend Architecture for Navi on Hermes

```
Navi Platform
├── Onboarding UI (web)
│   ├── User selects archetype (barber, attorney, contractor, etc.)
│   ├── Answers 5-10 personalization questions
│   └── Triggers: SOUL.md generation + skill config + cron schedule
│
├── Hermes Profile Provisioner (backend service — Navi builds this)
│   ├── Creates ~/.hermes/profiles/<user_id>/
│   ├── Writes SOUL.md from archetype template + user answers
│   ├── Writes config.yaml (model, gateway, Telegram bot token)
│   ├── Installs archetype-specific skills from Navi skill library
│   └── Sets up cron: "Every morning at [user_time], run morning_briefing skill"
│
├── Navi Skill Library (per archetype — Navi builds this)
│   ├── /skills/barber/morning-briefing.md
│   ├── /skills/barber/appointment-reminder.md
│   ├── /skills/attorney/intake-coordinator.md
│   ├── /skills/attorney/deadline-tracker.md
│   └── ... (one purpose-built skill set per archetype category)
│
├── Security Middleware (Navi builds this — see Part 5)
│   ├── Input sanitization (injection scan on every inbound message)
│   ├── Per-user routing (message → correct profile only)
│   ├── Rate limiting per user
│   ├── Output sanitization (no credential leakage in responses)
│   └── Kill switch + audit log
│
└── Existing Navi Infrastructure
    ├── FastAPI dashboard (real-time stats — already built)
    ├── SQLite (user/session/referral tracking — already built)
    └── Telegram bot gateway (already built — integrates with Hermes gateway)
```

**How archetypes become personalizable:**
1. SOUL.md template per archetype — defines personality, role, default behaviors
2. Onboarding answers inject specifics: business name, client terminology, hours, communication style
3. Skills are pre-written, purpose-built per archetype category (not generic)
4. Hermes's self-improving skill memory means the agent writes *new* skills as it learns each user's specific patterns over time

---

## Part 5: Security Architecture

### Threat Model

LLM agents fail in predictable ways:
1. **Prompt injection** — hostile instructions hidden in messages, documents, or web content the agent reads
2. **Tool abuse** — agent tricked into invoking destructive or unauthorized tool calls
3. **Data exfiltration** — secrets, credentials, or user data leaked through logs or tool outputs
4. **Runaway spending** — uncontrolled LLM API or external service calls
5. **Memory poisoning** — malicious instructions written to persistent memory, persisting across sessions
6. **Secrets leakage** — API keys, tokens, or passwords surfacing in agent responses or logs

**The core insight:**
> The model is not the security boundary. The boundary is the orchestration layer, tool layer, and execution environment around it.
> The question is not "can the model be trusted" — it's "what can this agent do if the model is tricked."

---

### The Five Security Layers

**Layer 1 — Identity**
Every agent action tied to a specific user identity. No shared master keys. One Hermes profile per user, one Telegram bot token per profile, one credential set per archetype.

**Layer 2 — Permissions**
Tools are allowlisted and scoped per task, per user, and per session. Default-deny. Explicit allowlists only.

**Layer 3 — Tool Validation**
Structured inputs, schema validation, argument allowlists, explicit deny rules for anything destructive or ambiguous. No raw shell command construction from user text. No unrestricted file read/write or network access.

**Layer 4 — Execution Sandbox**
Code execution, file access, browser access, and network access all constrained by default. Assume compromise; limit blast radius.

**Layer 5 — Observability**
Immutable logs, redaction of secrets before logging, alerts for risky actions or unusual tool chains.

---

### What Hermes Ships With (Built-In)

**User Authorization:**
- Default posture: all users denied unless explicitly allowlisted
- DM pairing: 8-character cryptographic code, 1-hour TTL, rate-limited (1 attempt/10min), 5 failures = 1-hour lockout
- Per-platform allowlists: `TELEGRAM_ALLOWED_USERS`, `DISCORD_ALLOWED_USERS`, etc.

**Dangerous Command Approval:**
Curated pattern list checked before every execution. Requires user approval for: `rm -r`, SQL `DROP/DELETE without WHERE`, `curl | sh`, `chmod 777`, `> /etc/`, `kill -9 -1`, and 20+ other destructive patterns. Default choice: deny.

**Container Isolation (Docker backend):**
- `--cap-drop ALL` (all Linux capabilities stripped)
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- tmpfs with `nosuid` for all temp directories
- CPU, memory, disk all configurable and capped

**Credential Filtering:**
- API keys/tokens stripped before reaching LLM or MCP subprocesses
- Blocks env vars with `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL` in name
- Error messages sanitized: GitHub PATs, OpenAI keys, bearer tokens, `password=` all redacted

**SOUL.md / Context Injection Scanning:**
Before loading into system prompt, scans for: "ignore previous instructions" variants, hidden HTML comments, instructions to read `.env`/credentials, credential exfiltration via `curl`, invisible Unicode (zero-width spaces, bidirectional overrides).

**Tirith Pre-Execution Scanner:**
Every shell command scanned for: homograph URL spoofing, pipe-to-interpreter patterns, terminal injection. Suspicious commands surface findings + safer alternatives. (Note: `tirith_fail_open: true` by default — scanner timeout allows command through.)

**SSRF Protection (Always Active):**
Blocks private networks (RFC 1918), loopback, cloud metadata (169.254.169.254), link-local, CGNAT. DNS failures fail closed. Redirect chains re-validated.

**Supply Chain Hardening (v2026.3.28):**
Removed compromised litellm dependency, pinned all dependency versions, regenerated uv.lock with hashes, added CI workflow scanning PRs for supply chain attack patterns.

---

### What Navi Must Build

**A. Input Sanitization Middleware**
Every inbound Telegram message passes through sanitization before reaching the Hermes agent. Detects and quarantines:
- "Ignore previous instructions" and variants
- Instructions to disclose SOUL.md, config, or credentials
- Hidden Unicode (zero-width spaces, bidirectional overrides)
- Natural language attempts to invoke system commands

Suspicious messages are quarantined. User sees: "Sorry, I couldn't process that — try rephrasing." Navi ops receives alert. Logs all quarantine events.

Implementation: thin middleware function between Telegram webhook and Hermes gateway. Runs on every message.

**B. Per-User Credential Isolation**
Each Hermes profile gets its own `.env` with credentials scoped to exactly what that archetype needs:
- Barber agent: calendar API + Telegram bot token only
- Attorney agent: document storage + calendar + Telegram bot token only
- No profile ever holds credentials it doesn't actively use

The provisioning service writes credentials. Profiles never share a credential store. Resource parameters come only from channel config, never from message payload.

**C. Memory Audit Log**
When Hermes writes to persistent memory (autonomous), Navi logs the write with: timestamp, originating conversation context, profile ID. Creates a trail for detecting memory poisoning. If a user's agent starts behaving strangely, memory audit log reveals which entries are driving it.

**D. SOUL.md as Protected Asset**
- Write-only by Navi's provisioning service
- Never exposed to the user via Telegram interface
- Never readable by any tool the agent can invoke
- Checksum on deploy; re-generated from archetype template on suspected tampering
- Users cannot successfully ask "show me your system prompt"

**E. Deterministic Execution Pipeline**
Every agent action follows this sequence — never skipped:
```
Inbound message
→ Auth check (is this user allowlisted for this profile?)
→ Tenant boundary check (does this message route to the correct profile only?)
→ Input sanitization (injection scan)
→ Hermes agent processes
→ Output sanitization (no credential leakage in response)
→ Deliver to Telegram
```

**F. Rate Limiting Per User**
Per-user rate limiting at the gateway layer. Slows automated injection attacks. Protects against accidental or intentional agent abuse.

**G. Kill Switch**
Single admin command: disables any user's agent immediately. Stops all cron jobs, blocks all Telegram routing, freezes the profile. Navi ops tool — invisible to end users. Used when anomalous behavior is detected.

**H. Trust Tier Separation**
Three tiers of agent capability:
- **Read-only research tier** (auto-approved): summarization, briefings, drafts for review
- **Write-capable workflow tier** (JIT approval): sending messages, creating calendar events, external API calls
- **Privileged admin tier** (explicit per-action approval): file writes outside workspace, credential access, system commands

Common cases run fast and smooth. Dangerous actions require explicit approval. User experience: "safe by default, fast when low-risk, explicit when dangerous."

---

### Practical Security Defaults (Hermes Production Checklist)

From Hermes official documentation:

1. Explicit allowlists — never `GATEWAY_ALLOW_ALL_USERS=true`
2. Docker backend (`terminal.backend: docker`)
3. CPU, memory, disk limits on every container
4. Secrets in `~/.hermes/.env`, `chmod 600`
5. DM pairing enabled, not hardcoded IDs
6. Audit `command_allowlist` periodically
7. `MESSAGING_CWD` locked to restrict agent working directory
8. Run as non-root user
9. Monitor `~/.hermes/logs/` for unauthorized access patterns
10. `hermes update` on a schedule

---

### What Users Never Need to Know

| Security mechanism | How it appears to the user |
|---|---|
| Allowlist + DM pairing | "Just text the bot — it'll ask us to let you in" |
| Input sanitization | Invisible. Flagged messages: "try rephrasing that" |
| Credential isolation | Invisible. User never touches an API key |
| Memory audit | Invisible. Navi ops dashboard sees anomaly alerts |
| Container isolation | Invisible. User talks to a Telegram bot |
| Kill switch | "Your agent is temporarily paused" if triggered |
| SOUL.md protection | User never knows the system prompt exists |
| Rate limiting | "Too many messages — try again in a moment" |

The platform's security is a property of the infrastructure. Not a burden on the user.

---

## Part 6: Ongoing Security — Staying Current Against "The One Honest Limitation"

OWASP's honest assessment:
> "Current defenses only slow attacks due to power-law scaling behavior. For consumer safety, assume motivated attackers will eventually find bypasses — human oversight remains essential."

No defense is permanently complete. The goal is: casual attacks fail automatically, sophisticated attacks are logged and killable, and users bear none of this burden. Sustaining that goal requires an active security posture, not a one-time setup.

### The Living Security Strategy

**1. Automated Dependency Scanning (Weekly)**
- Run automated CVE scans against all Hermes dependencies on a weekly schedule
- Pin to the latest Hermes release within 7 days of any security-tagged release
- CI pipeline blocks deploy if known-vulnerable packages are present
- Use the supply chain audit pattern established in Hermes v2026.3.28: regenerate lock file with hashes on every dependency update

**2. Prompt Injection Red-Teaming (Monthly)**
- Dedicate one session per month to adversarial testing: attempt to break Navi agents using known injection patterns
- Test vectors: "ignore previous instructions," hidden Unicode, indirect injection via fake client messages, SOUL.md extraction attempts
- Maintain a living `injection-test-vectors.md` document in the repo
- Document what was tested, what passed, what was found
- Update input sanitization middleware with any new patterns discovered

**3. Threat Intelligence Monitoring (Ongoing)**
- Subscribe to: OWASP GenAI Security mailing list, NousResearch/hermes-agent GitHub releases, OpenClaw security advisories
- Track: HackerNews "AI agent security" tag, arXiv LLM security papers, NIST AI Risk Management Framework updates
- Assign 30 minutes/week to reviewing new published attack techniques
- When a new attack class emerges (e.g., a new MCP injection vector), evaluate Navi's exposure within 48 hours

**4. Memory Audit Review (Weekly)**
- Review the memory audit log for anomalous writes
- Flag: any memory write that includes credential-like patterns, any write originating from an external source (not user conversation), any write that modifies agent behavior on high-risk tools
- Purge suspicious memory entries and notify affected users if warranted

**5. Incident Response Playbook**
Maintain a documented playbook for the scenarios most likely to occur:

| Scenario | Response |
|---|---|
| Prompt injection suspected | Kill switch → memory audit → input log review → sanitization rule update → restore from clean profile |
| Memory poisoning confirmed | Wipe affected memory store → re-seed from archetype defaults → review what was poisoned → patch injection vector |
| Credential exposure in logs | Rotate affected keys immediately → audit log for what was accessed → notify user if their data was exposed |
| Agent behaving anomalously | Kill switch → full memory + session audit → identify root cause → controlled restore |
| New CVE in Hermes dependency | Assess exposure → patch within 24h if critical, 7 days if moderate → deploy and verify |

**6. Security Changelog**
Every security change — patch, new rule, incident response, red-team finding — is logged in `docs/security-changelog.md` with date and outcome. This document is the institutional memory of Navi's security posture. It informs new team members, surfaces patterns, and proves due diligence.

**7. User Communication Protocol**
When a security event affects users:
- Users are informed in plain language (no technical jargon)
- They're told what happened, what was affected, and what Navi did about it
- They're not asked to do anything technical
- Trust is maintained by transparency, not silence

**8. Quarterly Security Review**
Four times per year: full review of the threat model, attack surface, and control effectiveness. Answer:
- Has the agent's capability set expanded? (New tools = new attack surface)
- Have any past injection test vectors stopped working? (Confirm the fix still holds)
- Are there new published attack classes against Hermes/LLM agents generally?
- Is the kill switch still functional? (Test it.)
- Are all credential stores still correctly scoped? (Audit them.)
- Is the memory audit log being reviewed regularly? (Check the log of logs.)

---

## Summary: The Right Mental Model

> Secure the agent like a production service, not like a chat app.

The biggest wins come from: least privilege, strong sandboxing, tight tool permissions, and runtime checks on every action — while keeping user experience smooth through sensible defaults, just-in-time approvals, and well-designed safe paths.

**The recommended baseline:**
1. Default-deny tool access, with explicit allowlists
2. Per-action authorization for high-risk tools
3. Sandboxed execution with no ambient credentials
4. Strict input/output validation and redaction
5. Separate memory for preferences vs secrets
6. Centralized logs and alerts for sensitive actions
7. Network egress control through a policy gateway
8. Short-lived credentials and scoped tokens

**The right production pattern:**
- One identity per agent session
- One sandbox per session with ephemeral state
- One tool policy layer for all external actions
- One approval gate for high-risk actions
- One audit pipeline for every sensitive event

That combination delivers most of the security benefit without making the agent unusable.

---

## Sources

- [Hermes Agent GitHub](https://github.com/nousresearch/hermes-agent)
- [Hermes Agent Security Docs](https://hermes-agent.nousresearch.com/docs/user-guide/security/)
- [Hermes Profiles Docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/)
- [Hermes Skills Docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)
- [Hermes Cron Docs](https://nousresearch-hermes-agent.mintlify.app/user-guide/features/cron)
- [MarkTechPost — Hermes Agent Release](https://www.marktechpost.com/2026/02/26/nous-research-releases-hermes-agent-to-fix-ai-forgetfulness-with-multi-level-memory-and-dedicated-remote-terminal-access-support/)
- [OpenAI Tools Hub — Hermes Review](https://www.openaitoolshub.org/en/blog/hermes-agent-ai-review)
- [OpenClaw Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)
- [OpenClaw Telegram Docs](https://docs.openclaw.ai/channels/telegram)
- [awesome-openclaw-usecases GitHub](https://github.com/hesamsheikh/awesome-openclaw-usecases)
- [OpenClaw 20 Workflows Gist](https://gist.github.com/velvet-shark/b4c6724c391f612c4de4e9a07b0a74b6)
- [Hostinger — OpenClaw 25 Use Cases](https://www.hostinger.com/tutorials/openclaw-use-cases)
- [getclaw.sh — OpenClaw vs Hermes Comparison](https://getclaw.sh/blog/openclaw-vs-hermes-agent-feature-comparison-founders-2026)
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [OWASP GenAI — LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [Penligent — AI Agents Hacking in 2026](https://www.penligent.ai/hackinglabs/ai-agents-hacking-in-2026-defending-the-new-execution-boundary/)
- [Scalekit — Access Control for Multi-Tenant AI Agents](https://www.scalekit.com/blog/access-control-multi-tenant-ai-agents)
- [Multi-Tenant AI Agent Architecture — Medium](https://medium.com/@vamshidhar.pandrapagada/how-to-deploy-multi-tenant-ai-agent-infrastructure-that-actually-scales-433f44515837)
- [X post — real Hermes user (@0xsachi)](https://x.com/0xsachi/status/2031719095658598417)
- [System Prompt Hardening — Security Boulevard](https://securityboulevard.com/2026/03/introducing-system-prompt-hardening-production-ready-protection-for-system-prompts/)
