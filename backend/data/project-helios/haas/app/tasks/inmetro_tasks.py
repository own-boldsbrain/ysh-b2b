"""
Tasks do Celery para processamento assíncrono de validações INMETRO.
"""

import logging
from typing import Dict, List, Optional

from app.core.celery_app import celery_app
from app.dependencies.inmetro import get_inmetro_pipeline
from app.services.inmetro_store import InmetroValidationStore
from app.models.inmetro import ValidationStatus, ValidationStatusEnum
from validators.inmetro.pipeline import EquipmentRequest

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.inmetro_tasks.validate_equipment_task")
def validate_equipment_task(
    self,
    request_id: str,
    equipment_data: Dict[str, str]
) -> Dict[str, str]:
    """
    Task assíncrona para validar um equipamento INMETRO.

    Args:
        request_id: ID único da requisição
        equipment_data: Dados do equipamento (categoria, fabricante, modelo, etc.)

    Returns:
        Dict com status da validação
    """
    try:
        logger.info(f"Iniciando validação assíncrona: {request_id}")

        # Carregar status atual do Redis
        status = InmetroValidationStore.get(request_id)
        if status is None:
            logger.error(f"Status não encontrado no Redis: {request_id}")
            return {"status": "error", "message": "Requisição não encontrada"}

        # Atualizar status para "in_progress"
        status.status = ValidationStatusEnum.IN_PROGRESS
        status.metadata["message"] = "Consultando portal INMETRO..."
        InmetroValidationStore.save(request_id, status)

        # Obter pipeline INMETRO (injetado via DI)
        pipeline = get_inmetro_pipeline()

        # Criar requisição estruturada
        eq_request = EquipmentRequest(
            categoria=equipment_data["categoria"],
            fabricante=equipment_data["fabricante"],
            modelo=equipment_data["modelo"],
            registry_id=equipment_data.get("registry_id"),
        )

        # Processar equipamento
        record = pipeline.process_equipment(eq_request)

        # Atualizar status com resultado
        status.status = ValidationStatusEnum.COMPLETED
        status.valid = True

        cert_info = record.certificacao
        if cert_info and cert_info.get("certificado_numero"):
            status.certification_number = cert_info["certificado_numero"]
        else:
            status.certification_number = "N/A"

        status.metadata["message"] = "Equipamento validado no INMETRO"
        status.metadata["record"] = record.dict() if hasattr(record, "dict") else str(record)
        status.completed_at = record.validado_em if hasattr(record, "validado_em") else None

        # Salvar status final
        InmetroValidationStore.save(request_id, status)

        logger.info(f"Validação concluída: {request_id}")
        return {"status": "completed", "request_id": request_id}

    except Exception as exc:
        logger.exception(f"Erro na validação assíncrona {request_id}")

        # Carregar e atualizar status com erro
        status = InmetroValidationStore.get(request_id)
        if status:
            status.status = ValidationStatusEnum.FAILED
            status.valid = False
            status.metadata["message"] = f"Erro: {str(exc)}"
            status.metadata["error_type"] = type(exc).__name__
            InmetroValidationStore.save(request_id, status)

        return {"status": "error", "request_id": request_id, "error": str(exc)}


@celery_app.task(bind=True, name="app.tasks.inmetro_tasks.validate_batch_task")
def validate_batch_task(
    self,
    request_ids: List[str],
    equipments_data: List[Dict[str, str]]
) -> Dict[str, List[Dict[str, str]]]:
    """
    Task assíncrona para validar múltiplos equipamentos em lote.

    Args:
        request_ids: Lista de IDs únicos das requisições
        equipments_data: Lista de dados dos equipamentos

    Returns:
        Dict com resultados de cada validação
    """
    results = []

    logger.info(f"Iniciando validação em lote: {len(request_ids)} equipamentos")

    for request_id, equipment_data in zip(request_ids, equipments_data):
        try:
            # Reutiliza a task individual
            result = validate_equipment_task.apply(args=[request_id, equipment_data])
            results.append(result.get())

        except Exception as exc:
            logger.exception(f"Erro na validação lote {request_id}")
            results.append({
                "status": "error",
                "request_id": request_id,
                "error": str(exc)
            })

    logger.info(f"Validação em lote concluída: {len(results)} resultados")
    return {"results": results}


@celery_app.task(bind=True, name="app.tasks.inmetro_tasks.invalidate_cache_task")
def invalidate_cache_task(
    self,
    pattern: str
) -> Dict[str, int]:
    """
    Task para invalidar cache Redis por padrão.

    Args:
        pattern: Padrão para invalidar (ex: "inmetro:Fronius:*")

    Returns:
        Dict com número de chaves deletadas
    """
    try:
        from core.cache import invalidate_cache

        deleted = invalidate_cache(pattern)
        logger.info(f"Cache invalidado: {pattern} - {deleted} chaves deletadas")

        return {"deleted_keys": deleted, "pattern": pattern}

    except Exception as exc:
        logger.exception(f"Erro invalidando cache: {pattern}")
        return {"error": str(exc), "pattern": pattern}


@celery_app.task(bind=True, name="app.tasks.inmetro_tasks.health_check_task")
def health_check_task(self) -> Dict[str, str]:
    """
    Task de health check para verificar se o Celery está funcionando.

    Returns:
        Dict com status do health check
    """
    try:
        # Testar conexão com Redis
        from core.cache import redis_client
        redis_client.ping()

        # Testar pipeline INMETRO
        pipeline = get_inmetro_pipeline()
        assert hasattr(pipeline, "process_equipment")

        return {
            "status": "healthy",
            "redis": "connected",
            "inmetro_pipeline": "ready",
            "timestamp": "now"
        }

    except Exception as exc:
        logger.exception("Health check falhou")
        return {
            "status": "unhealthy",
            "error": str(exc),
            "timestamp": "now"
        }