# Axiom

**Axiom — Governed AI for Coherent Software Engineering**

Axiom is a **hierarchical, multi-agent software engineering platform** designed to build, analyze, and evolve complex codebases with **architectural integrity, logical correctness, and human authority**.

Unlike traditional agent frameworks, Axiom does not optimize for autonomy.  
It optimizes for **coherence**.

---

## Why Axiom?

Modern AI coding tools struggle with:
- Large, undocumented codebases
- Architectural drift over time
- Broken business logic despite passing tests
- Context limits and token inefficiency
- Uncontrolled agent behavior

Axiom addresses these problems by enforcing:
- **Architecture-first development**
- **Persistent sources of truth**
- **Hierarchical reasoning**
- **Deterministic execution**
- **Human-owned decisions**

---

## Core Principles

- **Governed, not autonomous**  
  Humans own intent and truth. AI assists within explicit boundaries.

- **Persistent knowledge, ephemeral agents**  
  Architecture and constraints outlive agents.

- **Logic over locality**  
  System-wide reasoning matters more than file-level correctness.

- **Parallel execution, centralized control**  
  Execution scales without losing coherence.

- **Token efficiency as a design constraint**  
  Abstractions replace context bloat.

---

## Licensing

Axiom uses a **dual-license model** to ensure open collaboration while protecting commercial value:

- **AGPL-3.0-or-later**: For non-commercial, internal, open-source, and research use.
- **Commercial License**: Required for any monetized use, including SaaS, paid tools, or consulting.

### Commercial Use Examples
- **SaaS Offerings**: Hosting Axiom as part of a paid service.
- **Paid Developer Tools**: Embedding Axiom in a proprietary tool sold to customers.
- **Consulting Platforms**: Using Axiom as a core engine in a paid consulting engagement.

### Non-Commercial Use Examples
- **Internal Evaluation**: Testing Axiom prior to adoption
- **Research**: Academic or non-profit research
- **Open-Source Contributions**: Developing and sharing improvements to Axiom

> Note: For-profit companies using Axiom in production—whether internally or externally—should obtain a Commercial License.

For licensing questions, see [FAQ-LICENSING.md](FAQ-LICENSING.md).

For commercial licensing inquiries, please contact **Ramsanjiev** at `ramsanjiev@gmail.com`.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN USER                                  │
│                  Goals, Constraints, Approvals                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERACTION LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │  Axiom CLI  │  │ IDE Surface │  │ Copilot Interaction Layer   │ │
│  │  (axiom)    │  │  (VS Code)  │  │  (Witness, not Approver)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STRATEGIC LAYER (Axiom-Archon)                     │
│                      Long-lived, Persistent                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • System-wide coherence    • Logical reasoning              │   │
│  │ • Knowledge stewardship    • Human decision handling        │   │
│  │ • CPKG/BFM/UCIR management • Strategic review               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   TACTICAL LAYER (Axiom-Strata)                     │
│                       Ephemeral, Planning                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Intent interpretation    • Task graph generation          │   │
│  │ • Work decomposition       • Validation strategy            │   │
│  │ • LLM tactical planning    • Outcome summarization          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 TASK EXECUTOR (Axiom-Conductor)                     │
│                    Deterministic Control Plane                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Task graph execution     • Dependency ordering            │   │
│  │ • Parallel scheduling      • Retry and failure handling     │   │
│  │ • NO LLM calls             • Structured event emission      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  EXECUTION LAYER (Axiom-Forge)                      │
│                       Stateless Workers                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Code generation          • Refactoring                    │   │
│  │ • Test generation          • Tool invocation                │   │
│  │ • Shell execution          • Playwright automation          │   │
│  │ • Context-aware backends   • Remote execution               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │  Axiom-Logos     │  │  Axiom-Sentinel  │  │ Semantic        │   │
│  │  Logical         │  │  Behavioral      │  │ Regression      │   │
│  │  Validation      │  │  Validation      │  │ Detection       │   │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

| Component | Role | Persistence | Authority |
|-----------|------|-------------|-----------|
| **Axiom-Core** | Shared schemas, workflow orchestration | N/A | Workflow control |
| **Axiom-Canon** | Knowledge artifacts (CPKG, BFM, UCIR, TaskGraph) | Persistent | Source of truth |
| **Axiom-Archon** | Strategic reasoning, human decision handling | Long-lived | Coherence gate |
| **Axiom-Strata** | Tactical planning, task decomposition | Ephemeral | Plan generation |
| **Axiom-Conductor** | Deterministic task execution | Stateless | Execution control |
| **Axiom-Forge** | Code generation, tool invocation | Stateless | Task execution |
| **Axiom-Logos** | Logical validation | Stateless | Invariant checks |
| **Axiom-Sentinel** | Behavioral validation | Stateless | E2E testing |
| **Axiom-CLI** | Command-line interface | Stateless | Transport only |

---

## CLI Commands

Axiom provides a governed command-line interface:

```bash
# Initialize or adopt a project
axiom init                      # New project
axiom adopt                     # Existing project

# Plan and execute work
axiom plan "<intent>"           # Create execution plan
axiom preview                   # Validate and simulate
axiom approve --rationale "..." --yes  # Human approval (REQUIRED)
axiom execute                   # Execute approved plan

# Utilities
axiom status                    # Show workflow status
axiom docs                      # Generate documentation
axiom discover                  # Run discovery analysis
```

**Important:** Commands must be run in order. You cannot skip steps or auto-approve.

---

## Copilot Interaction

> **Key Principle:** Copilot acts as a **witness**, not an approver. It can help you formulate decisions, but it cannot make them for you.

**Approval Grammar (enforced by Axiom):**
```
APPROVE: <rationale explaining why you approve>
REJECT: <rationale explaining why you reject>
OVERRIDE: <rationale for overriding AI recommendation>
EXECUTE (no rationale, requires prior approval)
```

**Invalid (will be REJECTED):**
- "yes", "ok", "looks good", "lgtm", "approved", "👍"

---

## Persistent Knowledge Artifacts

Axiom avoids long prompts and fragile memory by using **explicit, minimal artifacts**.

### Canonical Project Knowledge Graph (CPKG)
- Components, responsibilities, dependencies
- Decisions, invariants, risks
- Human-approved, token-efficient

### Business Flow Map (BFM)
- End-to-end user and system flows
- Drives logical reasoning and E2E validation

### User Constraint & Instruction Registry (UCIR)
- Persistent architectural, UX, and business constraints
- Enforced across all layers
- Editable at any time

These artifacts are the **only long-lived memory** in the system.

---

## AI vs Human Authority

**AI recommends. Human decides.**

| Actor | Authority |
|-------|-----------|
| **Human** | Final decision, approval, override |
| **AI (Strategic)** | Advise, recommend, surface risks |
| **AI (Tactical)** | Plan, decompose, organize |
| **AI (Execution)** | Execute approved tasks only |

Key principles:
- No execution without explicit human approval
- AI approval alone never authorizes action
- Override requires rationale
- Silence equals rejection (no timeout-based approval)

See: [GOVERNANCE.md](GOVERNANCE.md)

---

## Validation Beyond Tests

Axiom does not assume "tests passing = system correct".

It validates software through:
- **Static logical reasoning** (flows, invariants, dependencies)
- **Behavioral testing** (Playwright, E2E flows)
- **Semantic regression detection** (intent vs outcome)

All validation results are surfaced for **human ratification**.

---

## GitHub Copilot Integration

Copilot is treated as a **controlled execution assistant**, not an architect.

- Scoped tasks only
- Explicit constraints
- Minimal context
- No architectural invention

See: `.copilot/copilot-instructions.md`

---

## Supported Use Cases

- Greenfield project bootstrapping
- Large legacy codebase refactoring
- Architecture enforcement over time
- Parallel feature development
- Safer AI-assisted engineering

---

## What Axiom Is Not

- ❌ A fully autonomous coding agent
- ❌ A prompt-heavy agent swarm
- ❌ A replacement for engineering judgment
- ❌ A "magic" AI that understands everything

Axiom is a **system**, not a shortcut.

---

## Project Status

✅ **v1.0.0 — Production Ready**

Axiom v1.0.0 is a stable release with:
- Complete governance model
- Deterministic task execution
- Multi-layer validation framework
- Copilot integration with strict approval grammar
- Human Decision Intake API
- New project and existing project onboarding
- First-run guardrails
- CLI with workflow enforcement

**Test Coverage:** 716 tests passing

---

## Getting Started

See: [ONBOARDING.md](ONBOARDING.md)

### Installation

```bash
pip install axiom-engine
```

### New Projects

```bash
# Using CLI
axiom init
axiom plan "Create a REST API for user management"
axiom preview
axiom approve --rationale "Reviewed plan, architecture looks correct" --yes
axiom execute
```

### Existing Projects

```bash
# Using CLI
axiom adopt
axiom discover
axiom plan "Refactor authentication module"
axiom preview
axiom approve --rationale "Reviewed changes, low risk" --yes
axiom execute
```

### Python API

```python
from axiom_core import AxiomWorkflow
from axiom_canon import CPKG, BFM, UCIR

workflow = AxiomWorkflow()
result = workflow.run(
    user_request="Add user authentication",
    cpkg=cpkg,
    ucir=ucir,
    bfm=bfm
)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, components, and workflows |
| [GOVERNANCE.md](GOVERNANCE.md) | Authority model and approval rules |
| [ONBOARDING.md](ONBOARDING.md) | Getting started guide |
| [INSTALLATION.md](INSTALLATION.md) | Installation and setup |
| [SECURITY.md](SECURITY.md) | Threat model and security invariants |
| [SIGNING.md](SIGNING.md) | Code signing and release verification |
| [PUBLIC_API.md](PUBLIC_API.md) | API stability tiers |
| [FAQ-LICENSING.md](FAQ-LICENSING.md) | Licensing questions and answers |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Philosophy

> Software systems are not files.  
> They are **structures of intent**.

Axiom exists to preserve that intent — even as code changes.

---

## License

Axiom is available under a **dual-license model**:

- **AGPL-3.0-or-later** — for non-commercial, internal, open-source, and research use
- **Commercial License** — required for any monetized use (SaaS, paid tools, consulting platforms)

See:
- [LICENSE-AGPL](LICENSE-AGPL)
- [LICENSE-COMMERCIAL](LICENSE-COMMERCIAL)

For commercial licensing inquiries, contact **Ramsanjiev** at `ramsanjiev@gmail.com`.
