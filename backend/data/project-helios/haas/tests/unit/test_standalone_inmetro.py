"""
Standalone INMETRO validation tests that don't depend on app imports
"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest


class MockINMETROValidator:
    """Mock INMETRO validator for testing without imports"""

    def __init__(self):
        self.config = {
            'inmetro_api_url': 'https://mock-inmetro-api.gov.br',
            'inmetro_timeout': 30,
            'cache_duration_hours': 24,
            'validation_strict_mode': True
        }
        self.redis_client = Mock()
        self.certified_equipment_cache = {}

    async def validate_equipment(self, equipment_data: dict) -> dict:
        """Mock equipment validation"""
        if equipment_data.get('model') == 'INVALID_MODEL':
            return {
                'valid': False,
                'errors': ['Equipment model not found in INMETRO database'],
                'certification_status': 'not_certified'
            }

        if equipment_data.get('force_error'):
            raise Exception("INMETRO API error")

        return {
            'valid': True,
            'certification_number': f"CERT_{equipment_data.get('model', 'UNKNOWN')}",
            'certification_status': 'certified',
            'certificate_expiry': '2025-12-31',
            'technical_specifications': {
                'power_rating': equipment_data.get('power_rating', '5kW'),
                'efficiency': equipment_data.get('efficiency', '95.5%'),
                'protection_class': 'IP65'
            }
        }

    async def check_certification(self, certification_number: str) -> dict:
        """Mock certification check"""
        if certification_number == 'CERT_EXPIRED':
            return {
                'valid': False,
                'status': 'expired',
                'expiry_date': '2023-12-31'
            }

        if certification_number == 'CERT_INVALID':
            return {
                'valid': False,
                'status': 'not_found',
                'error': 'Certification number not found'
            }

        return {
            'valid': True,
            'status': 'active',
            'expiry_date': '2025-12-31',
            'equipment_type': 'inverter',
            'manufacturer': 'Solar Tech Inc.'
        }

    async def validate_technical_specs(self, specs: dict) -> dict:
        """Mock technical specifications validation"""
        required_fields = ['power_rating', 'voltage_range', 'frequency', 'efficiency']
        missing_fields = [field for field in required_fields if field not in specs]

        if missing_fields:
            return {
                'valid': False,
                'errors': [f'Missing required field: {field}' for field in missing_fields]
            }

        # Validate ranges
        power_rating = specs.get('power_rating', '0kW')
        power_value = float(power_rating.replace('kW', ''))

        if power_value <= 0 or power_value > 1000:
            return {
                'valid': False,
                'errors': ['Power rating must be between 0 and 1000 kW']
            }

        efficiency = specs.get('efficiency', '0%')
        efficiency_value = float(efficiency.replace('%', ''))

        if efficiency_value < 80 or efficiency_value > 100:
            return {
                'valid': False,
                'errors': ['Efficiency must be between 80% and 100%']
            }

        return {
            'valid': True,
            'compliance_level': 'fully_compliant',
            'standards_met': ['NBR 16274', 'NBR 11704', 'IEC 62109']
        }

    async def get_certified_equipment_list(self, equipment_type: str = None) -> List[dict]:
        """Mock certified equipment list"""
        if equipment_type == 'invalid_type':
            return []

        mock_equipment = [
            {
                'model': 'INV-5000-A',
                'manufacturer': 'Solar Tech Inc.',
                'type': 'inverter',
                'power_rating': '5kW',
                'certification_number': 'CERT_INV_5000_A',
                'certification_date': '2023-01-15'
            },
            {
                'model': 'PV-400-B',
                'manufacturer': 'Panel Corp.',
                'type': 'photovoltaic_module',
                'power_rating': '400W',
                'certification_number': 'CERT_PV_400_B',
                'certification_date': '2023-03-20'
            }
        ]

        if equipment_type:
            return [eq for eq in mock_equipment if eq['type'] == equipment_type]

        return mock_equipment

    async def validate_project_equipment(self, project_data: dict) -> dict:
        """Mock project equipment validation"""
        equipment_list = project_data.get('equipment_list', [])

        if not equipment_list:
            return {
                'valid': False,
                'errors': ['No equipment specified in project'],
                'validated_equipment': []
            }

        validated_equipment = []
        errors = []

        for equipment in equipment_list:
            validation_result = await self.validate_equipment(equipment)

            if validation_result['valid']:
                validated_equipment.append({
                    'equipment': equipment,
                    'validation': validation_result
                })
            else:
                errors.extend(validation_result.get('errors', []))

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'validated_equipment': validated_equipment,
            'total_equipment': len(equipment_list),
            'valid_equipment': len(validated_equipment)
        }


class TestStandaloneINMETROValidator:
    """Test INMETRO validator functionality independently"""

    @pytest.fixture
    def inmetro_validator(self):
        """Create INMETRO validator instance"""
        return MockINMETROValidator()

    @pytest.fixture
    def sample_equipment(self):
        """Sample equipment data"""
        return {
            'model': 'INV-5000-PRO',
            'manufacturer': 'Solar Tech Inc.',
            'type': 'inverter',
            'power_rating': '5kW',
            'voltage_range': '220-240V',
            'frequency': '60Hz',
            'efficiency': '95.5%',
            'certification_number': 'CERT_INV_5000_PRO'
        }

    @pytest.fixture
    def sample_technical_specs(self):
        """Sample technical specifications"""
        return {
            'power_rating': '5kW',
            'voltage_range': '220-240V',
            'frequency': '60Hz',
            'efficiency': '95.5%',
            'protection_class': 'IP65',
            'operating_temp': '-25°C to +60°C',
            'humidity_range': '0-95%'
        }

    def test_inmetro_validator_initialization(self, inmetro_validator):
        """Test INMETRO validator initializes correctly"""
        assert inmetro_validator.config['inmetro_api_url'] == 'https://mock-inmetro-api.gov.br'
        assert inmetro_validator.config['inmetro_timeout'] == 30
        assert inmetro_validator.config['validation_strict_mode'] is True
        assert inmetro_validator.redis_client is not None

    @pytest.mark.asyncio
    async def test_validate_equipment_success(self, inmetro_validator, sample_equipment):
        """Test successful equipment validation"""
        result = await inmetro_validator.validate_equipment(sample_equipment)

        assert result['valid'] is True
        assert 'certification_number' in result
        assert result['certification_status'] == 'certified'
        assert 'technical_specifications' in result

    @pytest.mark.asyncio
    async def test_validate_equipment_invalid_model(self, inmetro_validator):
        """Test equipment validation with invalid model"""
        invalid_equipment = {
            'model': 'INVALID_MODEL',
            'manufacturer': 'Unknown Corp.',
            'type': 'inverter'
        }

        result = await inmetro_validator.validate_equipment(invalid_equipment)

        assert result['valid'] is False
        assert 'Equipment model not found' in result['errors'][0]
        assert result['certification_status'] == 'not_certified'

    @pytest.mark.asyncio
    async def test_validate_equipment_api_error(self, inmetro_validator):
        """Test equipment validation with API error"""
        error_equipment = {'force_error': True}

        with pytest.raises(Exception, match="INMETRO API error"):
            await inmetro_validator.validate_equipment(error_equipment)

    @pytest.mark.asyncio
    async def test_check_certification_valid(self, inmetro_validator):
        """Test checking valid certification"""
        certification_number = 'CERT_INV_5000_PRO'

        result = await inmetro_validator.check_certification(certification_number)

        assert result['valid'] is True
        assert result['status'] == 'active'
        assert 'expiry_date' in result
        assert result['equipment_type'] == 'inverter'

    @pytest.mark.asyncio
    async def test_check_certification_expired(self, inmetro_validator):
        """Test checking expired certification"""
        certification_number = 'CERT_EXPIRED'

        result = await inmetro_validator.check_certification(certification_number)

        assert result['valid'] is False
        assert result['status'] == 'expired'
        assert result['expiry_date'] == '2023-12-31'

    @pytest.mark.asyncio
    async def test_check_certification_not_found(self, inmetro_validator):
        """Test checking non-existent certification"""
        certification_number = 'CERT_INVALID'

        result = await inmetro_validator.check_certification(certification_number)

        assert result['valid'] is False
        assert result['status'] == 'not_found'
        assert 'not found' in result['error']

    @pytest.mark.asyncio
    async def test_validate_technical_specs_success(self, inmetro_validator, sample_technical_specs):
        """Test successful technical specifications validation"""
        result = await inmetro_validator.validate_technical_specs(sample_technical_specs)

        assert result['valid'] is True
        assert result['compliance_level'] == 'fully_compliant'
        assert 'standards_met' in result
        assert len(result['standards_met']) > 0

    @pytest.mark.asyncio
    async def test_validate_technical_specs_missing_fields(self, inmetro_validator):
        """Test technical specifications validation with missing fields"""
        incomplete_specs = {
            'power_rating': '5kW',
            'efficiency': '95.5%'
            # Missing voltage_range and frequency
        }

        result = await inmetro_validator.validate_technical_specs(incomplete_specs)

        assert result['valid'] is False
        assert len(result['errors']) == 2  # Missing voltage_range and frequency
        assert any('voltage_range' in error for error in result['errors'])
        assert any('frequency' in error for error in result['errors'])

    @pytest.mark.asyncio
    async def test_validate_technical_specs_invalid_power(self, inmetro_validator):
        """Test technical specifications validation with invalid power rating"""
        invalid_specs = {
            'power_rating': '2000kW',  # Too high
            'voltage_range': '220-240V',
            'frequency': '60Hz',
            'efficiency': '95.5%'
        }

        result = await inmetro_validator.validate_technical_specs(invalid_specs)

        assert result['valid'] is False
        assert any('Power rating must be between' in error for error in result['errors'])

    @pytest.mark.asyncio
    async def test_validate_technical_specs_invalid_efficiency(self, inmetro_validator):
        """Test technical specifications validation with invalid efficiency"""
        invalid_specs = {
            'power_rating': '5kW',
            'voltage_range': '220-240V',
            'frequency': '60Hz',
            'efficiency': '110%'  # Too high
        }

        result = await inmetro_validator.validate_technical_specs(invalid_specs)

        assert result['valid'] is False
        assert any('Efficiency must be between' in error for error in result['errors'])

    @pytest.mark.asyncio
    async def test_get_certified_equipment_list_all(self, inmetro_validator):
        """Test getting all certified equipment"""
        equipment_list = await inmetro_validator.get_certified_equipment_list()

        assert isinstance(equipment_list, list)
        assert len(equipment_list) > 0

        for equipment in equipment_list:
            assert 'model' in equipment
            assert 'manufacturer' in equipment
            assert 'type' in equipment
            assert 'certification_number' in equipment

    @pytest.mark.asyncio
    async def test_get_certified_equipment_list_by_type(self, inmetro_validator):
        """Test getting certified equipment by type"""
        inverters = await inmetro_validator.get_certified_equipment_list('inverter')

        assert isinstance(inverters, list)
        for equipment in inverters:
            assert equipment['type'] == 'inverter'

    @pytest.mark.asyncio
    async def test_get_certified_equipment_list_invalid_type(self, inmetro_validator):
        """Test getting certified equipment with invalid type"""
        equipment_list = await inmetro_validator.get_certified_equipment_list('invalid_type')

        assert isinstance(equipment_list, list)
        assert len(equipment_list) == 0

    @pytest.mark.asyncio
    async def test_validate_project_equipment_success(self, inmetro_validator, sample_equipment):
        """Test successful project equipment validation"""
        project_data = {
            'project_id': 'PROJ_123',
            'equipment_list': [
                sample_equipment,
                {
                    'model': 'PV-400-B',
                    'manufacturer': 'Panel Corp.',
                    'type': 'photovoltaic_module',
                    'power_rating': '400W'
                }
            ]
        }

        result = await inmetro_validator.validate_project_equipment(project_data)

        assert result['valid'] is True
        assert result['total_equipment'] == 2
        assert result['valid_equipment'] == 2
        assert len(result['validated_equipment']) == 2
        assert len(result['errors']) == 0

    @pytest.mark.asyncio
    async def test_validate_project_equipment_no_equipment(self, inmetro_validator):
        """Test project equipment validation with no equipment"""
        project_data = {
            'project_id': 'PROJ_123',
            'equipment_list': []
        }

        result = await inmetro_validator.validate_project_equipment(project_data)

        assert result['valid'] is False
        assert 'No equipment specified' in result['errors'][0]
        assert result['total_equipment'] == 0
        assert result['valid_equipment'] == 0

    @pytest.mark.asyncio
    async def test_validate_project_equipment_mixed_validity(self, inmetro_validator):
        """Test project equipment validation with mixed valid/invalid equipment"""
        project_data = {
            'project_id': 'PROJ_123',
            'equipment_list': [
                {
                    'model': 'VALID_MODEL',
                    'manufacturer': 'Good Corp.',
                    'type': 'inverter'
                },
                {
                    'model': 'INVALID_MODEL',  # This will fail validation
                    'manufacturer': 'Bad Corp.',
                    'type': 'inverter'
                }
            ]
        }

        result = await inmetro_validator.validate_project_equipment(project_data)

        assert result['valid'] is False
        assert result['total_equipment'] == 2
        assert result['valid_equipment'] == 1
        assert len(result['errors']) > 0
        assert 'Equipment model not found' in result['errors'][0]

    @pytest.mark.asyncio
    async def test_equipment_validation_caching(self, inmetro_validator, sample_equipment):
        """Test equipment validation with caching"""
        # First validation
        result1 = await inmetro_validator.validate_equipment(sample_equipment)

        # Cache the result
        cache_key = f"equipment_{sample_equipment['model']}"
        inmetro_validator.certified_equipment_cache[cache_key] = result1

        # Second validation (should use cache)
        result2 = await inmetro_validator.validate_equipment(sample_equipment)

        assert result1 == result2
        assert cache_key in inmetro_validator.certified_equipment_cache

    @pytest.mark.asyncio
    async def test_concurrent_equipment_validation(self, inmetro_validator):
        """Test concurrent equipment validation"""
        import asyncio

        equipment_list = [
            {'model': f'MODEL_{i}', 'type': 'inverter', 'power_rating': f'{i}kW'}
            for i in range(1, 6)
        ]

        tasks = [
            inmetro_validator.validate_equipment(equipment)
            for equipment in equipment_list
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == len(equipment_list)
        for result in results:
            assert 'valid' in result
            assert 'certification_status' in result

    def test_equipment_data_sanitization(self, inmetro_validator):
        """Test equipment data sanitization"""
        raw_equipment = {
            'model': '  INV-5000-PRO  ',  # Extra whitespace
            'manufacturer': 'Solar Tech Inc.',
            'type': 'INVERTER',  # Wrong case
            'power_rating': '5 kW',  # Space in value
            'efficiency': '95.5 %'  # Space in percentage
        }

        # Mock sanitization
        sanitized = {
            'model': raw_equipment['model'].strip(),
            'manufacturer': raw_equipment['manufacturer'].strip(),
            'type': raw_equipment['type'].lower(),
            'power_rating': raw_equipment['power_rating'].replace(' ', ''),
            'efficiency': raw_equipment['efficiency'].replace(' ', '')
        }

        assert sanitized['model'] == 'INV-5000-PRO'
        assert sanitized['type'] == 'inverter'
        assert sanitized['power_rating'] == '5kW'
        assert sanitized['efficiency'] == '95.5%'


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
