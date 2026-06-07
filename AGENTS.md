# Repository Guidelines

> **For AI Agents and Developers:** This document is the single source of truth for **coding standards, stack conventions, and reusable patterns**. It is intentionally project-agnostic and applies to any project built on this Django + HTMX + AlpineJS stack.

> **For project-specific context** (business domain,  module scope) read [project.md](project.md) first, then return here for implementation rules.

**Role:** You are a Senior Full-Stack Django Architect and Developer that right simple code that is easy to understand and modify.

**Workflow:**
1. Read [project.md](project.md) first to understand the project domain, architecture decisions, and functional scope.
2. Read this file for all coding conventions, patterns, and reusable infrastructure.
3. Review existing code before implementing anything -- search for utilities before writing new ones.
4. Never reinvent what already exists in `apps/core/`.


**Objective:** Build a scalable, a multi modules (apps) app like CRM, billing, financial, projects managment  with a hybrid architecture (HTMX for web).

1. Read this file first for all repository conventions and style guidelines.
2. Review existing code for patterns before adding features or code.
3. Search for existing utilities before implementing new solutions; never reinvent the wheel.

## Key Principles

- **Expert-Level Answers:** Provide clear, concise technical explanations with precise examples. Assume deep knowledge of Python and Django.
- **Django Features:** Leverage Django’s built-in features (ORM, auth, forms, admin, etc.) instead of custom implementations. Use class-based views (CBVs) to reuse code through inheritance and mixins located in the core app . Simple views can use function-based views (FBVs).
- **Code Readability:** Follow PEP 8 style for Python. Use descriptive names (snake_case for functions/vars, CamelCase for classes, UPPER_SNAKE for constants). Format code with tools like Black and Ruff (which enforces style and unused import checks). Use type hints and run Pyright for static type checking.
- **Modularity:** Organize code into logical Django apps for each feature or domain. For example, an account app for user-related code or a core app for common utilities. Each app should have its own models.py, views.py, forms.py, etc., promoting separation of concerns.
- **Variables:** Variables and attributes may not begin with underscores
---



<!-- ### A. Restaurant Partner App (Web/PWA)
- **Goal:** Allow restaurants to digitalize menus and manage incoming orders.
- **Key Features:**
    - Menu CRUD (Categories, Items, Options).
    - QR Code Generation: Generate a unique QR linking to the restaurant's public menu.
    - Order Dashboard (Kanban style: Pending -> Preparing -> Ready).

### B. Customer App (Web/PWA)
- **Goal:** A mobile-first web interface for finding food and ordering.
- **Key Features:**
    - Geolocation (Browser-based) to sort restaurants by distance.
    - Restaurant Listing & Search.
    - Cart & Checkout flows (HTMX driven).
    - Favorites & Rating System.

### C. Driver App (React Native)
- **Goal:** High-performance native app for logistics.
- **Key Features:**
    - Order Acceptance/Rejection.
    - Real-time GPS Tracking: Must update location in background via GraphQL mutations.
    - Navigation integration.

### D. Super Admin (Web - Django Admin)
- **Goal:** Platform oversight.
- **Key Features:** Rider validation, Commission settings, Global stats. -->

---
<!-- 
## 1. The Architecture (The "Hybrid Monolith")
We are building a single Django backend that serves two distinct types of clients:

- **Hypermedia Clients (HTML):** The Restaurant Dashboard, Customer App, and Admin Panel consume server-side rendered HTML via HTMX.
- **Data Clients (JSON):** The Driver Mobile App consumes structured data via GraphQL (Strawberry). -->


## 2. Technology Stack & Constraints

### Python Tooling
- **Package & env management:** `uv` (astral-sh). Use `uv add <pkg>`, `uv lock`, `uv run <cmd>`.
- **Linting:** Ruff with auto-fix (`uv run ruff check --fix`).
- **Formatting:** Ruff format (Black-compatible, `uv run ruff format`).
- **Line length:** 120 characters.
- **Import sorting:** isort via Ruff (`I` ruleset).
- **Type checking:** Pyright.
- Configure all of the above in `pyproject.toml`.

### Python
- **Linting**: Ruff with automatic fixing
- **Formatting**: Ruff format (Black-compatible)
- **Line Length**: 120 characters
- **Import Sorting**: isort via Ruff

### Backend Core
- **Framework:** Django 6.x (Python).
- **Database:** PostgreSQL 14+ via `psycopg` / `psycopg3` (never `psycopg2`).
- **Auth:** `django-allauth` (email, social, passwordless/OTP).
- **Async / queues:** Celery + Celery Beat, Redis as broker and cache backend.
- **API layer:** Django Ninja (REST). Strawberry GraphQL only when a native mobile client requires it.
- **Filters:** `django-filter` for all querystring-driven filtering.
- **Tables:** `django-tables2` for all server-rendered tabular data.
- **Forms:** we  have a AbstractModelForm that need to be used on every form enless there is a clear exceptrion .
- **Realtime (optional):** Django Channels + Redis when WebSocket support is needed.

### Frontend 1: Web  
- **Template Engine:** Django Templates (Standard).
- **Interactivity:** HTMX (for server interaction) + AlpineJS (for client-side UI state).
- **Styling:** Bootstrap and metronic dashboard template 
- **Rule:**  write Views that return partial HTML.
- **Theme Support**: All UI components must support both light and dark modes
---

## 3. Django Coding Standards and Rules

### Django & HTMX Rules
- **HATEOAS:** Return HTML fragments, not JSON, for the web frontends.
- **MVT Pattern:** Follow Django’s Model-View-Template architecture strictly.
- **Apps:** Each Django app should encapsulate a feature domain.
- **Authentication:** Use django-allauth for all authentication flows.
- **Filters:** Use django-filter for all filtering flows.
- **Tables:** Use django-tables2 for all table flows.
- **Caching & Queues:** Redis for Django cache and Celery broker.
- **Task Processing:** Celery workers and Celery Beat for background jobs.
- **Database:** PostgreSQL 14+ with pgvector extension using psycopg/psycopg3 not psycopg2 .
- **API Layer:** Use Django rest framework for building APIs .

- **Partials:** Store reusable template parts in `templates/components/`.
- **Optimization:** Use `select_related` and `prefetch_related` strictly to avoid N+1 queries in GraphQL resolvers.




Decision tree:
1. **Create or update anything in a modal** -> `BaseManageHtmxFormView`
2. **Create or update anything on a full page** -> `BaseManageHtmxPageFormView`
3. **Inline creation (inside a parent form/modal)** -> `BaseHtmxInlineCreateView`
4. **Delete a single object** -> `DeleteMixinHTMX`
5. **Delete multiple selected rows** -> `BulkDeleteMixinHTMX`
6. **Apply an action to a bulk selection** -> `BaseActionView`
7. **Charts / analytics** -> `ChartMixin`
8. **Import from CSV/Excel** -> `ImportDataMixin`
9. **Show import field spec table** -> `TableImportFieldsMixin`
11. **Any dashboard view needing breadcrumbs** -> add `BreadcrumbMixin`.

General rules:
- Return `201` for created, `204` for no-content, `400` for invalid forms, `404` / `403` for access errors.
- For list / detail pages use Django generic CBVs (`ListView`, `DetailView`, etc.).
- For delete: never build a custom delete flow -- always use `DeleteMixinHTMX`.

---
Reusable Mixins Reference (`apps/core/mixins.py`)

All mixins live in `apps/core/mixins.py`. Always import from there -- never duplicate logic.

---
### Views
- if its create or update view  use the BaseManageHtmxFormView / BaseManageHtmxPageFormView depending if the view should be in a modal (popup) or a page from apps/core/mixins.py
- Validate request.method explicitly (if request.method == 'POST': ... or use CBV post() method). Return appropriate HTTP status codes (e.g. 201 for created, 204 for no content). For list/detail/update/delete actions, prefer Django’s generic CBVs or django-rest-framework to reduce boilerplate. Use HttpResponseRedirect, JsonResponse, or DRF responses as appropriate.
- Use DeleteMixin from apps/core/mixins.py for delete objects.
- Ensure that all business logic, especially calculations, is implemented in models.py (or appropriate service layers), not in views.

### Forms & Validation # TODO need to change this forms and emprove the code for better reusability
- Use AbstractModelForm for model-backed forms. In Meta, explicitly set fields or exclude to avoid accidentally exposing new model fields.
- Use [Grid Form](templates/forms/grid-form.html) for forms with a lot of fields.
- Use [Vertical Form](templates/forms/vertical-form.html) for forms with a few fields.
- Use [Horizontal Formset](templates/forms/horizontal-formset.html) for formsets.
- if its a complexe form use {{ form.field.as_field_group }}  for each field and don't rely on grid vertical or horizontal templates
- Implement validation in clean() and clean_<field>() methods.
- Always call is_valid() in views if its a custom view, if its a BaseManageHtmxFormView, it will be called automatically. 
- Handle and display form errors in templates.
- Disable submit buttons during HTMX submissions (e.g. ```<button hx-disable>``` ).
- Customize widgets in Meta.widgets if needed. Always include ```{% csrf_token %}``` in POST forms. 


### Templates & HTMX
- Use template inheritance ({% extends "base.html" %} and {% block %}) for structure. Keep HTML clean. For HTMX interactions, create partial templates with suffix _partial.html. Detect HTMX requests via if request.htmx: (django-htmx provides utilities). Always include an hx-indicator attribute on interactive elements to show loading spinners.
- Partials as <name>_partial.html.


### Models
- Name models in singular (e.g. User, not Users). Define a sensible __str__ for each model. Use UUIDField for primary keys if needing non-sequential IDs. 
- if its a public Model it should inherit from BaseModel class.
For search/AI features, use PostgreSQL’s pgvector extension: add from pgvector.django import VectorField and use VectorField(dimensions=<n>) for embedding fields. Run the makemigrations --empty step to enable pgvector in the database.

| Model | Purpose |
|-------|---------|
| `TimestampedModel` | Abstract — adds `created_at`, `updated_at` |
| `CRUDUrlMixin` | Abstract — provides `get_create_url()`, `get_list_url()`, `get_update_url()`, `get_delete_url()` via convention |

### Celery Tasks
- Define tasks in a dedicated tasks.py or celery.py module. Use @app.task (or @shared_task) for tasks. Ensure tasks are idempotent (safe to retry). Do not perform side-effects multiple times on retry. Use bind=True and call self.retry(exc=e, countdown=...) for retries with exponential backoff. Set sensible max_retries. Always log when a task starts, succeeds, or fails. Pass only primitive or JSON-serializable arguments. Use django.utils.timezone for datetime in tasks.

### URLS
- we have class CRUDUrlMixin that auto include get_create_url, get_list_url, get_update_url, get_delete_url
``` python
class CRUDUrlMixin:
    @classmethod
    def get_create_url(cls):
        return reverse(f"{cls._meta.app_label}:create_{cls._meta.model_name}")

    @classmethod
    def get_list_url(cls):
        return reverse(f"{cls._meta.app_label}:list_{cls._meta.model_name}")

    def get_update_url(self):
        return reverse(
            f"{self._meta.app_label}:update_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )

    def get_delete_url(self):
        return reverse(
            f"{self._meta.app_label}:delete_{self._meta.model_name}",
            kwargs={"pk": self.pk},
        )
urlpatterns = [
    path("<model_name>/create/", ManageView.as_view(), name="create_<model_name>"),
    path("<model_name>/update/<int:pk>/", ManageView.as_view(), name="update_<model_name>"),
    path("<model_name>/list/", ListView.as_view(), name="list_<model_name>"),
    path("<model_name>/delete/<int:pk", DeleteView.as_view(), name="delete_<model_name>"),
]
```
- follow this pattern to create urls ex: create_product, update_product, delete_product, list_product for creation, update, delete, list actions ...Etc



### Mixins (`mixins.py`)

The project's central reusable logic library (~1145 lines):

| Mixin | Purpose |
|-------|---------|
| `BreadcrumbMixin` | Auto-generates page title and breadcrumb navigation from model metadata |
| `BaseManageHtmxFormView` | **Core HTMX form handler** — modal-based create/update with auto-permission derivation, formset support, HX-Trigger responses, `created_by` auto-assignment |
| `BaseManageHtmxPageFormView` | Full-page variant of the above |
| `DeleteMixinHTMX` | HTMX-aware delete with ProtectedError handling and HX-Trigger events |
| `BulkDeleteMixinHTMX` | Bulk delete selected rows with cascade preview |
| `ImportDataMixin` | **Excel/CSV import engine** — auto field-type detection, ForeignKey resolution via get_or_create, duplicate checking, custom `process_{field}` hooks |
| `ExportDataMixin` | Export to Excel/CSV/PDF via `DataExporter` |
| `ChartMixin` | Chart data generator with monthly/grouped aggregation (TruncMonth) |
| `TableImportFieldsMixin` | Introspects model fields to generate import UI metadata |
| `BaseActionView` | Generic action modal for selected rows (abstract `process_action()`) |
| `BaseOptionsMixinView` | Generic view to display only the queryset for that model used where we create on the fly instance we need to get the new instance with the old ones so we call this view |
#### Custom Columns (`columns.py`)

Reusable django-tables2 column types: `IsActiveColumn`, `HTMXLinkColumn`, `HTMXUpdateLinkColumn`, `HTMXDeleteLinkColumn`, `HTMXCircleColumn`, `CustomCheckBoxColumn`, `BadgeColumn`, `BadgeColumnCssStyle`, `ActionColumn`, `ReusableBadgeColumn`, `ManyToManyBadgeColumn`, `ManyToManyPhoneColumn`, `PrintColumn`, `PrintTransactionColumn`, `AbonnementValidColumn`, `HideColumn`.
- every new custom Table column goes here 

#### Custom Widgets (`widgets.py`)

`QuillWidget` (rich text), `BooleanAllSelect`, `RichSelect` (with icon/subcontent data attributes), `SwitchWidget`, `StatusAllSelect`, `MultipleFileInput`/`MultipleFileField`.
- every new custom form widget goes here 

### Performance Patterns
  - Optimize query performance using Django ORM's select_related and prefetch_related for related object fetching.
  - Use Django’s cache framework with backend support (usually Redis ) to reduce database load.
  - Implement database indexing and query optimization techniques for better performance.
  - Use asynchronous views and background tasks (via Celery) for I/O-bound or long-running operations.
  - Optimize static file handling with Django’s static file management system (e.g., WhiteNoise or CDN integration).

### Management Commands

| Command | Purpose |
|---------|---------|
| `init_project` | Run migrations, create superuser (`admin@admin.com`/`admin`), load Wilaya/Commune fixtures |
| `restart_project` | Post-deploy: migrations, collectstatic, clear cache, restart gunicorn/celery/nginx |

#### Template Tags

- **`change_lang`**: `change_lang(path, lang)`, `get_lang_icon(lang)` — i18n URL switching
- **`permissions_tags`**: `can_edit(obj, user)`, `can_delete(obj, user)` — permission template filters


---
## General Coding Standards and rules

### Utilities & Dependencies
- Use the uv tool (by astral-sh) for Python environment and dependency management. For example, uv add <package> to install, uv lock to generate lockfiles, and uv run <command> to execute scripts. Integrate Black/Ruff by adding them to dependencies (uv add black ruff) and configure in pyproject.toml.
### Error Handling
- Do not swallow exceptions. Use try-except blocks in business logic and views to catch expected errors, log them with context, and return user-friendly messages (e.g. via Django’s messages framework or HTTP error responses). Configure custom 404/500 pages for production.



---

## Internationalization

- Default language: **French** (`fr`)
- UI labels and verbose names are in French throughout
- `set_language` view stores preference in user model + session + cookie
- `change_lang` template tag for URL translation
- `num2words` used for French number-to-words conversion (bill totals)
- `django-rosetta` available for translation management (dev dependency)
 

---


### 4.1 `BaseManageHtmxFormView`

**Purpose:** Standard create/update view rendered inside a **modal/popup**. Used in ~80% of CRUD operations on dashboard.

**Default template:** `templates/forms/_create_form.html`



**What it handles:**
- Detects create vs update from URL `pk` kwarg.
- Auto-resolves the instance from the model.
- Calls `form.save()`, handles `created_by`, triggers success messages.
- On success: returns `HTTP 204` with `HX-Trigger` headers so the HTMX table refreshes and the modal closes -- no page reload.
- On invalid: re-renders the form with errors inside the modal.
- Supports **formsets** via `get_formsets()` override.
- Supports **Dropzone file uploads** via `dropzone_config`.
- Supports **parent URL kwargs** via `parent_url_kwarg` for nested resources.

**Key attributes:**
| Attribute | Purpose |
|---|---|
| `model` | The Django model class |
| `form_class` | The form class (must extend `AbstractModelForm`) |
| `hx_triggers` | Dict of HTMX events fired after successful save |
| `parent_url_kwarg` | List of URL kwargs passed through to form |
| `dropzone_config` | Dict `{field_name, model, post_key}` for async file uploads |



### 4.2 `BaseManageHtmxPageFormView`

**Purpose:** Same as `BaseManageHtmxFormView` but for **full-page** create/update flows (not modals).

**Default template:** `templates/forms/grid-form.html`

**Differences from modal version:**
- On success, redirects to the list view (or update page / create page based on `submit_action` POST param).
- Supports `save_continue` -> redirect to updated instance's update URL.
- Supports `save_add_another` -> redirect to create URL.
- Does not emit HTMX trigger headers.



## Testing

### Test-Driven Development
- Write a failing test before implementing a feature. Ensure tests cover all branches of logic (success, failure, edge cases).

### Pytest / Django
- Use pytest with the pytest-django plugin. Do not use Unitests

### Test Organization
- Tests in `tests/` directories within each app
- Separate test files: `test_models.py`, `test_views.py`, `test_api.py`
- Mock external services (LLM providers, etc.)
- Store isolation in all tests

### Test Structure
- Tests use **pytest** with Django integration
- Fixtures in `apps/fixtures/*.json` or app-specific `fixtures.json`
- Factory Boy for test data generation
- Coverage reporting available

### Behavior Over Implementation
- Write tests that assert behavior, not implementation details.

### Continuous Testing
- Run uv run pytest locally and in CI on every commit. Use uv run ruff check to lint. 
- check and Fix any lint or type errors.


---

## Error Handling and Validation

### View-Level Handling
- Catch exceptions and return appropriate responses. Use Http404 or PermissionDenied when resources or permissions are missing. Re-render invalid forms with errors and a 400 status code.
- don't use LoginRequired on every View as we have the login required middleware

### Model Validation
- Use Django’s built-in field validators and Model.clean() or full_clean() for model-level validation.
- Use Django’s built-in constraints on Meta Class for DB constraints as an alternative to the Model.clean() ( don't forget that The check keyword argument of CheckConstraint is deprecated in favor of condition.)

### Security
- Sanitize user input. Escape or use autoescape in templates to prevent XSS. Always use parameterized ORM queries to prevent SQL injection.

### Logging and Signals
- Configure Django’s logging to record errors. Use Django signals to decouple audit/log logic from core models.

### User Feedback
- Use the Django messages framework to flash error or success messages. For HTMX requests, set HTTP status or include HX-Trigger headers.

---

### Configuration
- Split settings by environment. Use environment variables.

### Version Control
- Use .gitignore. Commit lockfiles with uv lock.
---


### Package Management
- uv (Python) don't use pip or try to run commands with python manage.py ...etc

---

## Performance Optimization

- Database
- Caching
- Query Efficiency
- Asynchrony
- Static Assets
- Code Profiling
- HTMX Efficiency
- lazy images loading

---

## Key Conventions

- Naming
- Indentation & Line Length
- Imports
- Docstrings
- Translations
- Time Zones
- Error Messages
- Commit Messages

---

### Debug Mode
- Set `DEBUG=True` in `.env` for development
- Use Django debug toolbar for SQL query analysis
- Check Celery logs for background task issues



## Development Commands

### Backend (Django)
```bash
# Development server
uv run manage.py runserver      # Direct Django command

# Database
uv run manage.py migrate        # Run migrations
uv run manage.py makemigrations # Create migrations
uv run manage.py shell          # Django shell

# Task queue
celery -A config worker                      # Start Celery worker with beat

# Testing
pytest                         # Run all tests
pytest apps/experiments/       # Run specific app tests
pytest -k test_name           # Run specific test
pytest --cov                  # With coverage
pytest -x                     # Stop on first failure
```


## Project Structure & Module Organization

### Directory Layout
- Organize apps under apps/

### App File Structure
Each app follows this pattern:
```
apps/
├── app_name/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
├── forms.py              # Form definitions
├── models.py             # Model definitions
├── signals.py            # Django signals
├── filters.py            # Django signals
├── tables.py             # Django-tables2 definitions
├── urls.py               # URL patterns
├── views.py              # View definitions
├── migrations/           # Database migrations
├── tests/                # Test modules
├── templatetags/         # Custom template tags
├── management/           # Custom management commands
├── exceptions.py         # Custom exceptions
└── tasks.py              # Celery task definitions
```

## Template Organization

<!-- ### at the project level need improvment -->

#### Common Template Patterns
```html
<!-- Extend app_base.html overall layout and navigation -->
{% extends "base.html" %}

{% block page_head %}
  {{ block.super }}
  <!-- custom 'head' contents e.g. page-specific stylesheets -->
{% block extra_css %}
  {{ block.super }}
{% endblock extra_css %}
{% endblock page_head %}

{% block app %}
  <!-- page specific content -->
{% endblock app %}

{% block extra_js %}
  {{ block.super }}
  <!-- page-specific JavaScript -->
{% endblock extra_js %}

<!-- HTMX for dynamic content -->
<div hx-get="{% url 'app:view-name' store.slug %}" hx-trigger="load">
    Loading...
</div>

<!-- Reusable components -->
{% include "generic/chip.html" with object=my_object %}
```



