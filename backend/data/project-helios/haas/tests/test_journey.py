import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime
from app.routers.journey import router as journey_router
from app.schemas.journey import (
    EconomySimulationRequest,
    EconomySimulationResponse,
    PaybackCalculationRequest,
    PaybackCalculationResponse,
    ProjectValidationRequest,
    ProjectValidationResponse,
    ProjectSubmissionRequest,
    ProjectSubmissionResponse,
    StatusMonitoringRequest,
    StatusMonitoringResponse,
)


# Create a test app with just the journey router
def create_test_app() -> FastAPI:
    app = FastAPI(title="Test HaaS Journey API")
    app.include_router(journey_router, prefix="/api", tags=["journey"])
    return app


@pytest.fixture
def client():
    """Create test client with journey router only."""
    app = create_test_app()
    return TestClient(app)


@pytest.fixture
def mock_journey_service():
    """Mock journey service for testing."""
    with patch("app.routers.journey.JourneyService") as mock_service:
        # Create mock instance
        mock_instance = Mock()
        mock_service.return_value = mock_instance

        # Mock economy simulation
        mock_instance.simulate_economy.return_value = EconomySimulationResponse(
            monthly_savings=450.50,
            annual_savings=5406.00,
            payback_years=4.2,
            total_investment=25000.00,
            roi_percentage=15.5,
        )

        # Mock payback calculation
        mock_instance.calculate_payback.return_value = PaybackCalculationResponse(
            payback_period_years=4.2,
            net_present_value=15000.00,
            internal_rate_return=0.12,
            cash_flow_projection=[
                {"year": 1, "cash_flow": -25000.0, "cumulative": -25000.0},
                {"year": 2, "cash_flow": 5406.0, "cumulative": -19694.0},
                {"year": 3, "cash_flow": 5406.0, "cumulative": -14288.0},
                {"year": 4, "cash_flow": 5406.0, "cumulative": -8882.0},
                {"year": 5, "cash_flow": 5406.0, "cumulative": -3476.0},
                {"year": 6, "cash_flow": 5406.0, "cumulative": 1930.0},
            ],
        )

        # Mock project validation
        mock_instance.validate_project.return_value = ProjectValidationResponse(
            is_valid=True,
            validation_errors=[],
            warnings=["Equipment efficiency slightly below optimal"],
            estimated_approval_time_days=30,
            required_documents=["INMETRO certificate", "Technical report"],
        )

        # Mock project submission
        mock_instance.submit_project.return_value = ProjectSubmissionResponse(
            project_id="PRJ-2024-001",
            submission_status="submitted",
            protocol_number="PROTO-12345",
            estimated_completion_days=45,
            next_steps=["Document review", "Technical validation", "Field inspection"],
        )

        # Mock status monitoring
        mock_instance.monitor_status.return_value = StatusMonitoringResponse(
            project_id="PRJ-2024-001",
            current_status="under_review",
            status_history=[
                {
                    "date": "2024-01-01",
                    "status": "submitted",
                    "notes": "Projeto submetido",
                },
                {
                    "date": "2024-01-15",
                    "status": "under_review",
                    "notes": "Análise inicial",
                },
            ],
            completion_percentage=25.0,
            issues=[],
            next_actions=["Enviar documentação pendente"],
            last_updated=datetime(2024, 1, 15, 10, 30, 0),
        )

        yield mock_instance


def test_simulate_economy_residential(client, mock_journey_service):
    """Test economy simulation for residential segment"""
    response = client.post(
        "/api/journey/residential/discovery/simulate_economy",
        json={
            "capacity_kw": 5.0,
            "location": "São Paulo",
            "tariff_type": "GD II",
            "monthly_consumption_kwh": 800,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "monthly_savings" in data
    assert "payback_years" in data
    assert data["payback_years"] > 0


def test_calculate_payback_commercial(client, mock_journey_service):
    """Test payback calculation for commercial segment"""
    response = client.post(
        "/api/journey/commercial/education/payback_calculator",
        json={
            "capacity_kw": 50.0,
            "investment_cost": 300000.0,
            "monthly_consumption_kwh": 5000,
            "electricity_cost_per_kwh": 0.8,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "payback_period_years" in data
    assert "cash_flow_projection" in data


def test_validate_project_industrial(client, mock_journey_service):
    """Test project validation for industrial segment"""
    response = client.post(
        "/api/journey/industrial/consideration/validate_project",
        json={
            "capacity_kw": 300.0,
            "location": "Minas Gerais",
            "distributor_code": "CEMIG",
            "equipment_list": [
                {"categoria": "inversores", "fabricante": "WEG", "modelo": "SIW300H"}
            ],
            "consumer_unit": "12345678",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "required_documents" in data


def test_submit_project_rural(client, mock_journey_service):
    """Test project submission for rural segment"""
    response = client.post(
        "/api/journey/rural/purchase/submit_project",
        json={
            "project_name": "Sistema Solar Rural",
            "capacity_kw": 20.0,
            "location": "Goiás",
            "distributor_code": "ENEL",
            "consumer_unit": "87654321",
            "equipment_details": {"inverter": "WEG SIW20H"},
            "financing_required": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert "submission_status" in data


def test_monitor_status(client, mock_journey_service):
    """Test status monitoring"""
    # First submit a project to get an ID
    submit_response = client.post(
        "/api/journey/residential/purchase/submit_project",
        json={
            "project_name": "Test Project",
            "capacity_kw": 5.0,
            "location": "Test",
            "distributor_code": "TEST",
            "consumer_unit": "12345",
            "equipment_details": {},
            "financing_required": False,
        },
    )
    project_id = submit_response.json()["project_id"]

    # Now monitor status
    response = client.post(
        "/api/journey/residential/post_sale/monitor_status",
        json={"project_id": project_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert "current_status" in data


def test_invalid_segment(client, mock_journey_service):
    """Test invalid segment returns error"""
    response = client.post(
        "/api/journey/invalid/discovery/simulate_economy",
        json={
            "capacity_kw": 5.0,
            "location": "Test",
            "tariff_type": "GD II",
            "monthly_consumption_kwh": 800,
        },
    )
    assert response.status_code == 400
