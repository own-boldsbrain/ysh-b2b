from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.models import Distributor as DBDistributor, ConnectionRequest as DBConnectionRequest
from app.models.distributors import (
    Distributor, ConnectionRequest, ConnectionResponse
)
from app.services.distributor_workflow_service import DistributorWorkflowService


# Mock distributor database - replace with real database later
mock_distributors: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "CPFL Energia",
        "code": "CPFL",
        "region": "São Paulo",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 2,
        "name": "Enel São Paulo",
        "code": "ENEL_SP",
        "region": "São Paulo",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 3,
        "name": "CEMIG",
        "code": "CEMIG",
        "region": "Minas Gerais",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
]


# Mock distributor database - replace with real database later
mock_distributors: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "CPFL Energia",
        "code": "CPFL",
        "region": "São Paulo",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 2,
        "name": "Enel São Paulo",
        "code": "ENEL_SP",
        "region": "São Paulo",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 3,
        "name": "CEMIG",
        "code": "CEMIG",
        "region": "Minas Gerais",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
]


def get_distributors(db: Session) -> List[Distributor]:
    """Get all available distributors."""
    db_distributors = db.query(DBDistributor).filter(DBDistributor.status == "active").all()
    return [Distributor(
        id=d.id,
        name=d.name,
        code=d.code,
        region=d.region,
        status=d.status,
        contact_email=d.contact_email,
        contact_phone=d.contact_phone,
        service_area=d.service_area,
        created_at=d.created_at,
        updated_at=d.updated_at
    ) for d in db_distributors]


def get_distributor_by_id(db: Session, distributor_id: int) -> Optional[Distributor]:
    """Get distributor by ID."""
    db_distributor = db.query(DBDistributor).filter(DBDistributor.id == distributor_id).first()
    if not db_distributor:
        return None
    return Distributor(
        id=db_distributor.id,
        name=db_distributor.name,
        code=db_distributor.code,
        region=db_distributor.region,
        status=db_distributor.status,
        contact_email=db_distributor.contact_email,
        contact_phone=db_distributor.contact_phone,
        service_area=db_distributor.service_area,
        created_at=db_distributor.created_at,
        updated_at=db_distributor.updated_at
    )


def get_distributor_by_code(db: Session, code: str) -> Optional[Distributor]:
    """Get distributor by code."""
    db_distributor = db.query(DBDistributor).filter(DBDistributor.code == code).first()
    if not db_distributor:
        return None
    return Distributor(
        id=db_distributor.id,
        name=db_distributor.name,
        code=db_distributor.code,
        region=db_distributor.region,
        status=db_distributor.status,
        contact_email=db_distributor.contact_email,
        contact_phone=db_distributor.contact_phone,
        service_area=db_distributor.service_area,
        created_at=db_distributor.created_at,
        updated_at=db_distributor.updated_at
    )


async def submit_connection_request(
    db: Session,
    distributor_id: int,
    request: ConnectionRequest,
    user_id: Optional[int] = None,
) -> ConnectionResponse:
    """Submit a connection request to a distributor using the workflow service."""
    workflow_service = DistributorWorkflowService()
    return await workflow_service.execute_workflow(db, distributor_id, request, user_id)


def get_connection_status(db: Session, request_id: str) -> Optional[ConnectionResponse]:
    """Get connection request status by ID."""
    db_request = db.query(DBConnectionRequest).filter(DBConnectionRequest.request_id == request_id).first()
    if not db_request:
        return None

    return ConnectionResponse(
        request_id=db_request.request_id,
        status=db_request.status,
        estimated_cost=db_request.estimated_cost,
        estimated_time_days=db_request.estimated_time_days,
        requirements=db_request.requirements or [],
        rejection_reason=db_request.rejection_reason,
        created_at=db_request.created_at,
        updated_at=db_request.updated_at
    )


def validate_connection_request(request: ConnectionRequest) -> Dict[str, Any]:
    """Validate connection request data."""
    workflow_service = DistributorWorkflowService()
    return workflow_service.validate_request(request)
