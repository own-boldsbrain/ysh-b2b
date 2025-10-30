from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# Schemas para Discovery
class EconomySimulationRequest(BaseModel):
    capacity_kw: float
    location: str
    tariff_type: str  # e.g., "GD I", "GD II"
    monthly_consumption_kwh: float


class EconomySimulationResponse(BaseModel):
    monthly_savings: float
    annual_savings: float
    payback_years: float
    total_investment: float
    roi_percentage: float


# Schemas para Education
class PaybackCalculationRequest(BaseModel):
    capacity_kw: float
    investment_cost: float
    monthly_consumption_kwh: float
    electricity_cost_per_kwh: float
    degradation_rate: Optional[float] = 0.005  # 0.5% per year


class PaybackCalculationResponse(BaseModel):
    payback_period_years: float
    net_present_value: float
    internal_rate_return: float
    cash_flow_projection: List[Dict[str, Any]]


# Schemas para Consideration
class ProjectValidationRequest(BaseModel):
    capacity_kw: float
    location: str
    distributor_code: str
    equipment_list: List[Dict[str, Any]]
    consumer_unit: str


class ProjectValidationResponse(BaseModel):
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    estimated_approval_time_days: int
    required_documents: List[str]


# Schemas para Purchase
class ProjectSubmissionRequest(BaseModel):
    project_name: str
    capacity_kw: float
    location: str
    distributor_code: str
    consumer_unit: str
    equipment_details: Dict[str, Any]
    financing_required: bool
    financing_details: Optional[Dict[str, Any]] = None


class ProjectSubmissionResponse(BaseModel):
    project_id: str
    submission_status: str
    protocol_number: Optional[str]
    estimated_completion_days: int
    next_steps: List[str]


# Schemas para Post-Sale
class StatusMonitoringRequest(BaseModel):
    project_id: str


class StatusMonitoringResponse(BaseModel):
    project_id: str
    current_status: str
    status_history: List[Dict[str, Any]]
    completion_percentage: float
    issues: List[str]
    next_actions: List[str]
    last_updated: datetime
