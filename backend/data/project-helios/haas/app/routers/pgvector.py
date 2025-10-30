"""
Router para operações de busca semântica com pgvector

Fornece endpoints para:
- Armazenamento de embeddings
- Busca semântica em documentos ANEEL
- Busca de projetos similares
- Verificação de compliance regulatório
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.pgvector_service import PGVectorService

router = APIRouter(
    tags=["pgvector"],
    responses={404: {"description": "Not found"}},
)

# Instância do serviço pgvector
pgvector_service = PGVectorService()


# ============================================================================
# MODELS / SCHEMAS
# ============================================================================


class DocumentEmbeddingRequest(BaseModel):
    """Solicitação para armazenar embedding de documento."""

    document_id: str = Field(..., description="ID único do documento")
    document_type: str = Field(
        ..., description="Tipo: 'regulatory', 'technical', 'guideline'"
    )
    title: str = Field(..., description="Título do documento")
    content: str = Field(..., description="Conteúdo completo do documento")
    embedding: List[float] = Field(
        ..., description="Vetor de embedding (1536 dimensões)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados adicionais"
    )
    source_url: Optional[str] = Field(None, description="URL de origem do documento")


class ProjectEmbeddingRequest(BaseModel):
    """Solicitação para armazenar embedding de projeto."""

    project_id: str = Field(..., description="ID único do projeto")
    ceg: Optional[str] = Field(None, description="Código CEG do projeto")
    embedding: List[float] = Field(
        ..., description="Vetor de embedding (1536 dimensões)"
    )
    project_data: Dict[str, Any] = Field(..., description="Dados completos do projeto")


class RegulatoryEmbeddingRequest(BaseModel):
    """Solicitação para armazenar embedding de regulamentação."""

    regulation_id: str = Field(..., description="ID único da regulamentação")
    regulation_type: str = Field(
        ...,
        description="Tipo: 'aneel_resolution', 'technical_standard', 'legal_requirement'",
    )
    title: str = Field(..., description="Título da regulamentação")
    content: str = Field(..., description="Conteúdo completo")
    embedding: List[float] = Field(
        ..., description="Vetor de embedding (1536 dimensões)"
    )
    applicability_rules: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Regras de aplicabilidade"
    )
    compliance_checks: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Checks de compliance"
    )
    effective_date: Optional[str] = Field(
        None, description="Data de vigência (YYYY-MM-DD)"
    )
    expiry_date: Optional[str] = Field(
        None, description="Data de expiração (YYYY-MM-DD)"
    )


class SemanticSearchRequest(BaseModel):
    """Solicitação de busca semântica."""

    query_embedding: List[float] = Field(..., description="Embedding da query de busca")
    document_type: Optional[str] = Field(
        None, description="Filtrar por tipo de documento"
    )
    limit: int = Field(
        default=10, ge=1, le=50, description="Número máximo de resultados"
    )
    threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Threshold de similaridade"
    )


class SimilarProjectsRequest(BaseModel):
    """Solicitação de busca de projetos similares."""

    query_embedding: List[float] = Field(
        ..., description="Embedding do projeto de referência"
    )
    limit: int = Field(
        default=5, ge=1, le=20, description="Número máximo de projetos similares"
    )
    threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Threshold de similaridade"
    )


class ComplianceCheckRequest(BaseModel):
    """Solicitação de verificação de compliance."""

    project_embedding: List[float] = Field(..., description="Embedding do projeto")
    project_data: Dict[str, Any] = Field(
        ..., description="Dados do projeto para avaliação"
    )


class EmbeddingStatsResponse(BaseModel):
    """Resposta com estatísticas dos embeddings."""

    documents: Dict[str, int] = Field(..., description="Contagem por tipo de documento")
    projects: int = Field(..., description="Número total de projetos")
    regulations: Dict[str, int] = Field(
        ..., description="Contagem por tipo de regulamentação"
    )
    total_embeddings: int = Field(..., description="Total de embeddings armazenados")


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/documents/store", response_model=Dict[str, Any])
async def store_document_embedding(request: DocumentEmbeddingRequest):
    """
    Armazena embedding de documento ANEEL para busca semântica.

    **Uso típico**: Após processar documento com LLM/OpenAI, armazenar o embedding
    para consultas posteriores sobre regulamentações e normas técnicas.
    """
    try:
        success = await pgvector_service.store_document_embedding(
            document_id=request.document_id,
            document_type=request.document_type,
            title=request.title,
            content=request.content,
            embedding=request.embedding,
            metadata=request.metadata,
            source_url=request.source_url,
        )

        if success:
            return {
                "success": True,
                "message": f"Documento {request.document_id} armazenado com sucesso",
                "document_id": request.document_id,
                "document_type": request.document_type,
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao armazenar documento")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/projects/store", response_model=Dict[str, Any])
async def store_project_embedding(request: ProjectEmbeddingRequest):
    """
    Armazena embedding de projeto para busca de similaridade.

    **Uso típico**: Após criar projeto, gerar embedding dos dados do projeto
    para encontrar projetos similares ou casos de uso parecidos.
    """
    try:
        success = await pgvector_service.store_project_embedding(
            project_id=request.project_id,
            ceg=request.ceg,
            embedding=request.embedding,
            project_data=request.project_data,
        )

        if success:
            return {
                "success": True,
                "message": f"Projeto {request.project_id} armazenado com sucesso",
                "project_id": request.project_id,
                "ceg": request.ceg,
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao armazenar projeto")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/regulations/store", response_model=Dict[str, Any])
async def store_regulatory_embedding(request: RegulatoryEmbeddingRequest):
    """
    Armazena embedding de regulamentação para compliance automático.

    **Uso típico**: Processar resoluções ANEEL, normas técnicas e requisitos legais
    para verificação automática de compliance em projetos.
    """
    try:
        success = await pgvector_service.store_regulatory_embedding(
            regulation_id=request.regulation_id,
            regulation_type=request.regulation_type,
            title=request.title,
            content=request.content,
            embedding=request.embedding,
            applicability_rules=request.applicability_rules,
            compliance_checks=request.compliance_checks,
            effective_date=request.effective_date,
            expiry_date=request.expiry_date,
        )

        if success:
            return {
                "success": True,
                "message": f"Regulamentação {request.regulation_id} armazenada com sucesso",
                "regulation_id": request.regulation_id,
                "regulation_type": request.regulation_type,
            }
        else:
            raise HTTPException(
                status_code=500, detail="Erro ao armazenar regulamentação"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/documents/search", response_model=List[Dict[str, Any]])
async def semantic_search_documents(request: SemanticSearchRequest):
    """
    Busca semântica em documentos ANEEL.

    **Exemplo de uso**:
    ```json
    {
      "query_embedding": [0.1, 0.2, ...],
      "document_type": "regulatory",
      "limit": 10,
      "threshold": 0.7
    }
    ```

    **Retorna**: Documentos ordenados por relevância semântica
    """
    try:
        results = await pgvector_service.semantic_search_documents(
            query_embedding=request.query_embedding,
            document_type=request.document_type,
            limit=request.limit,
            threshold=request.threshold,
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro na busca semântica: {str(e)}"
        )


@router.post("/projects/similar", response_model=List[Dict[str, Any]])
async def find_similar_projects(request: SimilarProjectsRequest):
    """
    Encontra projetos similares baseado em embeddings.

    **Uso**: Recomendação de projetos similares para benchmarking,
    análise de padrões ou identificação de casos de uso parecidos.
    """
    try:
        results = await pgvector_service.find_similar_projects(
            query_embedding=request.query_embedding,
            limit=request.limit,
            threshold=request.threshold,
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro na busca de projetos similares: {str(e)}"
        )


@router.post("/compliance/check", response_model=List[Dict[str, Any]])
async def check_regulatory_compliance(request: ComplianceCheckRequest):
    """
    Verifica compliance regulatório usando busca semântica.

    **Processo**:
    1. Busca regulamentações relevantes via similaridade de embeddings
    2. Avalia aplicabilidade baseada em regras do projeto
    3. Executa checks de compliance automatizados
    4. Retorna status detalhado por regulamentação

    **Retorna**: Lista de regulamentações aplicáveis com status de compliance
    """
    try:
        results = await pgvector_service.check_regulatory_compliance(
            project_embedding=request.project_embedding,
            project_data=request.project_data,
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro na verificação de compliance: {str(e)}"
        )


@router.get("/stats", response_model=EmbeddingStatsResponse)
async def get_embedding_stats():
    """
    Retorna estatísticas dos embeddings armazenados.

    **Inclui**:
    - Contagem de documentos por tipo
    - Número total de projetos
    - Contagem de regulamentações por tipo
    - Total geral de embeddings
    """
    try:
        stats = await pgvector_service.get_embedding_stats()
        return EmbeddingStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro obtendo estatísticas: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def health_check():
    """
    Health check do módulo pgvector
    """
    try:
        stats = await pgvector_service.get_embedding_stats()

        return {
            "status": "healthy",
            "module": "pgvector",
            "vector_extension": "enabled",
            "embedding_dimension": 1536,
            "stats": stats,
            "endpoints": {
                "/documents/store": "Armazenar embedding de documento",
                "/projects/store": "Armazenar embedding de projeto",
                "/regulations/store": "Armazenar embedding de regulamentação",
                "/documents/search": "Busca semântica em documentos",
                "/projects/similar": "Encontrar projetos similares",
                "/compliance/check": "Verificar compliance regulatório",
                "/stats": "Estatísticas dos embeddings",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "module": "pgvector",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
