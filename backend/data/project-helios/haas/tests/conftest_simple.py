"""
Simplified test configuration to avoid import issues.
"""
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return Mock()


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_bacen_client():
    """Mock BACEN client."""
    return Mock()


@pytest.fixture
def mock_crawler_storage():
    """Mock crawler storage service."""
    return Mock()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "id": "proj-123",
        "name": "Test Solar Project",
        "capacity_kw": 5.0,
        "location": "São Paulo, SP",
        "status": "pending"
    }


@pytest.fixture
def sample_equipment_data():
    """Sample equipment data for testing."""
    return {
        "manufacturer": "Test Manufacturer",
        "model": "TEST-MODEL-123",
        "power_rating": 5000,
        "certification": "CERT-12345",
        "valid_until": "2026-12-31"
    }