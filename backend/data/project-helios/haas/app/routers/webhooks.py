from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.models.webhooks import WebhookConfig
from app.models.auth import User
from app.auth.dependencies import get_current_admin_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Webhook receiver models
class StatusUpdatePayload(BaseModel):
    project_id: str
    status: str
    client_email: str
    client_name: str
    project_name: str
    distributor: str
    approval_date: str = None
    rejection_reason: str = None
    certificate_url: str = None
    submitted_date: str = None
    estimated_review_time: int = None


class FinancialDataPayload(BaseModel):
    date: str
    selic_rate: float = None
    cdi_rate: float = None
    spread: float = None
    timestamp: str


class MarketDataPayload(BaseModel):
    source: str
    equipment_type: str
    price_data: Dict[str, Any]
    timestamp: str


class RegulatoryUpdatePayload(BaseModel):
    regulation_id: str
    title: str
    publication_date: str
    impact: str
    affected_projects: int
    timestamp: str


class DistributorDataPayload(BaseModel):
    distributor_code: str
    requirements: Dict[str, Any]
    last_updated: str


class ComplianceDataPayload(BaseModel):
    compliance_issues: List[Dict[str, Any]]
    regulation_updates: List[Dict[str, Any]]
    timestamp: str


class NotificationLogPayload(BaseModel):
    type: str
    project_id: str
    client_email: str
    message: str
    priority: str
    timestamp: str


@router.post("/status-update")
async def receive_status_update(payload: StatusUpdatePayload):
    """Receive homologation status updates from Huginn scenarios."""
    # Process status update - log to database, trigger internal actions
    print(f"Received status update: {payload.dict()}")

    # Here you would:
    # 1. Update project status in database
    # 2. Send notifications to relevant teams
    # 3. Trigger downstream processes

    return {
        "status": "received",
        "message": f"Status update processed for project {payload.project_id}",
    }


@router.post("/financial-data")
async def receive_financial_data(payload: FinancialDataPayload):
    """Receive financial data (BACEN rates) from Huginn scenarios."""
    print(f"Received financial data: {payload.dict()}")

    # Here you would:
    # 1. Store financial rates in database
    # 2. Update financial calculations
    # 3. Trigger financial analysis processes

    return {"status": "received", "message": "Financial data processed"}


@router.post("/market-intelligence")
async def receive_market_data(payload: MarketDataPayload):
    """Receive market intelligence data from Huginn scenarios."""
    print(f"Received market data: {payload.dict()}")

    # Here you would:
    # 1. Store market data in database
    # 2. Update pricing models
    # 3. Trigger market analysis

    return {"status": "received", "message": "Market intelligence data processed"}


@router.post("/regulatory-updates")
async def receive_regulatory_updates(payload: RegulatoryUpdatePayload):
    """Receive regulatory updates from Huginn scenarios."""
    print(f"Received regulatory update: {payload.dict()}")

    # Here you would:
    # 1. Store regulatory changes
    # 2. Flag affected projects
    # 3. Send alerts to compliance team

    return {"status": "received", "message": "Regulatory update processed"}


@router.post("/distributor-data")
async def receive_distributor_data(payload: DistributorDataPayload):
    """Receive distributor requirements data from Huginn scenarios."""
    print(f"Received distributor data: {payload.dict()}")

    # Here you would:
    # 1. Update distributor requirements in database
    # 2. Validate existing projects against new requirements
    # 3. Send notifications for requirement changes

    return {"status": "received", "message": "Distributor data processed"}


@router.post("/compliance-status")
async def receive_compliance_data(payload: ComplianceDataPayload):
    """Receive compliance monitoring data from Huginn scenarios."""
    print(f"Received compliance data: {payload.dict()}")

    # Here you would:
    # 1. Log compliance issues
    # 2. Update compliance status
    # 3. Trigger remediation processes

    return {"status": "received", "message": "Compliance data processed"}


@router.post("/notifications/log")
async def log_notification(payload: NotificationLogPayload):
    """Log notifications sent by Huginn scenarios."""
    print(f"Logged notification: {payload.dict()}")

    # Here you would:
    # 1. Store notification log in database
    # 2. Update notification history
    # 3. Generate notification analytics

    return {"status": "received", "message": "Notification logged"}


@router.get("/configs", response_model=List[WebhookConfig])
async def list_webhook_configs(current_user: User = Depends(get_current_admin_user)):
    """List all webhook configurations (admin only)."""
    from app.services.webhook_service import webhook_service

    return webhook_service.get_all_webhook_configs()


@router.post("/configs", response_model=WebhookConfig)
async def create_webhook_config(
    config: WebhookConfig, current_user: User = Depends(get_current_admin_user)
):
    """Create new webhook configuration (admin only)."""
    from app.services.webhook_service import webhook_service

    return webhook_service.create_webhook_config(config)


@router.get("/configs/{config_id}", response_model=WebhookConfig)
async def get_webhook_config(
    config_id: str, current_user: User = Depends(get_current_admin_user)
):
    """Get webhook configuration by ID (admin only)."""
    from app.services.webhook_service import webhook_service

    config = webhook_service.get_webhook_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found",
        )
    return config


@router.put("/configs/{config_id}", response_model=WebhookConfig)
async def update_webhook_config(
    config_id: str,
    config: WebhookConfig,
    current_user: User = Depends(get_current_admin_user),
):
    """Update webhook configuration (admin only)."""
    from app.services.webhook_service import webhook_service

    updated_config = webhook_service.update_webhook_config(config_id, config)
    if not updated_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found",
        )
    return updated_config


@router.delete("/configs/{config_id}")
async def delete_webhook_config(
    config_id: str, current_user: User = Depends(get_current_admin_user)
):
    """Delete webhook configuration (admin only)."""
    from app.services.webhook_service import webhook_service

    success = webhook_service.delete_webhook_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found",
        )
    return {"message": "Webhook configuration deleted"}


@router.post("/test/{config_id}")
async def test_webhook_config(
    config_id: str, current_user: User = Depends(get_current_admin_user)
):
    """Test webhook configuration by sending a test event."""
    from app.services.webhook_service import webhook_service
    from app.models.webhooks import WebhookEvent
    from app.models.distributors import Distributor
    from datetime import datetime

    config = webhook_service.get_webhook_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook configuration not found",
        )

    # Create test distributor
    test_distributor = Distributor(
        id=999,
        name="Test Distributor",
        code="TEST",
        region="Test Region",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Create test event
    test_event = WebhookEvent(
        event_type="test",
        request_id="test_123",
        distributor_id=999,
        distributor_code="TEST",
        data={"message": "Test webhook event"},
        timestamp=datetime.utcnow(),
    )

    # Send test webhook
    try:
        delivery = await webhook_service.send_webhook(test_event, test_distributor)
        return {
            "message": "Test webhook sent",
            "status": delivery.status,
            "response_status": delivery.response_status,
            "error_message": delivery.error_message,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test webhook: {str(e)}",
        )
