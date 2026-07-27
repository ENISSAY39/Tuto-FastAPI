from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from .authentication import get_authenticated_user


def auth_guard(request: Request, session: Session):
    """
    Returns the authenticated user if present; otherwise returns a 303 redirect response.
    """
    user = get_authenticated_user(request, session)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return user
