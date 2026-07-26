"""Integration tests for authenticated, user-owned portfolio records."""

from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from core.security import create_access_token
from schemas.Education import Education
from schemas.Experiences import Experience
from schemas.User import User


PortfolioModel = type[Experience] | type[Education]


RESOURCE_CASES = [
    pytest.param(
        Experience,
        "experience",
        {
            "title": "  Backend developer  ",
            "date_start": "2024-01-01",
            "date_end": "2024-06-30",
            "description": "  Built a FastAPI service.  ",
            "company": "  Example Corp  ",
        },
        {
            "title": "Senior backend developer",
            "date_start": "2024-07-01",
            "date_end": "2025-06-30",
            "description": "Led the API team.",
            "company": "New Example Corp",
        },
        "title",
        "Backend developer",
        "Senior backend developer",
        id="experience",
    ),
    pytest.param(
        Education,
        "education",
        {
            "school_name": "  EPF Engineering School  ",
            "date_start": "2022-09-01",
            "date_end": "2025-06-30",
            "description": "  Computer science curriculum.  ",
            "major": "  Software engineering  ",
        },
        {
            "school_name": "EPF Graduate School",
            "date_start": "2022-09-01",
            "date_end": "2026-06-30",
            "description": "Extended computer science curriculum.",
            "major": "Cloud engineering",
        },
        "school_name",
        "EPF Engineering School",
        "EPF Graduate School",
        id="education",
    ),
]


def authenticate(client: TestClient, mail: str) -> None:
    """Authenticate the test browser as the user identified by ``mail``."""
    client.cookies.set("access_token", create_access_token({"sub": mail}))


@pytest.mark.parametrize("resource", ["experience", "education"])
def test_owned_crud_pages_redirect_anonymous_users(
    client: TestClient,
    resource: str,
) -> None:
    response = client.get(f"/profil/{resource}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


@pytest.mark.parametrize(
    (
        "model",
        "resource",
        "create_data",
        "update_data",
        "display_attribute",
        "created_display_value",
        "updated_display_value",
    ),
    RESOURCE_CASES,
)
def test_owner_can_create_update_and_delete_a_portfolio_record(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    csrf_token: Callable[[str], str],
    model: PortfolioModel,
    resource: str,
    create_data: dict[str, str],
    update_data: dict[str, str],
    display_attribute: str,
    created_display_value: str,
    updated_display_value: str,
) -> None:
    owner = user_factory(mail=f"owner-{resource}@example.com")
    authenticate(client, owner.mail)
    token = csrf_token(path=f"/profil/{resource}")

    create_response = client.post(
        f"/profil/{resource}",
        data={"csrf_token": token, **create_data},
        follow_redirects=False,
    )

    assert create_response.status_code == 303
    assert create_response.headers["location"] == "/profil"
    records = session.exec(select(model)).all()
    assert len(records) == 1
    record = records[0]
    assert record.user_id == owner.id
    assert getattr(record, display_attribute) == created_display_value

    update_response = client.post(
        f"/profil/{resource}/edit/{record.id}",
        data={"csrf_token": token, **update_data},
        follow_redirects=False,
    )

    assert update_response.status_code == 303
    session.refresh(record)
    assert getattr(record, display_attribute) == updated_display_value

    record_id = record.id
    delete_response = client.post(
        f"/profil/{resource}/delete/{record_id}",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert delete_response.status_code == 303
    session.expire_all()
    assert session.get(model, record_id) is None


@pytest.mark.parametrize(
    (
        "model",
        "resource",
        "form_data",
        "display_attribute",
        "original_display_value",
        "record_fields",
    ),
    [
        pytest.param(
            Experience,
            "experience",
            {
                "title": "Stolen experience",
                "date_start": "2025-01-01",
                "date_end": "2025-12-31",
                "description": "Must not be persisted",
                "company": "Attacker Corp",
            },
            "title",
            "Owner experience",
            {
                "title": "Owner experience",
                "date_start": datetime(2024, 1, 1),
                "date_end": datetime(2024, 12, 31),
                "description": "Private owner record",
                "company": "Owner Corp",
            },
            id="experience",
        ),
        pytest.param(
            Education,
            "education",
            {
                "school_name": "Stolen education",
                "date_start": "2025-01-01",
                "date_end": "2025-12-31",
                "description": "Must not be persisted",
                "major": "Attacker major",
            },
            "school_name",
            "Owner school",
            {
                "school_name": "Owner school",
                "date_start": datetime(2021, 9, 1),
                "date_end": datetime(2024, 6, 30),
                "description": "Private owner record",
                "major": "Owner major",
            },
            id="education",
        ),
    ],
)
def test_another_user_cannot_view_update_or_delete_owned_records(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    csrf_token: Callable[[str], str],
    model: PortfolioModel,
    resource: str,
    form_data: dict[str, str],
    display_attribute: str,
    original_display_value: str,
    record_fields: dict[str, Any],
) -> None:
    owner = user_factory(mail=f"record-owner-{resource}@example.com")
    attacker = user_factory(mail=f"attacker-{resource}@example.com")
    record = model(**record_fields, user_id=owner.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    record_id = record.id

    authenticate(client, attacker.mail)
    token = csrf_token(path=f"/profil/{resource}")

    update_response = client.post(
        f"/profil/{resource}/edit/{record_id}",
        data={"csrf_token": token, **form_data},
        follow_redirects=False,
    )
    assert update_response.status_code == 303
    assert update_response.headers["location"] == "/profil"
    session.refresh(record)
    assert getattr(record, display_attribute) == original_display_value

    delete_response = client.post(
        f"/profil/{resource}/delete/{record_id}",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert delete_response.status_code == 303
    session.expire_all()
    assert session.get(model, record_id) is not None
