"""Router para APIs de monitoramento - HaaS Platform."""

from __future__ import annotations

import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.auth import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ==================== ENUMS ====================

class ServiceStatus(str, Enum):
    """Status de serviços."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class AlertSeverity(str, Enum):
    """Severidade de alertas."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MetricPeriod(str, Enum):
    """Períodos de métricas."""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"


# ==================== SCHEMAS ====================

class ServiceHealth(BaseModel):
    """Health check de um serviço."""
    name: str
    status: ServiceStatus
    latency_ms: Optional[float] = None
    message: str
    last_checked: datetime


class DashboardMetrics(BaseModel):
    """Métricas do dashboard em tempo real."""
    uptime_seconds: float
    total_requests: int
    requests_per_minute: float
    avg_latency_ms: float
    error_rate_pct: float
    active_users: int
    services: List[ServiceHealth]
    active_alerts: int
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "uptime_seconds": 86400,
                "total_requests": 152340,
                "requests_per_minute": 42.5,
                "avg_latency_ms": 125.3,
                "error_rate_pct": 0.8,
                "active_users": 15,
                "services": [
                    {
                        "name": "PostgreSQL",
                        "status": "healthy",
                        "latency_ms": 12.5,
                        "message": "Connected",
                        "last_checked": "2025-10-14T10:30:00Z"
                    }
                ],
                "active_alerts": 2,
                "timestamp": "2025-10-14T10:30:00Z"
            }
        }


class MetricDataPoint(BaseModel):
    """Ponto de dados de métrica."""
    timestamp: datetime
    value: float
    label: Optional[str] = None


class HistoricalMetrics(BaseModel):
    """Métricas históricas."""
    period: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    total_errors: int
    error_rate_pct: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    requests_by_endpoint: Dict[str, int]
    latency_over_time: List[MetricDataPoint]
    requests_over_time: List[MetricDataPoint]


class Alert(BaseModel):
    """Alerta de monitoramento."""
    id: str
    severity: AlertSeverity
    title: str
    description: str
    service: str
    metric: str
    threshold: float
    current_value: float
    triggered_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


class ProjectStatus(str, Enum):
    """Status de projetos."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    INSTALLED = "installed"


class ProjectMetrics(BaseModel):
    """Métricas de um projeto."""

    total_power_kwp: float
    estimated_generation_kwh_month: float
    equipment_count: int
    inmetro_certified_equipment_pct: float
    validation_score: Optional[float] = None
    last_updated: datetime


class ProjectSummary(BaseModel):
    """Resumo de projeto para listagem."""

    id: str
    name: str
    client_name: str
    status: ProjectStatus
    location: str
    distributor: str
    created_at: datetime
    updated_at: datetime
    metrics: ProjectMetrics


class ProjectDetail(BaseModel):
    """Detalhes completos de um projeto."""

    id: str
    name: str
    client_name: str
    client_cpf_cnpj: str
    status: ProjectStatus
    location: Dict[str, str]  # address, city, state, zip_code
    distributor: str
    installation_type: str
    connection_type: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    metrics: ProjectMetrics
    equipments: List[Dict]  # Lista simplificada de equipamentos
    documents_generated: int
    last_document_generated: Optional[datetime] = None


class ProjectsListResponse(BaseModel):
    """Resposta paginada de projetos."""

    total: int
    page: int
    page_size: int
    total_pages: int
    projects: List[ProjectSummary]
    filters_applied: Dict[str, str]


class SystemStatistics(BaseModel):
    """Estatísticas abrangentes do sistema."""

    total_projects: int
    projects_by_status: Dict[str, int]
    total_power_installed_kwp: float
    avg_project_power_kwp: float
    total_users: int
    active_users_today: int
    documents_generated_today: int
    documents_generated_month: int
    inmetro_validations_today: int
    inmetro_validations_month: int
    avg_response_time_ms: float
    error_rate_pct: float
    top_distributors: List[Dict[str, Union[str, int]]]
    equipment_stats: Dict[str, int]
    generated_at: datetime


# ==================== HELPER FUNCTIONS ====================

def get_system_metrics() -> Dict:
    """Coleta métricas do sistema."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available_gb": memory.available / (1024**3),
        "disk_percent": disk.percent,
        "disk_free_gb": disk.free / (1024**3)
    }


def check_service_health(
    service_name: str,
    db: Optional[Session] = None
) -> ServiceHealth:
    """Verifica health de um serviço."""
    if service_name == "PostgreSQL" and db:
        try:
            from sqlalchemy import text
            start = datetime.utcnow()
            db.execute(text("SELECT 1"))
            latency = (datetime.utcnow() - start).total_seconds() * 1000

            return ServiceHealth(
                name="PostgreSQL",
                status=ServiceStatus.HEALTHY,
                latency_ms=round(latency, 2),
                message="Database connection healthy",
                last_checked=datetime.utcnow()
            )
        except Exception as e:
            return ServiceHealth(
                name="PostgreSQL",
                status=ServiceStatus.DOWN,
                message=f"Database error: {str(e)}",
                last_checked=datetime.utcnow()
            )

    elif service_name == "Redis":
        # TODO: Implementar check Redis
        return ServiceHealth(
            name="Redis",
            status=ServiceStatus.HEALTHY,
            latency_ms=5.2,
            message="Cache operational",
            last_checked=datetime.utcnow()
        )

    elif service_name == "InmetroCrawler":
        # TODO: Implementar check InmetroCrawler
        return ServiceHealth(
            name="InmetroCrawler",
            status=ServiceStatus.HEALTHY,
            latency_ms=250.0,
            message="Crawler operational",
            last_checked=datetime.utcnow()
        )

    return ServiceHealth(
        name=service_name,
        status=ServiceStatus.DOWN,
        message="Service not found",
        last_checked=datetime.utcnow()
    )


def generate_mock_projects() -> List[ProjectSummary]:
    """Gera projetos mock para demonstração."""
    now = datetime.utcnow()

    projects = [
        ProjectSummary(
            id="proj_001",
            name="Sistema Solar Residencial 8kWp",
            client_name="João Silva",
            status=ProjectStatus.APPROVED,
            location="Belo Horizonte, MG",
            distributor="CEMIG",
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=2),
            metrics=ProjectMetrics(
                total_power_kwp=8.0,
                estimated_generation_kwh_month=960,
                equipment_count=18,
                inmetro_certified_equipment_pct=100.0,
                validation_score=95.5,
                last_updated=now - timedelta(days=2),
            ),
        ),
        ProjectSummary(
            id="proj_002",
            name="Instalação Comercial 25kWp",
            client_name="Empresa XYZ Ltda",
            status=ProjectStatus.UNDER_REVIEW,
            location="São Paulo, SP",
            distributor="CPFL",
            created_at=now - timedelta(days=15),
            updated_at=now - timedelta(hours=6),
            metrics=ProjectMetrics(
                total_power_kwp=25.0,
                estimated_generation_kwh_month=3125,
                equipment_count=55,
                inmetro_certified_equipment_pct=95.0,
                validation_score=88.2,
                last_updated=now - timedelta(hours=6),
            ),
        ),
        ProjectSummary(
            id="proj_003",
            name="Sistema Rural 15kWp",
            client_name="Fazenda ABC",
            status=ProjectStatus.SUBMITTED,
            location="Uberlândia, MG",
            distributor="CEMIG",
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(hours=12),
            metrics=ProjectMetrics(
                total_power_kwp=15.0,
                estimated_generation_kwh_month=1875,
                equipment_count=33,
                inmetro_certified_equipment_pct=90.0,
                validation_score=None,
                last_updated=now - timedelta(hours=12),
            ),
        ),
        ProjectSummary(
            id="proj_004",
            name="Condomínio Solar 50kWp",
            client_name="Condomínio XYZ",
            status=ProjectStatus.DRAFT,
            location="Rio de Janeiro, RJ",
            distributor="Light",
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(hours=1),
            metrics=ProjectMetrics(
                total_power_kwp=50.0,
                estimated_generation_kwh_month=6250,
                equipment_count=110,
                inmetro_certified_equipment_pct=85.0,
                validation_score=None,
                last_updated=now - timedelta(hours=1),
            ),
        ),
        ProjectSummary(
            id="proj_005",
            name="Microgeração 3kWp",
            client_name="Maria Santos",
            status=ProjectStatus.REJECTED,
            location="Salvador, BA",
            distributor="Coelba",
            created_at=now - timedelta(days=45),
            updated_at=now - timedelta(days=10),
            metrics=ProjectMetrics(
                total_power_kwp=3.0,
                estimated_generation_kwh_month=375,
                equipment_count=7,
                inmetro_certified_equipment_pct=100.0,
                validation_score=78.5,
                last_updated=now - timedelta(days=10),
            ),
        ),
    ]

    return projects


def get_mock_project_detail(project_id: str) -> Optional[ProjectDetail]:
    """Retorna detalhes mock de um projeto específico."""
    projects = generate_mock_projects()
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        return None

    # Equipamentos mock
    equipments = [
        {
            "type": "panel",
            "manufacturer": "Canadian Solar",
            "model": "CS3W-450MS",
            "quantity": 18,
            "power_w": 450,
            "inmetro_certified": True,
        },
        {
            "type": "inverter",
            "manufacturer": "SMA",
            "model": "Sunny Tripower 8000TL",
            "quantity": 1,
            "power_w": 8000,
            "inmetro_certified": True,
        },
    ]

    return ProjectDetail(
        id=project.id,
        name=project.name,
        client_name=project.client_name,
        client_cpf_cnpj="123.456.789-00",
        status=project.status,
        location={
            "address": "Rua das Flores, 123",
            "city": project.location.split(", ")[0],
            "state": project.location.split(", ")[1],
            "zip_code": "30000-000",
        },
        distributor=project.distributor,
        installation_type="residencial",
        connection_type="monofásico",
        created_at=project.created_at,
        updated_at=project.updated_at,
        created_by="user@example.com",
        metrics=project.metrics,
        equipments=equipments,
        documents_generated=2,
        last_document_generated=datetime.utcnow() - timedelta(days=1),
    )


def generate_mock_statistics() -> SystemStatistics:
    """Gera estatísticas mock do sistema."""
    projects = generate_mock_projects()

    # Calcular estatísticas
    total_projects = len(projects)
    projects_by_status = {}
    total_power = 0.0

    for project in projects:
        status = project.status.value
        projects_by_status[status] = projects_by_status.get(status, 0) + 1
        total_power += project.metrics.total_power_kwp

    return SystemStatistics(
        total_projects=total_projects,
        projects_by_status=projects_by_status,
        total_power_installed_kwp=round(total_power, 1),
        avg_project_power_kwp=round(total_power / total_projects, 1),
        total_users=45,
        active_users_today=12,
        documents_generated_today=8,
        documents_generated_month=156,
        inmetro_validations_today=34,
        inmetro_validations_month=1247,
        avg_response_time_ms=145.8,
        error_rate_pct=0.7,
        top_distributors=[
            {"name": "CEMIG", "projects": 2, "power_kwp": 23.0},
            {"name": "CPFL", "projects": 1, "power_kwp": 25.0},
            {"name": "Light", "projects": 1, "power_kwp": 50.0},
            {"name": "Coelba", "projects": 1, "power_kwp": 3.0},
        ],
        equipment_stats={
            "panels_validated": 223,
            "inverters_validated": 45,
            "certificates_issued": 198,
            "pending_validations": 12,
        },
        generated_at=datetime.utcnow(),
    )


# ==================== ENDPOINTS ====================

@router.get(
    "/dashboard",
    response_model=DashboardMetrics,
    summary="Dashboard em tempo real",
    description="""
    Retorna métricas do dashboard em tempo real.

    **Inclui:**
    - Uptime do sistema
    - Total de requests e taxa atual (req/min)
    - Latência média e taxa de erro
    - Status de serviços (PostgreSQL, Redis, InmetroCrawler)
    - Número de alertas ativos

    Atualizar a cada 30 segundos para dados em tempo real.
    """
)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> DashboardMetrics:
    """
    Retorna métricas do dashboard.

    Requires: Admin ou Distributor role
    """
    # Coletar métricas do sistema
    # system_metrics = get_system_metrics()  # TODO: usar quando implementar alertas de sistema

    # Check de serviços
    services = [
        check_service_health("PostgreSQL", db),
        check_service_health("Redis"),
        check_service_health("InmetroCrawler")
    ]

    # TODO: Buscar métricas reais do banco/Redis
    # Por enquanto retorna dados mock
    uptime = 86400  # 24 horas em segundos

    return DashboardMetrics(
        uptime_seconds=uptime,
        total_requests=152340,
        requests_per_minute=42.5,
        avg_latency_ms=125.3,
        error_rate_pct=0.8,
        active_users=15,
        services=services,
        active_alerts=2,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/metrics",
    response_model=HistoricalMetrics,
    summary="Métricas históricas",
    description="""
    Retorna métricas históricas para análise de performance.

    **Períodos disponíveis:**
    - `1h`: Última hora (granularidade 1min)
    - `24h`: Últimas 24 horas (granularidade 5min)
    - `7d`: Últimos 7 dias (granularidade 1h)
    - `30d`: Últimos 30 dias (granularidade 6h)

    **Métricas:**
    - Volume de requests por endpoint
    - Taxa de erro ao longo do tempo
    - Latência P50/P95/P99
    - Séries temporais para gráficos
    """
)
async def get_historical_metrics(
    period: MetricPeriod = Query(
        MetricPeriod.DAY,
        description="Período de métricas"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> HistoricalMetrics:
    """
    Retorna métricas históricas.

    Args:
        period: Período de análise (1h, 24h, 7d, 30d)
    """
    logger.info(f"Fetching metrics for period: {period.value}")

    # Calcular timestamps
    end_time = datetime.utcnow()
    if period == MetricPeriod.HOUR:
        start_time = end_time - timedelta(hours=1)
    elif period == MetricPeriod.DAY:
        start_time = end_time - timedelta(days=1)
    elif period == MetricPeriod.WEEK:
        start_time = end_time - timedelta(days=7)
    else:  # MONTH
        start_time = end_time - timedelta(days=30)

    # TODO: Buscar métricas reais do banco/Redis
    # Por enquanto retorna dados mock
    mock_latency_data = [
        MetricDataPoint(
            timestamp=start_time + timedelta(minutes=i*15),
            value=100 + (i % 5) * 10,
            label=f"t+{i*15}min"
        )
        for i in range(10)
    ]

    mock_requests_data = [
        MetricDataPoint(
            timestamp=start_time + timedelta(minutes=i*15),
            value=500 + (i % 3) * 100,
            label=f"t+{i*15}min"
        )
        for i in range(10)
    ]

    return HistoricalMetrics(
        period=period.value,
        start_time=start_time,
        end_time=end_time,
        total_requests=12345,
        total_errors=98,
        error_rate_pct=0.79,
        latency_p50_ms=95.3,
        latency_p95_ms=245.8,
        latency_p99_ms=412.5,
        requests_by_endpoint={
            "/api/inmetro/validate": 5432,
            "/api/inmetro/search": 3210,
            "/api/inmetro/certificate/{id}": 2103,
            "/api/inmetro/batch": 890,
            "/auth/login": 710
        },
        latency_over_time=mock_latency_data,
        requests_over_time=mock_requests_data
    )


@router.get(
    "/alerts",
    response_model=AlertsResponse,
    summary="Alertas ativos",
    description="""
    Retorna lista de alertas ativos no sistema.

    **Severidades:**
    - `critical`: Requer ação imediata (sistema em risco)
    - `warning`: Requer atenção (degradação de performance)
    - `info`: Informativo (eventos normais)

    **Tipos de alerta:**
    - Taxa de erro > 5%
    - Latência P95 > 2s
    - Uso de disco > 80%
    - Uso de memória > 85%
    - Pool de conexões > 90%
    - Rate limit violations
    """
)
async def get_active_alerts(
    severity: Optional[AlertSeverity] = Query(
        None,
        description="Filtrar por severidade"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> AlertsResponse:
    """
    Retorna alertas ativos.

    Args:
        severity: Filtrar por severidade (optional)
    """
    logger.info(f"Fetching alerts, severity filter: {severity}")

    # TODO: Buscar alertas reais do banco
    # Por enquanto retorna dados mock
    all_alerts = generate_mock_alerts()

    # Filtrar por severidade se especificado
    if severity:
        filtered_alerts = [
            a for a in all_alerts if a.severity == severity
        ]
    else:
        filtered_alerts = all_alerts

    # Contar por severidade
    critical_count = sum(
        1 for a in all_alerts if a.severity == AlertSeverity.CRITICAL
    )
    warning_count = sum(
        1 for a in all_alerts if a.severity == AlertSeverity.WARNING
    )
    info_count = sum(
        1 for a in all_alerts if a.severity == AlertSeverity.INFO
    )

    return AlertsResponse(
        total=len(all_alerts),
        critical=critical_count,
        warning=warning_count,
        info=info_count,
        alerts=filtered_alerts
    )


@router.get(
    "/projects",
    response_model=ProjectsListResponse,
    summary="Listar projetos do usuário",
    description="""
    Lista projetos do usuário atual com filtros e paginação.

    **Filtros disponíveis:**
    - `status`: Filtrar por status (draft, submitted, under_review, approved, rejected, installed)
    - `distributor`: Filtrar por concessionária
    - `date_from`: Projetos criados após esta data (YYYY-MM-DD)
    - `date_to`: Projetos criados antes desta data (YYYY-MM-DD)
    - `min_power`: Potência mínima em kWp
    - `max_power`: Potência máxima em kWp

    **Ordenação:**
    - `created_at`: Data de criação (padrão: desc)
    - `updated_at`: Data de atualização
    - `name`: Nome do projeto
    - `power`: Potência instalada

    **Paginação:**
    - `page`: Página atual (padrão: 1)
    - `page_size`: Itens por página (padrão: 20, máximo: 100)
    """,
)
async def get_user_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filtrar por status"),
    distributor: Optional[str] = Query(None, description="Filtrar por concessionária"),
    date_from: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    min_power: Optional[float] = Query(None, description="Potência mínima (kWp)"),
    max_power: Optional[float] = Query(None, description="Potência máxima (kWp)"),
    sort_by: str = Query("created_at", description="Campo para ordenação"),
    sort_order: str = Query("desc", description="Ordem: asc ou desc"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectsListResponse:
    """
    Lista projetos do usuário com filtros e paginação.

    Args:
        status: Filtrar por status do projeto
        distributor: Filtrar por concessionária
        date_from: Data inicial de criação
        date_to: Data final de criação
        min_power: Potência mínima
        max_power: Potência máxima
        sort_by: Campo para ordenação
        sort_order: Ordem da ordenação
        page: Página atual
        page_size: Itens por página
    """
    logger.info(f"Listing projects for user {current_user.email}, page {page}")

    # TODO: Buscar projetos reais do banco
    # Por enquanto retorna dados mock
    all_projects = generate_mock_projects()

    # Aplicar filtros
    filtered_projects = all_projects

    if status:
        filtered_projects = [p for p in filtered_projects if p.status == status]

    if distributor:
        filtered_projects = [
            p for p in filtered_projects if p.distributor == distributor
        ]

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            filtered_projects = [
                p for p in filtered_projects if p.created_at >= from_date
            ]
        except ValueError:
            pass  # Ignorar filtro inválido

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            filtered_projects = [
                p for p in filtered_projects if p.created_at <= to_date
            ]
        except ValueError:
            pass  # Ignorar filtro inválido

    if min_power is not None:
        filtered_projects = [
            p for p in filtered_projects if p.metrics.total_power_kwp >= min_power
        ]

    if max_power is not None:
        filtered_projects = [
            p for p in filtered_projects if p.metrics.total_power_kwp <= max_power
        ]

    # Ordenação
    reverse = sort_order.lower() == "desc"
    if sort_by == "created_at":
        filtered_projects.sort(key=lambda p: p.created_at, reverse=reverse)
    elif sort_by == "updated_at":
        filtered_projects.sort(key=lambda p: p.updated_at, reverse=reverse)
    elif sort_by == "name":
        filtered_projects.sort(key=lambda p: p.name.lower(), reverse=reverse)
    elif sort_by == "power":
        filtered_projects.sort(key=lambda p: p.metrics.total_power_kwp, reverse=reverse)

    # Paginação
    total = len(filtered_projects)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_projects = filtered_projects[start_idx:end_idx]

    total_pages = (total + page_size - 1) // page_size

    # Filtros aplicados
    filters_applied = {}
    if status:
        filters_applied["status"] = status.value
    if distributor:
        filters_applied["distributor"] = distributor
    if date_from:
        filters_applied["date_from"] = date_from
    if date_to:
        filters_applied["date_to"] = date_to
    if min_power is not None:
        filters_applied["min_power"] = str(min_power)
    if max_power is not None:
        filters_applied["max_power"] = str(max_power)

    return ProjectsListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        projects=paginated_projects,
        filters_applied=filters_applied,
    )


@router.get(
    "/projects/{project_id}",
    response_model=ProjectDetail,
    summary="Detalhes de projeto específico",
    description="""
    Retorna detalhes completos de um projeto específico.

    **Inclui:**
    - Informações básicas do projeto
    - Dados do cliente
    - Localização e concessionária
    - Métricas técnicas (potência, geração estimada)
    - Lista de equipamentos
    - Status de documentos gerados
    - Histórico de validações

    **Métricas calculadas:**
    - Pontuação de validação INMETRO
    - Percentual de equipamentos certificados
    - Status de conformidade técnica
    """,
)
async def get_project_detail(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectDetail:
    """
    Retorna detalhes completos de um projeto.

    Args:
        project_id: ID único do projeto
    """
    logger.info(f"Fetching project detail: {project_id}")

    # TODO: Buscar projeto real do banco
    # Por enquanto retorna dados mock
    project_detail = get_mock_project_detail(project_id)

    if not project_detail:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Projeto {project_id} não encontrado"
        )

    return project_detail


@router.get(
    "/statistics",
    response_model=SystemStatistics,
    summary="Estatísticas abrangentes do sistema",
    description="""
    Retorna estatísticas abrangentes do sistema HaaS.

    **Métricas incluídas:**
    - **Projetos**: Total, por status, potência instalada média
    - **Usuários**: Total cadastrados, ativos hoje
    - **Documentos**: Gerados hoje/mês
    - **Validações INMETRO**: Realizadas hoje/mês
    - **Performance**: Tempo médio de resposta, taxa de erro
    - **Distribuidoras**: Top concessionárias por projetos
    - **Equipamentos**: Estatísticas de validação

    **Atualização:** Dados atualizados em tempo real
    """,
)
async def get_system_statistics(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> SystemStatistics:
    """
    Retorna estatísticas abrangentes do sistema.
    """
    logger.info("Fetching system statistics")

    # TODO: Calcular estatísticas reais do banco
    # Por enquanto retorna dados mock
    return generate_mock_statistics()
