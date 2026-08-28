"""Create and configure the FastAPI e-portfolio application.

This module is deliberately limited to application wiring: the database schema
and optional demo data are prepared during startup, CSRF protection is
installed, error responses are given one uniform JSON shape, the JSON routers
are registered, and the compiled frontend is served when it has been built.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from core.config import settings
from core.csrf import (
    CSRF_COOKIE_NAME,
    SAFE_METHODS,
    get_or_create_csrf_token,
    set_csrf_cookie,
    validate_csrf_token,
)
from core.database import SessionDep, create_db_and_tables
from routers import auth, education, experience, user
from seed import seed

# The Vite build writes its pages and hashed assets here. Resolving the path
# from this file keeps it correct even when the process is started from another
# working directory.
FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare persistent application state before accepting HTTP requests.

    The schema is created first so route handlers never execute against a
    database with missing tables. Demo data is then synchronized only when the
    active environment has explicitly enabled it (or when development defaults
    apply).
    """
    # ``create_all`` is a no-op for tables that already exist, which keeps
    # repeated startups safe on an already populated database.
    create_db_and_tables()
    if settings.seed_demo_data_enabled:
        seed()

    # Control returns to FastAPI for the complete lifetime of the application.
    yield


# Passing the lifespan explicitly makes startup preparation part of FastAPI's
# supported lifecycle rather than relying on deprecated startup events.
app = FastAPI(title="e-portfolio", lifespan=lifespan)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    """Issue the CSRF token, and require it on every state-changing request.

    Guarding here rather than route by route means a new mutating endpoint is
    protected the moment it is registered, instead of the day someone remembers
    to add the check.

    Errors raised inside middleware bypass the exception handlers below, so the
    rejection is built by hand to keep the one error shape the client expects.
    """
    csrf_token = get_or_create_csrf_token(request)

    if request.method not in SAFE_METHODS:
        try:
            validate_csrf_token(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    response = await call_next(request)

    # Only emit Set-Cookie when the client has no token (or sent an invalid
    # one) so normal requests do not keep refreshing the cookie lifetime.
    if request.cookies.get(CSRF_COOKIE_NAME) != csrf_token:
        set_csrf_cookie(response, csrf_token)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return raised HTTP errors as ``{"error": "..."}``.

    The browser client reads that single key for every failure, so overriding
    FastAPI's default ``{"detail": ...}`` envelope here means no handler has to
    build error responses by hand.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Report a malformed request body in the same error envelope.

    Field-level rules live in ``core.validation`` and already produce readable
    messages; reaching this handler means the payload was structurally wrong
    (a missing key, or a value of the wrong JSON type), which the interface
    only has to report generically.
    """
    return JSONResponse(
        status_code=422,
        content={"error": "The submitted data is invalid or incomplete."},
    )


# Le healthcheck sert aux sondes externes (Docker, supervision) : il ne se
# contente pas de repondre, il verifie que la base repond elle aussi.
@app.get("/api/health")
def health_check(session: SessionDep):
    """Signale que l'application et sa base de donnees repondent."""
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


# Register the discovery/authentication, profile, experience, and education
# routes. Every one of them lives under /api.
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(experience.router)
app.include_router(education.router)


# The compiled frontend is mounted last so that none of the API routes above
# can be shadowed by a static file. In development the directory does not
# exist: the Vite dev server serves the pages and proxies /api here, so the
# mount is simply skipped.
if FRONTEND_DIST.is_dir():
    # ``html=True`` resolves a bare directory request to index.html, which is
    # what makes "/" load the landing page of this multi-page frontend.
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
