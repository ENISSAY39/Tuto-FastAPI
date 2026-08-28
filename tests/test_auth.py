"""Integration tests for registration and Bearer-token authentication."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient
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


def test_login_normalizes_the_email_and_returns_a_usable_token(
    client: TestClient,
    user_factory: Callable[..., User],
    bearer: Callable[[str], dict[str, str]],
) -> None:
    user_factory(mail="ada@example.com")

    response = client.post(
        "/api/login",
        json={"mail": "  ADA@EXAMPLE.COM  ", "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["mail"] == "ada@example.com"
    assert "hashed_password" not in body["user"]

    # The token is only proven good by the protected route accepting it.
    profile_response = client.get("/api/me", headers=bearer(body["token"]))
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


def test_login_rejects_an_unknown_address_the_same_way(client: TestClient) -> None:
    response = client.post(
        "/api/login",
        json={"mail": "nobody@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid email or password."


def test_logout_acknowledges_without_needing_server_state(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post("/api/logout")

    assert response.status_code == 200
    assert response.json() == {"status": "logged out"}


def test_profile_rejects_an_anonymous_request(client: TestClient) -> None:
    response = client.get("/api/me")

    assert response.status_code == 401
    assert "error" in response.json()


def test_profile_rejects_a_token_that_is_not_a_valid_signature(
    client: TestClient,
    bearer: Callable[[str], dict[str, str]],
) -> None:
    response = client.get("/api/me", headers=bearer("not-a-real-token"))

    assert response.status_code == 401


def test_profile_rejects_a_token_whose_account_no_longer_exists(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    access_token: Callable[..., str],
    bearer: Callable[[str], dict[str, str]],
) -> None:
    user = user_factory(mail="ada@example.com")
    token = access_token(user.mail)

    session.delete(user)
    session.commit()

    # A signature that still verifies is not enough: the subject must still
    # resolve to a stored account.
    response = client.get("/api/me", headers=bearer(token))

    assert response.status_code == 401
