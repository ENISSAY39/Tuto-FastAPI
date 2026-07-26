"""Integration tests for public user portfolio pages."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from schemas.Education import Education
from schemas.Experiences import Experience
from schemas.User import User


def test_public_portfolio_renders_only_the_requested_users_records(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
) -> None:
    owner = user_factory(mail="owner@example.com", first_name="PortfolioOwner")
    other_user = user_factory(mail="other@example.com", first_name="OtherUser")

    session.add_all(
        [
            Experience(
                title="Owner role",
                date_start=datetime(2020, 1, 1),
                date_end=datetime(2021, 1, 1),
                description="Owner experience description",
                company="Owner Company",
                user_id=owner.id,
            ),
            Experience(
                title="Hidden role",
                date_start=datetime(2020, 1, 1),
                date_end=datetime(2021, 1, 1),
                description="Other experience description",
                company="Other Company",
                user_id=other_user.id,
            ),
            Education(
                school_name="Owner University",
                date_start=datetime(2015, 9, 1),
                date_end=datetime(2019, 6, 1),
                description="Owner education description",
                major="Computer Science",
                user_id=owner.id,
            ),
        ]
    )
    session.commit()

    response = client.get(f"/portfolio/{owner.id}")

    assert response.status_code == 200
    assert "Owner role" in response.text
    assert "Owner University" in response.text
    assert "Hidden role" not in response.text
    assert response.context["user"].id == owner.id


def test_public_portfolio_redirects_for_an_unknown_user(client: TestClient) -> None:
    response = client.get("/portfolio/999999", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
