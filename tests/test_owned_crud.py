"""Integration tests for the experience and education CRUD routes.

Both resources enforce the same ownership contract, so every case below is
parametrized over the two rather than written twice: a rule that stops holding
for one of them fails here immediately.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from schemas.Education import Education
from schemas.Experiences import Experience
from schemas.User import User


EXPERIENCE_RESOURCE = pytest.param(
    "/api/experiences",
    Experience,
    "title",
    {
        "title": "Backend intern",
        "company": "Acme",
        "description": "Built the reporting endpoints.",
        "date_start": "2020-01-01",
        "date_end": "2020-06-30",
    },
    {
        "title": "Backend engineer",
        "company": "Acme",
        "description": "Owned the reporting service.",
        "date_start": "2020-07-01",
        "date_end": "2022-01-31",
    },
    {
        "title": "Stored role",
        "company": "Stored Company",
        "description": "Stored description",
        "date_start": datetime(2019, 1, 1),
        "date_end": datetime(2019, 12, 31),
    },
    id="experiences")

EDUCATION_RESOURCE = pytest.param(
    "/api/educations",
    Education,
    "school_name",
    {
        "school_name": "EPF",
        "major": "Computer Science",
        "description": "Engineering degree.",
        "date_start": "2015-09-01",
        "date_end": "2019-06-30",
    },
    {
        "school_name": "EPF Sceaux",
        "major": "Software Engineering",
        "description": "Engineering degree, software major.",
        "date_start": "2015-09-01",
        "date_end": "2020-06-30",
    },
    {
        "school_name": "Stored University",
        "major": "Stored Major",
        "description": "Stored description",
        "date_start": datetime(2014, 9, 1),
        "date_end": datetime(2018, 6, 30),
    },
    id="educations")

RESOURCES = (EXPERIENCE_RESOURCE, EDUCATION_RESOURCE)

# Signature shared by every parametrized case below.
RESOURCE_ARGS = "endpoint, model, display_attribute, create_payload, update_payload, stored_fields"


def _store_record(
    session: Session,
    model: type[SQLModel],
    stored_fields: dict[str, Any],
    owner: User) -> SQLModel:
    """Persist one record directly, bypassing the routes under test."""
    record = model(**stored_fields, user_id=owner.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_every_route_rejects_an_anonymous_request(
    client: TestClient,
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    responses = {
        "list": client.get(endpoint),
        "create": client.post(endpoint, json=create_payload),
        "update": client.put(f"{endpoint}/1", json=update_payload),
        "delete": client.delete(f"{endpoint}/1"),
    }

    assert {name: response.status_code for name, response in responses.items()} == {
        "list": 401,
        "create": 401,
        "update": 401,
        "delete": 401,
    }


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_owner_can_create_list_update_and_delete_a_record(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    login_as(owner.mail)

    created = client.post(endpoint, json=create_payload)
    assert created.status_code == 201
    record_id = created.json()["id"]
    assert created.json()[display_attribute] == create_payload[display_attribute]

    listed = client.get(endpoint)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [record_id]

    updated = client.put(f"{endpoint}/{record_id}", json=update_payload)
    assert updated.status_code == 200
    assert updated.json()[display_attribute] == update_payload[display_attribute]

    # The stored row, not just the response, must carry the new value.
    session.expire_all()
    assert getattr(session.get(model, record_id), display_attribute) == (
        update_payload[display_attribute]
    )

    deleted = client.delete(f"{endpoint}/{record_id}")
    assert deleted.status_code == 204

    session.expire_all()
    assert session.get(model, record_id) is None


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_creation_owns_the_record_regardless_of_a_submitted_user_id(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    victim = user_factory(mail="victim@example.com")
    login_as(owner.mail)

    # Ownership comes from the verified token; a user_id in the body is not
    # part of the request model and cannot redirect the record to someone else.
    created = client.post(
        endpoint,
        json={**create_payload, "user_id": victim.id})

    assert created.status_code == 201
    stored = session.get(model, created.json()["id"])
    assert stored.user_id == owner.id


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_another_user_cannot_update_or_delete_an_owned_record(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    intruder = user_factory(mail="intruder@example.com")
    record = _store_record(session, model, stored_fields, owner)
    original_value = getattr(record, display_attribute)

    login_as(intruder.mail)

    updated = client.put(f"{endpoint}/{record.id}", json=update_payload)
    deleted = client.delete(f"{endpoint}/{record.id}")

    # A foreign record answers exactly like a missing one, so its existence is
    # never revealed.
    assert updated.status_code == 404
    assert deleted.status_code == 404

    session.expire_all()
    surviving = session.get(model, record.id)
    assert surviving is not None
    assert getattr(surviving, display_attribute) == original_value


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_listing_excludes_records_owned_by_someone_else(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    other_user = user_factory(mail="other@example.com")
    _store_record(session, model, stored_fields, other_user)

    login_as(owner.mail)
    listed = client.get(endpoint)

    assert listed.status_code == 200
    assert listed.json() == []


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_a_reversed_period_is_refused_without_storing_anything(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    login_as(owner.mail)

    response = client.post(
        endpoint,
        json={**create_payload, "date_start": "2021-01-01", "date_end": "2020-01-01"})

    assert response.status_code == 400
    assert "End date" in response.json()["error"]
    assert client.get(endpoint).json() == []


@pytest.mark.parametrize(RESOURCE_ARGS, RESOURCES)
def test_editing_applies_the_same_rules_as_creation(
    client: TestClient,
    session: Session,
    user_factory: Callable[..., User],
    login_as: Callable[..., dict],
    endpoint: str,
    model: type[SQLModel],
    display_attribute: str,
    create_payload: dict[str, str],
    update_payload: dict[str, str],
    stored_fields: dict[str, Any]) -> None:
    owner = user_factory(mail="owner@example.com")
    record = _store_record(session, model, stored_fields, owner)
    original_value = getattr(record, display_attribute)

    login_as(owner.mail)

    # An edit must not be able to persist a value creation would have refused.
    response = client.put(
        f"{endpoint}/{record.id}",
        json={**update_payload, display_attribute: "   "})

    assert response.status_code == 400

    session.expire_all()
    assert getattr(session.get(model, record.id), display_attribute) == original_value
