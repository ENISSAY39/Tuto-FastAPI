"""Integration tests for public portfolio discovery and search."""

from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from schemas.User import User


def _create_public_users(session: Session, names: list[str]) -> None:
    """Persist lightweight public accounts without doing irrelevant password work."""
    for index, name in enumerate(names):
        session.add(
            User(
                name=name,
                first_name=f"Public{index:02d}",
                birth_date=date(1990, 1, 1),
                mail=f"public{index:02d}@example.com",
                phone=f"060000{index:04d}",
                hashed_password="unused-test-password-hash",
            )
        )
    session.commit()


def test_home_lists_public_portfolios(client: TestClient, session: Session) -> None:
    _create_public_users(session, ["Alpha", "Beta"])

    response = client.get("/")

    assert response.status_code == 200
    assert response.text.count('href="/portfolio/') == 2
    assert response.context["users"] != []


def test_search_filters_results_by_query(client: TestClient, session: Session) -> None:
    _create_public_users(session, ["Match", "Unrelated"])

    response = client.get("/search", params={"query": "Match"})

    assert response.status_code == 200
    assert "Match" in response.text
    assert "Unrelated" not in response.text
    assert response.context["query"] == "Match"
