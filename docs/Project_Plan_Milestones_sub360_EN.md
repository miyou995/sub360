# Project Plan & Milestones – Backend Relaunch sub360.ch

| | |
|---|---|
| **Project** | Relaunch of the sub360.ch application platform (Phase 1 + Phase 2) |
| **Basis** | Requirements Specification (Pflichtenheft) sub360 |
| **Status** | Draft v0.1 |
| **Date** | 25 May 2026 |

> Phase 2 follows **directly** after Phase 1 and is budgeted. Milestone order is binding; concrete dates/durations are set by the agency at kickoff. The technical solution design (architecture and all stack items not pre-set below) is **owned and finalized by the agency**.

---

## 1. Technology Stack

Only the items below are pre-set. **All other items are intentionally left open for the agency to define and finalize.**

| Component | Decision |
|---|---|
| Web / API framework | **Python** |
| Database | **PostgreSQL** |
| Payment | **Stripe** (card / TWINT) **+ Swiss QR-bill** |
| Hosting / infrastructure | _[to be defined by agency]_ |
| Data residency / region | _[to be defined by agency]_ |
| Application UI technology | _[to be defined by agency]_ |
| Async / background jobs | _[to be defined by agency]_ |
| File / object storage | _[to be defined by agency]_ |
| Search | _[to be defined by agency]_ |
| Authentication method | _[to be defined by agency]_ |
| Containerization / CI-CD | _[to be defined by agency]_ |
| Email / newsletter service | _[to be defined by agency]_ |
| Monitoring / logging | _[to be defined by agency]_ |

*Note: Python is the mandated language; the specific Python framework may be proposed by the agency.*

---

## 2. Architecture Overview

The platform behind the login is a greenfield build, **fully decoupled** from the existing WordPress landing site. The only touch points are login/register links and a public metrics endpoint (e.g. company count).

Environments (dev/test/staging/production), CI/CD pipeline, secrets management and infrastructure-as-code are defined by the agency as part of the solution design.

---

## 3. Milestones

### Phase 0 – Preparation

**M0 – Kickoff & Setup**
- NDA signed; development contract incl. IP assignment, code ownership, test coverage, exit clause in place.
- Agency finalizes architecture & remaining stack (on Python/PostgreSQL); environments + CI/CD running.
- Open decisions made: UI technology, hosting/data residency, GDPR relevance.
- Backlog derived from the Requirements Specification.

### Phase 1 – New Platform (feature parity + improvements)

**M1 – Foundation**
- Data model, authentication, roles/permissions, team management, UI skeleton per CD.
- **Acceptance:** login/registration (client & subcontractor) works, roles enforced.

**M2 – Core Processes**
- Company dossier (subcontractor), job tendering (client), application/quote (subcontractor), search & filter (public/client).
- Document upload, proof capture, Zefix validation, expiry reminders; verification/approval back office.
- **Acceptance:** end-to-end flow tender → application → review → approval confirmed in test.

**M3 – Monetization & Communication**
- Payments & subscriptions via Stripe incl. **QR-bill**; transactional emails; newsletter/mass mail; multilingualism DE/FR/IT/EN; ad banners.
- **Acceptance:** subscription purchase, renewal and failed-payment dunning tested in production.

**M4 – Migration & Landing-Site Connection**
- Migration of ~280 companies incl. users, documents, active data (validated in staging).
- Landing-site connection: public metrics endpoint + login/register links.
- **Acceptance:** sample reconciliation passed; metrics correct on landing site.

**M5 – Hardening & Acceptance**
- Security/penetration test (**go-live gate**), performance test, UAT.
- **Acceptance:** no open critical/high findings; all MUST requirements confirmed in UAT.

**M6 – Go-Live Phase 1**
- Staged cutover with data freeze; smoke tests; hypercare.
- **Acceptance:** production stable, monitoring/backups active.

### Phase 2 – Differentiation (directly following)

**M7 – Tendering Depth**
- Online bills of quantities (NPK), import SIA 451 / CBRX, sub-projects with quantities/units/dates.
- **Acceptance:** BoQ creatable/importable, sub-projects functional.

**M8 – Quote Comparison & Award**
- Position-level quote comparison, logged bid opening, automatic reminders/rejections, tender procedures (public/by invitation), award/awarding workflow.
- **Acceptance:** comparison and award incl. log confirmed in test.

**M9 – Automation**
- Automatic matching job ↔ subcontractor; OCR-based proof checking.
- **Acceptance:** matching returns relevant results; OCR with manual fallback in production.

**M10 – Compliance Cockpit (differentiation module)**
- Continuous compliance monitoring + automatic due-diligence record (joint-liability protection) – see Future-Features roadmap, lever 1.
- **Acceptance:** compliance status per subcontractor current, due-diligence record generatable.

**M11 – Acceptance & Go-Live Phase 2**
- Security check of new modules, UAT, cutover.
- **Acceptance:** all Phase 2 MUST requirements confirmed, production stable.

---

## 4. Data Migration (summary)

Analyze legacy schema → map to target → ETL → cleanse → trial migration in staging → validate (sample, documents) → final migration at cutover. Password reset flow if hashing is incompatible. Sample reconciliation is the acceptance criterion (see M4).

## 5. QA & Security Strategy

Unit/integration tests; end-to-end tests of core flows; SAST/DAST and dependency scanning in CI; **external penetration test as a go-live gate** (mandatory – legacy system was insecure); 

## 6. Roles & Responsibilities (RACI, condensed)

| Activity | sub360 (PO) | Agency |
|---|---|---|
| Requirements / prioritization | A/R | C |
| Architecture & stack (beyond pre-set) | A | R |
| Development & tests | I | R |
| Content / translations | R | C |
| Verification business rules | A/R | C |
| Data migration | A | R |
| Acceptance / UAT | A/R | C |
| Operations / maintenance (post go-live) | A | R (per contract) |

A = accountable/decides, R = responsible/executes, C = consulted, I = informed.

## 7. Risks & Measures

| ID | Risk | Impact | Measure |
|---|---|---|---|
| R1 | UI technology/scope of login area not decided early | medium | Decide UI tech at M0; provide CD assets early |
| R2 | Stats/login handoff landing↔platform unspecified | low | Specify public metrics endpoint + links early |
| R3 | OCR automation of proofs inaccurate | medium | Manual fallback; iterate automation (Phase 2) |
| R4 | Poor data quality of the ~280 records | medium | Profile early; cleansing as its own task |
| R5 | Payment/tax/QR-bill logic underestimated | medium | Treat as an early, dedicated work item; business acceptance |
| R6 | Compliance (FADP/GDPR) considered too late | high | Data protection/DPA from the start; erasure/access functions planned in |
| R7 | Server/hosting decision open | medium | Build cloud-agnostic (containers); decide residency in time |

## 8. Go-Live & Cutover

Staged cutover with a short data freeze – migrate after staging validation, point the application to production, smoke tests, then release. Rollback plan and a short hypercare phase (intensive monitoring/support right after go-live).

---

## 9. After Phase 2

Marketing campaign starts after Phase 2 go-live (deliberately only once the differentiation is in place). Phase 3 / further modules: see the separate "Future-Features – Differentiation Roadmap".
