# Yassine Gharbi & Guillaume de Montgolfier — e-Portfolio

## Live Demo

Deployed application:

https://k2vm-229.mde.epf.fr/

---

## Overview

This project is a web application built with FastAPI that allows users to create and manage a personal e-portfolio.

The platform provides both public and private features:

* User registration
* Secure authentication
* Personal profile management
* Experience management
* Education management
* Public portfolio publication
* Portfolio search system
* Portfolio pagination system

The application is split in two: a FastAPI backend exposing a JSON API under `/api`, and a React interface that consumes it. PostgreSQL persists the data in Docker, and SQLite remains available as a fallback for local runs outside Docker.

The interface is a **multi-page application**: each screen is its own HTML document with its own React entry point, and moving between screens is a normal browser navigation rather than client-side routing. In production a single container serves both — the image builds the interface into static files that the API server also serves.

---

## Tech Stack

### Backend

* Python 3.12
* FastAPI
* SQLModel
* PostgreSQL (Docker)
* SQLite (local fallback)

### Security

* JWT Authentication (Bearer token)
* Argon2 Password Hashing
* Server-side ownership checks on every record

### Frontend

* React 19
* Vite (multi-page build)
* Tailwind CSS v4

### DevOps

* Docker
* Docker Compose
* Git
* Cron-based Continuous Deployment

---

## Features

### Public Features

* Public homepage listing all available portfolios
* Search portfolios by name
* Pagination system
* Public portfolio pages accessible without authentication

### Authentication & Security

* User registration
* Secure login/logout
* JWT-based authentication
* HTTP-only authentication cookies
* Password hashing using Argon2
* Protected routes
* Session invalidation after logout

### Profile Management

* Personal profile page
* Automatic age calculation from birth date
* Display personal information

### Experience Management

* Create experiences
* Read experiences
* Update experiences
* Delete experiences

### Education Management

* Create education entries
* Read education entries
* Update education entries
* Delete education entries

### Multi-user Support

* Data ownership system
* User isolation
* Protected user resources
* Users cannot modify another user's data

---

## Application Routes

### Pages

| Page               | Description                          |
| ------------------ | ------------------------------------ |
| `/`                | Landing page                         |
| `/portfolios.html` | Public directory, search, pagination |
| `/portfolio.html?id={id}` | Public portfolio               |
| `/login.html`      | Login                                |
| `/signup.html`     | Registration                         |
| `/profile.html`    | Private dashboard                    |

### API

Every endpoint answers JSON, and reports a failure as `{"error": "..."}`.
Protected endpoints expect an `Authorization: Bearer <token>` header.

| Method   | Endpoint                  | Auth | Description                          |
| -------- | ------------------------- | ---- | ------------------------------------ |
| `GET`    | `/api/health`             | no   | Application and database liveness    |
| `GET`    | `/api/portfolios`         | no   | Directory; `?query=` and `?page=`    |
| `GET`    | `/api/portfolios/{id}`    | no   | One public portfolio                 |
| `POST`   | `/api/signup`             | no   | Create an account                    |
| `POST`   | `/api/login`              | no   | Returns `{token, user}`              |
| `POST`   | `/api/logout`             | yes  | Stateless acknowledgement            |
| `GET`    | `/api/me`                 | yes  | Own profile, experiences, educations |
| `GET`    | `/api/experiences`        | yes  | Own experiences                      |
| `POST`   | `/api/experiences`        | yes  | Add an experience                    |
| `PUT`    | `/api/experiences/{id}`   | yes  | Update an owned experience           |
| `DELETE` | `/api/experiences/{id}`   | yes  | Delete an owned experience           |
| `GET`    | `/api/educations`         | yes  | Own education entries                |
| `POST`   | `/api/educations`         | yes  | Add an education entry               |
| `PUT`    | `/api/educations/{id}`    | yes  | Update an owned education entry      |
| `DELETE` | `/api/educations/{id}`    | yes  | Delete an owned education entry      |

A record belonging to another account answers `404`, exactly like one that does
not exist, so a response never reveals that a foreign record exists.

---

## Database Design

The application uses a relational database implemented with SQLModel.

### User

| Field           | Type        |
| --------------- | ----------- |
| id              | Primary Key |
| name            | String      |
| first_name      | String      |
| birth_date      | Date        |
| mail            | String      |
| phone           | String      |
| hashed_password | String      |

### Experience

| Field       | Type        |
| ----------- | ----------- |
| id          | Primary Key |
| title       | String      |
| company     | String      |
| date_start  | Date        |
| date_end    | Date        |
| description | String      |
| user_id     | Foreign Key |

### Education

| Field       | Type        |
| ----------- | ----------- |
| id          | Primary Key |
| school_name | String      |
| major       | String      |
| date_start  | Date        |
| date_end    | Date        |
| description | String      |
| user_id     | Foreign Key |

---

## Relationships

### User → Experience (1:N)

A user can own multiple professional experiences.

### User → Education (1:N)

A user can own multiple education entries.

Relationship rules:

* One experience belongs to one user.
* One education entry belongs to one user.
* Deleting a user removes access to their associated records.

---

## Project Structure

```text
.
├── core/
│   ├── authentication.py     # Bearer token -> User, CurrentUser dependency
│   ├── config.py             # validated environment settings
│   ├── database.py           # engine, schema creation, session dependency
│   ├── security.py           # Argon2 hashing, JWT signing
│   └── validation.py         # shared input rules and their messages
│
├── routers/                  # every route lives under /api
│   ├── auth.py               # directory, search, login, logout
│   ├── user.py               # signup, dashboard, public portfolio
│   ├── experience.py         # owned CRUD
│   └── education.py          # owned CRUD
│
├── schemas/
│   ├── User.py               # SQLModel tables
│   ├── Experiences.py
│   ├── Education.py
│   └── api.py                # JSON request and response bodies
│
├── frontend/
│   ├── index.html            # one document per screen
│   ├── login.html
│   ├── signup.html
│   ├── portfolios.html
│   ├── portfolio.html
│   ├── profile.html
│   ├── vite.config.js        # declares those six entries, proxies /api
│   └── src/
│       ├── entries/          # one React mount per document
│       ├── pages/            # page-level components
│       ├── components/       # shared UI, with ui/ holding the primitives
│       ├── lib/              # API client, session, formatters
│       └── styles/           # Tailwind theme and design tokens
│
├── tests/
├── docker-compose.yml
├── dockerfile                # builds the frontend, then the Python runtime
├── requirements.txt
├── seed.py
└── main.py

```

---

## Local development with Docker

### 1. Clone the Repository

```bash
git clone <repository-url>
cd e-portfolio
```

### 2. Configure the environment

Create the local environment file and replace every placeholder secret:

```powershell
Copy-Item .env.example .env
```

Keep the development values below when accessing the application over local HTTP:

```dotenv
APP_ENV=development
COOKIE_SECURE=false
SEED_DEMO_DATA=true
```

### 3. Build and start the complete stack

```powershell
docker compose up -d --build
docker compose ps
```

Follow the application logs with:

```powershell
docker compose logs -f eportfolio
```

The application is available at `http://127.0.0.1:8000` and pgAdmin at
`http://127.0.0.1:5050`. The image builds the interface itself, so that single
address serves both the pages and the API. Docker Compose is the reference
full-stack workflow for this project.

## Local development without Docker

Working on the interface is faster outside Docker, because the Vite dev server
reloads a change instantly instead of rebuilding an image. This mode runs **two
processes**.

Install both sets of dependencies once:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

cd frontend
npm ci
cd ..
```

Start the API in one shell:

```powershell
fastapi dev main.py
```

Start the interface in a second shell:

```powershell
cd frontend
npm run dev
```

Then open **`http://127.0.0.1:5173`**, not the FastAPI port: the Vite server
serves the pages and forwards every `/api` call to FastAPI on port 8000.
Browsing port 8000 directly shows only the API, because `frontend/dist` does
not exist until you run `npm run build`.

With `SEED_DEMO_DATA=true`, startup fills the database with ten demonstration
portfolios (one education entry and two experiences each), so the directory and
the search have something to show immediately. Those accounts log in with the
password `test` — for example `user1@mail.com`. Seeding is idempotent and
disabled by default in production.

## Automated tests

The automated test suite uses a temporary SQLite database and does not read or
modify the developer's `database.db`. Run it in its own Python 3.12 virtual
environment so packages installed for another application cannot conflict with
this project's pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

`pytest.ini` enables branch coverage for the application code and the terminal
report lists uncovered lines.

The interface has its own checks, run from `frontend/`:

```powershell
npm run lint
npm run build
```

GitHub Actions runs both suites on every push and pull request: a Python job
that verifies the dependency set, checks that the application imports, and runs
pytest against an isolated SQLite database, and a Node job that installs from
the lockfile, lints, and builds the interface.

## AI-assisted development with local LLMs

This project is developed with [Cline](https://cline.bot) (a VS Code extension)
driving **local** models served by [Ollama](https://ollama.com). Nothing is sent
to a third-party API, and no API key is required. This setup is entirely
optional: it does not affect the application, the tests, or the Docker build.

> Earlier revisions of this README documented an [Aider](https://aider.chat)
> setup. It was removed in favour of Cline — see
> [Why Cline replaced Aider](#why-cline-replaced-aider) below.

### Prerequisites

Install Ollama, install Cline from the VS Code marketplace, then pull the
models. Ollama stores them wherever `OLLAMA_MODELS` points (a `blobs/` directory
holding the weights and a `manifests/` directory indexing them); leave the
variable unset to use the default location.

```powershell
ollama pull gpt-oss:20b          # heavy tasks: refactors, features, tests
ollama pull qwen2.5-coder:7b     # commit messages, PR titles and descriptions
ollama pull qwen3-coder:30b      # alternative for heavy tasks
```

Check that the local server is answering before starting:

```powershell
ollama list
```

In Cline, select the **Ollama** provider and point it at
`http://127.0.0.1:11434`; the model list is populated from `ollama list`.

### Server environment variables

These are read by the **Ollama server**, not by the client. On Windows the desktop
app reads them at launch, so set them at user scope and restart Ollama:

```powershell
# 1. Persist them for future sessions (writes to the registry).
[Environment]::SetEnvironmentVariable('OLLAMA_MODELS','D:\llms','User')
[Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION','1','User')
[Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE','q8_0','User')
[Environment]::SetEnvironmentVariable('OLLAMA_CONTEXT_LENGTH','65536','User')

# 2. Also set them in THIS shell — see the trap below.
$env:OLLAMA_FLASH_ATTENTION = '1'
$env:OLLAMA_KV_CACHE_TYPE   = 'q8_0'
$env:OLLAMA_CONTEXT_LENGTH  = '65536'

# 3. Restart the server so it reads them.
Get-Process 'ollama app','ollama' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
```

> **Trap: step 2 is not redundant.** `SetEnvironmentVariable(..., 'User')` writes
> to the registry but does **not** refresh the environment block of processes
> that are already running — including the shell you are typing in. Restarting
> Ollama from that shell hands it a stale environment, and it starts with the
> variables unset while the registry says otherwise. Either set them in the
> current session as above, or log out and back in before restarting Ollama.

**Always verify rather than assume.** The server logs its entire configuration
at startup, which is the only trustworthy confirmation:

```powershell
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" |
  Select-String 'server config' | Select-Object -Last 1
```

Expect `OLLAMA_CONTEXT_LENGTH:65536`, `OLLAMA_FLASH_ATTENTION:true` and
`OLLAMA_KV_CACHE_TYPE:q8_0`. A `CONTEXT_LENGTH:0`, `FLASH_ATTENTION:false` or an
empty `KV_CACHE_TYPE` means the restart did not pick them up — the models still
load and answer normally, so nothing warns you that the tuning is inactive.

| Variable | Role |
|---|---|
| `OLLAMA_MODELS` | Where weights are stored. Point it at a data drive — the models are tens of GB |
| `OLLAMA_FLASH_ATTENTION` | Required for `OLLAMA_KV_CACHE_TYPE` to take effect; ignored silently without it |
| `OLLAMA_KV_CACHE_TYPE` | `q8_0` halves the memory the context cache needs, for a negligible quality cost |
| `OLLAMA_CONTEXT_LENGTH` | Server-side default window. **A model's own `num_ctx` overrides it** — see below |
| `OLLAMA_KEEP_ALIVE` | How long an idle model stays in memory (default `5m`) |

These variables configure the **server** only. A client cannot set them.

### Model configuration: custom Modelfiles

Cline sends no per-request `num_ctx`, so the context window has to be baked into
the model itself. Without that, Ollama falls back to its own default and the
window is either too small for the repository map or large enough to fail on
`cudaMalloc failed: out of memory`. The fix is a derived model:

```dockerfile
# gpt-oss-cline.Modelfile
FROM gpt-oss:20b
PARAMETER num_ctx 32768
PARAMETER temperature 1
```

```powershell
ollama create gpt-oss-cline -f gpt-oss-cline.Modelfile
```

Derived models cost no extra disk: they reference the same blobs as the parent
and only add a manifest. The two used here:

| Model | Derived from | Parameters |
|---|---|---|
| `gpt-oss-cline` | `gpt-oss:20b` | `num_ctx 32768`, `temperature 1` |
| `qwen3-coder-cline` | `qwen3-coder:30b` | `num_ctx 32768`, `repeat_penalty 1.1`, `top_p 0.8`, `top_k 20`, `temperature 0.7` |

`repeat_penalty 1.1` is the usual guard against a small model looping on the same
paragraph inside a single answer.

### Which model for which task

| Task | Model | Why |
|---|---|---|
| Refactors, features, writing tests | `gpt-oss-cline` | Best quality/speed compromise on 8 GB of VRAM |
| Commit messages, PR titles and descriptions | `qwen2.5-coder:7b` | Fits entirely in VRAM, so these stay instant |

Project rules live in `AGENTS.md` — add it to Cline's context at the start of a
session so ownership checks and the schema-change workflow are respected.

### Why Cline replaced Aider

Aider was used first, with a per-model context file and a set of `/model`
aliases. It was dropped for three practical reasons:

- **Fewer hallucinations** on the same local models and the same prompts —
  Cline's tool-based editing gives the model less room to invent file contents
  than a free-form diff it has to format correctly.
- **Editor integration.** Cline runs inside VS Code, so the diff to review is the
  one shown in the editor, instead of a terminal round-trip.
- **No client-side model configuration to maintain.** Baking `num_ctx` into a
  Modelfile fixes the window at the source, for every client, rather than in one
  tool's settings file.

Nothing about the Ollama server setup below changed with the switch — that part
is client-agnostic.

### Limits of running LLMs locally

The reference machine for this configuration is a **Dell G15 5530: RTX 4060
Laptop with 8 GB of VRAM, 32 GB of system RAM**. Every value below is derived
from that budget — recompute them if your hardware differs.

**Active parameters matter more than model size.** What a GPU must move for each
generated token is the *active* parameters, not the total. A mixture-of-experts
model such as `qwen3-coder:30b` holds 30 B weights but activates only ~3.3 B per
token, so it stays usable even when two thirds of it sits in system RAM. A dense
model activates everything: once `qwen2.5-coder:32b` overflows 8 GB of VRAM,
every token drags 19 GB across the PCIe bus. This is why a MoE model is the
practical default here while a 32 B dense one is unusable for editing loops.

**Measured on the reference machine.** Same prompt for every model, a cold load
each time, generation rate as reported by `ollama run --verbose`:

| Model | Arch. | Size | Load | Prefill (tok/s) | **Generation (tok/s)** |
|---|---|---|---|---|---|
| `qwen2.5-coder:7b` | dense | 4.7 GB | 3.5 s | 276.0 | **31.9** |
| `deepseek-coder-v2:16b` | MoE | 8.9 GB | 21.8 s | 23.9 | **18.8** |
| `qwen3-coder:30b` | MoE | 18 GB | 35.3 s | 21.7 | **17.5** |
| `gpt-oss:20b` | MoE | 13 GB | 27.9 s | 61.8 | **15.9** |
| `qwen2.5-coder:14b` | dense | 9.0 GB | 30.4 s | 54.2 | **6.8** |
| `qwen2.5-coder:32b` | dense | 19 GB | 38.4 s | 21.6 | **1.85** |

Read it by architecture, not by size. `deepseek-coder-v2:16b` (MoE, 8.9 GB) is
**2.8× faster** than `qwen2.5-coder:14b` (dense, 9.0 GB) at essentially the same
footprint — the only difference is how many parameters each token activates.
Below the VRAM ceiling that penalty disappears: the 7 B model is dense and the
fastest of the set precisely because it never spills.

At the other end, `qwen2.5-coder:32b` produces **1.85 tok/s** — roughly seven
minutes for a single answer. It is not a slow option, it is not an option.

Two cautions when comparing these figures. *Prefill* (ingesting the prompt) and
*generation* are different rates, and the first is several times the second —
quoting the prefill number overstates what the model actually feels like. And
these come from one prompt on one machine: expect drift with a different context
length or a warm cache, but the ordering holds.

**The context window is not free.** Ollama 0.32 defaults to 4096 tokens, which
silently truncates the repository map and the files submitted for editing. But
raising it allocates a *KV cache* that grows linearly with the window and sits
in memory **on top of the weights**. For `qwen3-coder:30b` (48 layers, 4 KV
heads, head_dim 128) one token costs ~96 KB in f16:

| Window | KV cache f16 | KV cache q8_0 | Total with 17.3 GB of weights |
|---|---|---|---|
| 32K | 3.1 GB | 1.6 GB | 18.9 GB |
| 64K | 6.3 GB | **3.1 GB** | **20.4 GB** |
| 128K | 12.6 GB | 6.3 GB | 23.6 GB |
| 256K | 25.2 GB | 12.6 GB | 29.9 GB — will not load |

Advertising a 256K context does not mean your hardware can hold it.

That table only counts *total* memory, though, and fitting is not the goal —
staying on the GPU is. Both windows were measured on the reference machine:

| `num_ctx` | Footprint | CPU/GPU split | Free system RAM |
|---|---|---|---|
| 65536 | 22 GB | 72% / 28% | 3.3 GB |
| **32768** | **20 GB** | **69% / 31%** | **6.2 GB** |

Generation runs at **~16-17 tok/s** either way (the table above measured 17.5 at
32768). The lesson is that shrinking the
window buys far less GPU residency than the arithmetic suggests: 18 GB of
weights will never fit in 6.9 GB of usable VRAM whatever the context, so the
split is dominated by model size, not by the KV cache. Going below 32K would
gain almost nothing.

The real payoff is elsewhere — free system RAM nearly doubles, which is what
keeps the machine off the page file when a browser or an editor asks for memory
mid-generation. That is the reason to prefer 32768 here, not the GPU split.

If you genuinely want a mostly-GPU-resident model, the only lever is a smaller
one: `deepseek-coder-v2:16b` (8.9 GB) fits far better, at a cost in quality.
`OLLAMA_CONTEXT_LENGTH` stays at 65536 as a server-side ceiling, but the
per-model value is what actually runs.

**First load takes time.** Reading 18 GB from disk costs ~100 s; afterwards the
model stays resident for `OLLAMA_KEEP_ALIVE` (5 minutes). Raise that variable to
`30m` if reloads become annoying — at the cost of holding the memory that long.

**Precedence trap.** The effective window is the first of: an option sent with
the request, then the model's own `PARAMETER num_ctx`, then
`OLLAMA_CONTEXT_LENGTH`. Cline sends nothing, so the Modelfile value is what
actually runs — and a model used *without* a derived variant silently falls back
to the server default. Create the variant for every model you intend to drive
from Cline.

**Measure, do not trust the table.** The figures above are arithmetic, not a
benchmark of your machine. Start a session, then in a second terminal:

```powershell
ollama ps    # qwen3-coder:30b   20 GB   69%/31% CPU/GPU   32768
```

Read the split together with free system RAM, not on its own: a high CPU share
is expected here and still yields usable speed, whereas an exhausted RAM budget
means swapping and does not. Confirm the CUDA device is the one being used —
Ollama excludes integrated GPUs by default, and the startup log says so
explicitly:

```powershell
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" |
  Select-String 'inference compute|dropping integrated GPU' | Select-Object -Last 2
```

On the reference machine that reports `library=CUDA … RTX 4060 Laptop GPU` and
`dropping integrated GPU` for the Intel controller — the discrete card is doing
the work.

### Disk usage: what to clean, and where

Two different things get called "cache". Only one of them ever touches the disk.

**The KV cache never does.** It lives in VRAM and RAM, is rebuilt for each
loaded model, and is released when Ollama unloads it after `OLLAMA_KEEP_ALIVE`
(5 minutes idle by default). There is nothing to delete and no maintenance to
schedule — restarting Ollama, or simply waiting, frees it. To release it now:

```powershell
ollama ps                 # models currently resident in memory
ollama stop qwen3-coder:30b
```

**The weights do, and they are the only large item.** They live under
`OLLAMA_MODELS` — `D:\llms` here, not on `C:` — and grow **only** when you run
`ollama pull`. They never grow on their own, so no periodic cleanup is needed;
you delete a model when you have stopped using it:

```powershell
Get-ChildItem D:\llms\blobs -File | Measure-Object Length -Sum   # actual footprint
ollama rm qwen2.5-coder:32b                                      # frees its blobs
```

Always use `ollama rm`. Deleting files inside `blobs/` by hand leaves the
manifests pointing at missing layers, and the model then fails to load with no
way to repair it short of re-pulling. Note that blobs are shared: a layer used
by two models is only reclaimed once the last of them is removed, so `ollama rm`
does not always free the size shown by `ollama list`.

**What remains on `C:` is negligible** and needs no upkeep:

| Path | Contents | Growth |
|---|---|---|
| `%LOCALAPPDATA%\Programs\Ollama` | The Ollama binaries | Fixed; the installer manages it |
| `%LOCALAPPDATA%\Ollama` | `server.log`, `app.log`, `db.sqlite` | Under a MB, rotated automatically |
| `%USERPROFILE%\.ollama` | SSH keypair identifying the machine to the registry, plus an empty `cache/` | Effectively zero — do not delete the keys |

**Cline stores its task history in the VS Code extension's own storage**, not in
the repository, so nothing accumulates here and `.gitignore` needs no entry for
it.

Review AI-written diffs like any other contribution: the project rules in
`AGENTS.md` — ownership checks, the JSON error envelope, schema changes —
still apply.

## Dependencies

This section explains the key dependencies and why they were chosen.

### Core Framework

| Package | Role |
|---|---|
| `fastapi` | Web framework — chosen for its automatic OpenAPI docs, native Pydantic integration, and async support |
| `uvicorn` | ASGI server used to run the FastAPI app in production |
| `starlette` | Underlying toolkit FastAPI is built on (routing, middleware, static files) |
| `pydantic-settings` | Loads and validates environment configuration, failing fast on an unsafe setup |

### Database

| Package | Role |
|---|---|
| `sqlmodel` | ORM chosen for its dual role: defines models used both as database tables and as Pydantic validation schemas, avoiding code duplication |
| `sqlalchemy` | Underlying database engine used by SQLModel |
| `psycopg` | PostgreSQL driver used by SQLAlchemy in Docker |
| `greenlet` | Required by SQLAlchemy for async context support |

### Security

| Package | Role |
|---|---|
| `argon2-cffi` | Argon2 password hashing — chosen over bcrypt or SHA-256 for its resistance to GPU and ASIC brute-force attacks (memory-hard algorithm) |
| `pwdlib` | High-level wrapper around argon2-cffi for password hashing/verification |
| `pyjwt` | JWT token generation and verification for stateless authentication |
| `python-dotenv` | Loads environment variables (secret key, config) from a `.env` file |

### Validation

| Package | Role |
|---|---|
| `pydantic` | Data validation library, used natively by FastAPI for request/response schemas |
| `annotated-types` | Extends Python type annotations, used internally by Pydantic |

### Dev & CLI

| Package | Role |
|---|---|
| `fastapi-cli` | Provides the `fastapi run` and `fastapi dev` commands |
| `click`, `typer`, `rich` | CLI utilities used internally by fastapi-cli |
| `watchfiles` | File watching for hot-reload in development mode |

### Tests

| Package | Role |
|---|---|
| `pytest` | Discovers and executes unit and HTTP integration tests |
| `httpx` | Provides the transport used by Starlette's synchronous `TestClient` |
| `pytest-cov`, `coverage` | Measure line and branch coverage and enforce the initial CI threshold |

> **Note:** Some packages in `requirements.txt` are transitive dependencies (automatically installed by the packages above) and are not imported directly in the application code.

### Frontend

Declared in `frontend/package.json` and locked in `frontend/package-lock.json`.

| Package | Role |
|---|---|
| `react`, `react-dom` | Render the interface; each page mounts its own root |
| `vite` | Dev server with instant reload, and the production build that emits one bundle per page |
| `@vitejs/plugin-react` | Adds JSX and fast refresh to Vite |
| `tailwindcss`, `@tailwindcss/vite` | Utility styling driven by the design tokens in `src/styles/tailwind.css` |
| `eslint` and its React plugins | Catch invalid hook and effect usage before it reaches the browser |

There is deliberately no routing library: pages are separate documents, so
navigation is handled by the browser.

---

## Docker Deployment

Docker Compose starts three containers:

* `eportfolio-app`: the FastAPI application, available on port `8000`.
* `eportfolio-db`: PostgreSQL, available on port `5432` and persisted in the `postgres_data` Docker volume.
* `eportfolio-pgadmin`: pgAdmin, available on port `5050` and persisted in the `pgadmin_data` Docker volume.

Copy `.env.example` to `.env`, then replace `SECRET_KEY`, `POSTGRES_PASSWORD`, and `PGADMIN_DEFAULT_PASSWORD`. `SECRET_KEY` must contain at least 32 characters and cannot keep the example placeholder. Docker Compose deliberately refuses to start when required variables are absent. The real `.env` file is ignored by Git and must remain local to each developer or deployment server.

Linux/macOS:

```bash
cp .env.example .env
chmod 600 .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

For production, use the following security settings:

```dotenv
APP_ENV=production
COOKIE_SECURE=true
SEED_DEMO_DATA=false
```

`COOKIE_SECURE` defaults to `true` and demonstration seeding defaults to `false` when `APP_ENV=production`. Development keeps HTTP cookies and sample data available unless these values are explicitly overridden.

### Build Image

```bash
docker build -t e-portfolio .
```

### Start Container

```bash
docker compose up -d
```

### Rebuild Container

```bash
docker compose up -d --build
```

### Check Services

```bash
docker compose ps
docker compose logs -f
```

### Connect to PostgreSQL

Use `localhost:5432` from a database client such as DBeaver or pgAdmin. The database name, user, password, and exposed port are configured in `.env`. PostgreSQL is bound to the host's loopback interface, so its port is not publicly exposed by the server.

To open a SQL shell inside the database container:

```bash
docker compose exec db psql -U eportfolio -d eportfolio
```

`docker compose down` keeps the database. Use `docker compose down -v` only when you intentionally want to delete the PostgreSQL data volume.

### Open pgAdmin

Open `http://127.0.0.1:5050` and sign in with `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` from `.env`.

On the first connection, register the PostgreSQL server with these values:

| Field | Value |
|---|---|
| Name | `ePortfolio` |
| Host name/address | `db` |
| Port | `5432` |
| Maintenance database | value of `POSTGRES_DB` |
| Username | value of `POSTGRES_USER` |
| Password | value of `POSTGRES_PASSWORD` |

Use `db`, not `localhost`, because pgAdmin connects to PostgreSQL through the internal Docker Compose network.

### Changing the database schema

The files in `schemas/` are SQLModel table definitions. At startup `main.py`
calls `create_db_and_tables()`, which issues `CREATE TABLE IF NOT EXISTS` for
every declared table.

That creates tables the database does not have yet. It does **not** alter a
table that already exists: adding a column to `schemas/User.py` has no effect on
a PostgreSQL volume that already holds a `user` table, and the application will
then fail when it queries the missing column.

There is no migration framework in this project, so a change to an existing
table has to be applied deliberately. Depending on the situation:

* **Local development, data you can lose.** Drop the volume and let startup
  recreate the schema. This deletes every row:

```powershell
docker compose down -v
docker compose up -d --build
```

* **Data you want to keep.** Apply the change by hand with SQL before deploying
  the code, for example through pgAdmin or `psql`:

```sql
ALTER TABLE "user" ADD COLUMN bio VARCHAR;
```

* **A shared environment.** Adopt a migration tool before the first schema
  change that matters. Anything else is a manual step someone will eventually
  forget to run.

Because `create_all` never drops anything, removing a field from a model leaves
its column in place, holding data nothing reads any more. Drop it explicitly
when that matters.

## Automated Deployment

The production environment uses an automated deployment strategy directly executed on the virtual machine.

Every 2 minutes, a deployment script checks the `prod-vm` branch and automatically deploys any new version.

### Deployment Script

```bash
#!/bin/bash

echo "DEPLOY $(date)"

cd /home/yassine/web_prog/e-portfolio || exit 1

git pull origin prod-vm

sudo docker compose up -d --build

sudo docker image prune -f

echo "DEPLOY DONE $(date)"
```

### Cron Configuration

```cron
*/2 * * * * /home/yassine/deploy.sh >> /home/yassine/deploy.log 2>&1
```

### Deployment Workflow

1. Fetch latest code from GitHub.
2. Pull updates from the `prod-vm` branch.
3. Rebuild Docker image.
4. Recreate application container.
5. Remove unused Docker images.
6. Store deployment logs.

### Deployment Logs

```text
/home/yassine/deploy.log
```

### Benefits

* Fully automated deployment.
* No manual intervention required.
* No public SSH exposure.
* Compatible with Proxmox and NAT environments.
* Automatic Docker image cleanup.
* Continuous synchronization with the production branch.

---

## Notes

* Missing tables are created at startup; altering an existing table is a deliberate manual step, since the project has no migration framework.
* Demonstration data is enabled by default only outside production and is controlled by `SEED_DEMO_DATA`.
* Authentication relies on a JWT sent as an `Authorization: Bearer` header, so no credential is attached to a cross-site request.
* Passwords are hashed before storage using Argon2.
* Pagination is implemented on the public directory and its search results.
* Docker is used for production deployment.
