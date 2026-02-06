"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from fastapi import FastAPI

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"


@pytest.fixture
def app() -> FastAPI:
    """Create FastAPI app instance for testing."""
    from rootcauseai.app import app

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client for FastAPI app."""
    return TestClient(app)
