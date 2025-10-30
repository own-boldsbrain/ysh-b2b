"""Serviço de integração BACEN SGS - Sistema Gerenciador de Séries Temporais."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import asdict

from validators.bacen_client import BacenSGSClient, SGSSeries, SGSDataPoint
from app.services.redis_service import redis_service
from core.cache import cache_bacen_result, invalidate_cache

# Metrics decorators
from core.metrics import track_bacen_request

logger = logging.getLogger(__name__)


class BacenService:
    """Serviço para dados econômicos e financeiros do BACEN via SGS.

    Funcionalidades:
    - Taxas de juros (SELIC, CDI)
    - Índices de inflação (IPCA, IGP-M)
    - Taxa de câmbio (PTAX)
    - Cache Redis com TTL configurável
    - Métricas de uso
    """

    def __init__(self, client: Optional[BacenSGSClient] = None):
        """
        Inicializa serviço com cliente BACEN.

        Args:
            client: BacenSGSClient opcional (cria novo se não fornecido)
        """
        self.client = client or BacenSGSClient()
        logger.info("BacenService inicializado")

    @cache_bacen_result(ttl=3600)  # 1 hora
    def get_selic_rate(self) -> Dict[str, Any]:
        """
        Obtém taxa SELIC atual.

        Returns:
            Dict com taxa SELIC e metadados

        Cache:
            TTL de 1h no Redis
            Key: bacen:selic:current
        """
        logger.info("Obtendo taxa SELIC atual")

        rate = self.client.get_current_selic()
        if rate is None:
            return {
                "error": "Não foi possível obter taxa SELIC",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "rate": rate,
            "unit": "percentual ao ano",
            "description": "Taxa SELIC",
            "timestamp": datetime.now().isoformat(),
            "source": "BACEN SGS"
        }

    @cache_bacen_result(ttl=3600)
    def get_cdi_rate(self) -> Dict[str, Any]:
        """
        Obtém taxa CDI atual.

        Returns:
            Dict com taxa CDI e metadados
        """
        logger.info("Obtendo taxa CDI atual")

        rate = self.client.get_current_cdi()
        if rate is None:
            return {
                "error": "Não foi possível obter taxa CDI",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "rate": rate,
            "unit": "percentual ao ano",
            "description": "Taxa CDI",
            "timestamp": datetime.now().isoformat(),
            "source": "BACEN SGS"
        }

    @cache_bacen_result(ttl=86400)  # 24 horas
    def get_selic_history(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém histórico da taxa SELIC.

        Args:
            days: Número de dias de histórico

        Returns:
            Dict com série histórica
        """
        logger.info(f"Obtendo histórico SELIC - últimos {days} dias")

        try:
            series = self.client.get_series_data("selic", last_n=days)

            return {
                "series_id": series.series_id,
                "name": series.name,
                "unit": series.unit,
                "frequency": series.frequency,
                "data": [
                    {
                        "date": point.date.isoformat(),
                        "value": point.value,
                        "metadata": point.metadata
                    }
                    for point in series.data
                ],
                "count": len(series.data),
                "last_update": series.last_update.isoformat(),
                "source": "BACEN SGS"
            }

        except Exception as e:
            logger.error(f"Erro ao obter histórico SELIC: {e}")
            return {
                "error": f"Erro ao obter histórico SELIC: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @cache_bacen_result(ttl=86400)
    def get_inflation_data(
        self,
        indicator: str = "ipca",
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Obtém dados de inflação.

        Args:
            indicator: Indicador ('ipca' ou 'igpm')
            months: Número de meses de histórico

        Returns:
            Dict com dados do indicador
        """
        if indicator not in ["ipca", "igpm"]:
            return {
                "error": f"Indicador inválido: {indicator}. Use 'ipca' ou 'igpm'",
                "timestamp": datetime.now().isoformat()
            }

        logger.info(f"Obtendo dados de inflação - {indicator.upper()} últimos {months} meses")

        try:
            # Calcula período
            end_date = date.today()
            start_date = date(end_date.year, end_date.month, 1) - timedelta(days=30 * (months - 1))
            start_date = date(start_date.year, start_date.month, 1)

            series = self.client.get_series_data(indicator, start_date=start_date, end_date=end_date)

            return {
                "indicator": indicator.upper(),
                "series_id": series.series_id,
                "name": series.name,
                "unit": series.unit,
                "frequency": series.frequency,
                "data": [
                    {
                        "date": point.date.isoformat(),
                        "value": point.value,
                        "metadata": point.metadata
                    }
                    for point in series.data
                ],
                "count": len(series.data),
                "period_months": months,
                "last_update": series.last_update.isoformat(),
                "source": "BACEN SGS"
            }

        except Exception as e:
            logger.error(f"Erro ao obter dados de inflação {indicator}: {e}")
            return {
                "error": f"Erro ao obter dados de inflação {indicator}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @cache_bacen_result(ttl=3600)
    def get_exchange_rate(self) -> Dict[str, Any]:
        """
        Obtém taxa de câmbio PTAX atual.

        Returns:
            Dict com taxa de câmbio
        """
        logger.info("Obtendo taxa de câmbio PTAX atual")

        try:
            series = self.client.get_series_data("dolar_ptax", last_n=1)
            if not series.data:
                return {
                    "error": "Não foi possível obter taxa de câmbio",
                    "timestamp": datetime.now().isoformat()
                }

            latest = series.data[-1]

            return {
                "rate": latest.value,
                "currency": "USD/BRL",
                "description": "Taxa de Câmbio - Dólar Americano (PTAX)",
                "date": latest.date.isoformat(),
                "timestamp": datetime.now().isoformat(),
                "source": "BACEN SGS"
            }

        except Exception as e:
            logger.error(f"Erro ao obter taxa de câmbio: {e}")
            return {
                "error": f"Erro ao obter taxa de câmbio: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @cache_bacen_result(ttl=86400)
    def get_exchange_rate_history(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém histórico da taxa de câmbio PTAX.

        Args:
            days: Número de dias de histórico

        Returns:
            Dict com série histórica
        """
        logger.info(f"Obtendo histórico PTAX - últimos {days} dias")

        try:
            data_points = self.client.get_exchange_rate_history(days)

            return {
                "currency": "USD/BRL",
                "description": "Taxa de Câmbio - Dólar Americano (PTAX)",
                "data": [
                    {
                        "date": point.date.isoformat(),
                        "value": point.value,
                        "metadata": point.metadata
                    }
                    for point in data_points
                ],
                "count": len(data_points),
                "period_days": days,
                "timestamp": datetime.now().isoformat(),
                "source": "BACEN SGS"
            }

        except Exception as e:
            logger.error(f"Erro ao obter histórico PTAX: {e}")
            return {
                "error": f"Erro ao obter histórico PTAX: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_available_series(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todas as séries disponíveis.

        Returns:
            Dict com informações das séries
        """
        return self.client.get_available_series()

    def invalidate_cache(self, pattern: str = "*") -> int:
        """
        Invalida cache do BACEN.

        Args:
            pattern: Padrão para invalidar (default: todos)

        Returns:
            Número de chaves deletadas
        """
        full_pattern = f"bacen:{pattern}"
        deleted = invalidate_cache(full_pattern)
        logger.info(f"Cache BACEN invalidado: {full_pattern} - {deleted} chaves deletadas")
        return deleted

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Estatísticas do cache BACEN.

        Returns:
            Dict com estatísticas
        """
        # Implementar estatísticas específicas do BACEN se necessário
        return {
            "service": "bacen",
            "cached_keys_pattern": "bacen:*",
            "timestamp": datetime.now().isoformat()
        }


# Dependency injection para FastAPI
def get_bacen_service(client: Optional[BacenSGSClient] = None) -> BacenService:
    """Dependency injection para BacenService."""
    return BacenService(client=client)