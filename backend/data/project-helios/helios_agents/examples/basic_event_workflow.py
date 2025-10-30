"""
Exemplo básico de workflow com eventos, gatilhos e agregação.

Execute:
  python -m helios_agents.examples.basic_event_workflow
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from helios_agents.events.event_router import EventRouter
from helios_agents.events.conditional_trigger import ConditionalTrigger, TriggerType
from helios_agents.events.aggregator import Aggregator


async def main() -> None:
    router = EventRouter()
    triggers = ConditionalTrigger()
    aggregator = Aggregator(window_size_seconds=60)

    received = []

    async def on_progress_event(event: Dict[str, Any]) -> None:
        received.append(event)
        print(f"[handler] recebido: {event['event_type']} -> {event.get('payload')}")
        aggregator.add_event(event)

    # Inscreve handler para eventos de progresso
    router.subscribe(
        event_type="progress.update",
        handler=on_progress_event,
        filter_func=lambda e: e.get("payload", {}).get("step", 0) >= 1,
    )

    # Registra gatilho: ativa quando progress >= 90
    async def on_high_progress(ctx: Dict[str, Any]) -> None:
        print(f"[trigger] threshold atingido: {ctx}")
        await router.publish(
            {
                "event_type": "progress.threshold_reached",
                "payload": ctx,
                "source_agent": "example.basic",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    triggers.register_trigger(
        trigger_id="progress90",
        trigger_type=TriggerType.THRESHOLD,
        condition={"field": "progress", "operator": "gt", "value": 90},
        action=on_high_progress,
        debounce_seconds=5,
    )

    # Publica eventos simulados de progresso
    for step, progress in enumerate([5, 25, 50, 75, 92, 100], start=1):
        event = {
            "event_type": "progress.update",
            "payload": {"step": step, "progress": progress},
            "source_agent": "example.basic",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await router.publish(event)
        await triggers.evaluate({"progress": progress})

    # Agrega eventos da janela
    aggregated = aggregator.aggregate("progress.update")
    print(f"\n[aggregate] resultados: {aggregated}")


if __name__ == "__main__":
    asyncio.run(main())
