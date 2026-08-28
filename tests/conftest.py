"""Shared pytest fixtures backed by an isolated temporary SQLite database."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from datetime import date

import pytest

# Configuration must be deterministic before importing the application.  The
# fallback engine is deliberately in-memory as an additional safeguard: route
# dependencies are overridden below, and no test may reach ``database.db``.
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "pytest-only-secret-key-that-is-never-used-in-production"
os.environ["COOKIE_SECURE"] = "false"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import URL, Engine  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

import main as main_module  # noqa: E402
from core.database import get_session  # noqa: E402
from core.security import hash_password  # noqa: E402
from main import app  # noqa: E402
from schemas.User import User  # noqa: E402


DEFAULT_PASSWORD = "ValidPass123"


@pytest.fixture
def test_engine(tmp_path) -> Iterator[Engine]:
    """Create a fresh SQLite schema in pytest's temporary directory."""
    database_path = tmp_path / "test.db"
    engine = create_engine(
        URL.create("sqlite", database=str(database_path)),
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session(test_engine: Engine) -> Iterator[Session]:
    """Expose a test session for arranging and inspecting persisted records."""
    with Session(test_engine) as database_session:
        yield database_session


@pytest.fixture
def client(
    test_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    """Serve the real app while replacing every persistent database access."""

    def override_get_session() -> Iterator[Session]:
        with Session(test_engine) as request_session:
            yield request_session

    # Entering TestClient runs the application lifespan.  Patch both startup
    # actions so it cannot touch or seed the developer's configured database.
    monkeypatch.setattr(main_module, "create_db_and_tables", lambda: None)
    monkeypatch.setattr(main_module, "seed", lambda: None)
    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app, base_url="http://testserver") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def user_factory(session: Session) -> Callable[..., User]:
    """Return a factory that persists users with safely hashed passwords."""

    def create_user(
        *,
        mail: str = "owner@example.com",
        password: str = DEFAULT_PASSWORD,
        name: str = "Lovelace",
        first_name: str = "Ada",
        birth_date: date = date(1990, 1, 1),
        phone: str = "0612345678",
    ) -> User:
        user = User(
            name=name,
            first_name=first_name,
            birth_date=birth_date,
            mail=mail,
            phone=phone,
            hashed_password=hash_password(password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return create_user


@pytest.fixture
def access_token(client: TestClient) -> Callable[..., str]:
    """Return a helper that logs in through the real route and yields its token.

    Obtaining the credential the way the browser does keeps these tests honest:
    a change that breaks login breaks every authenticated test with it, instead
    of being hidden behind a hand-signed token.
    """

    def login(mail: str, password: str = DEFAULT_PASSWORD) -> str:
        response = client.post("/api/login", json={"mail": mail, "password": password})
        assert response.status_code == 200
        return response.json()["token"]

    return login


@pytest.fixture
def bearer() -> Callable[[str], dict[str, str]]:
    """Return a helper building the Authorization header for one token."""

    def header(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return header


@pytest.fixture
def registered_user(user_factory: Callable[..., User]) -> User:
    """Persist the default account shared by authenticated route tests."""
    return user_factory()


@pytest.fixture
def authenticated_client(
    client: TestClient,
    registered_user: User,
    access_token: Callable[..., str],
) -> TestClient:
    """Return a client sending a valid Bearer credential on every request."""
    client.headers["Authorization"] = f"Bearer {access_token(registered_user.mail)}"
    return client
