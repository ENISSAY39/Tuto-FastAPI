"""Integration tests for registration and cookie-based authentication routes."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import Session, select

from core.security import verify_password
from schemas.User import User


VALID_PASSWORD = "ValidPass123"
REGISTRATION_DATA = {
    "name": "  Lovelace  ",
    "first_name": "  Ada  ",
    "birth_date": "1990-01-01",
    "mail": "  Ada.Lovelace@Example.COM  ",
    "phone": "+33 (0)6 12 34 56 78",
    "password": VALID_PASSWORD,
}


def test_registration_normalizes_and_hashes_account_data(
    client: TestClient,
    session: Session,
    csrf_token: Callable[[str], str],
) -> None:
    form_data = {**REGISTRATION_DATA, "csrf_token": csrf_token("/create_user")}

    response = client.post(
        "/create_user",
        data=form_data,
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    user = session.exec(
        select(User).where(User.mail == "ada.lovelace@example.com")
    ).one()
    assert user.name == "Lovelace"
    assert verify_password(VALID_PASSWORD, user.hashed_password) is True


def test_registration_returns_validation_errors_without_creating_an_account(
    client: TestClient,
    session: Session,
    csrf_token: Callable[[str], str],
) -> None:
    form_data = {
        **REGISTRATION_DATA,
        "password": "too-short",
        "csrf_token": csrf_token("/create_user"),
    }

    response = client.post("/create_user", data=form_data)

    assert response.status_code == 400
    assert session.exec(select(User)).all() == []


def test_login_normalizes_email_and_sets_a_protected_access_cookie(
    client: TestClient,
    user_factory: Callable[..., User],
    login_user: Callable[..., Response],
) -> None:
    user_factory(mail="ada@example.com")

    response = login_user("  ADA@EXAMPLE.COM  ", VALID_PASSWORD)

    assert response.status_code == 303
    assert response.headers["location"] == "/profil"
    assert client.cookies.get("access_token") is not None

    profile_response = client.get("/profil")
    assert profile_response.status_code == 200
    assert "ada@example.com" in profile_response.text


def test_login_returns_a_generic_error_for_invalid_credentials(
    client: TestClient,
    user_factory: Callable[..., User],
    login_user: Callable[..., Response],
) -> None:
    user_factory(mail="ada@example.com")

    response = login_user("ada@example.com", "WrongPassword9")

    assert response.status_code == 401
    assert "Invalid email or password." in response.text
    assert client.cookies.get("access_token") is None


def test_logout_deletes_authentication_and_csrf_cookies(
    authenticated_client: TestClient,
    csrf_token: Callable[[str], str],
) -> None:
    token = csrf_token("/profil")

    response = authenticated_client.post(
        "/logout",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert authenticated_client.cookies.get("access_token") is None

    private_response = authenticated_client.get("/profil", follow_redirects=False)
    assert private_response.status_code == 303
    assert private_response.headers["location"] == "/login"


def test_profile_redirects_when_not_authenticated(client: TestClient) -> None:
    response = client.get("/profil", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
