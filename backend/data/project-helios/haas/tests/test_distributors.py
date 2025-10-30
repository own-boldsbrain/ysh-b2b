import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.distributors import ConnectionRequest, Distributor
from app.services.distributor_workflow_service import DistributorWorkflowService
from app.services.distributor_service import submit_connection_request, validate_connection_request
from app.database import get_db


class TestDistributorWorkflowService:
    """Test cases for DistributorWorkflowService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.workflow_service = DistributorWorkflowService()

    def test_validate_request_valid(self):
        """Test validation of a valid connection request."""
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=5.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.validate_request(request)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_request_invalid_power(self):
        """Test validation of request with invalid power requirement."""
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.validate_request(request)

        assert result["valid"] is False
        assert "Power requirement must be greater than 0" in result["errors"]

    def test_validate_request_invalid_location(self):
        """Test validation of request with missing location."""
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=5.0,
            location={},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.validate_request(request)

        assert result["valid"] is False
        assert "Location information is required" in result["errors"]

    def test_validate_request_invalid_connection_type(self):
        """Test validation of request with invalid connection type."""
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="invalid_type",
            voltage_level="127/220V",
            power_requirement=5.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.validate_request(request)

        assert result["valid"] is False
        assert "Invalid connection type. Must be one of: residential, commercial, industrial" in result["errors"]

    def test_calculate_costs_cpfl(self):
        """Test cost calculation for CPFL distributor."""
        distributor = Distributor(
            id=1,
            name="CPFL Energia",
            code="CPFL",
            region="São Paulo",
            status="active",
            contact_email="contato@cpfl.com.br",
            contact_phone="0800-123-456",
            service_area="São Paulo",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.calculate_costs_and_requirements(distributor, request, False)

        assert result["estimated_cost"] == 1500  # 10 * 150
        assert result["estimated_time_days"] == 15
        assert len(result["requirements"]) == 4  # Basic requirements only

    def test_calculate_costs_enel_sp(self):
        """Test cost calculation for ENEL_SP distributor."""
        distributor = Distributor(
            id=2,
            name="Enel São Paulo",
            code="ENEL_SP",
            region="São Paulo",
            status="active",
            contact_email="contato@enel.com.br",
            contact_phone="0800-123-456",
            service_area="São Paulo",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        request = ConnectionRequest(
            distributor_id=2,
            connection_type="commercial",
            voltage_level="380V",
            power_requirement=20.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.calculate_costs_and_requirements(distributor, request, False)

        assert result["estimated_cost"] == 3600  # 20 * 180
        assert result["estimated_time_days"] == 20
        assert len(result["requirements"]) == 4

    def test_calculate_costs_cemig(self):
        """Test cost calculation for CEMIG distributor."""
        distributor = Distributor(
            id=3,
            name="CEMIG",
            code="CEMIG",
            region="Minas Gerais",
            status="active",
            contact_email="contato@cemig.com.br",
            contact_phone="0800-123-456",
            service_area="Minas Gerais",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        request = ConnectionRequest(
            distributor_id=3,
            connection_type="industrial",
            voltage_level="13.8kV",
            power_requirement=50.0,
            location={"address": "Belo Horizonte, MG"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.calculate_costs_and_requirements(distributor, request, False)

        assert result["estimated_cost"] == 7000  # 50 * 140
        assert result["estimated_time_days"] == 18
        assert len(result["requirements"]) == 4

    def test_calculate_costs_with_inmetro(self):
        """Test cost calculation with INMETRO validation."""
        distributor = Distributor(
            id=1,
            name="CPFL Energia",
            code="CPFL",
            region="São Paulo",
            status="active",
            contact_email="contato@cpfl.com.br",
            contact_phone="0800-123-456",
            service_area="São Paulo",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = self.workflow_service.calculate_costs_and_requirements(distributor, request, True)

        assert result["estimated_cost"] == 1500
        assert result["estimated_time_days"] == 15
        assert len(result["requirements"]) == 7  # Basic + INMETRO requirements


class TestDistributorIntegration:
    """Integration tests for distributor connection requests."""

    @pytest.mark.asyncio
    @patch('app.services.distributor_workflow_service.DistributorWorkflowService.execute_workflow')
    async def test_submit_connection_cpfl_success(self, mock_execute_workflow, db_session):
        """Test successful connection submission to CPFL."""
        # Mock workflow response
        mock_response = MagicMock()
        mock_response.request_id = "test-request-id"
        mock_response.status = "pending"
        mock_response.estimated_cost = 1500
        mock_response.estimated_time_days = 15
        mock_execute_workflow.return_value = mock_response

        # Test request
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        # Execute
        response = await submit_connection_request(db_session, 1, request, user_id=1)

        # Assertions
        assert response.request_id == "test-request-id"
        assert response.status == "pending"
        assert response.estimated_cost == 1500
        assert response.estimated_time_days == 15
        mock_execute_workflow.assert_called_once()
        mock_execute_workflow.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.distributor_workflow_service.DistributorWorkflowService.execute_workflow')
    async def test_submit_connection_enel_sp_success(self, mock_execute_workflow, db_session):
        """Test successful connection submission to ENEL_SP."""
        # Mock workflow response
        mock_response = MagicMock()
        mock_response.request_id = "test-request-id-enel"
        mock_response.status = "pending"
        mock_response.estimated_cost = 3600
        mock_response.estimated_time_days = 20
        mock_execute_workflow.return_value = mock_response

        # Test request
        request = ConnectionRequest(
            distributor_id=2,
            connection_type="commercial",
            voltage_level="380V",
            power_requirement=20.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        # Execute
        response = await submit_connection_request(db_session, 2, request, user_id=1)

        # Assertions
        assert response.request_id == "test-request-id-enel"
        assert response.status == "pending"
        assert response.estimated_cost == 3600
        assert response.estimated_time_days == 20
        mock_execute_workflow.assert_called_once()
        mock_execute_workflow.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.distributor_workflow_service.DistributorWorkflowService.execute_workflow')
    async def test_submit_connection_cemig_success(self, mock_execute_workflow, db_session):
        """Test successful connection submission to CEMIG."""
        # Mock workflow response
        mock_response = MagicMock()
        mock_response.request_id = "test-request-id-cemig"
        mock_response.status = "pending"
        mock_response.estimated_cost = 7000
        mock_response.estimated_time_days = 18
        mock_execute_workflow.return_value = mock_response

        # Test request
        request = ConnectionRequest(
            distributor_id=3,
            connection_type="industrial",
            voltage_level="13.8kV",
            power_requirement=50.0,
            location={"address": "Belo Horizonte, MG"},
            equipment=None,
            documents=None
        )

        # Execute
        response = await submit_connection_request(db_session, 3, request, user_id=1)

        # Assertions
        assert response.request_id == "test-request-id-cemig"
        assert response.status == "pending"
        assert response.estimated_cost == 7000
        assert response.estimated_time_days == 18
        mock_execute_workflow.assert_called_once()
        mock_execute_workflow.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.distributor_service.get_distributor_by_id')
    async def test_submit_connection_distributor_not_found(self, mock_get_distributor, db_session):
        """Test connection submission with non-existent distributor."""
        mock_get_distributor.return_value = None

        request = ConnectionRequest(
            distributor_id=999,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        # Execute and expect exception
        with pytest.raises(ValueError, match="Distributor with ID 999 not found"):
            await submit_connection_request(db_session, 999, request, user_id=1)

    def test_validate_connection_request_invalid_schema(self):
        """Test validation with invalid schema data."""
        # Test with negative power
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=-5.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = validate_connection_request(request)
        assert result["valid"] is False
        assert "Power requirement must be greater than 0" in result["errors"]

        # Test with empty location
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="residential",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={},
            equipment=None,
            documents=None
        )

        result = validate_connection_request(request)
        assert result["valid"] is False
        assert "Location information is required" in result["errors"]

        # Test with invalid connection type
        request = ConnectionRequest(
            distributor_id=1,
            connection_type="invalid",
            voltage_level="127/220V",
            power_requirement=10.0,
            location={"address": "São Paulo, SP"},
            equipment=None,
            documents=None
        )

        result = validate_connection_request(request)
        assert result["valid"] is False
        assert "Invalid connection type. Must be one of: residential, commercial, industrial" in result["errors"]