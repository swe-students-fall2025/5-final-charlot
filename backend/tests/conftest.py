"""Mocks client, db, and user"""

import pytest

from app import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create and configure new test app/client instance"""

    test_app = create_app()
    test_client = TestClient(test_app)
    yield test_client
