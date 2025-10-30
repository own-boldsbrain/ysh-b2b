import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    DATA_ANOMALY = "data_anomaly"
    REGULATORY_CHANGE = "regulatory_change"
    MARKET_VOLATILITY = "market_volatility"
    COMPLIANCE_ISSUE = "compliance_issue"
    SYSTEM_HEALTH = "system_health"


@dataclass
class AlertRule:
    id: str
    name: str
    data_type: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    alert_type: AlertType
    description: str
    enabled: bool = True
    cooldown_minutes: int = 60


@dataclass
class Alert:
    id: str
    rule_id: str
    data_type: str
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class IntelligentAlertService:
    """Intelligent alerting system for data anomalies and critical events."""

    def __init__(self, redis_service, data_provider_service):
        self.redis = redis_service
        self.data_provider = data_provider_service
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_channels: List[Callable] = []

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules[rule.id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    def add_notification_channel(self, channel: Callable):
        """Add a notification channel (webhook, email, etc.)."""
        self.notification_channels.append(channel)

    async def process_data_update(self, data_type: str, data: Dict[str, Any]):
        """Process incoming data and check against alert rules."""
        triggered_alerts = []

        for rule in self.alert_rules.values():
            if not rule.enabled or rule.data_type != data_type:
                continue

            # Check cooldown
            if await self._is_rule_on_cooldown(rule.id):
                continue

            # Evaluate condition
            try:
                if rule.condition(data):
                    alert = Alert(
                        id=f"alert_{rule.id}_{datetime.utcnow().timestamp()}",
                        rule_id=rule.id,
                        data_type=data_type,
                        severity=rule.severity,
                        alert_type=rule.alert_type,
                        message=self._generate_alert_message(rule, data),
                        data=data,
                        timestamp=datetime.utcnow(),
                    )

                    triggered_alerts.append(alert)
                    self.active_alerts[alert.id] = alert

                    # Set cooldown
                    await self._set_rule_cooldown(rule.id, rule.cooldown_minutes)

                    logger.warning(f"Alert triggered: {alert.message}")

            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.id}: {str(e)}")

        # Notify channels
        for alert in triggered_alerts:
            await self._notify_channels(alert)

        return triggered_alerts

    async def resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.active_alerts[alert_id].resolved_at = datetime.utcnow()
            logger.info(f"Alert resolved: {alert_id}")

    async def get_active_alerts(self, data_type: Optional[str] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by data type."""
        alerts = list(self.active_alerts.values())

        if data_type:
            alerts = [a for a in alerts if a.data_type == data_type and not a.resolved]

        return alerts

    async def get_alert_history(
        self, data_type: Optional[str] = None, hours: int = 24
    ) -> List[Alert]:
        """Get alert history for the specified time period."""
        # In production, this would query a database
        # For now, return from memory
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        all_alerts = list(self.active_alerts.values())

        filtered_alerts = [
            alert
            for alert in all_alerts
            if alert.timestamp >= cutoff_time
            and (data_type is None or alert.data_type == data_type)
        ]

        return filtered_alerts

    def _generate_alert_message(self, rule: AlertRule, data: Dict[str, Any]) -> str:
        """Generate human-readable alert message."""
        if rule.alert_type == AlertType.DATA_ANOMALY:
            return f"Anomalia detectada em {rule.data_type}: {rule.description}"
        elif rule.alert_type == AlertType.REGULATORY_CHANGE:
            return f"Mudança regulatória detectada: {rule.description}"
        elif rule.alert_type == AlertType.MARKET_VOLATILITY:
            return f"Volatilidade de mercado detectada: {rule.description}"
        elif rule.alert_type == AlertType.COMPLIANCE_ISSUE:
            return f"Problema de conformidade: {rule.description}"
        elif rule.alert_type == AlertType.SYSTEM_HEALTH:
            return f"Problema de saúde do sistema: {rule.description}"
        else:
            return f"Alerta: {rule.description}"

    async def _is_rule_on_cooldown(self, rule_id: str) -> bool:
        """Check if alert rule is on cooldown."""
        cooldown_key = f"alert_cooldown:{rule_id}"
        cooldown_time = self.redis.get(cooldown_key)
        return cooldown_time is not None

    async def _set_rule_cooldown(self, rule_id: str, minutes: int):
        """Set cooldown period for alert rule."""
        cooldown_key = f"alert_cooldown:{rule_id}"
        self.redis.set(cooldown_key, "1", ttl=minutes * 60)

    async def _notify_channels(self, alert: Alert):
        """Notify all registered channels about the alert."""
        for channel in self.notification_channels:
            try:
                await channel(alert)
            except Exception as e:
                logger.error(f"Notification channel error: {str(e)}")


# Predefined alert rules
def create_default_alert_rules() -> List[AlertRule]:
    """Create default alert rules for common scenarios."""

    rules = []

    # BACEN rate anomaly
    def bacen_rate_condition(data: Dict[str, Any]) -> bool:
        selic = data.get("selic_rate", 0)
        return selic > 15.0 or selic < 8.0  # Unusual rate levels

    rules.append(
        AlertRule(
            id="bacen_rate_anomaly",
            name="BACEN Rate Anomaly",
            data_type="bacen",
            condition=bacen_rate_condition,
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.DATA_ANOMALY,
            description="Taxa SELIC fora do intervalo esperado",
            cooldown_minutes=120,
        )
    )

    # Market price volatility
    def market_volatility_condition(data: Dict[str, Any]) -> bool:
        # Check for significant price changes (would compare with historical data)
        return False  # Placeholder - would implement proper volatility detection

    rules.append(
        AlertRule(
            id="market_volatility",
            name="Market Price Volatility",
            data_type="market",
            condition=market_volatility_condition,
            severity=AlertSeverity.MEDIUM,
            alert_type=AlertType.MARKET_VOLATILITY,
            description="Volatilidade significativa detectada nos preços de mercado",
            cooldown_minutes=60,
        )
    )

    # Compliance certificate expiry
    def compliance_expiry_condition(data: Dict[str, Any]) -> bool:
        # Check for expiring certificates
        certificates = data.get("certificates", [])
        expiring = [
            cert for cert in certificates if cert.get("days_to_expiry", 30) < 30
        ]
        return len(expiring) > 0

    rules.append(
        AlertRule(
            id="compliance_expiry",
            name="Certificate Expiry Alert",
            data_type="compliance",
            condition=compliance_expiry_condition,
            severity=AlertSeverity.MEDIUM,
            alert_type=AlertType.COMPLIANCE_ISSUE,
            description="Certificados próximos do vencimento",
            cooldown_minutes=1440,  # 24 hours
        )
    )

    # Regulatory change detection
    def regulatory_change_condition(data: Dict[str, Any]) -> bool:
        # Check for new regulatory documents or changes
        changes = data.get("changes", [])
        return len(changes) > 0

    rules.append(
        AlertRule(
            id="regulatory_change",
            name="Regulatory Change",
            data_type="regulatory",
            condition=regulatory_change_condition,
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.REGULATORY_CHANGE,
            description="Mudanças detectadas em normas regulatórias",
            cooldown_minutes=60,
        )
    )

    return rules
