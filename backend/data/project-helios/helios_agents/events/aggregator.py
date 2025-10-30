"""
Aggregator - Agregador de eventos e dados
Inspirado no Huginn DigestAgent
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict


class Aggregator:
    """
    Agregador de eventos para batch processing.
    
    Inspirado em Huginn DigestAgent:
    - Time-window aggregation
    - Event batching
    - Summary generation
    """

    def __init__(self, window_size_seconds: int = 300):
        self.window_size = window_size_seconds
        self.event_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.aggregation_history: List[Dict[str, Any]] = []

    def add_event(self, event: Dict[str, Any]) -> None:
        """Adiciona evento ao buffer de agregação"""
        event_type = event.get("event_type", "default")

        event["received_at"] = datetime.now(timezone.utc).isoformat()
        self.event_buffer[event_type].append(event)

    def aggregate(
        self,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Agrega eventos do buffer"""
        results = []

        event_types = [event_type] if event_type else list(self.event_buffer.keys())

        for et in event_types:
            events = self.event_buffer.get(et, [])

            if not events:
                continue

            # Filtra eventos dentro da janela temporal
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(seconds=self.window_size)

            window_events = [
                e for e in events
                if datetime.fromisoformat(e["received_at"]) > cutoff
            ]

            if window_events:
                aggregated = {
                    "event_type": f"{et}_aggregated",
                    "count": len(window_events),
                    "events": window_events,
                    "summary": self._generate_summary(window_events),
                    "aggregated_at": now.isoformat(),
                }

                results.append(aggregated)

                # Limpa buffer
                self.event_buffer[et] = []

                # Log
                self.aggregation_history.append(aggregated)

        return results

    def _generate_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera resumo dos eventos agregados"""
        return {
            "total_events": len(events),
            "event_types": list(set(e.get("event_type") for e in events)),
            "source_agents": list(set(e.get("source_agent") for e in events)),
        }
