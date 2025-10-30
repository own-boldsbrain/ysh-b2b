"""Tests for BACEN service functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date
import httpx

from app.services.bacen_service import BacenService
from app.validators.bacen_client import BacenSGSClient


class TestBacenService:
    """Test cases for BACEN service."""

    @pytest.fixture
    def bacen_service(self):
        """Create BACEN service instance."""
        return BacenService()

    @pytest.fixture
    def mock_bacen_client(self):
        """Mock BACEN SGS client."""
        return Mock(spec=BacenSGSClient)

    def test_bacen_service_initialization(self, bacen_service):
        """Test BACEN service initialization."""
        assert bacen_service is not None
        assert hasattr(bacen_service, 'client')

    @pytest.mark.asyncio
    async def test_get_selic_rate_success(self, bacen_service):
        """Test successful SELIC rate retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.return_value = {
                "rate": 12.75,
                "date": "2025-10-23",
                "series_code": "432"
            }
            
            result = await bacen_service.get_selic_rate()
            
            assert result["rate"] == 12.75
            assert result["date"] == "2025-10-23"
            mock_client.get_current_selic.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_selic_rate_failure(self, bacen_service):
        """Test SELIC rate retrieval failure."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.side_effect = Exception("API error")
            
            result = await bacen_service.get_selic_rate()
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_cdi_rate_success(self, bacen_service):
        """Test successful CDI rate retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_cdi.return_value = {
                "rate": 12.50,
                "date": "2025-10-23",
                "series_code": "12"
            }
            
            result = await bacen_service.get_cdi_rate()
            
            assert result["rate"] == 12.50
            mock_client.get_current_cdi.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inflation_data_success(self, bacen_service):
        """Test successful inflation data retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_series_data.return_value = [
                {"date": "2025-09-01", "value": 0.46},
                {"date": "2025-10-01", "value": 0.38}
            ]
            
            result = await bacen_service.get_inflation_data()
            
            assert "ipca_monthly" in result
            assert len(result["ipca_monthly"]) == 2
            assert result["ipca_monthly"][0]["value"] == 0.46

    @pytest.mark.asyncio
    async def test_get_exchange_rate_success(self, bacen_service):
        """Test successful exchange rate retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_exchange_rate.return_value = {
                "rate": 5.25,
                "currency": "USD/BRL",
                "date": "2025-10-23"
            }
            
            result = await bacen_service.get_exchange_rate("USD")
            
            assert result["rate"] == 5.25
            assert result["currency"] == "USD/BRL"

    @pytest.mark.asyncio
    async def test_get_historical_selic_success(self, bacen_service):
        """Test successful historical SELIC data retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_series_data.return_value = [
                {"date": "2025-01-01", "value": 11.75},
                {"date": "2025-02-01", "value": 12.00},
                {"date": "2025-03-01", "value": 12.25}
            ]
            
            start_date = date(2025, 1, 1)
            end_date = date(2025, 3, 31)
            
            result = await bacen_service.get_historical_selic(start_date, end_date)
            
            assert len(result) == 3
            assert result[0]["value"] == 11.75

    @pytest.mark.asyncio
    async def test_get_gdp_data_success(self, bacen_service):
        """Test successful GDP data retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_series_data.return_value = [
                {"date": "2024-Q4", "value": 2.1},
                {"date": "2025-Q1", "value": 1.8}
            ]
            
            result = await bacen_service.get_gdp_data()
            
            assert "quarterly_growth" in result
            assert len(result["quarterly_growth"]) == 2

    @pytest.mark.asyncio
    async def test_get_employment_data_success(self, bacen_service):
        """Test successful employment data retrieval."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_series_data.return_value = [
                {"date": "2025-08-01", "value": 7.8},
                {"date": "2025-09-01", "value": 7.6}
            ]
            
            result = await bacen_service.get_employment_data()
            
            assert "unemployment_rate" in result
            assert result["unemployment_rate"][1]["value"] == 7.6

    @pytest.mark.asyncio
    async def test_cache_integration(self, bacen_service):
        """Test Redis cache integration."""
        with patch('app.services.bacen_service.redis_client') as mock_redis:
            mock_redis.get.return_value = None  # No cached data
            mock_redis.set.return_value = True   # Cache set successful
            
            with patch.object(bacen_service, 'client') as mock_client:
                mock_client.get_current_selic.return_value = {"rate": 12.75}
                
                result = await bacen_service.get_selic_rate()
                
                # Verify cache was checked and set
                mock_redis.get.assert_called()
                mock_redis.set.assert_called()

    @pytest.mark.asyncio
    async def test_cache_hit(self, bacen_service):
        """Test cache hit scenario."""
        cached_data = '{"rate": 12.75, "date": "2025-10-23", "cached": true}'
        
        with patch('app.services.bacen_service.redis_client') as mock_redis:
            mock_redis.get.return_value = cached_data
            
            result = await bacen_service.get_selic_rate()
            
            assert result["cached"] is True
            assert result["rate"] == 12.75

    @pytest.mark.asyncio
    async def test_rate_limiting(self, bacen_service):
        """Test rate limiting enforcement."""
        with patch('app.services.bacen_service.rate_limiter') as mock_limiter:
            mock_limiter.is_allowed.return_value = False
            
            result = await bacen_service.get_selic_rate()
            
            assert result["success"] is False
            assert "rate limit" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_timeout_handling(self, bacen_service):
        """Test timeout handling for API calls."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await bacen_service.get_selic_rate()
            
            assert result["success"] is False
            assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_network_error_handling(self, bacen_service):
        """Test network error handling."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.side_effect = httpx.NetworkError("Network error")
            
            result = await bacen_service.get_selic_rate()
            
            assert result["success"] is False
            assert "network" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_data_validation(self, bacen_service):
        """Test data validation and sanitization."""
        invalid_data = {
            "rate": "invalid_number",
            "date": "invalid_date"
        }
        
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.return_value = invalid_data
            
            result = await bacen_service.get_selic_rate()
            
            # Should handle invalid data gracefully
            assert result["success"] is False or "validation_error" in result

    @pytest.mark.asyncio
    async def test_batch_data_retrieval(self, bacen_service):
        """Test batch data retrieval."""
        series_codes = ["432", "12", "433"]  # SELIC, CDI, IPCA
        
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_series_data.side_effect = [
                [{"date": "2025-10-23", "value": 12.75}],  # SELIC
                [{"date": "2025-10-23", "value": 12.50}],  # CDI
                [{"date": "2025-10-01", "value": 0.38}]    # IPCA
            ]
            
            result = await bacen_service.get_batch_data(series_codes)
            
            assert len(result) == 3
            assert all("series_code" in item for item in result)

    @pytest.mark.asyncio
    async def test_economic_indicators_summary(self, bacen_service):
        """Test economic indicators summary."""
        with patch.multiple(
            bacen_service,
            get_selic_rate=AsyncMock(return_value={"rate": 12.75}),
            get_cdi_rate=AsyncMock(return_value={"rate": 12.50}),
            get_inflation_data=AsyncMock(return_value={"ipca_monthly": [{"value": 0.38}]}),
            get_exchange_rate=AsyncMock(return_value={"rate": 5.25})
        ):
            
            result = await bacen_service.get_economic_summary()
            
            assert "selic" in result
            assert "cdi" in result
            assert "inflation" in result
            assert "exchange_rate" in result

    def test_series_code_mapping(self, bacen_service):
        """Test series code mapping functionality."""
        selic_code = bacen_service.get_series_code("selic")
        cdi_code = bacen_service.get_series_code("cdi")
        ipca_code = bacen_service.get_series_code("ipca")
        
        assert selic_code == "432"
        assert cdi_code == "12"
        assert ipca_code == "433"

    @pytest.mark.asyncio
    async def test_date_range_validation(self, bacen_service):
        """Test date range validation."""
        start_date = date(2025, 12, 31)  # Future start date
        end_date = date(2025, 1, 1)      # End before start
        
        with pytest.raises(ValueError):
            await bacen_service.get_historical_selic(start_date, end_date)

    @pytest.mark.asyncio
    async def test_metrics_collection(self, bacen_service):
        """Test metrics collection for monitoring."""
        with patch('app.services.bacen_service.metrics_collector') as mock_metrics:
            with patch.object(bacen_service, 'client') as mock_client:
                mock_client.get_current_selic.return_value = {"rate": 12.75}
                
                await bacen_service.get_selic_rate()
                
                # Verify metrics were recorded
                mock_metrics.increment.assert_called()
                mock_metrics.record_duration.assert_called()

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, bacen_service):
        """Test handling of concurrent requests."""
        import asyncio
        
        async def make_request():
            return await bacen_service.get_selic_rate()
        
        # Simulate concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete successfully
        for result in results:
            assert not isinstance(result, Exception)

    def test_configuration_validation(self, bacen_service):
        """Test service configuration validation."""
        config = bacen_service.get_configuration()
        
        assert "base_url" in config
        assert "timeout" in config
        assert "retry_config" in config

    @pytest.mark.asyncio
    async def test_health_check(self, bacen_service):
        """Test service health check."""
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.health_check.return_value = {"status": "healthy"}
            
            health_status = await bacen_service.health_check()
            
            assert health_status["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_response_parsing(self, bacen_service):
        """Test API response parsing and error handling."""
        malformed_response = {"unexpected_field": "value"}
        
        with patch.object(bacen_service, 'client') as mock_client:
            mock_client.get_current_selic.return_value = malformed_response
            
            result = await bacen_service.get_selic_rate()
            
            # Should handle malformed response gracefully
            assert "error" in result or result["success"] is False