"""
Serviço de integração INMETRO - Issue #2
Serviço com FastAPI Dependency Injection e Redis cache
"""

import logging
from typing import List, Optional

from fastapi import Depends

from validators.inmetro.pipeline import (
    InmetroPipeline,
    EquipmentRequest,
)
from validators.inmetro.models import EquipmentRecord, EquipmentBatch
from core.cache import cache_inmetro_result, invalidate_cache

# Metrics decorators
from core.metrics import track_llm_request, track_cache_operation

logger = logging.getLogger(__name__)


class InmetroService:
    """
    Serviço para validação INMETRO usando FastAPI Dependency Injection.

    Funcionalidades:
    - Pipeline completo (crawl → extract → validate)
    - Cache Redis com TTL 24h (@cache_inmetro_result)
    - Repository PostgreSQL para persistência
    """

    def __init__(self, pipeline: InmetroPipeline = Depends(get_inmetro_pipeline)):
        """
        Inicializa serviço com pipeline injetado.

        Args:
            pipeline: InmetroPipeline configurado via DI
        """
        self.pipeline = pipeline
        logger.info("InmetroService inicializado com FastAPI DI")

    @cache_inmetro_result(ttl=86400)  # 24 horas
    def validate_equipment(
        self,
        categoria: str,
        fabricante: str,
        modelo: str,
        registry_id: Optional[str] = None,
    ) -> dict:
        """
        Valida equipamento no INMETRO com cache Redis.

        Args:
            categoria: Tipo de equipamento (ex: inversores)
            fabricante: Fabricante
            modelo: Modelo
            registry_id: ID de registro opcional

        Returns:
            Dict com dados do EquipmentRecord

        Cache:
            TTL de 24h no Redis
            Key: inmetro:{categoria}:{fabricante}:{modelo}
        """
        logger.info(f"Validando equipamento: {categoria} - {fabricante} {modelo}")

        request = EquipmentRequest(
            categoria=categoria,
            fabricante=fabricante,
            modelo=modelo,
            registry_id=registry_id,
        )

        # Pipeline completo: crawl → extract → validate → save
        record: EquipmentRecord = self.pipeline.process_equipment(request)

        # Converter para dict para serialização Redis
        return record.dict()

    @cache_inmetro_result(ttl=86400)
    def validate_batch(self, equipments: List[dict]) -> dict:
        """
        Valida múltiplos equipamentos em lote.

        Args:
            equipments: Lista de dicts com categoria/fabricante/modelo

        Returns:
            Dict do EquipmentBatch serializado
        """
        logger.info(f"Validando lote de {len(equipments)} equipamentos")

        requests = [
            EquipmentRequest(
                categoria=eq["categoria"],
                fabricante=eq["fabricante"],
                modelo=eq["modelo"],
                registry_id=eq.get("registry_id"),
            )
            for eq in equipments
        ]

        batch: EquipmentBatch = self.pipeline.process_batch(requests)
        return batch.dict()

    def get_manufacturers(self, categoria: Optional[str] = None) -> List[str]:
        """
        Lista fabricantes certificados.

        Args:
            categoria: Filtrar por categoria (opcional)

        Returns:
            Lista de nomes de fabricantes
        """
        # TODO: Implementar query real no repository
        logger.info(f"Listando fabricantes - categoria: {categoria}")

        # Mock por enquanto
        manufacturers = [
            "Fronius",
            "Canadian Solar",
            "SMA",
            "ABB",
            "Huawei",
            "Sungrow",
            "GoodWe",
            "Growatt",
        ]

        return manufacturers

    def get_models(self, fabricante: str, categoria: Optional[str] = None) -> List[str]:
        """
        Lista modelos de um fabricante.

        Args:
            fabricante: Nome do fabricante
            categoria: Filtrar por categoria (opcional)

        Returns:
            Lista de modelos
        """
        # TODO: Implementar query real no repository
        logger.info(
            f"Listando modelos - fabricante: {fabricante}, " f"categoria: {categoria}"
        )

        # Mock por enquanto
        models = {
            "Fronius": [
                "Primo 8.2-1",
                "Primo 5.0-1",
                "Symo 10.0-3-M",
            ],
            "Canadian Solar": [
                "CS3W-450MS",
                "CS7N-665MS",
                "HiKu7 Mono 670W",
            ],
        }

        return models.get(fabricante, [])

    def invalidate_equipment_cache(
        self, categoria: str, fabricante: str, modelo: str
    ) -> int:
        """
        Invalida cache de um equipamento específico.

        Args:
            categoria: Categoria do equipamento
            fabricante: Fabricante
            modelo: Modelo

        Returns:
            Número de chaves deletadas
        """
        pattern = f"inmetro:{categoria}:{fabricante}:{modelo}"
        deleted = invalidate_cache(pattern)
        logger.info(f"Cache invalidado: {pattern} - {deleted} chaves deletadas")
        return deleted


# Dependency injection para FastAPI
def get_inmetro_service(
    pipeline: InmetroPipeline = Depends(get_inmetro_pipeline),
) -> InmetroService:
    """Dependency injection para InmetroService."""
    return InmetroService(pipeline=pipeline)


# Import necessário para evitar circular imports
from app.dependencies.inmetro import get_inmetro_pipeline
