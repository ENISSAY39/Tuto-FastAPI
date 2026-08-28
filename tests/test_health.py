"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check_reports_application_and_database(client: TestClient) -> None:
    """The endpoint answers 200 and confirms the database responded too."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
