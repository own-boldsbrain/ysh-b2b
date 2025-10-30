from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.distributors import Distributor, ConnectionRequest, ConnectionResponse
from app.models.auth import User
from app.services.distributor_service import (
    get_distributors,
    get_distributor_by_id,
    submit_connection_request,
    get_connection_status,
    validate_connection_request,
)
from app.services.utility_forms_manager import UtilityFormsManager, FormType
from app.services.forms.template_renderer import FormTemplateRenderer
from app.auth.dependencies import get_current_active_user
from app.services.agent_integration_service import get_agent_integration_service
from app.services.swe_agent_integration_service import get_swe_agent_integration_service
from app.models.workflows import (
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStatusResponse,
)

router = APIRouter()

# Instâncias dos serviços
forms_manager = UtilityFormsManager()
template_renderer = FormTemplateRenderer()
agent_service = get_agent_integration_service()
swe_agent_service = get_swe_agent_integration_service()


@router.get("/", response_model=List[Distributor])
async def list_distributors(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """List all available distributors."""
    return get_distributors(db)


@router.get("/{distributor_id}", response_model=Distributor)
async def get_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get distributor by ID."""
    distributor = get_distributor_by_id(db, distributor_id)
    if not distributor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Distributor not found"
        )
    return distributor


@router.post("/{distributor_id}/connection", response_model=ConnectionResponse)
async def submit_connection(
    distributor_id: int,
    request: ConnectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a connection request to a distributor."""
    # Validate the request
    validation = validate_connection_request(request)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation errors: {', '.join(validation['errors'])}",
        )

    try:
        response = await submit_connection_request(
            db, distributor_id, request, current_user.id
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/connection/{request_id}", response_model=ConnectionResponse)
async def get_connection_status_endpoint(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get connection request status."""
    status_response = get_connection_status(db, request_id)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Connection request not found"
        )
    return status_response


@router.get("/validate")
async def validate_endpoint(
    request: ConnectionRequest, current_user: User = Depends(get_current_active_user)
):
    """Validate a connection request without submitting it."""
    return validate_connection_request(request)


# ========================================
# UTILITY FORMS MANAGER ENDPOINTS
# ========================================


@router.get("/{utility_code}/forms", response_model=List[str])
async def get_available_forms(
    utility_code: str, current_user: User = Depends(get_current_active_user)
):
    """Get available form types for a utility company."""
    forms = forms_manager.get_available_forms(utility_code.upper())
    return [form.value for form in forms]


@router.get("/{utility_code}/forms/{form_type}")
async def get_form_definition(
    utility_code: str,
    form_type: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get form definition for a specific utility and form type."""
    try:
        form_enum = FormType(form_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid form type: {form_type}",
        )

    form = forms_manager.get_form(utility_code.upper(), form_enum)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form {form_type} not found for utility {utility_code}",
        )

    # Converte para dict serializável
    return {
        "utility_code": form.utility_code,
        "form_type": form.form_type.value,
        "title": form.title,
        "description": form.description,
        "url": form.url,
        "method": form.method,
        "enctype": form.enctype,
        "fields": [
            {
                "name": field.name,
                "label": field.label,
                "type": field.type.value,
                "required": field.required,
                "placeholder": field.placeholder,
                "help_text": field.help_text,
                "validation": field.validation,
                "options": field.options,
                "max_length": field.max_length,
                "min_value": field.min_value,
                "max_value": field.max_value,
                "mask": field.mask,
                "depends_on": field.depends_on,
            }
            for field in form.fields
        ],
        "attachments": [
            {
                "name": attachment.name,
                "label": attachment.label,
                "required": attachment.required,
                "max_size_mb": attachment.max_size_mb,
                "allowed_types": attachment.allowed_types,
                "help_text": attachment.help_text,
            }
            for attachment in form.attachments
        ],
        "validation_rules": form.validation_rules,
        "quirks": form.quirks,
    }


@router.post("/{utility_code}/forms/{form_type}/validate")
async def validate_form_data(
    utility_code: str,
    form_type: str,
    form_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
):
    """Validate form data against utility-specific rules."""
    try:
        form_enum = FormType(form_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid form type: {form_type}",
        )

    validation_result = forms_manager.validate_form_data(
        utility_code.upper(), form_enum, form_data
    )

    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Form validation failed",
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
            },
        )

    return validation_result


@router.get("/{utility_code}/forms/{form_type}/html", response_class=HTMLResponse)
async def get_form_html(
    utility_code: str,
    form_type: str,
    form_data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Get rendered HTML form for a specific utility and form type."""
    try:
        form_enum = FormType(form_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid form type: {form_type}",
        )

    form = forms_manager.get_form(utility_code.upper(), form_enum)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form {form_type} not found for utility {utility_code}",
        )

    try:
        html_content = template_renderer.render_form(form, form_data)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rendering form template: {str(e)}",
        )


@router.get("/forms/supported-utilities")
async def get_supported_utilities(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of supported utility companies."""
    return {
        "utilities": list(forms_manager.forms.keys()),
        "description": "Supported utility companies for form management",
    }


# ========================================
# WORKFLOWS POR DISTRIBUIDORA (AGENTES)
# ========================================


@router.get("/{utility_code}/workflows", response_model=List[str])
async def list_workflows(
    utility_code: str, current_user: User = Depends(get_current_active_user)
):
    """Lista workflows suportados para a distribuidora."""
    return agent_service.list_supported_workflows(utility_code)


@router.post(
    "/{utility_code}/workflows/{workflow}/run",
    response_model=WorkflowRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def run_workflow(
    utility_code: str,
    workflow: str,
    payload: WorkflowRunRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Dispara execução de um workflow por distribuidora via agentes."""
    task_id = await agent_service.run_workflow(
        utility_code=utility_code, workflow=workflow, payload=payload.model_dump()
    )
    return WorkflowRunResponse(
        task_id=task_id, status_url=f"/distributors/workflows/tasks/{task_id}"
    )


@router.get("/workflows/tasks/{task_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    task_id: str, current_user: User = Depends(get_current_active_user)
):
    """Consulta status/progresso de um workflow em execução."""
    report = await agent_service.get_task_status(task_id)
    return WorkflowStatusResponse(
        task_id=report["task_id"],
        status=report["status"],
        progress=report.get("progress", {}),
        current_subtasks=report.get("current_subtasks", []),
        completed_subtasks=report.get("completed_subtasks", []),
        failed_subtasks=report.get("failed_subtasks", []),
    )


# ========================================
# SWE-AGENT CODE GENERATION ENDPOINTS
# ========================================


@router.get("/workflows/code-gen/tasks", response_model=List[str])
async def list_code_generation_tasks(
    current_user: User = Depends(get_current_active_user),
):
    """Lista tarefas suportadas de geração de código."""
    return await swe_agent_service.list_supported_code_tasks()


@router.post(
    "/workflows/code-gen/generate",
    response_model=WorkflowRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_code(
    task_type: str,
    specifications: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
):
    """Inicia geração de código via SWE-agent."""
    task_id = await swe_agent_service.generate_code(
        task_type=task_type, specifications=specifications
    )
    return WorkflowRunResponse(
        task_id=task_id, status_url=f"/distributors/workflows/code-gen/tasks/{task_id}"
    )


@router.post("/workflows/code-gen/validate")
async def validate_generated_script(
    script_code: str,
    current_user: User = Depends(get_current_active_user),
):
    """Valida sintaxe de script gerado."""
    result = await swe_agent_service.validate_script(script_code)
    if result["status"] == "invalid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Script validation failed",
                "errors": result.get("errors", []),
            },
        )
    return result


@router.post("/workflows/code-gen/execute")
async def execute_data_script(
    script_path: str,
    parameters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Executa script de extração de dados."""
    result = await swe_agent_service.execute_script(
        script_path=script_path, parameters=parameters
    )
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Script execution failed: {result.get('reason', 'unknown error')}",
        )
    return result


@router.get(
    "/workflows/code-gen/tasks/{task_id}", response_model=WorkflowStatusResponse
)
async def get_code_generation_status(
    task_id: str, current_user: User = Depends(get_current_active_user)
):
    """Consulta status de tarefa de geração de código."""
    report = await swe_agent_service.get_task_status(task_id)
    return WorkflowStatusResponse(
        task_id=report["task_id"],
        status=report["status"],
        progress=report.get("progress", {}),
        current_subtasks=report.get("current_subtasks", []),
        completed_subtasks=report.get("completed_subtasks", []),
        failed_subtasks=report.get("failed_subtasks", []),
    )
