# project.md — sub360.ch

> **Read order for AI agents & developers:** Read **this file first** to understand *what* sub360 is, *who* uses it, and *what* belongs in Phase 1. Then read [Agents.md](Agents.md) for *how* to build it (coding standards, stack tooling, reusable mixins, URL/form/view patterns).
>
> **No overlap rule:** This file is **domain + scope + project-specific decisions only**. It deliberately does **not** repeat anything in Agents.md (no coding conventions, no tooling, no mixin/column/widget catalogue, no testing rules). If you need an implementation pattern, it is in Agents.md.

---

## 1. What sub360 is

sub360.ch is a **B2B platform for the Swiss construction industry**. It connects two sides of the market:

- **Clients** (general/total contractors, construction companies, SMEs) who post jobs/tenders and search for verified subcontractors.
- **Subcontractors** (service providers / sub-tradespeople) who maintain a company dossier, prove their credentials, view tenders and apply.

The platform is the **trusted layer** between them: every subcontractor is verified by the back office, proof documents (insurance, etc.) are tracked for validity, and clients can rely on the "verified" status when awarding work.

This project is a **greenfield rebuild** of the existing sub360 platform. The legacy backend had unfixable bugs, poor scalability and security weaknesses, so the application **behind the login** is being rebuilt from scratch on Django + PostgreSQL. The existing dataset (**~280 companies**) will be migrated.

### What is *in* this project ("backend / platform")
The entire **application platform behind the login**: the Django/PostgreSQL server, the application logic, and the **server-rendered application UI** (the login area), built to the existing corporate design using the **Metronic 8 (Bootstrap) — demo21** dashboard theme.

### What is *not* in this project
The public **WordPress landing site** stays as-is (marketing, construction news, glossary, SEO). It is **fully decoupled**. The only two touch points:
1. **Login / register links** from the landing site into the platform.
2. A small **public metrics endpoint** the landing site reads (e.g. total company count). This is the only public JSON the platform exposes.

---

## 2. Architecture decisions (project-specific)

These are decisions for *this* project. Anything not stated here follows Agents.md defaults.

| Decision | Choice for sub360 |
|---|---|
| Application style | **Server-rendered hybrid monolith** — Django Templates + HTMX + AlpineJS. No SPA. |
| UI theme | **Metronic 8, Bootstrap edition, demo21** layout. All screens are built on this theme; light + dark mode supported. |
| Landing site | External WordPress, **decoupled**. Platform never renders landing content; it only exposes login/register entry points and one public metrics endpoint. |
| Public API surface | Minimal. One small read-only **public metrics endpoint** (JSON) for the landing site. Everything else is HTML fragments behind the login. |
| UI languages | **DE / FR / IT / EN**, selected per user. *(This overrides the generic French-only default in Agents.md — sub360 is multilingual Swiss B2B.)* User-generated content (tender text, company descriptions) is **not** translated. |
| Real-time | **Server-Sent Events (SSE)** for messaging and live notification badges. No WebSockets needed in Phase 1. |
| Region / hosting | CH/EU preferred for personal & document data (final hosting decision is open — build cloud-agnostic / containerized). |

> The original requirements left "server-rendered vs SPA" open. **For this build it is decided: server-rendered Django + HTMX + Metronic.** Treat that as final.

---

## 3. Roles & permissions

Role-based access (RBAC). Build on `django-allauth` per Agents.md.

| Role | Auth | Team? | Subscription? | Core rights |
|---|---|---|---|---|
| **Public** | none | — | — | View basic company info; **fuzzy, non-actionable** subcontractor search (a registration incentive); start registration. |
| **Client** (contractor) | login | **Yes — has a team** (up to **2 users free**) | No (free tier) | Detailed verified-subcontractor search; create/manage tenders; view & accept/reject applications; message subcontractors; manage own company, team & account. |
| **Subcontractor** | login | **No — single user, no team** | **Yes — paid** | Maintain company dossier; upload & maintain proof documents; view tenders; apply/quote; message clients; manage subscription. |
| **Admin / Back office** | internal login | — | — | Verify & approve/reject subcontractors; manage users/companies/tenders/content/banners; newsletter; statistics & reporting; audit log. |

**Key asymmetry to remember everywhere:** **Clients have teams, subcontractors do not.** A client company can invite multiple users; a subcontractor account is one company = one login (team management UI must not appear for subcontractors).

---

## 4. The two user journeys (critical — they differ)

These two flows drive most onboarding/gating logic. Get them right.

### Client (contractor)
```
signup (register/ag) → email verification (double opt-in) → account validated → USE sub360 (free)
```
- No payment, no back-office approval gate.
- After verification the client can immediately search, post tenders and (optionally) invite up to 2 team members for free.

### Subcontractor
```
signup (register/sub) → email verification → onboarding
  → master data → trades → document upload → package selection
  → SUBSCRIBE (Stripe) → back-office review & approval → USE sub360
```
- A subcontractor is **only fully active when payment is received *and* the back office has approved the profile** (both gates).
- Onboarding must be **saveable and resumable** — a half-finished subcontractor can return and continue.
- Already-registered email/company addresses must **never abort** the flow (this was a legacy bug — handle gracefully).

---

## 5. Domain apps (module map)

Suggested Django apps under `apps/`. Each encapsulates one feature domain (see Agents.md for the per-app file layout). `apps/core/` already exists — reuse its mixins/columns/widgets; never reinvent.

| App | Responsibility |
|---|---|
| `accounts` | Users, login, registration flows (`register/ag`, `register/sub`), email verification, password policy/reset, **2FA (authenticator app + email code)**, sessions ("log out all sessions"), **client team management & invitations**, roles/permissions. |
| `companies` | Company dossier (master data, description, references, capacity, service regions), **trade catalogue (4 clusters)** + multi-select, profile public visibility opt-in/out, completeness indicator. Holds both client companies and subcontractor companies. |
| `documents` | Secure proof-document upload (PDF/image, size/type validation, malware scan, non-public object storage + signed URLs), validity/expiry capture & status (valid/expired/review), versioning/history, **insurance proof mandatory**. |
| `verification` | Back-office review queue and approve/reject workflow with reasons, pre-check flags, approval gating, and **tamper-evident audit log**. |
| `tenders` | Client job/project tendering: create/edit/close, status lifecycle (draft/published/closed/awarded), trade + type (new build/conversion/renovation) + location + attachments, optional material & volume, application deadlines, per-tender application overview. |
| `applications` | Subcontractor one-click apply/quote (with attachment), client accept/reject, status visible to subcontractor, client favourites. |
| `subscriptions` | Subcontractor packages, **Stripe Billing** (card + TWINT, recurring), **annual via Swiss QR-bill** with semi-automatic reconciliation, upgrade/downgrade/cancel/renew, dunning, **VAT-compliant invoices/receipts**. |
| `messaging` | **SSE-based** real-time messaging between client and subcontractor (around tenders/applications). |
| `notifications` | In-app notifications + transactional emails (registration, approval, application, payment, expiry warnings); multilingual templates. |
| `newsletter` | Segmentable mass mail (by trade/role/region), opt-in/opt-out, bounce/unsubscribe handling. Prefer integrating an established provider (Brevo/Mailchimp) via API over an in-house engine. |
| `integrations` | External services: **Zefix/UID** company validation, Stripe webhooks, mail provider. |
| `statistics` | Back-office **KPI dashboard** + the single **public metrics endpoint** for the landing site. |
| `banners` | (COULD) manageable ad slots for premium partners, with runtime + target region/trade. |
| `migration` | Legacy ETL + the **re-registration invitation flow** (see §9). |

> App names are a recommendation; if `apps/core/` already defines a different convention, follow it.

---

## 6. Core domain concepts

**Company dossier.** The heart of a subcontractor's presence: master data, description, references, selected trades, service regions and capacity. Profile visibility is opt-in/opt-out. A completeness/quality indicator nudges subcontractors to finish.

**Trade catalogue (4 clusters).** Subcontractors multi-select trades from a fixed catalogue with **4 clusters**: *Main construction trades · Secondary/finishing trades · Technology & industry · Planning & construction* (detailed positions per the current website — see Appendix A of the requirements spec). Trades are the primary axis for search/filter and for newsletter segmentation.

**Documents & proofs.** Subcontractors upload proof documents; **insurance proof is mandatory**. Each proof has a validity/expiry date (captured **manually** in Phase 1 — OCR auto-extraction is Phase 2) and a status. **Expiry monitoring** runs as a background job: it reminds the subcontractor, escalates to the back office, and **sets the profile to "restricted" when a mandatory proof expires.**

**Tenders (client).** A tender carries trade, build type, location, attachments and optional material/volume, and moves through draft → published → closed → awarded. Phase 1 supports public tenders; *by-invitation* procedure and auto-closing after deadline are SHOULD.

**Applications (subcontractor).** One-click apply with an optional quote/attachment; the client accepts/rejects and the status is visible to the subcontractor.

**Subscriptions.** Subcontractors pay; clients are free (up to 2 users). See §8.

**Messaging.** Direct client↔subcontractor conversations, delivered live via **SSE**.

**Notifications.** Two channels: **in-app** (live badge via SSE) and **transactional email** (multilingual). Both fire on the same domain events (registration, approval, application received/decided, payment, expiry warning).

**Statistics.** Internal KPI dashboard (new registrations, active subscriptions, tenders, applications, open reviews) plus the one outward-facing public metric (e.g. company count) the landing site reads.

---

## 7. Authentication & security specifics

(Mechanics & middleware live in Agents.md — this is just the project's required behaviour.)

- Email/password login with a **strong password policy** and password reset.
- **Email verification (double opt-in)** required before any account is activated.
- **Two-factor authentication**, with the user able to choose between:
  - **Authenticator app (TOTP)** — scan-a-QR style apps (Google Authenticator, Authy, etc.), and
  - **Email one-time code** verification.
  2FA is **mandatory for admin/back office**, offered to all users.
- Session/token management with expiry and **"log out of all sessions"**.
- Secure uploads (type/size validation, malware scan, non-public storage with signed URLs); OWASP-aligned (injection/CSRF/XSS protection, rate limiting).
- **Audit log** for all verification/approval and security-relevant actions (tamper-evident).

---

## 8. Payments & subscriptions

- **Subcontractors pay; clients are free** (up to 2 users per client team — exact tiers/prices in Appendix B of the requirements spec, to be confirmed).
- **Stripe Billing**: card + **TWINT** for one-off; recurring renewal via card/direct debit.
- **Annual subscription via Swiss QR-bill** (strong B2B preference here) with **semi-automatic reconciliation** of the incoming payment.
- Subscription management: upgrade/downgrade, cancel, renew, **dunning on failed payment**.
- **VAT-compliant invoices/receipts**, downloadable.
- **No card/bank data stored** in our system — tokenization stays at the provider (minimize PCI scope).
- **Activation gate:** a subcontractor becomes active only when **payment is received AND back-office approval is granted**.

---

## 9. Data migration (~280 companies)

**Strategy: invite, don't silently migrate logins.**

We migrate company data (dossiers, documents + metadata, validity status, active tenders/applications, subscription status) into the new schema, but for accounts we use a **special re-registration link**:

1. Migrate each company's data into the new platform in a *pre-registered / claimable* state.
2. Send each of the ~280 companies a **unique tokenized invitation link** ("re-inscription" link).
3. The link lands them in a **pre-filled onboarding**: they confirm/correct migrated master data and trades, set a **new password**, re-confirm/re-upload documents, and (subcontractors) confirm their package → subscribe.
4. This sidesteps incompatible legacy password hashes (no plaintext migration) and doubles as a data-cleansing pass.

ETL approach overall: analyze legacy schema → map to target → ETL scripts → cleanse → trial migration in staging → sample reconciliation (the acceptance criterion) → final migration at cutover. Exact migration scope (master data only vs. incl. active tenders/applications) is an **open point** to confirm.

---

## 10. External integrations

| System | Purpose | Notes |
|---|---|---|
| **Stripe Billing** | Subscriptions, payments, dunning, receipts | Card + TWINT + QR-bill. Swiss alternatives if needed: Wallee / Payrexx / Datatrans. |
| **Zefix / UID** | Automatic company validation (existence/status) | Used during onboarding & back-office verification (FA-0404, SHOULD). |
| **Email / newsletter provider** | Transactional + mass mail | Prefer an established provider (Brevo/Mailchimp) via API over in-house. |

---

## 11. Phase 1 scope — implementation checklist

This is the binding Phase 1 backlog. Grouped by audience.

### Cross-cutting (all users)
- [ ] **Signup** — separate client and subcontractor flows (`register/ag`, `register/sub`)
- [ ] **Onboarding** — multi-step subcontractor onboarding (master data → trades → documents → package → payment); save & resume; graceful handling of already-registered addresses
- [ ] **Authentication** — email/password + strong policy + reset; **2FA via authenticator app *and* email code option**; email verification (double opt-in); session management / log out all
- [ ] **Notifications** — in-app (SSE) + event-driven
- [ ] **Emailing** — transactional emails, multilingual DE/FR/IT/EN
- [ ] **Statistics** — KPI dashboard (internal) + public metrics endpoint (landing site)
- [ ] **Multilingual UI** — DE/FR/IT/EN

### Client (contractor)
- [ ] **Custom domain** — per-client custom domain support
- [ ] **Profile** — client company profile / master data
- [ ] **Projects page** — create/manage tenders (job tendering)
- [ ] **Team management** — invite & manage team users (up to 2 free)
- [ ] **Subcontractor list** — detailed, filterable verified-subcontractor search & directory

### Subcontractor
- [ ] **Company form (formulaire)** — the company dossier (master data, trades, regions, references, capacity)
- [ ] **Projects list** — browse available tenders
- [ ] **Subscription (Stripe)** — packages, card/TWINT + QR-bill, renewal, dunning, invoices
- [ ] **Messaging (SSE)** — real-time client↔subcontractor chat

### Back office (admin)
- [ ] **Zefix.ch API** — automatic company validation
- [ ] **Account validation** — review queue, approve/reject with reason, approval gating, audit log

### Supporting
- [ ] **Documents & proofs** — upload, validity capture, expiry reminders, "restricted" on expired mandatory proof
- [ ] **Applications** — one-click apply/quote; client accept/reject
- [ ] **Data migration** — re-registration invitation link for the ~280 companies
- [ ] **Banners** *(COULD)* — premium-partner ad slots

---

## 12. Out of scope (Phase 2 — do not build now)

Listed so nobody pulls these into Phase 1: online bills of quantities (NPK) & **SIA 451 / CBRX** import; sub-projects with quantities/units/dates; **position-level quote comparison** & logged bid opening; **automatic job↔subcontractor matching**; **OCR-based** proof checking; compliance cockpit / due-diligence record. The "staffing provider" role is **fully excluded**.

---

## 13. Open points to confirm at kickoff

| # | Point |
|---|---|
| 1 | Exact subscription tiers / prices + client free-tier model (Appendix B). |
| 2 | Hosting / data-residency decision (CH/EU). |
| 3 | GDPR relevance (EU data subjects) in addition to Swiss FADP/revDSG. |
| 4 | Newsletter: provider vs in-house (recommendation: provider). |
| 5 | Exact migration scope (master data only vs. incl. active tenders/applications). |
| 6 | "Custom domain" per client — exact behaviour & DNS/cert handling. |

---

## 14. Frontend / UI Component Directives

> **Binding rule for all HTML/template work in this project.**

### Theme: Metronic 8 — Bootstrap — Demo21

All UI is built on the **Metronic 8 Bootstrap edition, Demo21 layout**. This is non-negotiable.

### Core directive: use Metronic components exclusively

**Never invent custom HTML structures or CSS classes for UI elements that Metronic already provides.** Always locate and use the equivalent Metronic component. This keeps visual consistency, dark-mode support, and responsive behaviour correct without extra effort.

Specifically:

| Need | Do this |
|---|---|
| Cards / panels | Use Metronic `card`, `card-header`, `card-body`, `card-footer` markup |
| Tables | Use Metronic datatable or `table` variants (`table-rounded`, `table-striped`, etc.) |
| Modals | Use Metronic modal patterns (not raw Bootstrap `modal`) |
| Buttons | Use Metronic button classes (`btn btn-primary`, `btn-light-primary`, icon buttons, etc.) |
| Forms / inputs | Use Metronic `form-control`, `form-select`, `input-group`, floating labels |
| Badges / labels | Use Metronic `badge`, `badge-light-*` variants |
| Alerts / toasts | Use Metronic alert/toast components |
| Navigation | Use Demo21 sidebar/topbar/breadcrumb markup — never build custom nav |
| Tabs / pills | Use Metronic `nav-tabs` / `nav-pills` patterns |
| Stats / KPI boxes | Use Metronic stat/summary card widgets |
| Progress bars | Use Metronic progress component |
| Dropdowns | Use Metronic menu/dropdown components |
| Avatars / symbols | Use Metronic `symbol` component |
| Timeline | Use Metronic timeline component |
| Wizard / steps | Use Metronic stepper component |
| Empty states | Use Metronic empty-state illustration pattern |
| Loading / spinners | Use Metronic `spinner-border` / `indicator` pattern |

### Practical workflow

1. **Before writing any new HTML block**, open the Metronic Demo21 preview or source (`metronic/` folder in this repo) and find the matching component.
2. Copy the Metronic markup and adapt only the data/content — **do not alter class names or structure** unless strictly required by Django template logic.
3. For HTMX partial templates (`*_partial.html`), the same rule applies — the fragment must use Metronic classes so it blends seamlessly when injected into the page.
4. Light/dark mode is handled automatically by Metronic's theme engine — never hard-code colours or use custom CSS variables for theme colours.
5. If a design requirement genuinely cannot be met by any existing Metronic component, escalate/discuss before inventing something — the default answer is "find the closest Metronic component and adapt it."

### Reference files in this repo

The `metronic/` directory at the project root contains Demo21 HTML reference pages. Use them as the first lookup source before searching externally.

```
metronic/
  dashboards.html       # Dashboard layouts & stat widgets
  apps.html             # App-level page patterns (lists, details)
  forms.html            # Form component examples
  widgets.html          # Charts, tables, cards, misc widgets
  pages.html            # Standard page patterns (empty states, errors, etc.)
  authentication/       # Login, register, 2FA page layouts
  account/              # Profile, settings, team pages
  ...
```

### Forms — custom field renderer (mandatory)

This project ships a **custom form-field renderer**, wired globally in settings:

```python
# config/settings.py
FORM_RENDERER = "apps.core.renderer.CustomFormRenderer"
```

`CustomFormRenderer` (`apps/core/renderer.py`) sets `field_template_name = 'forms/field.html'`, so **every** form field rendered with `{{ field.as_field_group }}` uses the project's Metronic-styled field template (`templates/forms/field.html`) — label, required marker, inline-create `+` button, help text and errors all in one consistent block.

**Rules:**

1. **Always render fields with `{{ field.as_field_group }}`** — never `{{ field }}` alone, never `{{ field.label_tag }}` / manual `<label>` markup. The renderer already produces the correct Metronic structure.
2. All model/non-model forms must extend the abstract bases in `apps/core/abstract_forms.py` (`AbstractModelForm`, `AbstractForm`, `AbstractFilterForm`). These auto-apply Bootstrap/Metronic classes (`form-control`, `form-select`, `form-check-input`), Select2 config, inline-create URLs and the responsive `field_group_class` column wrapper.
3. For multi-field layouts use `templates/forms/grid-form.html`, which loops `form.visible_fields` and renders each via `{{ field.as_field_group }}` inside its `field_group_class` column. Do not hand-roll grid markup per form.
4. Formsets use `templates/forms/_formset.html` / `_nested_formset.html`; filter forms use `templates/forms/filters.html`. Reuse these — do not duplicate.
5. Never inline custom field HTML in page templates — if a field needs different markup, adjust the widget/attrs on the form, not the template.

### Tables — HTMX renderer (mandatory)

All server-rendered tables use **django-tables2** with the project's HTMX-aware template, set globally:

```python
# config/settings.py
DJANGO_TABLES2_TEMPLATE = "tables/bootstrap_htmx.html"
```

`templates/tables/bootstrap_htmx.html` extends the Bootstrap 5 table template and overrides pagination, per-page selection and sortable headers to drive everything through **HTMX** (`hx-get` / `hx-target="#tableContainer"` / `hx-swap="innerHTML"`) — pagination, page-size changes and column sorting happen without full page reloads.

**Rules:**

1. **Do not set `template_name` on `Table.Meta`** — the global `DJANGO_TABLES2_TEMPLATE` already applies the correct HTMX template to every table. Only override it for a genuine one-off exception.
2. The table partial must be swapped into an element with `id="tableContainer"` (the template targets it for HTMX pagination/sort). Wrap list views accordingly.
3. Use the reusable column types in `apps/core/columns.py` (badge, link, HTMX action, checkbox columns, etc.) — never build column HTML inline. New column types go in that file.
4. Keep table styling on `Table.Meta.attrs` using Metronic table classes (`table align-middle table-row-dashed`, etc.) so the look stays consistent with Demo21.