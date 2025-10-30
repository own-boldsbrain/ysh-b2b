from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.auth import User
from app.auth.dependencies import get_current_user
from app.services.data_provider_service import DataProviderService

router = APIRouter()


class DataQuery(BaseModel):
    data_type: str  # bacen, distributor, market, regulatory, compliance
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 100
    include_metadata: bool = True


class DataResponse(BaseModel):
    data_type: str
    records: List[Dict[str, Any]]
    total_count: int
    query_timestamp: datetime
    data_freshness: str  # last_updated info
    metadata: Optional[Dict[str, Any]] = None


@router.post("/query", response_model=DataResponse)
async def query_data(query: DataQuery, current_user: User = Depends(get_current_user)):
    """Query collected data for MCP consumption."""
    try:
        service = DataProviderService()

        # Validate data type
        valid_types = ["bacen", "distributor", "market", "regulatory", "compliance"]
        if query.data_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: {', '.join(valid_types)}",
            )

        # Execute query
        result = await service.query_data(
            data_type=query.data_type,
            start_date=query.start_date,
            end_date=query.end_date,
            filters=query.filters,
            limit=query.limit,
            include_metadata=query.include_metadata,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data query failed: {str(e)}")


@router.get("/types")
async def list_data_types(current_user: User = Depends(get_current_user)):
    """List available data types for MCP consumption."""
    return {
        "data_types": [
            {
                "id": "bacen",
                "name": "Dados Econômicos BACEN",
                "description": "Taxas SELIC, CDI, spreads e indicadores econômicos",
                "update_frequency": "daily",
                "retention_days": 365,
            },
            {
                "id": "distributor",
                "name": "Dados das Concessionárias",
                "description": "Requisitos, prazos e taxas das distribuidoras",
                "update_frequency": "daily",
                "retention_days": 90,
            },
            {
                "id": "market",
                "name": "Inteligência de Mercado",
                "description": "Preços de equipamentos, tendências IRENA, análise de mercado",
                "update_frequency": "weekly",
                "retention_days": 180,
            },
            {
                "id": "regulatory",
                "name": "Atualizações Regulatórias",
                "description": "Mudanças em normas INMETRO/ANEEL, impactos regulatórios",
                "update_frequency": "daily",
                "retention_days": 365,
            },
            {
                "id": "compliance",
                "name": "Dados de Conformidade",
                "description": "Problemas de conformidade, status de certificações",
                "update_frequency": "daily",
                "retention_days": 90,
            },
        ]
    }


@router.get("/health/{data_type}")
async def get_data_health(
    data_type: str, current_user: User = Depends(get_current_user)
):
    """Get health status of specific data type."""
    service = DataProviderService()

    health_info = await service.get_data_health(data_type)

    return health_info


@router.get("/schema/{data_type}")
async def get_data_schema(
    data_type: str, current_user: User = Depends(get_current_user)
):
    """Get schema definition for specific data type."""
    service = DataProviderService()

    schema_info = await service.get_data_schema(data_type)

    return schema_info


@router.post("/subscribe/{data_type}")
async def subscribe_to_data(
    data_type: str,
    webhook_url: str,
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
):
    """Subscribe to real-time data updates via webhook."""
    service = DataProviderService()

    subscription_id = await service.create_subscription(
        data_type=data_type,
        webhook_url=webhook_url,
        filters=filters,
        user_id=current_user.id,
    )

    return {
        "subscription_id": subscription_id,
        "status": "active",
        "data_type": data_type,
        "webhook_url": webhook_url,
    }


@router.delete("/subscribe/{subscription_id}")
async def unsubscribe_from_data(
    subscription_id: str, current_user: User = Depends(get_current_user)
):
    """Unsubscribe from data updates."""
    service = DataProviderService()

    await service.remove_subscription(subscription_id, current_user.id)

    return {"message": "Subscription removed successfully"}


@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get intelligent cache statistics."""
    service = DataProviderService()

    stats = await service.get_cache_stats()

    return stats


@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: str = Query(..., description="Cache key pattern to invalidate"),
    current_user: User = Depends(get_current_user),
):
    """Invalidate cache entries matching pattern."""
    service = DataProviderService()

    invalidated_count = await service.invalidate_cache_pattern(pattern)

    return {
        "message": f"Invalidated {invalidated_count} cache entries",
        "pattern": pattern,
    }


@router.post("/cache/warm")
async def warm_cache(current_user: User = Depends(get_current_user)):
    """Warm up the intelligent cache with frequently accessed data."""
    service = DataProviderService()

    await service.warm_cache()

    return {"message": "Cache warm-up initiated successfully"}


@router.get("/alerts/active")
async def get_active_alerts(
    data_type: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """Get active alerts."""
    service = DataProviderService()

    alerts = await service.get_active_alerts(data_type)

    return {"alerts": alerts}


@router.get("/alerts/history")
async def get_alert_history(
    data_type: Optional[str] = None,
    hours: int = Query(24, description="Hours of history to retrieve"),
    current_user: User = Depends(get_current_user),
):
    """Get alert history."""
    service = DataProviderService()

    alerts = await service.get_alert_history(data_type, hours)

    return {"alerts": alerts}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, current_user: User = Depends(get_current_user)):
    """Resolve an alert."""
    service = DataProviderService()

    await service.resolve_alert(alert_id)

    return {"message": "Alert resolved successfully"}


@router.post("/test/system")
async def test_system(current_user: User = Depends(get_current_user)):
    """Test the complete data provider system."""
    service = DataProviderService()

    # Test data that should trigger alerts
    test_data = {
        "selic_rate": 16.0,  # High rate that should trigger anomaly alert
        "cdi_rate": 15.8,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Process data and check for alerts
    triggered_alerts = await service.notify_subscribers("bacen", test_data)

    # Get cache stats
    cache_stats = await service.get_cache_stats()

    # Get active alerts
    active_alerts = await service.get_active_alerts()

    return {
        "message": "System test completed",
        "triggered_alerts": len(triggered_alerts),
        "cache_stats": cache_stats,
        "active_alerts_count": len(active_alerts),
        "test_data_processed": test_data,
    }
