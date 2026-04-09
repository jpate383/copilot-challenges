"""Pytest configuration and fixtures for the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "test.student@mergington.edu"
