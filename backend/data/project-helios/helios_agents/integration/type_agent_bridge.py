"""TypeAgent Bridge - adapts Helios actions to TypeAgent/AutoGen contracts."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set
from time import time

from jsonschema import Draft7Validator, ValidationError

from helios_agents.infrastructure.state_store import StateStore

ActionExecutor = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]

logger = logging.getLogger(__name__)


@dataclass
class TypedActionConfig:
    """Configuration for a typed action exposed to TypeAgent."""

    name: str
    description: str
    input_schema_path: Optional[Path] = None
    output_schema_path: Optional[Path] = None
    target_agent: Optional[str] = None
    capability_tags: Set[str] = field(default_factory=set)
    executor: Optional[ActionExecutor] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    simulate_only: bool = False

    input_schema: Optional[Dict[str, Any]] = field(default=None, init=False)
    output_schema: Optional[Dict[str, Any]] = field(default=None, init=False)
    _input_validator: Optional[Draft7Validator] = field(default=None, init=False)
    _output_validator: Optional[Draft7Validator] = field(default=None, init=False)

    def load_schemas(self) -> None:
        """Load JSON Schemas from disk if provided."""
        if self.input_schema_path and self.input_schema is None:
            self.input_schema = json.loads(self.input_schema_path.read_text(encoding="utf-8"))
            self._input_validator = Draft7Validator(self.input_schema)
        if self.output_schema_path and self.output_schema is None:
            self.output_schema = json.loads(self.output_schema_path.read_text(encoding="utf-8"))
            self._output_validator = Draft7Validator(self.output_schema)

    def validate_input(self, payload: Dict[str, Any]) -> None:
        """Validate incoming payload via JSON Schema if configured."""
        if self._input_validator:
            errors = sorted(self._input_validator.iter_errors(payload), key=lambda e: e.path)
            if errors:
                details = [
                    {
                        "message": error.message,
                        "path": list(error.path),
                        "validator": error.validator,
                    }
                    for error in errors
                ]
                raise ValidationError(
                    f"Payload inválido para ação {self.name}",
                    instance=payload,
                    schema=self.input_schema,
                    path=tuple(details[0]["path"]) if details else (),
                    context=tuple(errors),
                )

    def validate_output(self, response: Dict[str, Any]) -> None:
        """Validate executor response if output schema provided."""
        if self._output_validator:
            errors = sorted(self._output_validator.iter_errors(response), key=lambda e: e.path)
            if errors:
                details = [
                    {
                        "message": error.message,
                        "path": list(error.path),
                        "validator": error.validator,
                    }
                    for error in errors
                ]
                raise ValidationError(
                    f"Resposta inválida da ação {self.name}",
                    instance=response,
                    schema=self.output_schema,
                    path=tuple(details[0]["path"]) if details else (),
                    context=tuple(errors),
                )

    def tool_spec(self) -> Dict[str, Any]:
        """Return metadata for AutoGen tool registration."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": sorted(self.capability_tags),
            "metadata": self.metadata,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class TypeAgentBridge:
    """Bridge responsible for registering typed actions and orchestrating their execution."""

    def __init__(
        self,
        state_store: StateStore,
        schema_root: Optional[str] = None,
    ) -> None:
        self._state_store = state_store
        self._actions: Dict[str, TypedActionConfig] = {}
        self._schema_root = Path(schema_root or "haas/schemas").resolve()
        self._sessions: Dict[str, Dict[str, Any]] = {}

    @property
    def schema_root(self) -> Path:
        return self._schema_root

    def _resolve_schema_path(self, relative_path: str) -> Path:
        candidate = (self._schema_root / relative_path).resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"Schema não encontrado: {relative_path}")
        return candidate

    def register_action(self, config: TypedActionConfig) -> None:
        """Register action configuration with schema validation."""
        if config.name in self._actions:
            logger.debug("Atualizando ação TypeAgent existente: %s", config.name)
        if config.input_schema_path and not config.input_schema_path.is_absolute():
            config.input_schema_path = self._resolve_schema_path(str(config.input_schema_path))
        if config.output_schema_path and not config.output_schema_path.is_absolute():
            config.output_schema_path = self._resolve_schema_path(str(config.output_schema_path))
        config.load_schemas()
        self._actions[config.name] = config
        logger.info("Ação TypeAgent registrada: %s", config.name)

    def list_actions(self) -> List[Dict[str, Any]]:
        """Return catalog of registered actions (for TypeAgent dispatchers)."""
        return [config.tool_spec() for config in self._actions.values()]

    def create_session(self, label: Optional[str] = None) -> str:
        """Create a new TypeAgent session with persisted memory."""
        session_id = label or str(uuid.uuid4())
        self._sessions[session_id] = {"created_at": time(), "events": []}
        logger.debug("Sessão TypeAgent criada: %s", session_id)
        return session_id

    def record_memory(
        self,
        session_id: str,
        event: Dict[str, Any],
        namespace: str = "typeagent",
    ) -> None:
        """Persist structured memory for shared RAG/stateful behaviors."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {"created_at": time(), "events": []}
        self._sessions[session_id]["events"].append(event)
        entity_id = f"{namespace}:{session_id}"
        snapshot = {
            "session_id": session_id,
            "events": self._sessions[session_id]["events"][-50:],
        }
        self._state_store.save_state(entity_id, snapshot, metadata={"namespace": namespace})

    def get_session_memory(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve latest structured memory for session."""
        state = self._state_store.load_state(f"typeagent:{session_id}")
        events = state.get("events", []) if state else []
        return events[-limit:]

    async def execute_action(
        self,
        action_name: str,
        payload: Dict[str, Any],
        *,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate payload and dispatch to registered executor."""
        if action_name not in self._actions:
            raise ValueError(f"Ação TypeAgent não registrada: {action_name}")

        config = self._actions[action_name]
        config.validate_input(payload)

        if config.simulate_only:
            result = {
                "status": "simulated",
                "action": action_name,
                "payload": payload,
                "metadata": metadata or {},
            }
        elif config.executor is None:
            raise RuntimeError(f"Ação {action_name} não possui executor configurado")
        else:
            maybe_coro = config.executor(payload)
            if asyncio.iscoroutine(maybe_coro):
                result = await maybe_coro  # type: ignore[assignment]
            else:
                result = maybe_coro  # type: ignore[assignment]

        if not isinstance(result, dict):
            raise TypeError(
                f"Executor da ação {action_name} retornou tipo inválido: {type(result)!r}"
            )

        config.validate_output(result)

        if session_id:
            self.record_memory(
                session_id,
                {
                    "action": action_name,
                    "payload": payload,
                    "result": result,
                    "metadata": metadata or {},
                },
            )

        return result