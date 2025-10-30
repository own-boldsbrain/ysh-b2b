"""
EventRouter - Roteador de eventos entre agentes
Inspirado no padrão pub/sub do Huginn
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from collections import defaultdict


class EventRouter:
    """
    Roteador central de eventos para comunicação A2A.
    
    Inspirado em Huginn Agent communication:
    - Pub/Sub pattern
    - Event filtering
    - Routing rules
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[Callable]] = defaultdict(list)
        self.event_log: List[Dict[str, Any]] = []
        self.total_events_routed = 0

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
        filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> str:
        """Registra handler para tipo de evento"""
        subscription_id = f"sub_{len(self.subscriptions[event_type])}_{datetime.now(timezone.utc).timestamp()}"

        self.subscriptions[event_type].append({
            "id": subscription_id,
            "handler": handler,
            "filter": filter_func,
        })

        return subscription_id

    async def publish(self, event: Dict[str, Any]) -> int:
        """Publica evento para subscribers"""
        event_type = event.get("event_type")
        self.total_events_routed += 1

        # Log evento
        self.event_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": event,
            }
        )

        # Roteia para subscribers
        handlers_called = 0
        for subscription in self.subscriptions.get(event_type, []):
            # Aplica filtro se existe
            if subscription["filter"] and not subscription["filter"](event):
                continue

            # Chama handler
            try:
                await subscription["handler"](event)
                handlers_called += 1
            except Exception as e:
                # Log erro mas continua roteamento
                pass

        return handlers_called

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de roteamento"""
        return {
            "total_events": self.total_events_routed,
            "active_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "event_types": list(self.subscriptions.keys()),
        }
