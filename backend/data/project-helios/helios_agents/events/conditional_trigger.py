"""
ConditionalTrigger - Sistema de gatilhos condicionais
Inspirado no Huginn TriggerAgent
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from enum import Enum


class TriggerType(Enum):
    """Tipos de gatilho"""
    SCHEDULE = "schedule"  # Tempo/cron
    THRESHOLD = "threshold"  # Valor ultrapassa limite
    CHANGE = "change"  # Mudança de estado
    PATTERN = "pattern"  # Padrão detectado


class ConditionalTrigger:
    """
    Sistema de gatilhos condicionais para automação.
    
    Inspirado em Huginn TriggerAgent:
    - Múltiplos tipos de trigger
    - Condições declarativas
    - Debouncing
    """

    def __init__(self):
        self.triggers: Dict[str, Dict[str, Any]] = {}
        self.trigger_history: List[Dict[str, Any]] = []
        self.last_values: Dict[str, Any] = {}

    def register_trigger(
        self,
        trigger_id: str,
        trigger_type: TriggerType,
        condition: Dict[str, Any],
        action: Callable[[Dict[str, Any]], None],
        debounce_seconds: int = 0
    ) -> None:
        """Registra novo gatilho"""
        self.triggers[trigger_id] = {
            "type": trigger_type,
            "condition": condition,
            "action": action,
            "debounce": debounce_seconds,
            "last_triggered": None,
            "trigger_count": 0,
        }

    async def evaluate(self, context: Dict[str, Any]) -> List[str]:
        """Avalia todos os gatilhos e dispara os ativados"""
        triggered_ids = []

        for trigger_id, trigger in self.triggers.items():
            if self._should_trigger(trigger_id, trigger, context):
                # Executa ação
                await trigger["action"](context)

                # Atualiza metadados
                trigger["last_triggered"] = datetime.now(timezone.utc)
                trigger["trigger_count"] += 1

                # Log
                self.trigger_history.append(
                    {
                        "trigger_id": trigger_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "context": context,
                    }
                )

                triggered_ids.append(trigger_id)

        return triggered_ids

    def _should_trigger(
        self,
        trigger_id: str,
        trigger: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Verifica se gatilho deve ser ativado"""
        # Verifica debounce
        if trigger["last_triggered"] and trigger["debounce"] > 0:
            elapsed = (
                datetime.now(timezone.utc) - trigger["last_triggered"]
            ).total_seconds()
            if elapsed < trigger["debounce"]:
                return False

        # Avalia condição
        condition = trigger["condition"]
        trigger_type = trigger["type"]

        if trigger_type == TriggerType.THRESHOLD:
            return self._evaluate_threshold(trigger_id, condition, context)
        elif trigger_type == TriggerType.CHANGE:
            return self._evaluate_change(trigger_id, condition, context)

        return False

    def _evaluate_threshold(
        self,
        trigger_id: str,
        condition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Avalia gatilho de threshold"""
        field = condition["field"]
        operator = condition["operator"]
        threshold = condition["value"]

        current_value = context.get(field)

        if operator == "gt":
            return current_value > threshold
        elif operator == "lt":
            return current_value < threshold

        return False

    def _evaluate_change(
        self,
        trigger_id: str,
        condition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Avalia gatilho de mudança de estado"""
        field = condition["field"]
        current_value = context.get(field)
        last_value = self.last_values.get(f"{trigger_id}_{field}")

        # Atualiza último valor
        self.last_values[f"{trigger_id}_{field}"] = current_value

        # Detecta mudança
        return last_value is not None and current_value != last_value
