"""Tests for data provider service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import httpx

from app.services.data_provider_service import DataProviderService


class TestDataProviderService:
    """Test cases for DataProviderService."""

    @pytest.fixture
    def data_provider_service(self):
        """Create data provider service instance."""
        return DataProviderService()

    @pytest.fixture
    def mock_bacen_service(self):
        """Mock BACEN service."""
        return Mock()

    @pytest.fixture
    def mock_aneel_service(self):
        """Mock ANEEL service."""
        return Mock()

    def test_service_initialization(self, data_provider_service):
        """Test service initialization."""
        assert data_provider_service is not None
        assert hasattr(data_provider_service, 'bacen_service')
        assert hasattr(data_provider_service, 'aneel_service')

    @pytest.mark.asyncio
    async def test_get_economic_data_success(self, data_provider_service):
        """Test successful economic data retrieval."""
        with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
            mock_bacen.get_selic_rate.return_value = {"rate": 12.5, "date": "2025-10-23"}
            mock_bacen.get_inflation_data.return_value = {"ipca": 4.2, "period": "12m"}
            
            result = await data_provider_service.get_economic_data()
            
            assert "selic_rate" in result
            assert "inflation_data" in result
            assert result["selic_rate"]["rate"] == 12.5

    @pytest.mark.asyncio
    async def test_get_economic_data_failure(self, data_provider_service):
        """Test economic data retrieval failure."""
        with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
            mock_bacen.get_selic_rate.side_effect = Exception("BACEN API error")
            
            result = await data_provider_service.get_economic_data()
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_tariff_data_success(self, data_provider_service):
        """Test successful tariff data retrieval."""
        with patch.object(data_provider_service, 'aneel_service') as mock_aneel:
            mock_aneel.get_tariff_data.return_value = {
                "distributor": "ENEL SP",
                "tariff_class": "B1",
                "rate": 0.65,
                "currency": "BRL/kWh"
            }
            
            result = await data_provider_service.get_tariff_data("ENEL SP", "B1")
            
            assert result["distributor"] == "ENEL SP"
            assert result["rate"] == 0.65

    @pytest.mark.asyncio
    async def test_get_distributor_info_success(self, data_provider_service):
        """Test successful distributor info retrieval."""
        with patch.object(data_provider_service, 'aneel_service') as mock_aneel:
            mock_aneel.get_distributor_info.return_value = {
                "name": "ENEL São Paulo",
                "code": "ENEL_SP",
                "region": "Southeast",
                "coverage_area": ["São Paulo Capital", "Grande ABC"]
            }
            
            result = await data_provider_service.get_distributor_info("ENEL_SP")
            
            assert result["name"] == "ENEL São Paulo"
            assert "coverage_area" in result

    @pytest.mark.asyncio
    async def test_get_market_analysis_success(self, data_provider_service):
        """Test successful market analysis retrieval."""
        mock_data = {
            "total_capacity_mw": 15000,
            "growth_rate": 0.25,
            "regional_distribution": {
                "Southeast": 45,
                "South": 25,
                "Northeast": 20,
                "Others": 10
            }
        }
        
        with patch.object(data_provider_service, 'aneel_service') as mock_aneel:
            mock_aneel.get_market_analysis.return_value = mock_data
            
            result = await data_provider_service.get_market_analysis("solar", "2025")
            
            assert result["total_capacity_mw"] == 15000
            assert result["growth_rate"] == 0.25

    @pytest.mark.asyncio
    async def test_get_regulatory_updates_success(self, data_provider_service):
        """Test successful regulatory updates retrieval."""
        mock_updates = [
            {
                "id": "REG-001",
                "title": "New Solar Energy Regulations",
                "date": "2025-10-01",
                "summary": "Updated technical requirements for solar installations"
            },
            {
                "id": "REG-002", 
                "title": "Grid Connection Standards",
                "date": "2025-09-15",
                "summary": "New standards for distributed generation"
            }
        ]
        
        with patch.object(data_provider_service, 'aneel_service') as mock_aneel:
            mock_aneel.get_regulatory_updates.return_value = mock_updates
            
            result = await data_provider_service.get_regulatory_updates()
            
            assert len(result) == 2
            assert result[0]["id"] == "REG-001"

    @pytest.mark.asyncio
    async def test_get_project_statistics_success(self, data_provider_service):
        """Test successful project statistics retrieval."""
        mock_stats = {
            "total_projects": 1500,
            "approved_projects": 1200,
            "pending_projects": 250,
            "rejected_projects": 50,
            "average_approval_time": 45,  # days
            "by_state": {
                "SP": 500,
                "RJ": 300,
                "MG": 250
            }
        }
        
        with patch.object(data_provider_service, 'aneel_service') as mock_aneel:
            mock_aneel.get_project_statistics.return_value = mock_stats
            
            result = await data_provider_service.get_project_statistics("2025", "Q3")
            
            assert result["total_projects"] == 1500
            assert result["average_approval_time"] == 45

    @pytest.mark.asyncio
    async def test_search_equipment_success(self, data_provider_service):
        """Test successful equipment search."""
        mock_equipment = [
            {
                "manufacturer": "Solar Manufacturer A",
                "model": "SM-300W",
                "power_rating": 300,
                "certification": "INMETRO-12345",
                "price_range": "R$ 800-1000"
            },
            {
                "manufacturer": "Solar Manufacturer B", 
                "model": "SB-320W",
                "power_rating": 320,
                "certification": "INMETRO-67890",
                "price_range": "R$ 900-1100"
            }
        ]
        
        with patch.object(data_provider_service, 'inmetro_service') as mock_inmetro:
            mock_inmetro.search_equipment.return_value = mock_equipment
            
            result = await data_provider_service.search_equipment("solar", min_power=250)
            
            assert len(result) == 2
            assert result[0]["manufacturer"] == "Solar Manufacturer A"

    @pytest.mark.asyncio
    async def test_get_real_time_data_success(self, data_provider_service):
        """Test successful real-time data retrieval."""
        mock_real_time = {
            "grid_frequency": 60.0,
            "system_demand": 45000,  # MW
            "renewable_generation": 15000,  # MW
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with patch.object(data_provider_service, 'ons_service') as mock_ons:
            mock_ons.get_real_time_data.return_value = mock_real_time
            
            result = await data_provider_service.get_real_time_grid_data()
            
            assert result["grid_frequency"] == 60.0
            assert result["system_demand"] == 45000

    @pytest.mark.asyncio
    async def test_get_weather_data_success(self, data_provider_service):
        """Test successful weather data retrieval."""
        mock_weather = {
            "location": "São Paulo",
            "solar_irradiance": 850,  # W/m²
            "temperature": 25.5,  # °C
            "humidity": 65,  # %
            "wind_speed": 3.2,  # m/s
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with patch.object(data_provider_service, 'weather_service') as mock_weather_svc:
            mock_weather_svc.get_current_weather.return_value = mock_weather
            
            result = await data_provider_service.get_weather_data("São Paulo")
            
            assert result["location"] == "São Paulo"
            assert result["solar_irradiance"] == 850

    @pytest.mark.asyncio
    async def test_aggregate_data_dashboard_success(self, data_provider_service):
        """Test successful dashboard data aggregation."""
        with patch.multiple(
            data_provider_service,
            get_economic_data=AsyncMock(return_value={"selic_rate": {"rate": 12.5}}),
            get_market_analysis=AsyncMock(return_value={"total_capacity_mw": 15000}),
            get_project_statistics=AsyncMock(return_value={"total_projects": 1500}),
            get_real_time_grid_data=AsyncMock(return_value={"system_demand": 45000})
        ):
            
            result = await data_provider_service.get_dashboard_data()
            
            assert "economic_indicators" in result
            assert "market_overview" in result
            assert "project_metrics" in result
            assert "real_time_grid" in result

    @pytest.mark.asyncio
    async def test_cache_integration(self, data_provider_service):
        """Test data caching integration."""
        with patch('app.services.data_provider_service.redis_client') as mock_redis:
            mock_redis.get.return_value = None  # No cached data
            mock_redis.set.return_value = True   # Cache set successful
            
            with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
                mock_bacen.get_selic_rate.return_value = {"rate": 12.5}
                
                # First call - should cache result
                result1 = await data_provider_service.get_economic_data()
                
                # Verify cache was checked and set
                mock_redis.get.assert_called()
                mock_redis.set.assert_called()

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, data_provider_service):
        """Test rate limiting integration."""
        with patch('app.services.data_provider_service.rate_limiter') as mock_limiter:
            mock_limiter.is_allowed.return_value = True
            
            result = await data_provider_service.get_economic_data()
            
            mock_limiter.is_allowed.assert_called()

    @pytest.mark.asyncio
    async def test_error_handling_partial_failures(self, data_provider_service):
        """Test error handling with partial service failures."""
        with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
            mock_bacen.get_selic_rate.side_effect = Exception("BACEN error")
            mock_bacen.get_inflation_data.return_value = {"ipca": 4.2}
            
            result = await data_provider_service.get_economic_data()
            
            # Should still return partial data with error indication
            assert "inflation_data" in result
            assert result["inflation_data"]["ipca"] == 4.2
            assert "errors" in result

    @pytest.mark.asyncio
    async def test_timeout_handling(self, data_provider_service):
        """Test timeout handling for external API calls."""
        with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
            mock_bacen.get_selic_rate.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await data_provider_service.get_economic_data()
            
            assert result["success"] is False
            assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_data_validation_and_sanitization(self, data_provider_service):
        """Test data validation and sanitization."""
        invalid_data = {
            "selic_rate": {"rate": "invalid_number"},
            "inflation_data": None
        }
        
        with patch.object(data_provider_service, 'bacen_service') as mock_bacen:
            mock_bacen.get_selic_rate.return_value = invalid_data["selic_rate"]
            mock_bacen.get_inflation_data.return_value = invalid_data["inflation_data"]
            
            result = await data_provider_service.get_economic_data()
            
            # Should handle invalid data gracefully
            assert "validation_errors" in result or result["success"] is False

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self, data_provider_service):
        """Test handling of concurrent requests."""
        import asyncio
        
        async def make_request():
            return await data_provider_service.get_economic_data()
        
        # Simulate concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete successfully
        for result in results:
            assert not isinstance(result, Exception)

    def test_configuration_management(self, data_provider_service):
        """Test service configuration management."""
        config = data_provider_service.get_configuration()
        
        assert "api_endpoints" in config
        assert "cache_settings" in config
        assert "rate_limits" in config

    @pytest.mark.asyncio
    async def test_health_check(self, data_provider_service):
        """Test service health check."""
        health_status = await data_provider_service.health_check()
        
        assert "status" in health_status
        assert "services" in health_status
        assert health_status["status"] in ["healthy", "degraded", "unhealthy"]