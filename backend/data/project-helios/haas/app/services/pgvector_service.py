"""
PGVector Service for HaaS Platform

Gerencia operações de busca semântica e embeddings usando pgvector.
Integra com OpenAI embeddings para documentos ANEEL e projetos.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc
from sqlalchemy.dialects.postgresql import insert

from app.database import get_db

logger = logging.getLogger(__name__)


class PGVectorService:
    """Serviço para operações de busca semântica com pgvector."""

    def __init__(self):
        self.embedding_dimension = 1536  # OpenAI text-embedding-ada-002

    async def store_document_embedding(
        self,
        document_id: str,
        document_type: str,
        title: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
    ) -> bool:
        """
        Armazena embedding de documento ANEEL.

        Args:
            document_id: ID único do documento
            document_type: Tipo ('regulatory', 'technical', 'guideline')
            title: Título do documento
            content: Conteúdo do documento
            embedding: Vetor de embedding
            metadata: Metadados adicionais
            source_url: URL de origem

        Returns:
            True se armazenado com sucesso
        """
        try:
            db = next(get_db())

            # Converte embedding para formato pgvector
            embedding_vector = f"[{','.join(map(str, embedding))}]"

            # Upsert do documento
            stmt = text(
                """
                INSERT INTO aneel_document_embeddings
                (document_id, document_type, title, content, embedding, metadata, source_url)
                VALUES (:document_id, :document_type, :title, :content, :embedding::vector, :metadata, :source_url)
                ON CONFLICT (document_id, document_type)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    source_url = EXCLUDED.source_url,
                    updated_at = CURRENT_TIMESTAMP
            """
            )

            db.execute(
                stmt,
                {
                    "document_id": document_id,
                    "document_type": document_type,
                    "title": title,
                    "content": content,
                    "embedding": embedding_vector,
                    "metadata": metadata or {},
                    "source_url": source_url,
                },
            )

            db.commit()
            logger.info(f"Documento {document_id} armazenado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro armazenando documento {document_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    async def store_project_embedding(
        self,
        project_id: str,
        ceg: Optional[str],
        embedding: List[float],
        project_data: Dict[str, Any],
    ) -> bool:
        """
        Armazena embedding de projeto para busca de similaridade.

        Args:
            project_id: ID único do projeto
            ceg: Código CEG (opcional)
            embedding: Vetor de embedding
            project_data: Dados completos do projeto

        Returns:
            True se armazenado com sucesso
        """
        try:
            db = next(get_db())

            embedding_vector = f"[{','.join(map(str, embedding))}]"

            stmt = text(
                """
                INSERT INTO project_embeddings
                (project_id, ceg, embedding, project_data)
                VALUES (:project_id, :ceg, :embedding::vector, :project_data)
                ON CONFLICT (project_id)
                DO UPDATE SET
                    ceg = EXCLUDED.ceg,
                    embedding = EXCLUDED.embedding,
                    project_data = EXCLUDED.project_data,
                    updated_at = CURRENT_TIMESTAMP
            """
            )

            db.execute(
                stmt,
                {
                    "project_id": project_id,
                    "ceg": ceg,
                    "embedding": embedding_vector,
                    "project_data": project_data,
                },
            )

            db.commit()
            logger.info(f"Projeto {project_id} armazenado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro armazenando projeto {project_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    async def store_regulatory_embedding(
        self,
        regulation_id: str,
        regulation_type: str,
        title: str,
        content: str,
        embedding: List[float],
        applicability_rules: Optional[Dict[str, Any]] = None,
        compliance_checks: Optional[Dict[str, Any]] = None,
        effective_date: Optional[str] = None,
        expiry_date: Optional[str] = None,
    ) -> bool:
        """
        Armazena embedding de regulamentação para compliance automático.

        Args:
            regulation_id: ID único da regulamentação
            regulation_type: Tipo de regulamentação
            title: Título da regulamentação
            content: Conteúdo completo
            embedding: Vetor de embedding
            applicability_rules: Regras de aplicabilidade
            compliance_checks: Checks de compliance automatizados
            effective_date: Data de vigência
            expiry_date: Data de expiração

        Returns:
            True se armazenado com sucesso
        """
        try:
            db = next(get_db())

            embedding_vector = f"[{','.join(map(str, embedding))}]"

            stmt = text(
                """
                INSERT INTO regulatory_embeddings
                (regulation_id, regulation_type, title, content, embedding,
                 applicability_rules, compliance_checks, effective_date, expiry_date)
                VALUES (:regulation_id, :regulation_type, :title, :content, :embedding::vector,
                        :applicability_rules, :compliance_checks, :effective_date, :expiry_date)
                ON CONFLICT (regulation_id)
                DO UPDATE SET
                    regulation_type = EXCLUDED.regulation_type,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    applicability_rules = EXCLUDED.applicability_rules,
                    compliance_checks = EXCLUDED.compliance_checks,
                    effective_date = EXCLUDED.effective_date,
                    expiry_date = EXCLUDED.expiry_date,
                    updated_at = CURRENT_TIMESTAMP
            """
            )

            db.execute(
                stmt,
                {
                    "regulation_id": regulation_id,
                    "regulation_type": regulation_type,
                    "title": title,
                    "content": content,
                    "embedding": embedding_vector,
                    "applicability_rules": applicability_rules or {},
                    "compliance_checks": compliance_checks or {},
                    "effective_date": effective_date,
                    "expiry_date": expiry_date,
                },
            )

            db.commit()
            logger.info(f"Regulamentação {regulation_id} armazenada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro armazenando regulamentação {regulation_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    async def semantic_search_documents(
        self,
        query_embedding: List[float],
        document_type: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica em documentos ANEEL.

        Args:
            query_embedding: Embedding da query
            document_type: Tipo de documento para filtrar
            limit: Número máximo de resultados
            threshold: Threshold de similaridade (0-1)

        Returns:
            Lista de documentos similares ordenados por relevância
        """
        try:
            db = next(get_db())

            embedding_vector = f"[{','.join(map(str, query_embedding))}]"

            query = """
                SELECT
                    document_id,
                    document_type,
                    title,
                    content,
                    metadata,
                    source_url,
                    1 - (embedding <=> :query_embedding::vector) as similarity_score,
                    created_at
                FROM aneel_document_embeddings
                WHERE 1 - (embedding <=> :query_embedding::vector) > :threshold
            """

            params = {"query_embedding": embedding_vector, "threshold": threshold}

            if document_type:
                query += " AND document_type = :document_type"
                params["document_type"] = document_type

            query += " ORDER BY embedding <=> :query_embedding::vector LIMIT :limit"
            params["limit"] = limit

            result = db.execute(text(query), params)
            columns = result.keys()

            results = []
            for row in result.fetchall():
                doc = dict(zip(columns, row))
                # Converte similarity score para float
                doc["similarity_score"] = float(doc["similarity_score"])
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Erro na busca semântica de documentos: {str(e)}")
            return []
        finally:
            db.close()

    async def find_similar_projects(
        self, query_embedding: List[float], limit: int = 5, threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Encontra projetos similares baseado em embeddings.

        Args:
            query_embedding: Embedding do projeto de referência
            limit: Número máximo de projetos similares
            threshold: Threshold de similaridade

        Returns:
            Lista de projetos similares
        """
        try:
            db = next(get_db())

            embedding_vector = f"[{','.join(map(str, query_embedding))}]"

            query = """
                SELECT
                    project_id,
                    ceg,
                    project_data,
                    1 - (embedding <=> :query_embedding::vector) as similarity_score,
                    created_at
                FROM project_embeddings
                WHERE 1 - (embedding <=> :query_embedding::vector) > :threshold
                ORDER BY embedding <=> :query_embedding::vector
                LIMIT :limit
            """

            result = db.execute(
                text(query),
                {
                    "query_embedding": embedding_vector,
                    "threshold": threshold,
                    "limit": limit,
                },
            )

            columns = result.keys()
            results = []

            for row in result.fetchall():
                project = dict(zip(columns, row))
                project["similarity_score"] = float(project["similarity_score"])
                results.append(project)

            return results

        except Exception as e:
            logger.error(f"Erro na busca de projetos similares: {str(e)}")
            return []
        finally:
            db.close()

    async def check_regulatory_compliance(
        self, project_embedding: List[float], project_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Verifica compliance regulatório usando embeddings.

        Args:
            project_embedding: Embedding do projeto
            project_data: Dados do projeto

        Returns:
            Lista de regulamentações aplicáveis com status de compliance
        """
        try:
            db = next(get_db())

            embedding_vector = f"[{','.join(map(str, project_embedding))}]"

            # Busca regulamentações similares
            query = """
                SELECT
                    regulation_id,
                    regulation_type,
                    title,
                    content,
                    applicability_rules,
                    compliance_checks,
                    1 - (embedding <=> :project_embedding::vector) as relevance_score,
                    effective_date,
                    expiry_date
                FROM regulatory_embeddings
                WHERE 1 - (embedding <=> :project_embedding::vector) > 0.6
                ORDER BY embedding <=> :project_embedding::vector
                LIMIT 20
            """

            result = db.execute(text(query), {"project_embedding": embedding_vector})
            columns = result.keys()

            compliance_results = []
            for row in result.fetchall():
                reg = dict(zip(columns, row))
                reg["relevance_score"] = float(reg["relevance_score"])

                # Avalia aplicabilidade baseada nas regras
                applicable = self._evaluate_applicability(
                    reg["applicability_rules"], project_data
                )
                reg["applicable"] = applicable

                if applicable:
                    # Executa checks de compliance
                    compliance_status = self._run_compliance_checks(
                        reg["compliance_checks"], project_data
                    )
                    reg["compliance_status"] = compliance_status

                compliance_results.append(reg)

            return compliance_results

        except Exception as e:
            logger.error(f"Erro na verificação de compliance: {str(e)}")
            return []
        finally:
            db.close()

    def _evaluate_applicability(
        self, rules: Dict[str, Any], project_data: Dict[str, Any]
    ) -> bool:
        """Avalia se uma regulamentação se aplica ao projeto."""
        if not rules:
            return True

        # Implementar lógica de avaliação baseada nas regras
        # Por exemplo: potência > 75kW para mini-GD, etc.
        try:
            potencia = project_data.get("potencia_kw", 0)
            modalidade = project_data.get("modalidade", "").lower()

            if "min_power" in rules and potencia < rules["min_power"]:
                return False
            if "max_power" in rules and potencia > rules["max_power"]:
                return False
            if "modalities" in rules and modalidade not in rules["modalities"]:
                return False

            return True
        except:
            return False

    def _run_compliance_checks(
        self, checks: Dict[str, Any], project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa checks de compliance automatizados."""
        if not checks:
            return {"status": "unknown", "checks": []}

        results = []
        all_passed = True

        # Implementar checks específicos
        # Exemplo: validação de documentação obrigatória
        for check_name, check_config in checks.items():
            passed = self._execute_single_check(check_name, check_config, project_data)
            results.append(
                {"check": check_name, "passed": passed, "config": check_config}
            )
            if not passed:
                all_passed = False

        return {
            "status": "compliant" if all_passed else "non_compliant",
            "checks": results,
        }

    def _execute_single_check(
        self, check_name: str, config: Dict[str, Any], project_data: Dict[str, Any]
    ) -> bool:
        """Executa um check de compliance individual."""
        # Implementar lógica específica para cada tipo de check
        # Por exemplo: verificar se documento obrigatório está presente
        try:
            if check_name == "required_documentation":
                required_docs = config.get("documents", [])
                submitted_docs = project_data.get("submitted_documents", [])
                return all(doc in submitted_docs for doc in required_docs)

            elif check_name == "power_limits":
                potencia = project_data.get("potencia_kw", 0)
                min_power = config.get("min_power", 0)
                max_power = config.get("max_power", float("inf"))
                return min_power <= potencia <= max_power

            # Adicionar mais checks conforme necessário

            return True  # Default: assume compliant se check não reconhecido

        except:
            return False

    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos embeddings armazenados."""
        try:
            db = next(get_db())

            # Conta documentos por tipo
            doc_stats = db.execute(
                text(
                    """
                SELECT document_type, COUNT(*) as count
                FROM aneel_document_embeddings
                GROUP BY document_type
            """
                )
            ).fetchall()

            # Conta projetos
            project_count = db.execute(
                text(
                    """
                SELECT COUNT(*) FROM project_embeddings
            """
                )
            ).scalar()

            # Conta regulamentações por tipo
            reg_stats = db.execute(
                text(
                    """
                SELECT regulation_type, COUNT(*) as count
                FROM regulatory_embeddings
                GROUP BY regulation_type
            """
                )
            ).fetchall()

            return {
                "documents": dict(doc_stats),
                "projects": project_count or 0,
                "regulations": dict(reg_stats),
                "total_embeddings": sum(dict(doc_stats).values())
                + (project_count or 0)
                + sum(dict(reg_stats).values()),
            }

        except Exception as e:
            logger.error(f"Erro obtendo estatísticas: {str(e)}")
            return {}
        finally:
            db.close()
