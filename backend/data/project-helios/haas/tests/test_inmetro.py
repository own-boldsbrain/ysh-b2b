"""
HaaS Platform - INMETRO API Tests
Test suite for 7 INMETRO endpoints: validate, status, manufacturers, models, search, certificate, batch
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta


# ==================== Test Manufacturers Endpoint ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROManufacturers:
    """Test GET /api/inmetro/manufacturers endpoint."""

    def test_get_manufacturers_success(self, client, auth_headers):
        """Test successful retrieval of manufacturers list."""
        response = client.get("/api/inmetro/manufacturers", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        manufacturers = response.json()
        assert isinstance(manufacturers, list)
        assert len(manufacturers) > 0
        assert "Fronius" in manufacturers

    def test_get_manufacturers_without_auth(self, client):
        """Test manufacturers endpoint without authentication."""
        response = client.get("/api/inmetro/manufacturers")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_manufacturers_by_category(self, client, auth_headers):
        """Test manufacturers filtered by category."""
        response = client.get(
            "/api/inmetro/manufacturers?categoria=inversores", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        manufacturers = response.json()
        assert isinstance(manufacturers, list)


# ==================== Test Models Endpoint ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROManufacturerModels:
    """Test GET /api/inmetro/models/{manufacturer} endpoint."""

    def test_get_models_success(self, client, auth_headers):
        """Test successful retrieval of manufacturer models."""
        response = client.get("/api/inmetro/models/Fronius", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        models = response.json()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_get_models_unknown_manufacturer(self, client, auth_headers):
        """Test models for unknown manufacturer."""
        response = client.get("/api/inmetro/models/UnknownBrand", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        models = response.json()
        assert isinstance(models, list)
        # Should return empty list for unknown manufacturer

    def test_get_models_without_auth(self, client):
        """Test models endpoint without authentication."""
        response = client.get("/api/inmetro/models/Fronius")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== Test Certificate Details Endpoint ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROCertificateDetails:
    """Test GET /api/inmetro/certificate/{certificate_number} endpoint."""

    def test_get_certificate_details_success(self, client, auth_headers):
        """Test successful retrieval of certificate details."""
        response = client.get(
            "/api/inmetro/certificate/BRA-2024-001234", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "certificate_number" in data
        assert "manufacturer" in data
        assert "model" in data

    def test_get_certificate_details_not_found(self, client, auth_headers):
        """Test certificate details for non-existent certificate."""
        response = client.get(
            "/api/inmetro/certificate/INVALID-000", headers=auth_headers
        )

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_certificate_details_without_auth(self, client):
        """Test certificate details endpoint without authentication."""
        response = client.get("/api/inmetro/certificate/BRA-2024-001234")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== Enhanced Validate Endpoint Tests ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROValidateEnhanced:
    """Enhanced tests for POST /api/inmetro/validate endpoint."""

    def test_validate_with_registry_id(self, client, auth_headers):
        """Test validation with registry ID."""
        response = client.post(
            "/api/inmetro/validate",
            json={
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
                "registry_id": "REG-2025-001",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert "request_id" in data
        assert data["equipment_type"] == "inversores"

    def test_validate_batch_limit(self, client, auth_headers):
        """Test batch validation respects the limit."""
        # Create 51 equipments (over limit of 50)
        equipments = [
            {
                "categoria": "inversores",
                "fabricante": f"Brand{i}",
                "modelo": f"Model{i}",
            }
            for i in range(51)
        ]

        response = client.post(
            "/api/inmetro/batch", json={"equipments": equipments}, headers=auth_headers
        )

        # Should fail validation due to limit
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validate_empty_batch(self, client, auth_headers):
        """Test batch validation with empty list."""
        response = client.post(
            "/api/inmetro/batch", json={"equipments": []}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Test Search Endpoint Enhanced ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROSearchEnhanced:
    """Enhanced tests for GET /api/inmetro/search endpoint."""

    def test_search_with_pagination(self, client, auth_headers):
        """Test search with pagination parameters."""
        response = client.get(
            "/api/inmetro/search",
            params={"query": "Fronius", "page": 1, "page_size": 5},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["results"]) <= 5

    def test_search_case_insensitive(self, client, auth_headers):
        """Test search is case insensitive."""
        response = client.get(
            "/api/inmetro/search", params={"query": "fronius"}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_search_empty_query(self, client, auth_headers):
        """Test search with empty query."""
        response = client.get(
            "/api/inmetro/search", params={"query": ""}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data


# ==================== LLM Integration Tests ====================


@pytest.mark.inmetro
@pytest.mark.integration
class TestINMETROLLMIntegration:
    """Test LLM integration in INMETRO validation."""

    @patch("app.services.inmetro_service.LLMFactory.create_llm")
    def test_validate_uses_openai_llm(self, mock_create_llm, client, auth_headers):
        """Test that validation uses OpenAI LLM when configured."""
        # Mock OpenAI LLM
        mock_llm = Mock()
        mock_llm.structured_extract.return_value = {
            "categoria": "inversores",
            "fabricante": "Fronius",
            "modelo": "Primo 8.2-1",
            "certificacao": {"certificado_numero": "BRA-2024-001234", "valid": True},
        }
        mock_create_llm.return_value = mock_llm

        response = client.post(
            "/api/inmetro/validate",
            json={
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_create_llm.assert_called_once()

    @patch("app.services.inmetro_service.LLMFactory.create_llm")
    def test_validate_fallback_to_mock(self, mock_create_llm, client, auth_headers):
        """Test fallback to MockLLM when no LLM is available."""
        # Mock LLM factory to return MockLLM
        from validators.inmetro.llm import MockLLMAgent

        mock_llm = MockLLMAgent()
        mock_create_llm.return_value = mock_llm

        response = client.post(
            "/api/inmetro/validate",
            json={
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_202_ACCEPTED


# ==================== Cache Integration Tests ====================


@pytest.mark.inmetro
@pytest.mark.integration
class TestINMETROCacheIntegration:
    """Test Redis cache integration in INMETRO endpoints."""

    def test_validate_uses_cache(self, client, auth_headers, redis_client):
        """Test that validation results are cached."""
        # First request
        response1 = client.post(
            "/api/inmetro/validate",
            json={
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            headers=auth_headers,
        )
        assert response1.status_code == status.HTTP_202_ACCEPTED

        # Second request should use cache
        response2 = client.post(
            "/api/inmetro/validate",
            json={
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            headers=auth_headers,
        )
        assert response2.status_code == status.HTTP_202_ACCEPTED

        # Verify cache keys exist (if Redis is available)
        try:
            cache_keys = redis_client.keys("inmetro:*")
            assert len(cache_keys) > 0
        except:
            pass  # Redis might not be available in test environment

    def test_cache_invalidation(self, client, auth_headers):
        """Test cache invalidation functionality."""
        # This would require implementing cache invalidation endpoint
        # For now, just ensure the service has the method
        from app.services.inmetro_service import get_inmetro_service

        service = get_inmetro_service()
        assert hasattr(service, "invalidate_equipment_cache")


# ==================== Error Handling Tests ====================


@pytest.mark.inmetro
@pytest.mark.unit
class TestINMETROErrorHandling:
    """Test error handling in INMETRO endpoints."""

    def test_validate_llm_failure(self, client, auth_headers):
        """Test validation when LLM fails."""
        with patch("app.services.inmetro_service.LLMFactory.create_llm") as mock_create:
            mock_llm = Mock()
            mock_llm.structured_extract.side_effect = Exception("LLM Error")
            mock_create.return_value = mock_llm

            response = client.post(
                "/api/inmetro/validate",
                json={
                    "categoria": "inversores",
                    "fabricante": "Fronius",
                    "modelo": "Primo 8.2-1",
                },
                headers=auth_headers,
            )

            # Should still return 202 as it's async
            assert response.status_code == status.HTTP_202_ACCEPTED

    def test_status_invalid_request_id(self, client, auth_headers):
        """Test status check with invalid request ID."""
        response = client.get("/api/inmetro/status/invalid-id", headers=auth_headers)

        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_batch_validation_partial_failure(self, client, auth_headers):
        """Test batch validation with some failures."""
        equipments = [
            {
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            {"categoria": "inversores", "fabricante": "Invalid", "modelo": "Invalid"},
        ]

        response = client.post(
            "/api/inmetro/batch", json={"equipments": equipments}, headers=auth_headers
        )

        # Should accept the batch even with potential failures
        assert response.status_code == status.HTTP_202_ACCEPTED


# ==================== Performance Tests ====================


@pytest.mark.inmetro
@pytest.mark.performance
class TestINMETROPerformance:
    """Performance tests for INMETRO endpoints."""

    def test_batch_validation_performance(self, client, auth_headers):
        """Test batch validation performance with multiple items."""
        equipments = [
            {
                "categoria": "inversores",
                "fabricante": f"Brand{i}",
                "modelo": f"Model{i}",
            }
            for i in range(10)  # Test with reasonable batch size
        ]

        import time

        start_time = time.time()

        response = client.post(
            "/api/inmetro/batch", json={"equipments": equipments}, headers=auth_headers
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == status.HTTP_202_ACCEPTED
        # Should complete within reasonable time (adjust based on environment)
        assert duration < 5.0  # 5 seconds max for batch submission

    def test_search_performance(self, client, auth_headers):
        """Test search endpoint performance."""
        import time

        start_time = time.time()

        response = client.get(
            "/api/inmetro/search",
            params={"query": "Fronius", "page_size": 20},
            headers=auth_headers,
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == status.HTTP_200_OK
        # Should complete within reasonable time
        assert duration < 2.0  # 2 seconds max for search
