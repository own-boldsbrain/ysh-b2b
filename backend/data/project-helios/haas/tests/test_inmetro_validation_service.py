"""Tests for INMETRO validation service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, date

from app.services.inmetro_validation_service import (
    INMETROValidationService, 
    INMETROValidationError
)
from app.models.distributors import ConnectionRequest


class TestINMETROValidationService:
    """Test cases for INMETRO validation service."""

    @pytest.fixture
    def mock_schema(self):
        """Mock INMETRO datasheet schema."""
        return {
            "type": "object",
            "properties": {
                "fabricante": {"type": "string"},
                "modelo": {"type": "string"},
                "potencia_nominal": {"type": "number"},
                "certificado": {"type": "string"}
            },
            "required": ["fabricante", "modelo", "potencia_nominal"]
        }

    @pytest.fixture
    def validation_service(self, mock_schema):
        """Create validation service with mocked schema."""
        with patch('app.services.inmetro_validation_service.load_datasheet_schema') as mock_load:
            mock_load.return_value = mock_schema
            service = INMETROValidationService()
            return service

    @pytest.fixture
    def sample_connection_request(self):
        """Sample connection request."""
        return ConnectionRequest(
            id="req-123",
            distributor_id="dist-1",
            project_type="residential",
            capacity_kw=5.0,
            voltage_level="low",
            location="São Paulo, SP",
            status="pending"
        )

    @pytest.fixture
    def valid_equipment_data(self):
        """Valid equipment data."""
        return {
            "fabricante": "Test Manufacturer",
            "modelo": "TEST-MODEL-123",
            "potencia_nominal": 5000,
            "certificado": "CERT-12345",
            "data_validade": "2026-12-31",
            "normas_ensaios": ["NBR 16149", "NBR 16150"]
        }

    @pytest.fixture
    def invalid_equipment_data(self):
        """Invalid equipment data missing required fields."""
        return {
            "fabricante": "Test Manufacturer",
            # Missing modelo and potencia_nominal
            "certificado": "CERT-12345"
        }

    def test_service_initialization(self, validation_service):
        """Test service initialization."""
        assert validation_service.schema is not None
        assert validation_service.validator is not None

    def test_validate_equipment_valid_data(self, validation_service, valid_equipment_data, sample_connection_request):
        """Test validation with valid equipment data."""
        with patch.object(validation_service.validator, 'validate') as mock_validate:
            mock_validate.return_value = {"valid": True, "errors": []}
            
            result = validation_service.validate_equipment_for_connection(
                valid_equipment_data, 
                sample_connection_request
            )
            
            assert result["valid"] is True
            assert result["errors"] == []
            mock_validate.assert_called_once()

    def test_validate_equipment_invalid_data(self, validation_service, invalid_equipment_data, sample_connection_request):
        """Test validation with invalid equipment data."""
        with patch.object(validation_service.validator, 'validate') as mock_validate:
            mock_validate.return_value = {
                "valid": False, 
                "errors": ["Missing required field: modelo", "Missing required field: potencia_nominal"]
            }
            
            result = validation_service.validate_equipment_for_connection(
                invalid_equipment_data, 
                sample_connection_request
            )
            
            assert result["valid"] is False
            assert len(result["errors"]) == 2

    def test_validate_equipment_certification_expired(self, validation_service, sample_connection_request):
        """Test validation with expired certification."""
        expired_equipment = {
            "fabricante": "Test Manufacturer",
            "modelo": "TEST-MODEL-123",
            "potencia_nominal": 5000,
            "certificado": "CERT-12345",
            "data_validade": "2020-12-31"  # Expired
        }
        
        result = validation_service.validate_equipment_for_connection(
            expired_equipment, 
            sample_connection_request
        )
        
        assert result["valid"] is False
        assert any("expired" in error.lower() for error in result["errors"])

    def test_validate_equipment_power_mismatch(self, validation_service, sample_connection_request):
        """Test validation with power rating mismatch."""
        mismatched_equipment = {
            "fabricante": "Test Manufacturer",
            "modelo": "TEST-MODEL-123",
            "potencia_nominal": 10000,  # 10kW equipment for 5kW request
            "certificado": "CERT-12345",
            "data_validade": "2026-12-31"
        }
        
        result = validation_service.validate_equipment_for_connection(
            mismatched_equipment, 
            sample_connection_request
        )
        
        assert result["valid"] is False
        assert any("power" in error.lower() for error in result["errors"])

    def test_validate_certification_info(self, validation_service):
        """Test certification info validation."""
        cert_info = {
            "numero": "CERT-12345",
            "data_emissao": "2024-01-01",
            "data_validade": "2026-12-31",
            "laboratorio": "CEPEL",
            "normas": ["NBR 16149", "NBR 16150"]
        }
        
        result = validation_service.validate_certification_info(cert_info)
        
        assert result["valid"] is True

    def test_validate_certification_info_invalid(self, validation_service):
        """Test certification info validation with invalid data."""
        invalid_cert_info = {
            "numero": "",  # Empty certificate number
            "data_validade": "invalid-date",  # Invalid date format
            "laboratorio": "Unknown Lab"  # Not recognized
        }
        
        result = validation_service.validate_certification_info(invalid_cert_info)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_check_equipment_compatibility(self, validation_service, valid_equipment_data, sample_connection_request):
        """Test equipment compatibility checking."""
        result = validation_service.check_equipment_compatibility(
            valid_equipment_data, 
            sample_connection_request
        )
        
        assert "compatible" in result
        assert "compatibility_score" in result
        assert isinstance(result["compatibility_score"], (int, float))

    def test_check_equipment_incompatible_voltage(self, validation_service, sample_connection_request):
        """Test equipment incompatible with voltage level."""
        incompatible_equipment = {
            "fabricante": "Test Manufacturer",
            "modelo": "HIGH-VOLTAGE-MODEL",
            "potencia_nominal": 5000,
            "tensao_operacao": "high",  # High voltage for low voltage request
            "certificado": "CERT-12345",
            "data_validade": "2026-12-31"
        }
        
        result = validation_service.check_equipment_compatibility(
            incompatible_equipment, 
            sample_connection_request
        )
        
        assert result["compatible"] is False
        assert result["compatibility_score"] < 0.5

    def test_validate_technical_standards(self, validation_service, valid_equipment_data):
        """Test technical standards validation."""
        result = validation_service.validate_technical_standards(valid_equipment_data)
        
        assert "standards_compliance" in result
        assert "compliant_standards" in result
        assert "non_compliant_standards" in result

    def test_validate_technical_standards_missing(self, validation_service):
        """Test technical standards validation with missing standards."""
        equipment_no_standards = {
            "fabricante": "Test Manufacturer",
            "modelo": "TEST-MODEL-123",
            "potencia_nominal": 5000,
            "certificado": "CERT-12345"
            # Missing normas_ensaios
        }
        
        result = validation_service.validate_technical_standards(equipment_no_standards)
        
        assert result["standards_compliance"] is False

    def test_get_validation_summary(self, validation_service, valid_equipment_data, sample_connection_request):
        """Test validation summary generation."""
        result = validation_service.get_validation_summary(
            valid_equipment_data, 
            sample_connection_request
        )
        
        assert "overall_result" in result
        assert "validation_details" in result
        assert "recommendations" in result
        assert "timestamp" in result

    def test_batch_equipment_validation(self, validation_service, sample_connection_request):
        """Test batch validation of multiple equipment."""
        equipment_list = [
            {
                "fabricante": "Manufacturer A",
                "modelo": "MODEL-A",
                "potencia_nominal": 5000,
                "certificado": "CERT-A"
            },
            {
                "fabricante": "Manufacturer B",
                "modelo": "MODEL-B",
                "potencia_nominal": 5000,
                "certificado": "CERT-B"
            }
        ]
        
        results = validation_service.validate_equipment_batch(
            equipment_list, 
            sample_connection_request
        )
        
        assert len(results) == 2
        for result in results:
            assert "valid" in result
            assert "equipment_id" in result

    def test_validation_error_handling(self, validation_service):
        """Test validation error handling."""
        with patch.object(validation_service.validator, 'validate') as mock_validate:
            mock_validate.side_effect = Exception("Validation error")
            
            with pytest.raises(INMETROValidationError):
                validation_service.validate_equipment_for_connection({}, Mock())

    def test_schema_validation_caching(self, validation_service):
        """Test schema validation result caching."""
        equipment_data = {
            "fabricante": "Test",
            "modelo": "TEST-123",
            "potencia_nominal": 5000
        }
        
        # First validation
        result1 = validation_service._validate_against_schema(equipment_data)
        
        # Second validation (should use cache)
        result2 = validation_service._validate_against_schema(equipment_data)
        
        assert result1 == result2

    def test_certification_database_lookup(self, validation_service):
        """Test certification database lookup."""
        cert_number = "CERT-12345"
        
        with patch('app.services.inmetro_validation_service.get_certification_from_db') as mock_get:
            mock_cert = {
                "numero": cert_number,
                "status": "valid",
                "data_validade": "2026-12-31"
            }
            mock_get.return_value = mock_cert
            
            result = validation_service.lookup_certification(cert_number)
            
            assert result == mock_cert
            mock_get.assert_called_once_with(cert_number)

    def test_equipment_datasheet_parsing(self, validation_service):
        """Test equipment datasheet parsing."""
        datasheet_content = {
            "electrical_specs": {
                "power_rating": "5kW",
                "voltage": "220V",
                "current": "23A"
            },
            "certifications": ["NBR 16149", "IEC 61215"],
            "manufacturer_info": {
                "name": "Test Manufacturer",
                "model": "TEST-123"
            }
        }
        
        parsed = validation_service.parse_equipment_datasheet(datasheet_content)
        
        assert "fabricante" in parsed
        assert "modelo" in parsed
        assert "potencia_nominal" in parsed
        assert "normas_ensaios" in parsed

    def test_validation_report_generation(self, validation_service, valid_equipment_data, sample_connection_request):
        """Test validation report generation."""
        report = validation_service.generate_validation_report(
            valid_equipment_data, 
            sample_connection_request
        )
        
        assert "report_id" in report
        assert "validation_summary" in report
        assert "detailed_results" in report
        assert "generated_at" in report
        assert isinstance(report["generated_at"], datetime)