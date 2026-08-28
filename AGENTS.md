# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Project overview

This is an e-portfolio application split into a Python 3.12 JSON API and a
React frontend. The API is built with FastAPI and SQLModel; the interface is a
React 19 multi-page application built with Vite and Tailwind CSS v4. Docker
Compose uses PostgreSQL 17 for persistent data; SQLite remains the fallback for
direct local runs and the isolated test database.

Keep the current architecture: route handlers accept and return JSON under the
`/api` prefix and never render HTML, and the interface is a set of separate
pages rather than a single-page application with a client-side router.

Run backend commands from the repository root; run frontend commands from
`frontend/`.

## Important files

- `main.py`: creates the FastAPI app, installs the JSON error handlers,
  registers routers, mounts the compiled frontend, and creates the schema plus
  optional seeding during the application lifespan.
- `routers/`: HTTP routes, all prefixed with `/api`. Public discovery and login
  are in `auth.py`; signup, dashboard and public portfolio are in `user.py`;
  owned CRUD is split between `experience.py` and `education.py`.
- `schemas/`: SQLModel table models plus `api.py`, which declares every JSON
  request and response body. Preserve the existing case-sensitive table file
  names and imports (`User.py`, `Experiences.py`, and `Education.py`).
- `core/config.py`: validated environment settings and production-sensitive
  defaults for demonstration data.
- `core/database.py`: database URL selection, SQLModel engine,
  `create_db_and_tables()`, and the per-request session dependency. Resolution
  order is an explicit `DATABASE_URL`, Compose-style `POSTGRES_*` values, then
  SQLite.
- `core/authentication.py`: resolves the authenticated user from the
  `Authorization: Bearer` header and exposes the `CurrentUser` dependency.
- `core/security.py`: password hashing and JWT creation/validation.
- `core/validation.py`: shared normalization and form-validation helpers.
- `frontend/`: the Vite multi-page application — one HTML document per screen,
  one React entry per document in `src/entries/`, shared UI in
  `src/components/`, and the API client, session storage and formatters in
  `src/lib/`.
- `frontend/src/styles/tailwind.css`: the design tokens every component builds
  on.
- `seed.py`: idempotent sample-data seeding plus a destructive `reset_db()`
  helper.
- `tests/`: pytest unit and HTTP integration tests using isolated databases.
- `.github/workflows/ci.yml`: a Python job (dependency, import and test checks)
  and a Node job (install, lint and build) for pushes and pull requests.
- `docker-compose.yml`: local PostgreSQL, pgAdmin, and application services.
- `database.db`: optional SQLite fallback state; it is intentionally ignored by
  Git and is not used by Docker Compose.

## Setup and common commands

Create and activate a virtual environment, then install the pinned
dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install the frontend dependencies from the exact lockfile:

```powershell
cd frontend
npm ci
cd ..
```

Copy the environment template, then replace every placeholder secret:

```powershell
Copy-Item .env.example .env
```

For direct non-Docker development, `SECRET_KEY` is required and SQLite is used
when neither `DATABASE_URL` nor `POSTGRES_HOST` is configured. Docker Compose
also requires the PostgreSQL and pgAdmin values documented in `.env.example`.

Never commit `.env`, JWTs, passwords, password hashes, `database.db`, or
`frontend/node_modules`.

Local development runs two processes. Start the API:

```powershell
fastapi dev main.py
```

Then, in a second shell, the interface:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173` — the Vite dev server serves the pages and proxies
`/api` to FastAPI on port 8000, so browsing the FastAPI port directly shows only
the API. In production one container serves both, because the image builds
`frontend/dist` and `main.py` mounts it.

Startup creates any missing table in the configured database and synchronizes
optional demo data according to `APP_ENV` and `SEED_DEMO_DATA`.

Useful Docker commands:

```powershell
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs -f eportfolio
```

Compose reads secrets from the local `.env`; that file must remain untracked.
See the Docker safety notes below before deleting volumes or changing database
configuration.

## Implementation conventions

- Use four-space Python indentation, clear snake_case names, and type hints for
  new or changed functions. Keep the existing import grouping: standard library,
  third-party packages, then local modules.
- Keep route handlers and SQLModel database access synchronous unless a task
  deliberately converts the complete request path; do not mix in async database
  access piecemeal.
- Add routes to the router matching their domain, always under the `/api`
  prefix. When adding a router module, also register it in `main.py` **before**
  the static mount, which would otherwise shadow it.
- Obtain database sessions through `Depends(get_session)` (or the existing
  `SessionDep` alias); do not create long-lived global sessions.
- Declare every request and response body in `schemas/api.py`. Type incoming
  fields as `str` and validate them with `core/validation.py`, which owns the
  rules and the user-facing wording; never return a SQLModel table instance
  directly, so a stored column cannot leak into a response by accident.
- Report failures by raising `HTTPException`. The handlers in `main.py` turn
  every error into `{"error": "..."}`, which is the single key the client reads;
  do not build error responses by hand.
- Store `User.birth_date` as `date`. Experience and education dates are stored
  as `datetime` and parsed with `%Y-%m-%d`, and are serialized back as plain
  calendar dates — a timestamp would be re-read in the visitor's own timezone
  and could display a day early.
- In `frontend/`, build UI from the components in `src/components/ui/` and the
  tokens in `src/styles/tailwind.css` rather than introducing new colours or
  one-off controls. Adding a page means adding its HTML document, its entry in
  `src/entries/`, and its input line in `vite.config.js`.
- Keep page access guards in the entry file, before React mounts, so a protected
  page never renders for a logged-out visitor.
- Use UTF-8 and preserve existing French and English copy. Comments are French
  in `routers/` and English in `core/` and `frontend/`. Avoid unrelated text,
  naming, or formatting rewrites.

## TDD workflow (qwen3-coder:30b / qwen2.5-coder:32b)

When asked to add or change behavior, follow a strict Red-Green-Refactor
cycle instead of writing implementation and tests together. This needs a
capable model to hold the discipline across steps — use it with
`qwen3-coder:30b` or `qwen2.5-coder:32b`; do not expect the same rigor from
`qwen2.5-coder:14b`/`7b` or `deepseek-coder-v2:16b`.

**RED** — write exactly one new failing test in `tests/`, matching the
existing arrange/act/assert shape already used in this suite (build fixtures
and request data, call the route via `client`, then assert on the response).
Run `python -m pytest tests/<file>.py -k <test name>` and confirm it fails
for the right reason — the assertion, not an import error, a fixture
mistake, or a typo in the route path. Do not write any implementation code
in this step.

**GREEN** — write the minimal code needed to make that one test pass. Do not
add extra routes, fields, validation, or error handling beyond what the
failing test requires, and do not refactor existing code in this step. Run
`python -m pytest` and confirm the new test passes and no other test broke.

**REFACTOR** — only once every test is green, improve naming, extract shared
helpers, or remove duplication in the files you touched. Do not add new
behavior here. Re-run `python -m pytest` after each refactor step and stop
immediately if a previously passing test breaks.

Keep each cycle scoped to one behavior — one route, one validation rule, one
bug fix. Never mention "TDD", "red phase", or similar meta-commentary in
code, comments, or commit messages; the result should read the same as the
rest of this codebase.

## Authentication and data-ownership rules

- Protected routes read the `Authorization: Bearer <token>` header, decode it,
  use the JWT `sub` claim as the user's email, and load that user from the
  database. Use the `CurrentUser` dependency rather than repeating that logic.
- Treat a missing, invalid, or expired token and a missing user as
  unauthenticated, and answer `401` so the client can clear its stored session.
- There is no CSRF layer, and reintroducing one would be pointless as long as
  authentication stays header-based: a cross-site request carries no ambient
  credential. Do not add cookie authentication without also restoring CSRF
  protection.
- Normalize email addresses before account lookup or persistence so application
  checks remain aligned with the database uniqueness constraint.
- Before reading for edit, updating, or deleting an `Experience` or `Education`,
  verify that its `user_id` matches the authenticated user's `id`. Never trust a
  path ID or request body value as proof of ownership, and never add `user_id`
  to a request model.
- A record that does not exist and a record belonging to someone else must get
  the same `404`, so a response never reveals that a foreign record exists.
- Hash new passwords with `hash_password`; never store or log plaintext
  passwords. Do not print tokens, secrets, or full credentials. No response
  model may expose `hashed_password`.

## Database and seed safety

- There is no migration framework. `create_db_and_tables()` runs at startup and
  only issues `CREATE TABLE IF NOT EXISTS`, so it creates missing tables but
  never alters or drops an existing one.
- A change to a persisted model therefore does **not** reach a database that
  already has that table. Say so explicitly when proposing one, and describe how
  the existing environments are expected to be updated; do not assume startup
  will apply it.
- `reset_db()` drops every table on the currently configured engine, including
  PostgreSQL. Do not call it or remove `database.db` unless the user explicitly
  asks to reset local data. Tests for destructive helpers must first replace the
  engine with a temporary SQLite engine.
- Docker data lives in the named `postgres_data` volume. Never use
  `docker compose down -v` unless the user explicitly requests deletion of the
  local PostgreSQL data.
- Keep seeding safe to run on every application startup. Do not make it overwrite
  or duplicate existing user data. Production seeding defaults to disabled.
- Tests and experiments should use a temporary SQLite database or a dependency
  override rather than modifying a developer's real SQLite or PostgreSQL data.

## Verification

The repository has a smoke-level pytest suite: nominal and "not authorized"
cases per route, ownership checks on both owned resources, and a startup check.
`pytest.ini` reports line and branch coverage for visibility but does not fail
the run below a threshold. GitHub Actions runs both suites on every push and
pull request.

```powershell
python -m pytest
```

Also verify that the application and all registered routers import after
backend or startup changes. The `-B` flag avoids writing bytecode:

```powershell
python -B -c "from main import app; print(app.title)"
```

After any frontend change, both of these must pass:

```powershell
cd frontend
npm run lint
npm run build
```

ESLint covers the frontend only. **No Python linter is configured** — do not
claim lint verification for Python unless one is added and actually executed.

For route or interface changes, start both processes and smoke-test the
affected flow in a browser. Depending on scope, check:

- the landing page, the directory, its search and pagination, and a public
  portfolio as a signed-out visitor;
- registration, login, the dashboard, and logout;
- experience and education create, edit, and delete operations;
- attempts to edit or delete records belonging to another user;
- an invalid or expired token, which must return the visitor to the login page
  rather than leaving a broken screen.

For Docker-related changes, run `docker compose config` and, when Docker is
available, build and start the affected service — the build now includes the
frontend stage, so a frontend error fails the image build. Before finishing any
task, inspect the diff and ensure generated files, local data, coverage output,
`node_modules`, and secrets are not included.

## Docker safety

- The Dockerfile is currently named lowercase `dockerfile`. Use
  `docker build -f dockerfile ...`; Compose already selects that filename
  explicitly, including on case-sensitive hosts.
- The image uses `COPY . .`. Keep `.dockerignore` exclusions for `.env`,
  `database.db`, virtual environments, Git metadata, and cache directories so
  local secrets and state never enter the image.
- Compose does not bind-mount application source or `database.db`. Rebuild the
  `eportfolio` image after code or dependency changes.
- PostgreSQL and pgAdmin persist through the named `postgres_data` and
  `pgadmin_data` volumes. Normal `docker compose down` preserves them.
- Local HTTP development should use `APP_ENV=development` and
  `COOKIE_SECURE=false`; production defaults require secure cookies.

## Documentation and deployment

Update `README.md` when routes, setup steps, environment variables, dependency
requirements, migrations, Docker behavior, or deployment behavior change.

There is currently no active production VM and no active automated deployment
target. Do not assume that `prod-vm` is deployed, run remote deployment actions,
or revive old branch/cron assumptions without an explicit user request and a
new deployment plan. Treat any older production-VM instructions in project
documentation as historical until they are deliberately replaced.
