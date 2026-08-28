"""Tests for application startup orchestration without persistent I/O."""

import asyncio

import pytest

import main as main_module


def test_lifespan_creates_the_schema_before_the_enabled_demo_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_calls: list[str] = []

    monkeypatch.setattr(main_module.settings, "seed_demo_data", True)
    monkeypatch.setattr(
        main_module,
        "create_db_and_tables",
        lambda: startup_calls.append("schema"),
    )
    monkeypatch.setattr(
        main_module,
        "seed",
        lambda: startup_calls.append("seed"),
    )

    async def run_lifespan() -> None:
        # Seeding must never run against tables that do not exist yet, so the
        # order matters as much as the fact that both steps ran.
        async with main_module.lifespan(main_module.app):
            assert startup_calls == ["schema", "seed"]

    asyncio.run(run_lifespan())

    assert startup_calls == ["schema", "seed"]


def test_lifespan_skips_the_seed_when_demo_data_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_calls: list[str] = []

    monkeypatch.setattr(main_module.settings, "seed_demo_data", False)
    monkeypatch.setattr(
        main_module,
        "create_db_and_tables",
        lambda: startup_calls.append("schema"),
    )
    monkeypatch.setattr(
        main_module,
        "seed",
        lambda: startup_calls.append("seed"),
    )

    async def run_lifespan() -> None:
        async with main_module.lifespan(main_module.app):
            pass

    asyncio.run(run_lifespan())

    assert startup_calls == ["schema"]
