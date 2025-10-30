import asyncio
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.webhooks import (
    WebhookEvent, WebhookConfig, WebhookDelivery, WebhookPayload
)
from app.models.distributors import Distributor
from app.services.distributor_service import get_distributor_by_id


class WebhookService:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 60  # seconds
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_webhook_config(
        self, config_id: str = "default"
    ) -> Optional[WebhookConfigDB]:
        """Get webhook configuration by ID from database."""
        db: Session = SessionLocal()
        try:
            # First try to get by ID
            config = (
                db.query(WebhookConfigDB)
                .filter(WebhookConfigDB.id == config_id)
                .first()
            )
            if config:
                return config

            # If not found by ID, try to get by name
            config = (
                db.query(WebhookConfigDB)
                .filter(WebhookConfigDB.name == config_id)
                .first()
            )
            return config
        finally:
            db.close()

    def get_all_webhook_configs(self) -> list[WebhookConfig]:
        """Get all active webhook configurations."""
        db: Session = SessionLocal()
        try:
            configs_db = (
                db.query(WebhookConfigDB)
                .filter(WebhookConfigDB.is_active == True)
                .all()
            )
            # Convert to Pydantic models for API
            configs = []
            for config_db in configs_db:
                config = WebhookConfig(
                    url=config_db.url,
                    secret=config_db.secret,
                    events=config_db.event_types or [],
                    headers=None,  # Not stored in DB yet
                )
                configs.append(config)
            return configs
        finally:
            db.close()

    def create_webhook_config(self, config: WebhookConfig) -> WebhookConfig:
        """Create new webhook configuration in database."""
        db: Session = SessionLocal()
        try:
            config_db = WebhookConfigDB(
                name=getattr(config, "name", f"config_{datetime.utcnow().timestamp()}"),
                url=config.url,
                secret=config.secret,
                event_types=config.events,
                is_active=True,
            )
            db.add(config_db)
            db.commit()
            db.refresh(config_db)

            # Return Pydantic model
            return config
        finally:
            db.close()

    def update_webhook_config(
        self, config_id: str, config: WebhookConfig
    ) -> Optional[WebhookConfig]:
        """Update webhook configuration in database."""
        db: Session = SessionLocal()
        try:
            existing_config = (
                db.query(WebhookConfigDB)
                .filter(WebhookConfigDB.id == config_id)
                .first()
            )
            if not existing_config:
                return None

            # Update fields
            existing_config.url = config.url
            existing_config.secret = config.secret
            existing_config.event_types = config.events
            existing_config.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(existing_config)

            # Return updated Pydantic model
            return config
        finally:
            db.close()

    def delete_webhook_config(self, config_id: str) -> bool:
        """Delete webhook configuration from database."""
        db: Session = SessionLocal()
        try:
            config = (
                db.query(WebhookConfigDB)
                .filter(WebhookConfigDB.id == config_id)
                .first()
            )
            if not config:
                return False

            db.delete(config)
            db.commit()
            return True
        finally:
            db.close()

    def save_webhook_delivery(self, delivery: WebhookDeliveryDB) -> WebhookDeliveryDB:
        """Save webhook delivery to database."""
        db: Session = SessionLocal()
        try:
            db.add(delivery)
            db.commit()
            db.refresh(delivery)
            return delivery
        finally:
            db.close()

    def create_webhook_payload(
        self,
        event: WebhookEvent,
        distributor: Distributor,
        connection_request: Optional[Dict[str, Any]] = None,
        status_change: Optional[Dict[str, Any]] = None
    ) -> WebhookPayload:
        """Create standardized webhook payload."""
        payload = WebhookPayload(
            event_type=event.event_type,
            request_id=event.request_id,
            distributor={
                "id": distributor.id,
                "name": distributor.name,
                "code": distributor.code,
                "region": distributor.region
            },
            connection_request=connection_request,
            status_change=status_change,
            timestamp=event.timestamp
        )

        # Add signature for verification
        payload.signature = self._generate_signature(payload.dict())

        return payload

    def _generate_signature(self, payload_dict: Dict[str, Any]) -> str:
        """Generate HMAC signature for webhook verification."""
        config = self.get_webhook_config()
        if not config or not config.secret:
            return ""

        # Remove signature from payload for signing
        payload_copy = payload_dict.copy()
        payload_copy.pop('signature', None)

        # Create signature
        message = json.dumps(payload_copy, sort_keys=True, default=str)
        signature = hmac.new(
            config.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def send_webhook(
        self,
        event: WebhookEvent,
        distributor: Distributor,
        connection_request: Optional[Dict[str, Any]] = None,
        status_change: Optional[Dict[str, Any]] = None,
    ) -> WebhookDeliveryDB:
        """Send webhook notification asynchronously."""
        if not self.session:
            raise RuntimeError(
                "WebhookService must be used as async context manager"
            )

        config = self.get_webhook_config()
        if not config:
            raise ValueError("Webhook configuration not found")

        # Check if event type is enabled
        if event.event_type not in config.event_types:
            delivery = WebhookDeliveryDB(
                config_id=config.id,
                event_type=event.event_type,
                payload={
                    "event": event.dict(),
                    "distributor": distributor.__dict__,
                    "connection_request": connection_request,
                    "status_change": status_change,
                },
                signature="",
                status="skipped",
                attempt_count=0,
                max_attempts=self.max_retries,
                error_message="Event type not enabled",
            )
            return self.save_webhook_delivery(delivery)

        payload = self.create_webhook_payload(
            event, distributor, connection_request, status_change
        )

        timestamp = int(datetime.utcnow().timestamp())
        webhook_id = f"{event.request_id}_{event.event_type}_{timestamp}"

        delivery = WebhookDeliveryDB(
            config_id=config.id,
            event_type=event.event_type,
            payload=payload.dict(),
            signature=payload.signature,
            status="pending",
            attempt_count=0,
            max_attempts=self.max_retries,
        )

        # Send webhook with retry logic
        for attempt in range(self.max_retries):
            try:
                delivery.attempt_count = attempt + 1
                # delivery.last_attempt_at = datetime.utcnow()  # Not in DB model

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "HaaS-Platform/1.0",
                    "X-Webhook-ID": webhook_id,
                    "X-Event-Type": event.event_type
                }

                timeout = aiohttp.ClientTimeout(total=30)
                async with self.session.post(
                    config.url,
                    json=payload.dict(),
                    headers=headers,
                    timeout=timeout
                ) as response:
                    delivery.response_status = response.status

                    if response.status == 200:
                        delivery.status = "delivered"
                        delivery.delivered_at = datetime.utcnow()
                        break
                    else:
                        delivery.status = "failed"
                        delivery.error_message = f"HTTP {response.status}"
                        response_text = await response.text()
                        delivery.response_body = response_text[:1000]  # Limit size

            except Exception as e:
                delivery.status = "failed"
                delivery.error_message = str(e)

            # Schedule next retry if not successful
            if (delivery.status != "delivered" and
                    attempt < self.max_retries - 1):
                delay = timedelta(seconds=self.retry_delay)
                delivery.next_retry_at = datetime.utcnow() + delay
                await asyncio.sleep(self.retry_delay)

        return self.save_webhook_delivery(delivery)

    async def trigger_connection_event(
        self,
        event_type: str,
        request_id: str,
        distributor_id: int,
        connection_request: Optional[Dict[str, Any]] = None,
        status_change: Optional[Dict[str, Any]] = None,
    ) -> Optional[WebhookDeliveryDB]:
        """Trigger webhook for connection-related events."""
        distributor = get_distributor_by_id(distributor_id)
        if not distributor:
            return None

        event = WebhookEvent(
            event_type=event_type,
            request_id=request_id,
            distributor_id=distributor_id,
            distributor_code=distributor.code,
            data={
                "connection_request": connection_request,
                "status_change": status_change
            },
            timestamp=datetime.utcnow()
        )

        async with self as webhook_service:
            delivery = await webhook_service.send_webhook(
                event, distributor, connection_request, status_change
            )

        return delivery


# Global webhook service instance
webhook_service = WebhookService()


async def trigger_webhook_event(
    event_type: str,
    request_id: str,
    distributor_id: int,
    connection_request: Optional[Dict[str, Any]] = None,
    status_change: Optional[Dict[str, Any]] = None,
) -> Optional[WebhookDeliveryDB]:
    """Convenience function to trigger webhook events."""
    return await webhook_service.trigger_connection_event(
        event_type, request_id, distributor_id,
        connection_request, status_change
    )
