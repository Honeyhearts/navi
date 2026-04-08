# Navi Open-Source Integration Strategy
## Source: Navi_Agent_Architecture.pdf, Pages 12–21 (Section 2)

**Logged:** 2026-03-30
**Branch:** feature/conference-test-flight
**Purpose:** Reference document for architecture planning. Integrates with `agent-stack-research.md` and the office-hours design doc at `~/.gstack/projects/honeyhearts-navi/maitreya-feature/conference-test-flight-design-20260330-154753.md`.

---

## Section 2.1 — Framework Evaluation Table

Twelve open-source tools evaluated against Navi's Phase 0-3 requirements.

| Framework | Category | Verdict | Rationale |
|-----------|----------|---------|-----------|
| **CrewAI** | Multi-agent orchestration | **USE — Phase 1** | Role/goal/backstory maps to Navi archetype model. YAML-defined agents. Simple to add a new archetype without new Python classes. |
| **LangGraph** | Stateful workflow engine | **USE — Phase 2** | State machine per agent. Checkpointing for conversation resumption. Human-in-the-loop interrupts. Best for complex multi-step workflows. |
| **LangChain** | Tool and retrieval layer | **USE — Phase 2** | Wraps external APIs (calendar, booking, CRM). RAG pipelines. Per-user knowledge bases. NOT for orchestration — tools only. |
| **Dify** | Visual workflow builder | **USE — Phase 2/3** | Internal prototyping first, user-facing later. Calibration UI design candidate. NOT before PMF. |
| **AutoGen** | Agent-to-agent debate | **DEFER — Phase 3** | For agent-to-agent critique/negotiation patterns. Adds complexity before we need it. Revisit at 500+ users. |
| **Ollama** | Local inference | **DEFER — Phase 3** | Cost reduction after PMF. Self-hosted models. Not needed while API costs are manageable. |
| **RAGFlow** | Retrieval-augmented generation | **DEFER** | Potentially useful for attorney/SEN consultant archetypes with large document bases. Evaluate when archetype count grows. |
| **PyTorch** | ML framework | **DEFER** | Training custom models. Not in scope until we have enough user data and post-PMF resources. |
| **HuggingFace** | Model hub | **DEFER** | Fine-tuning on Navi-specific data. Post-PMF. |
| **Open WebUI** | Chat interface | **SKIP** | Navi's interface is Telegram. Open WebUI solves a different problem. |
| **Optuna** | Hyperparameter tuning | **SKIP** | ML optimization. Not relevant to current stack. |

**Note:** Hermes Agent and OpenClaw are evaluated separately in `agent-stack-research.md`. Hermes is the agent runtime layer; these frameworks operate above it.

---

## Section 2.2 — The Navi Stack

### Conference Stack (Phase 0 — Now → April 10, 2026)

**What it is:** The existing codebase. No new frameworks introduced.

```
Python
  + python-telegram-bot (Telegram interface)
  + OpenRouter API (LLM routing — model-agnostic)
  + SQLite (local persistence)
  + Hermes Agent (agent runtime per user, via Modal)
  + agentskills.io skills (SKILL.md format)
```

**Principle:** Validate that the skills and SOUL.md templates actually produce a useful agent before building orchestration layers around them.

### Post-Conference Stack

Built in phases — each layer added only when the previous is proven.

```
Phase 1 (April → June):
  + CrewAI             — multi-agent orchestration (archetype crews)
  + AgentRuntime       — abstraction layer over Hermes
  + ProfileProvisioner — automated onboarding → deployment pipeline

Phase 2 (June → August):
  + LangGraph          — stateful workflows (complex multi-step tasks)
  + LangChain          — tool wrapping (calendar, booking, CRM APIs)
  + Dify               — internal visual workflow prototyping

Phase 3 (August+):
  + Dify               — user-facing workflow builder (calibration UI candidate)
  + AutoGen            — agent debate/critique (quality improvement)
  + Ollama             — local inference (cost reduction)
```

---

## Section 2.3 — Decision Trees

### CrewAI vs. AutoGen for Phase 1

**Use CrewAI because:**
- Role/goal/backstory maps directly to Navi's archetype model
- YAML-defined agents — adding a new archetype is a config file, not new Python
- Simpler mental model for Navi's use case (one agent serving one user)
- AutoGen's debate patterns are overkill before we have multi-agent scenarios

**AutoGen upgrade path:** When Navi has agents that need to validate each other's work (e.g., attorney agent drafting → compliance agent reviewing before send), AutoGen becomes relevant. That's Phase 3.

### LangGraph Introduction Criteria (Phase 2 Gate)

Introduce LangGraph when:
- Multi-step workflows need interruption and resumption (e.g., intake → attorney review → client follow-up)
- Conversation state needs to survive agent restarts
- Human-in-the-loop approval is needed in the middle of a workflow

**Not before:** LangGraph adds complexity that isn't justified until we have workflow patterns complex enough to require it.

### API-Only Until PMF

Stay on OpenRouter/Claude API/GPT-4o API. No self-hosted inference until:
- Post-PMF
- Cost pressure is real (not theoretical)
- Engineering capacity exists to maintain it

---

## Section 2.4 — Phased Roadmap

### Phase 0: Conference Ship
**Timeline:** Now → April 10, 2026
**Goal:** Real agents, real users, real validation

Deliverables:
- 3-5 archetype SOUL.md templates (barber, tattoo, attorney minimum)
- 8-10 seed skills (2-3 per archetype, agentskills.io format)
- Manual provisioning script (JSON input → Modal function)
- Structural security (routing, credentials, volumes)
- Memory audit log

Framework additions: **None**

### Phase 1: CrewAI Archetype Prototype
**Timeline:** April 11 → May 15, 2026
**Goal:** Automated onboarding, multi-archetype support

Deliverables:
- AgentRuntime interface + HermesRuntimeAdapter
- ProfileProvisioner (signup → deployed agent)
- CrewAI archetype definitions (YAML per archetype)
- Onboarding flow (5-step web UI)
- Input sanitization middleware
- Rate limiting
- Basic calibration dashboard

Framework additions: **CrewAI**

### Phase 2: Platform Foundation
**Timeline:** May 16 → July 2026
**Goal:** Production-grade platform, first paying users

Deliverables:
- LangGraph stateful workflows (complex multi-step tasks)
- LangChain tool wrappers (calendar, booking, CRM)
- Full calibration UI (all three surfaces)
- Skill marketplace
- Admin fleet monitoring dashboard
- Hermes version pinning
- Dify for internal workflow prototyping

Framework additions: **LangGraph + LangChain + Dify (internal)**

### Phase 3: Scale
**Timeline:** August 2026+
**Goal:** 500+ users, capital raised, premium tier

Deliverables:
- Dify user-facing workflow builder
- AutoGen agent-to-agent critique
- Ollama local inference (cost reduction)
- VPS-per-user premium tier
- Multi-region deployment

Framework additions: **Dify (user-facing) + AutoGen + Ollama**

---

## Section 2.5 — Architecture Principles (The Five Rules)

These principles apply to every layer, every decision, from Phase 0 onward.

### 1. Abstraction Layers Over Direct Dependencies

Never let product code touch a framework directly. Every framework gets an adapter:
- Hermes → `AgentRuntime` interface → `HermesRuntimeAdapter`
- LangGraph → workflow adapter
- CrewAI → crew factory

**Why:** Frameworks evolve fast (some die). The abstraction makes the framework a swappable plugin. Swapping a framework = rewriting one adapter file, not auditing the codebase.

### 2. Config-Driven Archetypes

An archetype is a YAML/JSON config file, not a Python class. Adding a new archetype never requires new code — only a new config file.

```yaml
# archetypes/barber.yaml
archetype: barber
soul_template: barber_soul.md.j2
seed_skills:
  - _shared/morning-briefing
  - barber/appointment-reminder
  - barber/no-show-tracker
cron_defaults:
  morning_briefing: "0 8 * * *"
  evening_no_show_check: "0 19 * * *"
integrations:
  - calendly
  - google_calendar
```

**Why:** At 10 archetypes, config-driven is manageable. At 50, code-driven becomes unmaintainable.

### 3. One Database, Multiple Stores

Single source of truth for user/profile/billing data: **Navi's SQLite → PostgreSQL** (when we scale past single-machine).

Additional purpose-built stores:
- **Modal Volumes** — Hermes profile state (SOUL.md, memories, skills)
- **Redis** (Phase 2) — rate limiting, session cache
- **Vector DB** (Phase 2/3) — semantic memory, RAG for attorney/SEN archetypes

**Anti-pattern:** Don't replicate profile state into both Navi's DB and Hermes config. Navi's DB is authoritative for profile metadata. Modal Volumes are authoritative for agent runtime state.

### 4. Feature Flags for Framework Adoption

Every new framework starts behind a flag:

```python
FEATURE_FLAGS = {
    "crewai_orchestration": os.getenv("FF_CREWAI", "false") == "true",
    "langgraph_workflows": os.getenv("FF_LANGGRAPH", "false") == "true",
    "dify_builder": os.getenv("FF_DIFY", "false") == "true",
}
```

Roll out to 10% of users first. Monitor error rates and latency. If metrics are clean for 2 weeks: full rollout. If degraded: flag off, no incident.

**Why:** Every new framework integration is a potential regression. Flags mean you can isolate the new thing without a rollback.

### 5. Measure Before Expanding

Don't add a framework because it seems useful. Add it because you have measured pain that it solves.

Triggering metrics:
- "10% of sessions require multi-step workflows" → introduce LangGraph
- "API costs exceed $X/month" → evaluate Ollama
- "Adding new archetype takes > 2 days" → improve config tooling (not add frameworks)

**Anti-pattern:** Framework FOMO. The agent space moves fast. Most frameworks that seem essential in month 1 are either deprecated or absorbed by a better tool by month 6. Build the abstraction layer, stay behind it.

---

## Integration Notes — Reconciling PDF with Office-Hours Design

The PDF's phased roadmap and the office-hours architecture (Hermes + Modal + AgentRuntime) are not competing — they operate at different layers.

| Layer | Office-Hours Design | PDF Framework |
|-------|---------------------|---------------|
| Infrastructure | Modal serverless | — |
| Agent runtime | Hermes (via AgentRuntime interface) | — |
| Orchestration | — | CrewAI (Phase 1) → LangGraph (Phase 2) |
| Tool wrapping | MCP integrations via skills | LangChain (Phase 2) |
| Visual prototyping | Calibration UI (custom) | Dify (Phase 2 internal, Phase 3 user-facing) |
| Inference | OpenRouter/Claude/GPT-4o | Ollama (Phase 3, cost reduction) |

**Key reconciliation:** CrewAI in Phase 1 operates above the `AgentRuntime` interface — it orchestrates *between* agents (e.g., intake agent hands off to follow-up agent), while Hermes runs *inside* each individual Modal function. They don't conflict.

**What changes in the design doc:** The Phase 1 build sequence should include CrewAI archetype definitions alongside the AgentRuntime interface and ProfileProvisioner. This was already implied in the "config-driven archetypes" principle but not explicitly named.

---

## Source Citation

All content in this document is derived from:
- `/Users/maitreya/Desktop/Navi/Navi/Navi_Agent_Architecture.pdf`, pages 12–21 (Section 2: Open-Source Integration Strategy)

Cross-referenced with:
- `docs/agent-stack-research.md` (OpenClaw vs. Hermes research, security architecture)
- `~/.gstack/projects/honeyhearts-navi/maitreya-feature/conference-test-flight-design-20260330-154753.md` (office-hours architecture design)
