import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import aiohttp
from app.services.redis_service import redis_service
from app.services.intelligent_cache_service import IntelligentCacheService
from app.services.intelligent_alert_service import (
    IntelligentAlertService,
    create_default_alert_rules,
)
from app.services.bacen_service import BacenService
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataRecord:
    id: str
    data_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DataSubscription:
    id: str
    data_type: str
    webhook_url: str
    filters: Optional[Dict[str, Any]]
    user_id: int
    created_at: datetime
    last_triggered: Optional[datetime] = None


class DataProviderService:
    """Service for providing data and intelligence to MCPs, tools, and A2A agents."""

    def __init__(self):
        self.redis = redis_service
        self.cache = IntelligentCacheService(redis_service)
        self.alert_service = IntelligentAlertService(redis_service, self)
        self.bacen_service = BacenService()
        self.cache_ttl = 3600  # 1 hour cache

        # Initialize default alert rules
        self._initialize_alert_rules()

    async def query_data(
        self,
        data_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """Query collected data with filtering and pagination."""

        # Try intelligent cache first
        cache_key = self._build_cache_key(
            data_type, start_date, end_date, filters, limit
        )
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Intelligent cache hit for data query: {data_type}")
            return cached_result

        # Query database
        records = await self._query_database(
            data_type, start_date, end_date, filters, limit
        )

        # Build response
        response = {
            "data_type": data_type,
            "records": (
                [record.__dict__ for record in records]
                if include_metadata
                else [record.data for record in records]
            ),
            "total_count": len(records),
            "query_timestamp": datetime.utcnow(),
            "data_freshness": await self._get_data_freshness(data_type),
        }

        if include_metadata:
            response["metadata"] = await self._get_query_metadata(data_type)

        # Cache result with intelligent caching
        await self.cache.set(cache_key, response, ttl=self.cache_ttl)

        # Trigger prefetching for related data
        await self.cache.prefetch_related_data(data_type, filters or {})

        return response

    async def _query_database(
        self,
        data_type: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filters: Optional[Dict[str, Any]],
        limit: int,
    ) -> List[DataRecord]:
        """Query database for specific data type."""
        # This would integrate with actual database models
        # For now, return mock data based on data_type

        mock_records = []

        if data_type == "bacen":
            # Use real BACEN service
            try:
                selic_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.bacen_service.get_selic_rate
                )
                cdi_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.bacen_service.get_cdi_rate
                )

                mock_records = [
                    DataRecord(
                        id="bacen_selic",
                        data_type="bacen",
                        data={
                            "selic_rate": selic_data.get("rate"),
                            "unit": selic_data.get("unit", "percentual ao ano"),
                            "description": selic_data.get("description", "Taxa SELIC"),
                            "timestamp": selic_data.get("timestamp"),
                        },
                        timestamp=datetime.utcnow(),
                        source="bacen_sgs_api",
                        metadata={"confidence": 0.95, "error": selic_data.get("error")},
                    ),
                    DataRecord(
                        id="bacen_cdi",
                        data_type="bacen",
                        data={
                            "cdi_rate": cdi_data.get("rate"),
                            "unit": cdi_data.get("unit", "percentual ao ano"),
                            "description": cdi_data.get("description", "Taxa CDI"),
                            "timestamp": cdi_data.get("timestamp"),
                        },
                        timestamp=datetime.utcnow(),
                        source="bacen_sgs_api",
                        metadata={"confidence": 0.95, "error": cdi_data.get("error")},
                    ),
                ]
            except Exception as e:
                logger.error(f"Error fetching BACEN data: {e}")
                # Fallback to mock data
                mock_records = [
                    DataRecord(
                        id="bacen_001",
                        data_type="bacen",
                        data={
                            "selic_rate": 12.25,
                            "cdi_rate": 12.15,
                            "error": f"Failed to fetch real data: {str(e)}",
                        },
                        timestamp=datetime.utcnow(),
                        source="bacen_api_fallback",
                        metadata={"confidence": 0.0},
                    )
                ]
        elif data_type == "distributor":
            mock_records = [
                DataRecord(
                    id="dist_001",
                    data_type="distributor",
                    data={
                        "distributor": "CEMIG",
                        "requirements": "Documentação completa necessária",
                        "deadlines": "30 dias para análise",
                        "fees": "R$ 500,00",
                    },
                    timestamp=datetime.utcnow(),
                    source="web_scraping",
                    metadata={"region": "MG"},
                )
            ]
        elif data_type == "market":
            mock_records = [
                DataRecord(
                    id="market_001",
                    data_type="market",
                    data={
                        "inverters_avg": 2500.00,
                        "panels_avg": 1800.00,
                        "trends": "Aumento na demanda por painéis bifaciais",
                    },
                    timestamp=datetime.utcnow(),
                    source="market_analysis",
                    metadata={"currency": "BRL"},
                )
            ]

        return mock_records[:limit]

    async def get_data_health(self, data_type: str) -> Dict[str, Any]:
        """Get health status of data type."""
        # Mock health data - would check actual data freshness
        return {
            "data_type": data_type,
            "status": "healthy",
            "last_updated": datetime.utcnow().isoformat(),
            "record_count": 150,
            "update_frequency": "daily",
            "data_quality_score": 0.92,
        }

    async def get_data_schema(self, data_type: str) -> Dict[str, Any]:
        """Get schema definition for data type."""
        schemas = {
            "bacen": {
                "fields": [
                    {
                        "name": "selic_rate",
                        "type": "float",
                        "description": "Taxa SELIC",
                    },
                    {"name": "cdi_rate", "type": "float", "description": "Taxa CDI"},
                    {
                        "name": "spread",
                        "type": "float",
                        "description": "Spread SELIC-CDI",
                    },
                    {"name": "date", "type": "string", "description": "Data da taxa"},
                ]
            },
            "distributor": {
                "fields": [
                    {
                        "name": "distributor",
                        "type": "string",
                        "description": "Nome da distribuidora",
                    },
                    {
                        "name": "requirements",
                        "type": "string",
                        "description": "Requisitos necessários",
                    },
                    {
                        "name": "deadlines",
                        "type": "string",
                        "description": "Prazos estabelecidos",
                    },
                    {
                        "name": "fees",
                        "type": "string",
                        "description": "Taxas aplicáveis",
                    },
                ]
            },
            "market": {
                "fields": [
                    {
                        "name": "inverters_avg",
                        "type": "float",
                        "description": "Preço médio inversores",
                    },
                    {
                        "name": "panels_avg",
                        "type": "float",
                        "description": "Preço médio painéis",
                    },
                    {
                        "name": "trends",
                        "type": "string",
                        "description": "Tendências de mercado",
                    },
                ]
            },
        }

        return schemas.get(data_type, {"fields": []})

    async def create_subscription(
        self,
        data_type: str,
        webhook_url: str,
        filters: Optional[Dict[str, Any]],
        user_id: int,
    ) -> str:
        """Create data subscription for real-time updates."""
        subscription_id = f"sub_{data_type}_{user_id}_{datetime.utcnow().timestamp()}"

        subscription = DataSubscription(
            id=subscription_id,
            data_type=data_type,
            webhook_url=webhook_url,
            filters=filters,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )

        # Store in Redis for now (would be database in production)
        self.redis.set(
            f"subscription:{subscription_id}",
            json.dumps(
                {
                    "id": subscription.id,
                    "data_type": subscription.data_type,
                    "webhook_url": subscription.webhook_url,
                    "filters": subscription.filters,
                    "user_id": subscription.user_id,
                    "created_at": subscription.created_at.isoformat(),
                }
            ),
            ttl=86400 * 30,  # 30 days
        )

        return subscription_id

    async def remove_subscription(self, subscription_id: str, user_id: int):
        """Remove data subscription."""
        # Verify ownership (simplified)
        self.redis.delete(f"subscription:{subscription_id}")

    async def get_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's active subscriptions."""
        # In production, would query database
        # For now, return mock data
        return [
            {
                "id": "sub_bacen_123_1634567890",
                "data_type": "bacen",
                "webhook_url": "https://example.com/webhook",
                "status": "active",
                "created_at": "2025-10-22T10:00:00Z",
            }
        ]

    def _initialize_alert_rules(self):
        """Initialize default alert rules."""
        rules = create_default_alert_rules()
        for rule in rules:
            self.alert_service.add_alert_rule(rule)

    async def notify_subscribers(self, data_type: str, data: Dict[str, Any]):
        """Notify subscribers of new data and process alerts."""
        # Process alerts first
        triggered_alerts = await self.alert_service.process_data_update(data_type, data)

        # Notify regular subscribers
        subscriptions = await self._get_subscriptions_for_type(data_type)

        for subscription in subscriptions:
            # Check filters
            if self._matches_filters(data, subscription.filters):
                await self._send_webhook_notification(subscription.webhook_url, data)

        return triggered_alerts

    async def _get_subscriptions_for_type(
        self, data_type: str
    ) -> List[DataSubscription]:
        """Get subscriptions for data type."""
        # Mock implementation
        return []

    def _matches_filters(
        self, data: Dict[str, Any], filters: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if data matches subscription filters."""
        if not filters:
            return True

        for key, value in filters.items():
            if key not in data or data[key] != value:
                return False
        return True

    async def _send_webhook_notification(self, webhook_url: str, data: Dict[str, Any]):
        """Send webhook notification."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "event_type": "data_update",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                async with session.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent to {webhook_url}")
                    else:
                        logger.error(f"Webhook failed: {response.status}")

        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")

    def _build_cache_key(self, *args) -> str:
        """Build cache key from query parameters."""
        key_parts = [str(arg) for arg in args if arg is not None]
        return f"data_query:{':'.join(key_parts)}"

    async def _get_data_freshness(self, data_type: str) -> str:
        """Get data freshness information."""
        # Mock implementation
        return "Last updated: 2025-10-22T15:30:00Z"

    async def _get_query_metadata(self, data_type: str) -> Dict[str, Any]:
        """Get metadata about the query."""
        return {
            "data_type": data_type,
            "query_version": "1.0",
            "cache_used": True,
            "processing_time_ms": 150,
            "data_source": "mock_database",
        }

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get intelligent cache statistics."""
        return await self.cache.get_cache_stats()

    async def invalidate_cache_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        return await self.cache.invalidate_pattern(pattern)

    async def get_active_alerts(
        self, data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get active alerts."""
        alerts = await self.alert_service.get_active_alerts(data_type)
        return [alert.__dict__ for alert in alerts]

    async def get_alert_history(
        self, data_type: Optional[str] = None, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get alert history."""
        alerts = await self.alert_service.get_alert_history(data_type, hours)
        return [alert.__dict__ for alert in alerts]

    async def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        await self.alert_service.resolve_alert(alert_id)
