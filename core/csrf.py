"""Implement double-submit CSRF protection for the JSON API.

The token lives in a cookie the browser sends automatically and in a header the
client sets explicitly. A cross-site attacker can make the browser send the
cookie, but the same-origin policy stops them from *reading* it, so they cannot
produce the matching header.

The header requirement is itself a second barrier: a cross-site HTML form can
send a request, but it cannot set a custom header at all.
"""

import hmac
import secrets

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from core.config import settings


# CSRF tokens are independent from the access token and intentionally use their
# own cookie name and shorter lifetime.
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_TOKEN_BYTES = 32
CSRF_MAX_AGE_SECONDS = 60 * 60 * 2

# Methods that must not change state, and therefore need no token.
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def get_or_create_csrf_token(request: Request) -> str:
    """Reuse a plausibly formed cookie token or create a cryptographic token."""
    token = request.cookies.get(CSRF_COOKIE_NAME)
    # The size bounds reject obviously malformed input while accepting the
    # URL-safe encoding length produced by ``token_urlsafe``.
    if token and 32 <= len(token) <= 256:
        return token
    return secrets.token_urlsafe(CSRF_TOKEN_BYTES)


def set_csrf_cookie(response: Response, token: str) -> None:
    """Attach the CSRF cookie using environment-aware security flags.

    Unlike the access token, this cookie is deliberately readable by scripts:
    the client has to copy its value into the request header for the two halves
    of the double submit to be compared. It carries no authority on its own.
    """
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        max_age=CSRF_MAX_AGE_SECONDS,
        httponly=False,
        secure=settings.cookie_secure_enabled,
        # Lax blocks the cookie on cross-site state-changing requests while
        # preserving normal links into the application.
        samesite="lax",
        path="/",
    )


def validate_csrf_token(request: Request) -> None:
    """Reject a mutating request unless its header matches the CSRF cookie.

    ``compare_digest`` avoids data-dependent comparison timing. Both values are
    required: accepting an absent pair would defeat the protection entirely.
    """
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    if (
        not cookie_token
        or not header_token
        or not hmac.compare_digest(cookie_token, header_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token. Reload the page and try again.",
        )
