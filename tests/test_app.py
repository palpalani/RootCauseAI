"""Tests for the FastAPI application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RootCauseAI" in response.text


def test_health_endpoint(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "openai_api_key_configured" in data


def test_analyze_endpoint_no_file(client: TestClient) -> None:
    """Test analyze endpoint without file."""
    response = client.post("/analyze")
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_file_type(client: TestClient) -> None:
    """Test analyze endpoint with invalid file type."""
    files = {"file": ("test.log", b"test content", "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Only .txt log files are supported" in data["error"]


def test_analyze_endpoint_empty_file(client: TestClient) -> None:
    """Test analyze endpoint with empty file."""
    files = {"file": ("test.txt", b"", "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Log file is empty" in data["error"]
