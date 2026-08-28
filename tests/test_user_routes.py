"""Integration tests for the public portfolio and the private dashboard."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from schemas.Education import Education
from schemas.Experiences import Experience
from schemas.User import User


def _add_portfolio_records(session: Session, owner: User, other_user: User) -> None:
    """Give both accounts records so ownership filtering has something to hide."""
    session.add_all(
        [
            Experience(
                title="Owner role",
                date_start=datetime(2020, 1, 1),
                date_end=datetime(2021, 1, 1),
                description="Owner experience description",
                company="Owner Company",
                user_id=owner.id),
            Experience(
                title="Hidden role",
                date_start=datetime(2020, 1, 1),
                date_end=datetime(2021, 1, 1),
                description="Other experience description",
                company="Other Company",
                user_id=other_user.id),
            Education(
                school_name="Owner University",
                date_start=datetime(2015, 9, 1),
                date_end=datetime(2019, 6, 1),
                description="Owner education description",
                major="Computer Science",
                user_id=owner.id),
        ]
    )
    session.commit()


def test_public_portfolio_returns_only_the_requested_users_records(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User]) -> None:
    owner = user_factory(mail="owner@example.com", first_name="PortfolioOwner")
    other_user = user_factory(mail="other@example.com", first_name="OtherUser")
    _add_portfolio_records(session, owner, other_user)

    response = client.get(f"/api/portfolios/{owner.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["id"] == owner.id
    assert [item["title"] for item in body["experiences"]] == ["Owner role"]
    assert [item["school_name"] for item in body["educations"]] == ["Owner University"]


def test_public_portfolio_serializes_periods_as_plain_calendar_dates(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User]) -> None:
    owner = user_factory(mail="owner@example.com")
    other_user = user_factory(mail="other@example.com")
    _add_portfolio_records(session, owner, other_user)

    body = client.get(f"/api/portfolios/{owner.id}").json()

    # A timestamp would be re-read in the visitor's own timezone and could
    # display a day early; the API therefore sends the calendar date itself.
    assert body["experiences"][0]["date_start"] == "2020-01-01"
    assert body["experiences"][0]["date_end"] == "2021-01-01"


def test_public_portfolio_never_exposes_the_stored_credential(
    client: TestClient,
    user_factory: Callable[..., User]) -> None:
    owner = user_factory(mail="owner@example.com")

    response = client.get(f"/api/portfolios/{owner.id}")

    assert response.status_code == 200
    assert "hashed_password" not in response.text


def test_public_portfolio_reports_an_unknown_user_as_missing(
    client: TestClient) -> None:
    response = client.get("/api/portfolios/999999")

    assert response.status_code == 404
    assert "error" in response.json()


def test_dashboard_returns_the_authenticated_accounts_own_portfolio(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict]) -> None:
    owner = user_factory(mail="owner@example.com")
    other_user = user_factory(mail="other@example.com")
    _add_portfolio_records(session, owner, other_user)

    # The dashboard takes no identifier: the session alone decides whose
    # records are returned, so one account cannot request another's.
    login_as(owner.mail)
    response = client.get("/api/me")

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["mail"] == "owner@example.com"
    assert [item["title"] for item in body["experiences"]] == ["Owner role"]


def test_dashboard_reports_the_age_computed_from_the_birth_date(
    client: TestClient,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict]) -> None:
    from datetime import date

    today = date.today()
    # A birthday that already passed this year gives an age of exactly 30
    # whichever day the suite runs on.
    owner = user_factory(
        mail="owner@example.com",
        birth_date=date(today.year - 30, 1, 1),
    )
    login_as(owner.mail)

    body = client.get("/api/me").json()

    expected_age = 30 if (today.month, today.day) >= (1, 1) else 29
    assert body["user"]["age"] == expected_age
