"""Automation router exposing TypeAgent/AutoGen orchestration endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from app.services import (
    initialize_agent_runtime,
    list_typeagent_actions,
    run_homologation_pilot,
)

router = APIRouter()


class PilotRequest(BaseModel):
    """Request payload to execute a pilot workflow via AutoGen runtime."""

    distributor_code: str = Field(..., description="Código ou slug da distribuidora")
    workflow: str = Field(
        "solicitacao_acesso",
        description="Identificador do workflow habilitado no TaskOrchestrator",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional (login, documentos, schema overrides)",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Sessão TypeAgent pré-existente para compartilhar memória",
    )
    background: bool = Field(
        default=False,
        description="Executa o piloto em background e retorna imediatamente",
    )


@router.get("/automation/actions", tags=["Automation"])
async def automation_actions() -> Dict[str, Any]:
    """List registered TypeAgent actions."""
    await initialize_agent_runtime()
    return list_typeagent_actions()


@router.post("/automation/pilot", tags=["Automation"])
async def automation_pilot(
    request: PilotRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Execute homologation pilot using AutoGen runtime."""
    await initialize_agent_runtime()

    if request.background:
        background_tasks.add_task(
            run_homologation_pilot,
            request.distributor_code,
            request.workflow,
            context=request.context,
            session_id=request.session_id,
        )
        return {"status": "scheduled"}

    result = await run_homologation_pilot(
        request.distributor_code,
        request.workflow,
        context=request.context,
        session_id=request.session_id,
    )
    return {
        "status": "completed",
        "session_id": result.session_id,
        "workflow": result.workflow,
        "distributor_code": result.distributor_code,
        "subtasks": result.subtasks,
    }
