"""Router para APIs de validação INMETRO - Prioridade CRÍTICA (NOW Phase)."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.dependencies.inmetro import (
    get_inmetro_pipeline,
    get_inmetro_service,
    get_inmetro_repository,
)
from app.models.inmetro import (
    ValidationStatus,
    ValidationStatusEnum,
    ValidationError as ValError,
)
from validators.inmetro.pipeline import (
    InmetroPipeline,
    InmetroExtractionError,
    EquipmentRequest,
)
from app.tasks.inmetro_tasks import validate_equipment_task, validate_batch_task
from validators.inmetro.validator import DatasheetValidationError

# Metrics decorators
from core.metrics import (
    track_inmetro_validation,
    track_llm_request,
    track_cache_operation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inmetro", tags=["inmetro"])


# ==================== SCHEMAS ====================


class ValidationRequest(BaseModel):
    """Schema para solicitação de validação de equipamento."""

    categoria: str = Field(..., description="Categoria do equipamento (ex: inversores)")
    fabricante: str = Field(..., description="Fabricante do equipamento")
    modelo: str = Field(..., description="Modelo do equipamento")
    registry_id: Optional[str] = Field(None, description="ID de registro (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
                "registry_id": "INV-2024-00123",
            }
        }


class ValidationResponse(BaseModel):
    """Schema de resposta simplificado para validação (wrapper de ValidationStatus)."""

    request_id: str = Field(..., description="ID único da requisição")
    status: str = Field(
        ..., description="Status: pending, in_progress, completed, failed"
    )
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    certification_number: Optional[str] = None
    valid: bool = False
    message: str = Field(..., description="Mensagem descritiva do status")
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_a1b2c3d4",
                "status": "completed",
                "equipment_type": "inversores",
                "manufacturer": "Fronius",
                "model": "Primo 8.2-1",
                "certification_number": "BRA-123456",
                "valid": True,
                "message": "Equipamento certificado encontrado no INMETRO",
                "created_at": "2025-10-14T10:30:00Z",
                "completed_at": "2025-10-14T10:30:15Z",
            }
        }


class BatchValidationRequest(BaseModel):
    """Schema para validação em lote."""

    equipments: List[ValidationRequest] = Field(..., min_length=1, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "equipments": [
                    {
                        "categoria": "inversores",
                        "fabricante": "Fronius",
                        "modelo": "Primo 8.2-1",
                    },
                    {
                        "categoria": "modulos",
                        "fabricante": "Canadian Solar",
                        "modelo": "CS3W-450MS",
                    },
                ]
            }
        }


class CertificateDetail(BaseModel):
    """Schema detalhado de certificado INMETRO."""

    certificate_number: str
    equipment_type: str
    manufacturer: str
    model: str
    power_rating: Optional[str] = None
    valid_until: Optional[datetime] = None
    technical_specs: Dict[str, str] = Field(default_factory=dict)
    inmetro_url: Optional[str] = None
    datasheet_url: Optional[str] = None
    last_verified: datetime


class SearchResult(BaseModel):
    """Schema para resultado de busca."""

    total: int = Field(..., description="Total de resultados encontrados")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    results: List[CertificateDetail]


# ==================== DEPENDÊNCIAS ====================

from app.services.inmetro_store import InmetroValidationStore


# ==================== ENDPOINTS ====================


@router.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=202,
    summary="Validar equipamento no INMETRO",
    description="""
    Valida se um equipamento possui certificação INMETRO válida.
    
    **Processo**:
    1. Cria requisição assíncrona
    2. Consulta portal INMETRO
    3. Extrai dados de certificação
    4. Retorna status imediatamente (202 Accepted)
    
    **Use GET /status/{request_id}** para acompanhar o progresso.
    """,
)
@track_inmetro_validation(
    "inversores"
)  # Default category, will be overridden by actual request
async def validate_equipment(
    request: ValidationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ValidationResponse:
    """
    Inicia validação assíncrona de equipamento no INMETRO.

    Returns:
        ValidationResponse com request_id para acompanhamento
    """
    request_id = f"req_{uuid4().hex[:8]}"

    # Criar registro inicial no ValidationStatus
    status_obj = ValidationStatus(
        request_id=request_id,
        status=ValidationStatusEnum.PENDING,
        equipment_type=request.categoria,
        model=request.modelo,
        manufacturer=request.fabricante,
        valid=False,
        metadata={
            "request": request.dict(),
            "message": "Validação agendada. Use GET /status/{request_id} para acompanhar.",
        },
        created_at=datetime.now(),
    )

    # Salvar no Redis
    InmetroValidationStore.save(request_id, status_obj)

    # Converter para ValidationResponse
    response = ValidationResponse(
        request_id=status_obj.request_id,
        status=status_obj.status.value,
        equipment_type=status_obj.equipment_type,
        model=status_obj.model,
        manufacturer=status_obj.manufacturer,
        certification_number=status_obj.certification_number,
        valid=status_obj.valid,
        message=status_obj.metadata.get("message", ""),
        created_at=status_obj.created_at,
        completed_at=status_obj.completed_at,
    )

    # Agendar processamento com Celery
    task_result = validate_equipment_task.delay(
        request_id=request_id,
        equipment_data=request.dict(),
    )

    logger.info(
        f"Validação agendada no Celery: {request_id} - Task ID: {task_result.id}"
    )

    return response


@router.get(
    "/status/{request_id}",
    response_model=ValidationResponse,
    summary="Consultar status de validação",
    description=(
        "Retorna o status atual de uma validação " "em andamento ou concluída."
    ),
)
async def get_validation_status(
    request_id: str,
    current_user=Depends(get_current_user),
) -> ValidationResponse:
    """
    Consulta status de validação por request_id.

    Args:
        request_id: ID único retornado pelo POST /validate

    Returns:
        ValidationResponse com status atualizado

    Raises:
        HTTPException 404: Requisição não encontrada
    """
    status_obj = InmetroValidationStore.get(request_id)
    if status_obj is None:
        raise HTTPException(
            status_code=404, detail=f"Requisição {request_id} não encontrada"
        )

    # Converter ValidationStatus para ValidationResponse
    return ValidationResponse(
        request_id=status_obj.request_id,
        status=status_obj.status.value,
        equipment_type=status_obj.equipment_type,
        model=status_obj.model,
        manufacturer=status_obj.manufacturer,
        certification_number=status_obj.certification_number,
        valid=status_obj.valid,
        message=status_obj.metadata.get("message", ""),
        created_at=status_obj.created_at,
        completed_at=status_obj.completed_at,
    )


@router.get(
    "/certificate/{certificate_number}",
    response_model=CertificateDetail,
    summary="Detalhes de certificado INMETRO",
    description="Retorna informações detalhadas de um certificado específico.",
)
async def get_certificate_details(
    certificate_number: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CertificateDetail:
    """
    Busca detalhes completos de um certificado INMETRO.

    Args:
        certificate_number: Número do certificado (ex: BRA-123456)

    Returns:
        CertificateDetail com especificações técnicas

    Raises:
        HTTPException 404: Certificado não encontrado
    """
    # TODO: Implementar busca real no repositório
    # Por enquanto retorna mock

    logger.info(f"Buscando certificado: {certificate_number}")

    # Mock de resposta (substituir por query real)
    if certificate_number.startswith("BRA-"):
        return CertificateDetail(
            certificate_number=certificate_number,
            equipment_type="Inversor Fotovoltaico",
            manufacturer="Fronius",
            model="Primo 8.2-1",
            power_rating="8.2 kW",
            valid_until=datetime(2026, 12, 31),
            technical_specs={
                "efficiency": "97.3%",
                "voltage_input": "580-1000 VDC",
                "voltage_output": "220/380 VAC",
            },
            inmetro_url="https://www.inmetro.gov.br/...",
            datasheet_url="https://www.fronius.com/...",
            last_verified=datetime.now(),
        )

    raise HTTPException(
        status_code=404, detail=f"Certificado {certificate_number} não encontrado"
    )


@router.get(
    "/search",
    response_model=SearchResult,
    summary="Buscar equipamentos certificados",
    description="Busca equipamentos certificados por fabricante, modelo ou categoria.",
)
async def search_certified_equipment(
    query: str = Query(..., min_length=3, description="Termo de busca"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    page: int = Query(1, ge=1, description="Página de resultados"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResult:
    """
    Busca equipamentos certificados no INMETRO.

    Args:
        query: Termo de busca (mínimo 3 caracteres)
        category: Categoria para filtrar (opcional)
        page: Número da página
        page_size: Itens por página (máx 100)

    Returns:
        SearchResult com lista de certificados encontrados
    """
    logger.info(f"Busca INMETRO: query='{query}', " f"category={category}, page={page}")

    # TODO: Implementar busca real no repositório
    # Por enquanto retorna mock

    mock_results = [
        CertificateDetail(
            certificate_number="BRA-123456",
            equipment_type="Inversor",
            manufacturer="Fronius",
            model="Primo 8.2-1",
            power_rating="8.2 kW",
            technical_specs={"efficiency": "97.3%"},
            last_verified=datetime.now(),
        ),
        CertificateDetail(
            certificate_number="BRA-789012",
            equipment_type="Módulo Fotovoltaico",
            manufacturer="Canadian Solar",
            model="CS3W-450MS",
            power_rating="450 W",
            technical_specs={"efficiency": "20.9%"},
            last_verified=datetime.now(),
        ),
    ]

    # Filtrar por query (simulado)
    filtered = [r for r in mock_results if query.lower() in r.manufacturer.lower()]

    return SearchResult(
        total=len(filtered),
        page=page,
        page_size=page_size,
        results=filtered[:page_size],
    )


@router.get(
    "/manufacturers",
    response_model=List[str],
    summary="Listar fabricantes certificados",
    description="Retorna lista de fabricantes com equipamentos certificados.",
)
async def list_manufacturers(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    current_user=Depends(get_current_user),
    service=Depends(get_inmetro_service),
) -> List[str]:
    """
    Lista fabricantes certificados no INMETRO.

    Args:
        category: Categoria para filtrar (opcional)

    Returns:
        Lista de nomes de fabricantes
    """
    manufacturers = service.get_manufacturers(categoria=category)

    logger.info(f"Listando {len(manufacturers)} fabricantes")
    return manufacturers


@router.get(
    "/models/{manufacturer}",
    response_model=List[str],
    summary="Listar modelos de um fabricante",
    description="Retorna lista de modelos certificados de um fabricante específico.",
)
async def list_models(
    manufacturer: str,
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    current_user=Depends(get_current_user),
    service=Depends(get_inmetro_service),
) -> List[str]:
    """
    Lista modelos de um fabricante no INMETRO.

    Args:
        manufacturer: Nome do fabricante
        category: Categoria para filtrar (opcional)

    Returns:
        Lista de modelos
    """
    models = service.get_models(fabricante=manufacturer, categoria=category)

    logger.info(f"Listando {len(models)} modelos de {manufacturer}")
    return models


@router.post(
    "/batch",
    response_model=Dict[str, str],
    status_code=202,
    summary="Validação em lote",
    description="""
    Valida múltiplos equipamentos de uma vez (até 50).
    
    Retorna mapa de request_ids para cada equipamento.
    Use GET /status/{request_id} para cada um individualmente.
    """,
)
async def validate_batch(
    batch: BatchValidationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Valida múltiplos equipamentos em lote.

    Args:
        batch: Lista de equipamentos para validar (máx 50)

    Returns:
        Dict mapeando índice → request_id

    Example response:
        {
            "0": "req_a1b2c3d4",
            "1": "req_e5f6g7h8",
            "message": "2 validações agendadas"
        }
    """
    if len(batch.equipments) > 50:
        raise HTTPException(
            status_code=400, detail="Máximo de 50 equipamentos por lote"
        )

    request_ids = {}

    for idx, equipment in enumerate(batch.equipments):
        request_id = f"req_{uuid4().hex[:8]}"

        status_obj = ValidationStatus(
            request_id=request_id,
            status=ValidationStatusEnum.PENDING,
            equipment_type=equipment.categoria,
            model=equipment.modelo,
            manufacturer=equipment.fabricante,
            valid=False,
            metadata={
                "request": equipment.dict(),
                "message": "Validação em lote agendada",
            },
            created_at=datetime.now(),
        )

        InmetroValidationStore.save(request_id, status_obj)
        request_ids[str(idx)] = request_id

        # Agendar cada validação com Celery
        task_result = validate_equipment_task.delay(
            request_id=request_id,
            equipment_data=equipment.dict(),
        )

        logger.info(
            f"Validação em lote agendada no Celery: {request_id} - Task ID: {task_result.id}"
        )

    logger.info(f"Lote de {len(batch.equipments)} validações agendado")

    return {
        **request_ids,
        "message": f"{len(batch.equipments)} validações agendadas",
    }


# ==================== FUNÇÕES AUXILIARES ====================
