"""Resolve the authenticated user from the ``Authorization`` request header.

The browser client stores its access token in ``localStorage`` and attaches it
as a ``Bearer`` credential, so authentication is entirely header based and no
cookie is involved.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, SQLModel, select

from core.database import SessionDep
from core.security import decode_access_token
from schemas.User import User


def extract_bearer_token(request: Request) -> str | None:
    """Return the credential of an ``Authorization: Bearer <token>`` header.

    Anything else - a missing header, another scheme, or an empty credential -
    is reported as "no token" rather than as an error, so the caller can decide
    whether the route tolerates anonymous access.
    """
    header = request.headers.get("Authorization")
    if not header:
        return None

    scheme, _, credential = header.partition(" ")
    if scheme.lower() != "bearer":
        return None

    token = credential.strip()
    return token or None


def get_optional_user(request: Request, session: SessionDep) -> User | None:
    """Return the user named by a valid token, or ``None`` when anonymous.

    Token decoding handles missing, malformed, expired, and badly signed
    values. The database lookup is still required because a technically valid
    token may reference an account that has since been removed.
    """
    payload = decode_access_token(extract_bearer_token(request))
    if not payload:
        return None

    mail = payload.get("sub")
    # Never pass an attacker-controlled non-string subject into the SQL query.
    if not isinstance(mail, str):
        return None
    return session.exec(select(User).where(User.mail == mail)).first()


def get_current_user(request: Request, session: SessionDep) -> User:
    """Return the authenticated user or reject the request with 401.

    The client treats a 401 answered while it was holding a token as an expired
    session: it clears its storage and returns the visitor to the login page.
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
