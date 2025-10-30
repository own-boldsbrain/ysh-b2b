"""AutoGen runtime facade orchestrating Helios executors."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from helios_agents.integration.type_agent_bridge import TypeAgentBridge
from helios_agents.infrastructure.task_orchestrator import TaskOrchestrator

try:  # AutoGen é opcional
    import autogen  # type: ignore  # pragma: no cover

    AUTOGEN_AVAILABLE = True
except Exception:  # pragma: no cover - ambiente sem AutoGen instalado
    autogen = None  # type: ignore
    AUTOGEN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AutoGenScenarioResult:
    """Structured result for pilot executions."""

    session_id: str
    workflow: str
    distributor_code: str
    subtasks: List[Dict[str, Any]]


class AutoGenRuntime:
    """Coordinates AutoGen agents with Helios TaskOrchestrator via TypeAgentBridge."""

    def __init__(
        self,
        bridge: TypeAgentBridge,
        orchestrator: TaskOrchestrator,
        default_action_map: Optional[Dict[str, str]] = None,
    ) -> None:
        self._bridge = bridge
        self._orchestrator = orchestrator
        self._action_map: Dict[str, str] = default_action_map or {
            "BrowserController": "automation.browser.step",
            "DataExtractor": "automation.data.validate",
            "FileSystemManager": "automation.storage.persist",
        }

    def register_action_mapping(self, agent_type: str, action_name: str) -> None:
        """Map TaskOrchestrator agent types to TypeAgent actions."""
        self._action_map[agent_type] = action_name

    def list_action_mappings(self) -> Dict[str, str]:
        return dict(self._action_map)

    async def run_distributor_workflow(
        self,
        distributor_code: str,
        workflow: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> AutoGenScenarioResult:
        """Execute workflow via TaskOrchestrator and dispatch subtasks through TypeAgent."""
        effective_context = dict(context or {})
        effective_context.setdefault("distributor_code", distributor_code)
        effective_context.setdefault("workflow", workflow)

        session_ref = session_id or self._bridge.create_session()

        plan_subtasks = await self._orchestrator.decompose_task(
            f"{workflow}:{distributor_code}", effective_context
        )

        subtasks_results: List[Dict[str, Any]] = []
        for subtask in plan_subtasks:
            action_name = self._action_map.get(subtask.agent_type)
            if not action_name:
                logger.warning(
                    "Nenhum mapeamento TypeAgent para subtarefa %s (%s)",
                    subtask.id,
                    subtask.agent_type,
                )
                subtasks_results.append(
                    {
                        "subtask_id": subtask.id,
                        "status": "skipped",
                        "reason": "no_action_mapping",
                    }
                )
                continue

            payload = {
                "subtask_id": subtask.id,
                "description": subtask.description,
                "agent_type": subtask.agent_type,
                "parameters": subtask.parameters,
                "context": effective_context,
            }

            try:
                result = await self._bridge.execute_action(
                    action_name,
                    payload,
                    session_id=session_ref,
                    metadata={"subtask": subtask.id, "workflow": workflow},
                )
                subtasks_results.append(
                    {
                        "subtask_id": subtask.id,
                        "status": result.get("status", "completed"),
                        "result": result,
                    }
                )
            except Exception as exc:  # pragma: no cover - logging path
                logger.exception(
                    "Falha ao executar subtarefa %s via ação %s", subtask.id, action_name
                )
                subtasks_results.append(
                    {
                        "subtask_id": subtask.id,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        return AutoGenScenarioResult(
            session_id=session_ref,
            workflow=workflow,
            distributor_code=distributor_code,
            subtasks=subtasks_results,
        )

    def start_background_workflow(
        self,
        distributor_code: str,
        workflow: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> asyncio.Task:
        """Launch workflow execution as asyncio background task."""
        return asyncio.create_task(
            self.run_distributor_workflow(
                distributor_code,
                workflow,
                context=context,
                session_id=session_id,
            )
        )
