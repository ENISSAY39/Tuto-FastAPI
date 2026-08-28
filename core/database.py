"""Configure the database engine, schema creation, and request-scoped sessions."""

import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import URL
from sqlmodel import Session, SQLModel, create_engine


def get_database_url():
    """Return the configured database URL, with SQLite as a local fallback.

    A complete ``DATABASE_URL`` has highest priority. Compose-style PostgreSQL
    components are assembled only when ``POSTGRES_HOST`` is set, allowing the
    same application image to connect to the database service by hostname.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    postgres_host = os.getenv("POSTGRES_HOST")
    if postgres_host:
        # URL.create performs correct credential escaping and avoids manually
        # concatenating passwords that may contain reserved URL characters.
        return URL.create(
            drivername="postgresql+psycopg",
            username=os.getenv("POSTGRES_USER", "eportfolio"),
            password=os.getenv("POSTGRES_PASSWORD", "eportfolio_dev"),
            host=postgres_host,
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "eportfolio"),
        )

    # SQLite keeps a zero-configuration local fallback for non-Compose tooling.
    return "sqlite:///database.db"


database_url = get_database_url()
# Detect stale pooled connections before handing them to an HTTP request.
engine_options = {"pool_pre_ping": True}

if str(database_url).startswith("sqlite"):
    # FastAPI may serve requests on different threads, so the default SQLite
    # same-thread guard is incompatible with the shared engine.
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_options)


def create_db_and_tables() -> None:
    """Create every declared table that does not already exist.

    Importing the table modules is what registers them in
    ``SQLModel.metadata``; the import lives inside the function so ordinary
    session consumers do not pull the whole schema package merely by importing
    this module. ``create_all`` only issues ``CREATE TABLE IF NOT EXISTS`` and
    therefore never drops or alters an existing table.
    """
    # These imports are intentionally unused as Python values: defining the
    # classes is what populates the metadata used just below.
    from schemas.Education import Education  # noqa: F401
    from schemas.Experiences import Experience  # noqa: F401
    from schemas.User import User  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield one SQLModel session and close it after the request completes."""
    with Session(engine) as session:
        yield session


# Route annotations can use this alias to obtain the request-scoped dependency
# without repeating ``Depends(get_session)`` in every handler signature.
SessionDep = Annotated[Session, Depends(get_session)]
