"""
Router para endpoints da API ANEEL
Integra com o ANEEL Data MCP Server via Huginn
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
import httpx

from app.services.aneel_validator_service import ANEELValidatorService

router = APIRouter(
    tags=["aneel"],
    responses={404: {"description": "Not found"}},
)

# Instância do serviço ANEEL
aneel_service = ANEELValidatorService()


# ============================================================================
# MODELS / SCHEMAS
# ============================================================================


class ANEELSyncRequest(BaseModel):
    """Solicitação de sincronização de dados ANEEL"""

    force: bool = Field(
        default=False, description="Forçar atualização mesmo se dados estiverem frescos"
    )
    datasets: Optional[List[str]] = Field(
        default=None,
        description="Lista de datasets específicos para sincronizar (se vazio, sincroniza todos)",
    )


class ANEELSyncResponse(BaseModel):
    """Resposta da sincronização"""

    success: bool
    message: str
    synced_at: datetime
    datasets_updated: int
    details: Dict[str, Any]


class ANEELQueryRequest(BaseModel):
    """Query SQL-like sobre datasets ANEEL"""

    query_type: str = Field(
        ..., description="Tipo de query: gd, tariff, distributor, market"
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict, description="Filtros da query"
    )
    limit: int = Field(default=100, ge=1, le=10000, description="Limite de resultados")
    offset: int = Field(default=0, ge=0, description="Offset para paginação")


class ANEELQueryResponse(BaseModel):
    """Resposta de query"""

    success: bool
    query_type: str
    total_results: int
    returned_results: int
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ProjectValidationRequest(BaseModel):
    """Solicitação de validação de projeto contra base ANEEL"""

    ceg: Optional[str] = Field(None, description="Código CEG do projeto")
    distribuidora: str = Field(..., description="Nome ou código da distribuidora")
    potencia_kw: float = Field(..., description="Potência do projeto em kW")
    modalidade: str = Field(..., description="Micro ou Mini GD")
    fonte: str = Field(default="fotovoltaica", description="Fonte de geração")
    municipio: Optional[str] = Field(None, description="Município do projeto")
    uf: Optional[str] = Field(None, description="UF do projeto")


class ValidationResult(BaseModel):
    """Resultado individual de validação"""

    check: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class ProjectValidationResponse(BaseModel):
    """Resposta de validação de projeto"""

    success: bool
    overall_valid: bool
    validation_checks: List[ValidationResult]
    warnings: List[str]
    timestamp: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/sync", response_model=ANEELSyncResponse)
async def sync_aneel_data(request: ANEELSyncRequest):
    """
    Sincroniza dados ANEEL do HF Dataset para o banco de dados local HaaS

    Este endpoint:
    1. Acessa o dataset fernando-bold/aneel-datasets no Hugging Face
    2. Baixa os CSVs mais recentes (ou apenas os especificados)
    3. Atualiza as tabelas PostgreSQL correspondentes
    4. Retorna estatísticas da sincronização

    **Uso recomendado**: Executar 1x por dia via cron/Huginn
    """
    try:
        # Executa sincronização via serviço
        sync_result = await aneel_service.sync_datasets(
            force=request.force, specific_datasets=request.datasets
        )

        return ANEELSyncResponse(
            success=sync_result["success"],
            message=(
                "Sincronização concluída"
                if sync_result["success"]
                else "Erro na sincronização"
            ),
            synced_at=sync_result.get("synced_at", datetime.utcnow()),
            datasets_updated=sync_result.get("datasets_synced", 0),
            details=sync_result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")


@router.post("/query", response_model=ANEELQueryResponse)
async def query_aneel_data(request: ANEELQueryRequest):
    """
    Executa queries SQL-like sobre os datasets ANEEL

    **Tipos de query disponíveis**:

    - `gd`: Projetos de Geração Distribuída
        - Filtros: `uf`, `distribuidora`, `potencia_min`, `potencia_max`, `modalidade`

    - `tariff`: Tarifas e componentes tarifários
        - Filtros: `distribuidora`, `ano`, `mes`, `classe`

    - `distributor`: Informações de distribuidoras
        - Filtros: `uf`, `nome`, `codigo`

    - `market`: Análise de mercado
        - Filtros: `uf`, `periodo_inicio`, `periodo_fim`

    **Exemplo de uso**:
    ```json
    {
      "query_type": "gd",
      "filters": {
        "uf": "MG",
        "distribuidora": "CEMIG",
        "potencia_min": 75,
        "potencia_max": 5000
      },
      "limit": 100
    }
    ```
    """
    try:
        # Executa query via serviço
        query_result = await aneel_service.execute_query(
            query_type=request.query_type,
            filters=request.filters,
            limit=request.limit,
            offset=request.offset,
        )

        return ANEELQueryResponse(
            success=query_result["success"],
            query_type=query_result["query_type"],
            total_results=query_result["total_results"],
            returned_results=query_result["returned_results"],
            data=query_result["data"],
            metadata=query_result["metadata"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na query: {str(e)}")


@router.post("/validate", response_model=ProjectValidationResponse)
async def validate_project(request: ProjectValidationRequest):
    """
    Valida um projeto contra a base oficial ANEEL

    **Validações executadas**:

    1. **CEG Format**: Valida formato do código CEG (se fornecido)
    2. **Distributor**: Verifica se distribuidora existe na base ANEEL
    3. **Power Range**: Valida faixa de potência (micro: ≤75kW, mini: 75kW-5MW)
    4. **Municipality**: Verifica se município está na área de concessão
    5. **SIGA Cross-reference**: Busca projeto no SIGA (se CEG fornecido)

    **Retorna**:
    - `overall_valid`: True se todas validações passaram
    - `validation_checks`: Lista detalhada de cada validação
    - `warnings`: Avisos não-críticos

    **Exemplo de uso**:
    ```json
    {
      "ceg": "MG.GD.CEMIG-D.00012345",
      "distribuidora": "CEMIG",
      "potencia_kw": 150.5,
      "modalidade": "mini",
      "fonte": "fotovoltaica",
      "municipio": "Belo Horizonte",
      "uf": "MG"
    }
    ```
    """
    try:
        # Converte request para dict para o serviço
        validation_data = {
            "ceg": request.ceg,
            "distribuidora": request.distribuidora,
            "potencia_kw": request.potencia_kw,
            "modalidade": request.modalidade,
            "fonte": request.fonte,
            "municipio": request.municipio,
            "uf": request.uf,
        }

        # Executa validação via serviço
        validation_result = await aneel_service.validate_project(validation_data)

        # Converte resultados para o formato do response
        validation_checks = []
        for check in validation_result["validation_checks"]:
            validation_checks.append(
                ValidationResult(
                    check=check["check"],
                    passed=check["passed"],
                    message=check["message"],
                    details=check.get("details"),
                )
            )

        return ProjectValidationResponse(
            success=validation_result["success"],
            overall_valid=validation_result["overall_valid"],
            validation_checks=validation_checks,
            warnings=validation_result["warnings"],
            timestamp=validation_result["timestamp"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def health_check():
    """
    Health check do módulo ANEEL
    """
    return {
        "status": "healthy",
        "module": "aneel",
        "endpoints": {
            "/sync": "Sincronização de dados do Hugging Face",
            "/query": "Queries SQL-like sobre datasets ANEEL",
            "/validate": "Validação completa de projetos",
        },
        "huggingface_dataset": "fernando-bold/aneel-datasets",
        "service_status": "fully_implemented",
        "timestamp": datetime.utcnow().isoformat(),
    }
