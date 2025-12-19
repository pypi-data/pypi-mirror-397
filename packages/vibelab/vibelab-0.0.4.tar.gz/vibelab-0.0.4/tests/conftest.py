"""Pytest configuration."""

import pytest

from vibelab.db.connection import init_db


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Initialize an isolated VIBELAB_HOME + project DB for each test."""
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path / ".vibelab"))
    monkeypatch.setenv("VIBELAB_PROJECT", "test")
    init_db()
    yield
