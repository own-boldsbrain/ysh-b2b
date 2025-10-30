"""Tests for ANEEL validator service functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import pandas as pd

from app.services.aneel_validator_service import ANEELValidatorService


class TestANEELValidatorService:
    """Test cases for ANEEL validator service."""

    @pytest.fixture
    def aneel_service(self):
        """Create ANEEL validator service instance."""
        return ANEELValidatorService()

    @pytest.fixture
    def mock_crawler_storage(self):
        """Mock crawler storage service."""
        return Mock()

    @pytest.fixture
    def sample_gd_data(self):
        """Sample GD project data."""
        return [
            {
                "ceg": "SP.GD.ENEL.12345678",
                "uf": "SP",
                "nom_agente": "ENEL São Paulo",
                "potencia_instalada": 5.0,
                "modalidade": "micro",
                "fonte": "fotovoltaica",
                "municipio": "São Paulo"
            },
            {
                "ceg": "RJ.GD.LIGHT.87654321",
                "uf": "RJ",
                "nom_agente": "Light",
                "potencia_instalada": 50.0,
                "modalidade": "mini",
                "fonte": "solar",
                "municipio": "Rio de Janeiro"
            }
        ]

    @pytest.fixture
    def sample_distributor_data(self):
        """Sample distributor data."""
        return [
            {
                "cod_agente": "ENEL_SP",
                "nom_agente": "ENEL São Paulo",
                "sigla_uf": "SP",
                "dsc_classe_agente": "DISTRIBUIDORA"
            },
            {
                "cod_agente": "LIGHT",
                "nom_agente": "Light Serviços de Eletricidade S.A.",
                "sigla_uf": "RJ",
                "dsc_classe_agente": "DISTRIBUIDORA"
            }
        ]

    def test_aneel_service_initialization(self, aneel_service):
        """Test ANEEL service initialization."""
        assert aneel_service.hf_repo == "fernando-bold/aneel-datasets"
        assert aneel_service.cache_timeout.total_seconds() == 24 * 3600
        assert aneel_service.crawler_storage is not None

    @pytest.mark.asyncio
    async def test_sync_datasets_success(self, aneel_service):
        """Test successful dataset synchronization."""
        with patch.object(aneel_service, '_sync_single_dataset') as mock_sync:
            mock_sync.return_value = 100  # 100 records synced
            
            result = await aneel_service.sync_datasets(
                specific_datasets=['distribuidoras']
            )
            
            assert result["success"] is True
            assert result["datasets_synced"] == 1
            assert result["total_records"] == 100

    @pytest.mark.asyncio
    async def test_sync_datasets_partial_failure(self, aneel_service):
        """Test dataset synchronization with partial failures."""
        with patch.object(aneel_service, '_sync_single_dataset') as mock_sync:
            mock_sync.side_effect = [100, 0, 200]  # Second dataset fails
            
            result = await aneel_service.sync_datasets(
                specific_datasets=['distribuidoras', 'failed_dataset', 'empreendimentos_gd']
            )
            
            assert result["success"] is True
            assert result["datasets_synced"] == 2
            assert result["total_records"] == 300

    @pytest.mark.asyncio
    async def test_query_gd_projects_success(self, aneel_service, sample_gd_data):
        """Test successful GD projects query."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "total_results": 2,
                "returned_results": 2,
                "data": sample_gd_data,
                "metadata": {"dataset_info": {}}
            }
            
            filters = {"uf": "SP", "potencia_min": 1.0}
            result = await aneel_service.execute_query("gd", filters, limit=10)
            
            assert result["success"] is True
            assert result["total_results"] == 2
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_query_distributors_success(self, aneel_service, sample_distributor_data):
        """Test successful distributors query."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "total_results": 2,
                "returned_results": 2,
                "data": sample_distributor_data,
                "metadata": {"dataset_info": {}}
            }
            
            filters = {"uf": "SP"}
            result = await aneel_service.execute_query("distributor", filters)
            
            assert result["success"] is True
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_validate_project_complete(self, aneel_service):
        """Test complete project validation."""
        validation_data = {
            "ceg": "SP.GD.ENEL.12345678",
            "distribuidora": "ENEL São Paulo",
            "uf": "SP",
            "potencia_kw": 5.0,
            "modalidade": "micro",
            "fonte": "fotovoltaica",
            "municipio": "São Paulo"
        }
        
        # Mock all validation methods
        with patch.multiple(
            aneel_service,
            _validate_distributor_real=AsyncMock(return_value={"check": "distributor_exists", "passed": True}),
            _validate_siga_reference_real=AsyncMock(return_value={"check": "siga_reference", "passed": True}),
            _validate_municipality_real=AsyncMock(return_value={"check": "municipality_coverage", "passed": True}),
            _validate_technical_requirements=AsyncMock(return_value=[{"check": "energy_source", "passed": True}])
        ):
            
            result = await aneel_service.validate_project(validation_data)
            
            assert result["success"] is True
            assert result["overall_valid"] is True
            assert len(result["validation_checks"]) >= 4

    def test_validate_ceg_format_valid(self, aneel_service):
        """Test CEG format validation with valid format."""
        valid_ceg = "SP.GD.ENEL.12345678"
        
        result = aneel_service._validate_ceg_format(valid_ceg)
        
        assert result["passed"] is True
        assert result["check"] == "ceg_format"

    def test_validate_ceg_format_invalid_parts(self, aneel_service):
        """Test CEG format validation with invalid number of parts."""
        invalid_ceg = "SP.GD.ENEL"  # Missing number part
        
        result = aneel_service._validate_ceg_format(invalid_ceg)
        
        assert result["passed"] is False
        assert "4 partes" in result["message"]

    def test_validate_ceg_format_invalid_uf(self, aneel_service):
        """Test CEG format validation with invalid UF."""
        invalid_ceg = "S.GD.ENEL.12345678"  # UF too short
        
        result = aneel_service._validate_ceg_format(invalid_ceg)
        
        assert result["passed"] is False
        assert "UF deve ter 2 caracteres" in result["message"]

    def test_validate_ceg_format_invalid_type(self, aneel_service):
        """Test CEG format validation with invalid type."""
        invalid_ceg = "SP.TD.ENEL.12345678"  # Should be GD
        
        result = aneel_service._validate_ceg_format(invalid_ceg)
        
        assert result["passed"] is False
        assert "Tipo deve ser 'GD'" in result["message"]

    def test_validate_power_range_micro_valid(self, aneel_service):
        """Test power range validation for valid micro GD."""
        result = aneel_service._validate_power_range(50.0, "micro")
        
        assert result["passed"] is True
        assert "Micro GD" in result["message"]

    def test_validate_power_range_micro_invalid(self, aneel_service):
        """Test power range validation for invalid micro GD."""
        result = aneel_service._validate_power_range(100.0, "micro")
        
        assert result["passed"] is False
        assert "excede limite" in result["message"]

    def test_validate_power_range_mini_valid(self, aneel_service):
        """Test power range validation for valid mini GD."""
        result = aneel_service._validate_power_range(1000.0, "mini")
        
        assert result["passed"] is True
        assert "Mini GD" in result["message"]

    def test_validate_power_range_mini_too_low(self, aneel_service):
        """Test power range validation for mini GD below minimum."""
        result = aneel_service._validate_power_range(50.0, "mini")
        
        assert result["passed"] is False
        assert "abaixo do mínimo" in result["message"]

    def test_validate_power_range_invalid_modality(self, aneel_service):
        """Test power range validation with invalid modality."""
        result = aneel_service._validate_power_range(50.0, "invalid")
        
        assert result["passed"] is False
        assert "Modalidade 'invalid' inválida" in result["message"]

    @pytest.mark.asyncio
    async def test_validate_technical_requirements_valid_source(self, aneel_service):
        """Test technical requirements validation with valid energy source."""
        validation_data = {"fonte": "fotovoltaica"}
        
        results = await aneel_service._validate_technical_requirements(validation_data)
        
        assert len(results) >= 1
        energy_source_result = next(r for r in results if r["check"] == "energy_source")
        assert energy_source_result["passed"] is True

    @pytest.mark.asyncio
    async def test_validate_technical_requirements_invalid_source(self, aneel_service):
        """Test technical requirements validation with invalid energy source."""
        validation_data = {"fonte": "nuclear"}  # Not eligible for GD
        
        results = await aneel_service._validate_technical_requirements(validation_data)
        
        energy_source_result = next(r for r in results if r["check"] == "energy_source")
        assert energy_source_result["passed"] is False

    @pytest.mark.asyncio
    async def test_validate_distributor_real_success(self, aneel_service, sample_distributor_data):
        """Test distributor validation success."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "data": sample_distributor_data
            }
            
            result = await aneel_service._validate_distributor_real("ENEL São Paulo", "SP")
            
            assert result["passed"] is True
            assert result["check"] == "distributor_exists"

    @pytest.mark.asyncio
    async def test_validate_distributor_real_not_found(self, aneel_service):
        """Test distributor validation when not found."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "data": []
            }
            
            result = await aneel_service._validate_distributor_real("Unknown Distributor", "SP")
            
            assert result["passed"] is False
            assert "não encontrada" in result["message"]

    @pytest.mark.asyncio
    async def test_validate_siga_reference_found(self, aneel_service):
        """Test SIGA reference validation when CEG is found."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "data": [{"ceg": "SP.GD.ENEL.12345678"}]
            }
            
            result = await aneel_service._validate_siga_reference_real("SP.GD.ENEL.12345678")
            
            assert result["passed"] is True
            assert "encontrado no SIGA" in result["message"]

    @pytest.mark.asyncio
    async def test_validate_siga_reference_not_found(self, aneel_service):
        """Test SIGA reference validation when CEG is not found."""
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.query_dataset_data.return_value = {
                "success": True,
                "data": []
            }
            
            result = await aneel_service._validate_siga_reference_real("SP.GD.ENEL.99999999")
            
            assert result["passed"] is False
            assert "não encontrado no SIGA" in result["message"]

    @pytest.mark.asyncio
    async def test_sync_single_dataset_success(self, aneel_service):
        """Test successful single dataset synchronization."""
        mock_csv_data = "col1,col2\nvalue1,value2\nvalue3,value4"
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_csv_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with patch.object(aneel_service, '_insert_dataset_to_db') as mock_insert:
                mock_insert.return_value = 2  # 2 records inserted
                
                result = await aneel_service._sync_single_dataset(
                    "test_dataset", 
                    "test.csv", 
                    force=True
                )
                
                assert result == 2

    def test_needs_update_no_cache(self, aneel_service):
        """Test needs update when no cache exists."""
        with patch('app.services.aneel_validator_service.redis_client') as mock_redis:
            mock_redis.get.return_value = None
            
            result = aneel_service._needs_update("test_dataset")
            
            assert result is True

    def test_needs_update_expired_cache(self, aneel_service):
        """Test needs update when cache is expired."""
        from datetime import datetime, timedelta
        
        old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
        
        with patch('app.services.aneel_validator_service.redis_client') as mock_redis:
            mock_redis.get.return_value = old_timestamp
            
            result = aneel_service._needs_update("test_dataset")
            
            assert result is True

    def test_needs_update_fresh_cache(self, aneel_service):
        """Test needs update when cache is fresh."""
        from datetime import datetime, timedelta
        
        fresh_timestamp = (datetime.now() - timedelta(hours=1)).isoformat()
        
        with patch('app.services.aneel_validator_service.redis_client') as mock_redis:
            mock_redis.get.return_value = fresh_timestamp
            
            result = aneel_service._needs_update("test_dataset")
            
            assert result is False

    def test_update_cache_timestamp(self, aneel_service):
        """Test cache timestamp update."""
        with patch('app.services.aneel_validator_service.redis_client') as mock_redis:
            mock_redis.set.return_value = True
            
            aneel_service._update_cache_timestamp("test_dataset")
            
            mock_redis.set.assert_called_once()
            args, kwargs = mock_redis.set.call_args
            assert args[0] == "aneel:dataset:test_dataset:last_sync"
            assert kwargs["ex"] == 30 * 24 * 60 * 60  # 30 days

    @pytest.mark.asyncio
    async def test_execute_query_invalid_type(self, aneel_service):
        """Test execute query with invalid query type."""
        result = await aneel_service.execute_query("invalid_type", {})
        
        assert result["success"] is False
        assert "inválido" in result["error"]

    @pytest.mark.asyncio
    async def test_insert_dataset_to_db_success(self, aneel_service):
        """Test successful dataset insertion to database."""
        df = pd.DataFrame({
            "col1": ["value1", "value2"],
            "col2": ["value3", "value4"]
        })
        
        with patch.object(aneel_service, 'crawler_storage') as mock_storage:
            mock_storage.store_dataset.return_value = 1  # Record ID
            
            result = await aneel_service._insert_dataset_to_db("test_dataset", df)
            
            assert result == 2  # Number of records
            mock_storage.store_dataset.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_network_failure(self, aneel_service):
        """Test error handling for network failures."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = await aneel_service._sync_single_dataset(
                "test_dataset", 
                "test.csv", 
                force=True
            )
            
            assert result == 0

    @pytest.mark.asyncio
    async def test_concurrent_dataset_sync(self, aneel_service):
        """Test concurrent dataset synchronization."""
        import asyncio
        
        async def sync_dataset(dataset_name):
            return await aneel_service._sync_single_dataset(
                dataset_name, 
                f"{dataset_name}.csv", 
                force=True
            )
        
        with patch.object(aneel_service, '_insert_dataset_to_db') as mock_insert:
            mock_insert.return_value = 10
            
            with patch('httpx.AsyncClient.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = "col1,col2\nval1,val2"
                mock_response.raise_for_status.return_value = None
                mock_get.return_value.__aenter__.return_value = mock_response
                
                tasks = [sync_dataset(f"dataset_{i}") for i in range(3)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # All tasks should complete successfully
                for result in results:
                    assert not isinstance(result, Exception)