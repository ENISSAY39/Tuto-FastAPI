"""Integration tests for public portfolio discovery, search and pagination."""

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


def test_directory_lists_public_portfolios_without_authentication(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, ["Alpha", "Beta"])

    response = client.get("/api/portfolios")

    assert response.status_code == 200
    body = response.json()
    assert body["total_portfolios"] == 2
    assert {entry["name"] for entry in body["portfolios"]} == {"Alpha", "Beta"}


def test_directory_never_exposes_contact_details_or_credentials(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, ["Alpha"])

    response = client.get("/api/portfolios")

    entry = response.json()["portfolios"][0]
    # The listing is a name index, not a contact directory.
    assert set(entry) == {"id", "name", "first_name"}


def test_search_filters_results_by_query(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, ["Match", "Unrelated"])

    response = client.get("/api/portfolios", params={"query": "Match"})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "Match"
    assert [entry["name"] for entry in body["portfolios"]] == ["Match"]
    assert body["total_portfolios"] == 1


def test_search_without_results_still_returns_a_navigable_page(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, ["Alpha"])

    response = client.get("/api/portfolios", params={"query": "Nothing"})

    assert response.status_code == 200
    body = response.json()
    assert body["portfolios"] == []
    # One logical page keeps the pager arithmetic valid rather than reporting
    # zero pages the interface would have to special-case.
    assert body["total_pages"] == 1
    assert body["has_previous"] is False
    assert body["has_next"] is False


def test_directory_paginates_by_ten_and_reports_both_directions(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, [f"Name{index:02d}" for index in range(12)])

    first_page = client.get("/api/portfolios").json()
    assert len(first_page["portfolios"]) == 10
    assert first_page["total_pages"] == 2
    assert first_page["has_previous"] is False
    assert first_page["has_next"] is True

    second_page = client.get("/api/portfolios", params={"page": 2}).json()
    assert len(second_page["portfolios"]) == 2
    assert second_page["has_previous"] is True
    assert second_page["has_next"] is False


def test_directory_clamps_a_page_number_outside_the_results(
    client: TestClient,
    session: Session,
) -> None:
    _create_public_users(session, ["Alpha"])

    too_high = client.get("/api/portfolios", params={"page": 999}).json()
    too_low = client.get("/api/portfolios", params={"page": -3}).json()

    # The client displays the page it was answered with, so the clamp has to be
    # reported rather than silently applied.
    assert too_high["current_page"] == 1
    assert too_low["current_page"] == 1
