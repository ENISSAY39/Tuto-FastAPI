"""Integration tests for registration, the session cookies, and CSRF."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from core.authentication import ACCESS_COOKIE_NAME, SESSION_HINT_COOKIE_NAME
from core.csrf import CSRF_HEADER_NAME
from core.security import verify_password
from schemas.User import User


def set_cookie_attributes(response, name: str) -> str:
    """Return the raw Set-Cookie line for one cookie, flags included.

    The parsed cookie jar drops the attributes, and the attributes are exactly
    what these tests are about.
    """
    for header in response.headers.get_list("set-cookie"):
        if header.startswith(f"{name}="):
            return header
    raise AssertionError(f"{name} was not set by this response")


VALID_PASSWORD = "ValidPass123"
REGISTRATION_DATA = {
    "name": "  Lovelace  ",
    "first_name": "  Ada  ",
    "birth_date": "1990-01-01",
    "mail": "  Ada.Lovelace@Example.COM  ",
    "phone": "+33 (0)6 12 34 56 78",
    "password": VALID_PASSWORD,
}


def test_signup_normalizes_and_hashes_account_data(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post("/api/signup", json=REGISTRATION_DATA)

    assert response.status_code == 201
    body = response.json()
    assert body["mail"] == "ada.lovelace@example.com"
    assert body["name"] == "Lovelace"
    # No response model exposes the stored credential, in any shape.
    assert "hashed_password" not in body
    assert "password" not in body

    user = session.exec(
        select(User).where(User.mail == "ada.lovelace@example.com")
    ).one()
    assert user.name == "Lovelace"
    assert verify_password(VALID_PASSWORD, user.hashed_password) is True


def test_signup_reports_validation_errors_without_creating_an_account(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post(
        "/api/signup",
        json={**REGISTRATION_DATA, "password": "too-short"},
    )

    assert response.status_code == 400
    # The message is the one core.validation raised, so the interface can show
    # it to the visitor unchanged.
    assert "at least 10 characters" in response.json()["error"]
    assert session.exec(select(User)).all() == []


def test_signup_rejects_an_email_that_is_already_registered(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
) -> None:
    user_factory(mail="ada.lovelace@example.com")

    response = client.post("/api/signup", json=REGISTRATION_DATA)

    assert response.status_code == 409
    assert len(session.exec(select(User)).all()) == 1


def test_login_opens_a_session_the_page_cannot_read(
    client: TestClient,
    user_factory: Callable[..., User],
) -> None:
    user_factory(mail="ada@example.com")

    response = client.post(
        "/api/login",
        json={"mail": "  ADA@EXAMPLE.COM  ", "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mail"] == "ada@example.com"
    # The credential must not travel through the response body either, or it
    # would land in whatever the client decides to store.
    assert "token" not in body
    assert "hashed_password" not in body

    # This is the whole point of the change: a script on the page cannot read
    # the credential, so injected code cannot carry it away.
    assert "HttpOnly" in set_cookie_attributes(response, ACCESS_COOKIE_NAME)
    # Its companion says only that a session exists, and is readable on purpose.
    assert "HttpOnly" not in set_cookie_attributes(response, SESSION_HINT_COOKIE_NAME)

    # The session is only proven good by the protected route accepting it.
    profile_response = client.get("/api/me")
    assert profile_response.status_code == 200
    assert profile_response.json()["user"]["mail"] == "ada@example.com"


def test_login_returns_a_generic_error_for_invalid_credentials(
    client: TestClient,
    user_factory: Callable[..., User],
) -> None:
    user_factory(mail="ada@example.com")

    response = client.post(
        "/api/login",
        json={"mail": "ada@example.com", "password": "WrongPassword9"},
    )

    assert response.status_code == 401
    # The same wording answers an unknown address, so nothing here reveals
    # which accounts exist.
    assert response.json()["error"] == "Invalid email or password."
    assert client.cookies.get(ACCESS_COOKIE_NAME) is None


def test_login_rejects_an_unknown_address_the_same_way(client: TestClient) -> None:
    response = client.post(
        "/api/login",
        json={"mail": "nobody@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid email or password."


def test_logout_ends_the_session_server_side(
    authenticated_client: TestClient,
) -> None:
    assert authenticated_client.get("/api/me").status_code == 200

    response = authenticated_client.post("/api/logout")

    assert response.status_code == 200
    # Only the server can end this session, because only it can clear an
    # HTTP-only cookie — so the protected route must refuse straight after.
    assert authenticated_client.get("/api/me").status_code == 401


def test_profile_rejects_an_anonymous_request(client: TestClient) -> None:
    response = client.get("/api/me")

    assert response.status_code == 401
    assert "error" in response.json()


def test_profile_rejects_a_cookie_that_is_not_a_valid_signature(
    client: TestClient,
) -> None:
    client.cookies.set(ACCESS_COOKIE_NAME, "not-a-real-token")

    response = client.get("/api/me")

    assert response.status_code == 401


def test_profile_rejects_a_session_whose_account_no_longer_exists(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
) -> None:
    user = user_factory(mail="ada@example.com")
    login_as(user.mail)

    session.delete(user)
    session.commit()

    # A signature that still verifies is not enough: the subject must still
    # resolve to a stored account.
    response = client.get("/api/me")

    assert response.status_code == 401


def test_a_mutation_without_the_csrf_header_is_refused(
    authenticated_client: TestClient,
) -> None:
    # A cross-site caller can make the browser send the cookies, but it can
    # neither read the CSRF cookie nor set a custom header, so this is the
    # request such an attack would actually produce.
    del authenticated_client.headers[CSRF_HEADER_NAME]

    response = authenticated_client.post(
        "/api/experiences",
        json={
            "title": "Injected",
            "company": "Attacker",
            "description": "Should never be stored.",
            "date_start": "2020-01-01",
            "date_end": "2020-06-30",
        },
    )

    assert response.status_code == 403
    assert "CSRF" in response.json()["error"]


def test_a_mutation_with_a_mismatched_csrf_header_is_refused(
    authenticated_client: TestClient,
) -> None:
    authenticated_client.headers[CSRF_HEADER_NAME] = "a-token-from-somewhere-else"

    response = authenticated_client.delete("/api/experiences/1")

    assert response.status_code == 403


def test_reading_needs_no_csrf_token(authenticated_client: TestClient) -> None:
    del authenticated_client.headers[CSRF_HEADER_NAME]

    # Safe methods change nothing, so requiring a token there would only break
    # ordinary navigation.
    assert authenticated_client.get("/api/me").status_code == 200
