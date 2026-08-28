"""Establish and resolve the browser session.

The access token lives in an HTTP-only cookie: scripts on the page cannot read
it, so a cross-site script injection cannot carry the credential away. The
cookie is paired with a second, script-readable cookie that only says whether a
session exists — it grants nothing, and exists so the interface can decide
before rendering whether to show a protected page or redirect.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, SQLModel, select
from starlette.responses import Response

from core.config import settings
from core.csrf import CSRF_COOKIE_NAME
from core.database import SessionDep
from core.security import decode_access_token
from schemas.User import User


ACCESS_COOKIE_NAME = "access_token"
# Read by the client purely to choose between rendering and redirecting. It
# carries no authority: forging it only produces a request the API rejects.
SESSION_HINT_COOKIE_NAME = "signed_in"


def set_session_cookies(response: Response, token: str) -> None:
    """Start a browser session for the supplied access token."""
    max_age = settings.access_token_expire_minutes * 60

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        max_age=max_age,
        # The browser may send this credential; page scripts may never read it.
        httponly=True,
        secure=settings.cookie_secure_enabled,
        # Lax keeps the cookie off cross-site state-changing requests, which is
        # the CSRF vector the token in core.csrf then closes for good.
        samesite="lax",
        path="/",
    )

    # Expires together with the credential, so the interface never believes a
    # session outlived the token behind it.
    response.set_cookie(
        key=SESSION_HINT_COOKIE_NAME,
        value="1",
        max_age=max_age,
        httponly=False,
        secure=settings.cookie_secure_enabled,
        samesite="lax",
        path="/",
    )


def clear_session_cookies(response: Response) -> None:
    """End the browser session.

    Deletion only works when the attributes match those used to set the cookie,
    which is why they are repeated here rather than left to defaults.
    """
    for name, http_only in (
        (ACCESS_COOKIE_NAME, True),
        (SESSION_HINT_COOKIE_NAME, False),
        (CSRF_COOKIE_NAME, False),
    ):
        response.delete_cookie(
            key=name,
            path="/",
            httponly=http_only,
            secure=settings.cookie_secure_enabled,
            samesite="lax",
        )


def get_optional_user(request: Request, session: SessionDep) -> User | None:
    """Return the user named by a valid session, or ``None`` when anonymous.

    Token decoding handles missing, malformed, expired, and badly signed
    values. The database lookup is still required because a technically valid
    token may reference an account that has since been removed.
    """
    payload = decode_access_token(request.cookies.get(ACCESS_COOKIE_NAME))
    if not payload:
        return None

    mail = payload.get("sub")
    # Never pass an attacker-controlled non-string subject into the SQL query.
    if not isinstance(mail, str):
        return None
    return session.exec(select(User).where(User.mail == mail)).first()


def get_current_user(request: Request, session: SessionDep) -> User:
    """Return the authenticated user or reject the request with 401.

    The client treats a 401 on a page it believed was authenticated as an
    expired session: it drops its cached profile and returns to the login page.
    """
    user = get_optional_user(request, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required to access this resource.",
        )
    return user


# Protected routes annotate a parameter with this alias instead of repeating
# the dependency call in every handler signature.
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]


def load_owned_record(
    session: Session,
    model: type[SQLModel],
    record_id: int,
    user: User,
) -> SQLModel | None:
    """Return the record when it exists and belongs to user, otherwise None."""
    record = session.get(model, record_id)
    if record and user and record.user_id == user.id:
        return record
    return None
