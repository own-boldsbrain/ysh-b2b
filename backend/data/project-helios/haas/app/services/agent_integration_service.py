"""Agent integration service wiring TypeAgent, AutoGen and Helios executors."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from helios_agents import (
    AutoGenRuntime,
    AutoGenScenarioResult,
    BrowserAction,
    BrowserController,
    DataExtractor,
    FileSystemManager,
    StateStore,
    TypeAgentBridge,
    TypedActionConfig,
    StructuredRAGService,
)
from helios_agents.infrastructure.task_orchestrator import TaskOrchestrator, ExecutionMode

from app.config import settings

logger = logging.getLogger(__name__)

STATE_STORE = StateStore(storage_backend="memory")
BROWSER_CONTROLLER = BrowserController(headless=True)
DATA_EXTRACTOR = DataExtractor()
FILE_SYSTEM_MANAGER = FileSystemManager(settings.AGENT_STORAGE_PATH)
TASK_ORCHESTRATOR = TaskOrchestrator(
    execution_mode=ExecutionMode(settings.AGENT_EXECUTION_MODE),
    state_persistence_path=settings.AGENT_STATE_PATH,
    storage_path=settings.AGENT_STORAGE_PATH,
)
TYPE_AGENT_BRIDGE = TypeAgentBridge(STATE_STORE, schema_root=str(Path(__file__).parent.parent.parent / "schemas"))
STRUCTURED_RAG = StructuredRAGService(
    STATE_STORE,
    dataset_root=str(Path(__file__).parent.parent.parent / "aneel_datasets"),
    enable_embeddings=bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip()),
    embedding_service=settings.OPENAI_API_KEY if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() else None
)
AUTOGEN_RUNTIME = AutoGenRuntime(TYPE_AGENT_BRIDGE, TASK_ORCHESTRATOR)

_INITIALIZED = False


async def _execute_browser_step(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute browser actions sequentially via BrowserController."""
    actions = payload.get("parameters", {}).get("actions", [])
    if not isinstance(actions, list) or not actions:
        return {"status": "simulated", "reason": "no_actions"}

    if BROWSER_CONTROLLER.session is None:
        first_url = None
        for action in actions:
            url_candidate = action.get("url") if isinstance(action, dict) else None
            if url_candidate:
                first_url = url_candidate
                break
        try:
            await BROWSER_CONTROLLER.start_session(first_url)
        except RuntimeError as exc:
            logger.warning("Playwright indisponível, retornando simulação: %s", exc)
            return {
                "status": "simulated",
                "details": [
                    {
                        "action": action.get("type") if isinstance(action, dict) else "unknown",
                        "result": {"status": "simulated"},
                    }
                    for action in actions
                ],
            }

    executed = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        action_type = action.get("type", "").lower()
        params = {k: v for k, v in action.items() if k != "type"}
        try:
            browser_action = BrowserAction(action_type)
        except ValueError:
            logger.warning("Ação de browser desconhecida: %s", action_type)
            continue
        result = await BROWSER_CONTROLLER.execute_action(browser_action, params)
        executed.append({"action": action_type, "result": result})

    if BROWSER_CONTROLLER.session:
        await BROWSER_CONTROLLER.close_session()

    return {"status": executed[-1]["result"].get("status", "ok") if executed else "ok", "details": executed}


async def _execute_data_validation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate structured payload using DataExtractor."""
    params = payload.get("parameters", {})
    method = params.get("method", "validate")
    if method == "validate":
        schema = params.get("schema")
        data = params.get("data", {})
        if isinstance(schema, str):
            schema_path = Path(schema)
            if not schema_path.is_absolute():
                schema_path = Path("haas/schemas") / schema
            schema_dict = json.loads(schema_path.read_text(encoding="utf-8"))
        else:
            schema_dict = schema or {}
        result = DATA_EXTRACTOR.validate_against_schema(data, schema_dict)
        status = "valid" if result.get("valid") else "invalid"
        return {"status": status, "errors": result.get("errors", [])}

    if method == "extract_from_html":
        html = params.get("data", {}).get("html", "")
        selectors = params.get("data", {}).get("selectors", {})
        result = DATA_EXTRACTOR.extract_from_html(html, selectors)
        return {"status": result.get("status", "ok"), "metadata": result}

    if method == "extract_from_pdf":
        pdf_path = params.get("data", {}).get("path")
        fields = params.get("data", {}).get("fields", [])
        result = DATA_EXTRACTOR.extract_from_pdf(pdf_path, fields)
        return {"status": result.get("status", "ok"), "metadata": result}

    return {"status": "simulated", "reason": f"unsupported_method:{method}"}


async def _execute_storage_persist(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist documents using FileSystemManager."""
    params = payload.get("parameters", {})
    documents = params.get("documents", [])
    project_id = params.get("project_id", "default_project")
    stored_files = []
    for document in documents:
        if not isinstance(document, dict):
            continue
        filename = document.get("filename", "doc.bin")
        content_b64 = document.get("content", "")
        try:
            content_bytes = base64.b64decode(content_b64)
        except Exception:
            content_bytes = b""
        file_id = FILE_SYSTEM_MANAGER.save_file(
            content_bytes,
            filename,
            project_id,
            metadata=document.get("metadata"),
        )
        stored_files.append({"file_id": file_id, "filename": filename})
    return {"status": "stored", "stored_files": stored_files}


async def _execute_structured_rag_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    query = payload.get("query", "")
    limit = payload.get("limit", 5)
    results = STRUCTURED_RAG.query(query, limit=limit)
    return {
        "results": [entry.to_dict() for entry in results],
        "matched": len(results),
    }


def _register_typeagent_actions() -> None:
    schema_base = Path(__file__).parent.parent.parent / "schemas"
    
    TYPE_AGENT_BRIDGE.register_action(
        TypedActionConfig(
            name="automation.browser.step",
            description="Executa uma sequência de ações Playwright no BrowserController",
            input_schema_path=schema_base / "actions" / "browser_step.schema.json",
            output_schema_path=schema_base / "actions" / "browser_step_output.schema.json",
            executor=_execute_browser_step,
            capability_tags={"browser", "playwright", "automation"},
        )
    )

    TYPE_AGENT_BRIDGE.register_action(
        TypedActionConfig(
            name="automation.data.validate",
            description="Valida ou extrai dados estruturados usando DataExtractor",
            input_schema_path=schema_base / "actions" / "data_validation.schema.json",
            output_schema_path=schema_base / "actions" / "data_validation_output.schema.json",
            executor=_execute_data_validation,
            capability_tags={"validation", "jsonschema", "data"},
        )
    )

    TYPE_AGENT_BRIDGE.register_action(
        TypedActionConfig(
            name="automation.storage.persist",
            description="Persiste documentos no FileSystemManager",
            input_schema_path=schema_base / "actions" / "storage_persist.schema.json",
            output_schema_path=schema_base / "actions" / "storage_persist_output.schema.json",
            executor=_execute_storage_persist,
            capability_tags={"storage", "documents"},
        )
    )

    TYPE_AGENT_BRIDGE.register_action(
        TypedActionConfig(
            name="knowledge.structured_rag.query",
            description="Executa consultas no índice Structured RAG",
            input_schema_path=schema_base / "actions" / "structured_rag_query.schema.json",
            output_schema_path=schema_base / "actions" / "structured_rag_query_output.schema.json",
            executor=_execute_structured_rag_query,
            capability_tags={"rag", "aneel", "knowledge"},
        )
    )

    AUTOGEN_RUNTIME.register_action_mapping("BrowserController", "automation.browser.step")
    AUTOGEN_RUNTIME.register_action_mapping("DataExtractor", "automation.data.validate")
    AUTOGEN_RUNTIME.register_action_mapping("FileSystemManager", "automation.storage.persist")


async def initialize_agent_runtime(force_reindex: bool = False) -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return

    _register_typeagent_actions()

    if force_reindex or not STRUCTURED_RAG.indexed_datasets():
        await asyncio.to_thread(STRUCTURED_RAG.index, force_reindex)

    _INITIALIZED = True
    logger.info("Agent integration runtime initialized")


async def run_homologation_pilot(
    distributor_code: str,
    workflow: str,
    *,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> AutoGenScenarioResult:
    await initialize_agent_runtime()
    result = await AUTOGEN_RUNTIME.run_distributor_workflow(
        distributor_code,
        workflow,
        context=context,
        session_id=session_id,
    )
    return result


def list_typeagent_actions() -> Dict[str, Any]:
    return {action["name"]: action for action in TYPE_AGENT_BRIDGE.list_actions()}


def get_agent_integration_service():
    """Get the agent integration service instance."""
    return AgentIntegrationService()


class AgentIntegrationService:
    """Service class for agent integration operations."""

    async def list_supported_workflows(self, utility_code: str) -> List[str]:
        """List supported workflows for a utility."""
        # For now, return hardcoded workflows based on utility
        workflows = {
            "CPFL": ["solicitacao_acesso", "consulta_status", "upload_documentos"],
            "ENEL": ["solicitacao_acesso", "consulta_status"],
            "CEMIG": ["solicitacao_acesso", "consulta_status"],
        }
        return workflows.get(utility_code.upper(), [])

    async def run_workflow(
        self, utility_code: str, workflow: str, payload: Dict[str, Any]
    ) -> str:
        """Run a workflow for a utility."""
        # Use the existing run_homologation_pilot function
        result = await run_homologation_pilot(
            distributor_code=utility_code,
            workflow=workflow,
            context=payload.get("context"),
            session_id=payload.get("session_id"),
        )
        return result.task_id if hasattr(result, 'task_id') else "task_123"

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        # Mock implementation - in real implementation, this would query the task orchestrator
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": {"percentage": 100},
            "current_subtasks": [],
            "completed_subtasks": [{"id": "step1", "description": "Completed step"}],
            "failed_subtasks": [],
        }
