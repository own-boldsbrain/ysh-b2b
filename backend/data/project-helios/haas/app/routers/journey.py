from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.journey import (
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
from ..services.journey_service import JourneyService

router = APIRouter(prefix="/journey", tags=["Journey 360º"])


@router.post(
    "/{segment}/discovery/simulate_economy", response_model=EconomySimulationResponse
)
async def simulate_economy(
    segment: str, request: EconomySimulationRequest, db: Session = Depends(get_db)
):
    """Simula economia para descoberta na jornada"""
    if segment not in ["residential", "commercial", "industrial", "rural"]:
        raise HTTPException(status_code=400, detail="Segmento inválido")

    service = JourneyService(db)
    return service.simulate_economy(segment, request)


@router.post(
    "/{segment}/education/payback_calculator", response_model=PaybackCalculationResponse
)
async def calculate_payback(
    segment: str, request: PaybackCalculationRequest, db: Session = Depends(get_db)
):
    """Calcula payback para educação na jornada"""
    if segment not in ["residential", "commercial", "industrial", "rural"]:
        raise HTTPException(status_code=400, detail="Segmento inválido")

    service = JourneyService(db)
    return service.calculate_payback(segment, request)


@router.post(
    "/{segment}/consideration/validate_project",
    response_model=ProjectValidationResponse,
)
async def validate_project(
    segment: str, request: ProjectValidationRequest, db: Session = Depends(get_db)
):
    """Valida projeto preliminar para consideração"""
    if segment not in ["residential", "commercial", "industrial", "rural"]:
        raise HTTPException(status_code=400, detail="Segmento inválido")

    service = JourneyService(db)
    return service.validate_project(segment, request)


@router.post(
    "/{segment}/purchase/submit_project", response_model=ProjectSubmissionResponse
)
async def submit_project(
    segment: str, request: ProjectSubmissionRequest, db: Session = Depends(get_db)
):
    """Submete projeto para homologação"""
    if segment not in ["residential", "commercial", "industrial", "rural"]:
        raise HTTPException(status_code=400, detail="Segmento inválido")

    service = JourneyService(db)
    return service.submit_project(segment, request)


@router.post(
    "/{segment}/post_sale/monitor_status", response_model=StatusMonitoringResponse
)
async def monitor_status(
    segment: str, request: StatusMonitoringRequest, db: Session = Depends(get_db)
):
    """Monitora status pós-venda"""
    if segment not in ["residential", "commercial", "industrial", "rural"]:
        raise HTTPException(status_code=400, detail="Segmento inválido")

    service = JourneyService(db)
    return service.monitor_status(segment, request)
