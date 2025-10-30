"""
StatefulAgent - Nó base para agentes com memória persistente
Inspirado no padrão Huginn Agent com receive()/check()/create_event()
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
import json


class AgentState(Enum):
    """Estados possíveis do agente"""

    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class StatefulAgent:
    """
    Agente base com gerenciamento de estado persistente.

    Baseado no padrão Huginn Agent:
    - receive(events): Processa eventos recebidos
    - check(): Executa verificações periódicas
    - create_event(payload): Gera novos eventos

    Memória persistente inspirada em browser-use Agent:
    - memory: Histórico de contexto
    - next_goal: Objetivo atual
    - actions: Log de ações executadas
    """

    def __init__(
        self, agent_id: str, name: str, config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}

        # Estado interno
        self.state = AgentState.IDLE
        self.memory: List[Dict[str, Any]] = []
        self.next_goal: Optional[str] = None
        self.actions: List[Dict[str, Any]] = []

        # Metadados
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.execution_count = 0

    def receive(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa eventos recebidos de outros agentes.

        Args:
            events: Lista de eventos para processar

        Returns:
            Lista de eventos gerados em resposta
        """
        self.state = AgentState.PROCESSING
        self.execution_count += 1
        output_events = []

        try:
            for event in events:
                # Armazena evento na memória
                self._store_in_memory(event)

                # Processa evento
                result = self._process_event(event)

                if result:
                    output_events.append(result)

            self.state = AgentState.IDLE

        except Exception as e:
            self.state = AgentState.ERROR
            output_events.append(self._create_error_event(str(e)))

        finally:
            self.updated_at = datetime.now(timezone.utc)

        return output_events

    def check(self) -> List[Dict[str, Any]]:
        """
        Executa verificação periódica (scheduled check).

        Returns:
            Lista de eventos gerados pela verificação
        """
        self.state = AgentState.PROCESSING
        output_events = []

        try:
            # Verifica condições de gatilho
            if self._should_trigger():
                event = self._create_trigger_event()
                output_events.append(event)

            self.state = AgentState.IDLE

        except Exception as e:
            self.state = AgentState.ERROR
            output_events.append(self._create_error_event(str(e)))

        finally:
            self.updated_at = datetime.now(timezone.utc)

        return output_events

    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        target_agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Cria um novo evento para ser distribuído.

        Args:
            event_type: Tipo do evento
            payload: Dados do evento
            target_agents: IDs dos agentes destinatários

        Returns:
            Evento formatado
        """
        event = {
            "id": f"{self.agent_id}_{self.execution_count}_{datetime.now(timezone.utc).timestamp()}",
            "source_agent": self.agent_id,
            "event_type": event_type,
            "payload": payload,
            "target_agents": target_agents or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Log da ação
        self._log_action("create_event", event)

        return event

    def get_state(self) -> Dict[str, Any]:
        """Retorna o estado completo do agente para persistência"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "memory": self.memory[-10:],  # Últimas 10 entradas
            "next_goal": self.next_goal,
            "actions": self.actions[-20:],  # Últimas 20 ações
            "execution_count": self.execution_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restaura o estado do agente"""
        self.state = AgentState(state.get("state", AgentState.IDLE.value))
        self.memory = state.get("memory", [])
        self.next_goal = state.get("next_goal")
        self.actions = state.get("actions", [])
        self.execution_count = state.get("execution_count", 0)

    # Métodos privados (a serem sobrescritos por subclasses)

    def _process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Lógica de processamento específica do agente"""
        # Implementação padrão: apenas retorna ACK
        return self.create_event(
            event_type="event_processed",
            payload={"original_event_id": event.get("id")},
        )

    def _should_trigger(self) -> bool:
        """Verifica se deve disparar um evento periódico"""
        return False

    def _create_trigger_event(self) -> Dict[str, Any]:
        """Cria evento de gatilho periódico"""
        return self.create_event(
            event_type="scheduled_trigger",
            payload={"triggered_at": datetime.now(timezone.utc).isoformat()},
        )

    def _store_in_memory(self, event: Dict[str, Any]) -> None:
        """Armazena evento na memória do agente"""
        memory_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event.get("id"),
            "event_type": event.get("event_type"),
            "summary": self._summarize_event(event),
        }
        self.memory.append(memory_entry)

        # Limita memória a 100 entradas
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    def _log_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Registra ação executada"""
        action = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "details": details,
        }
        self.actions.append(action)

        # Limita log a 200 ações
        if len(self.actions) > 200:
            self.actions = self.actions[-200:]

    def _summarize_event(self, event: Dict[str, Any]) -> str:
        """Gera resumo do evento para memória"""
        return f"{event.get('event_type')} from {event.get('source_agent')}"

    def _create_error_event(self, error_message: str) -> Dict[str, Any]:
        """Cria evento de erro"""
        return self.create_event(
            event_type="agent_error",
            payload={
                "error": error_message,
                "agent_state": self.state.value,
            },
        )
