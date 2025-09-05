import pytest
from fastapi.testclient import TestClient

from src.main import app

@pytest.fixture(scope="session")
def test_client():
    """Provides a TestClient for testing FastAPI endpoints."""
    with TestClient(app) as client:
        yield client