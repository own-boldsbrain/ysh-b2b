"""Workflow models for agent-based operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""

    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class WorkflowRunResponse(BaseModel):
    """Response from running a workflow."""

    task_id: str
    status_url: str


class WorkflowStatusResponse(BaseModel):
    """Response with workflow status."""

    task_id: str
    status: str
    progress: Dict[str, Any]
    current_subtasks: List[Dict[str, Any]]
    completed_subtasks: List[Dict[str, Any]]
    failed_subtasks: List[Dict[str, Any]]