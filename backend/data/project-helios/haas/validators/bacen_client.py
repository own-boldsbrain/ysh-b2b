"""Cliente para API do Sistema Gerenciador de Séries Temporais (SGS) do BACEN."""

import logging
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import httpx
import json

logger = logging.getLogger(__name__)


@dataclass
class SGSDataPoint:
    """Ponto de dados da série temporal do SGS."""

    date: date
    value: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SGSSeries:
    """Série temporal completa do SGS."""

    series_id: str
    name: str
    unit: str
    frequency: str
    last_update: datetime
    data: List[SGSDataPoint]


class BacenSGSClient:
    """Cliente para API do SGS do BACEN.

    Documentação: https://www.bcb.gov.br/estatisticas/series-temporais
    Base URL: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados
    """

    BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados"
    DEFAULT_TIMEOUT = 30.0

    # Séries importantes do SGS
    SERIES = {
        "selic": {
            "id": "432",
            "name": "Taxa SELIC",
            "unit": "percentual ao ano",
            "frequency": "daily"
        },
        "cdi": {
            "id": "4389",
            "name": "Taxa CDI",
            "unit": "percentual ao ano",
            "frequency": "daily"
        },
        "ipca": {
            "id": "433",
            "name": "IPCA - Índice Nacional de Preços ao Consumidor Amplo",
            "unit": "percentual",
            "frequency": "monthly"
        },
        "igpm": {
            "id": "189",
            "name": "IGP-M - Índice Geral de Preços do Mercado",
            "unit": "percentual",
            "frequency": "monthly"
        },
        "dolar_ptax": {
            "id": "10813",
            "name": "Taxa de Câmbio - Dólar Americano (PTAX)",
            "unit": "BRL/USD",
            "frequency": "daily"
        },
        "pib": {
            "id": "1207",
            "name": "PIB - Produto Interno Bruto",
            "unit": "milhões de reais",
            "frequency": "quarterly"
        }
    }

    def __init__(
        self,
        http_client: Optional[httpx.Client] = None,
        cache_dir: Optional[str] = None,
    ):
        self.http_client = http_client or httpx.Client(timeout=self.DEFAULT_TIMEOUT)
        self.cache_dir = cache_dir

    def get_series_info(self, series_key: str) -> Dict[str, Any]:
        """Retorna informações sobre uma série específica."""
        if series_key not in self.SERIES:
            raise ValueError(f"Série '{series_key}' não encontrada. Séries disponíveis: {list(self.SERIES.keys())}")

        return self.SERIES[series_key].copy()

    def get_series_data(
        self,
        series_key: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        last_n: Optional[int] = None,
    ) -> SGSSeries:
        """Obtém dados de uma série temporal.

        Args:
            series_key: Chave da série (ex: 'selic', 'cdi', 'ipca')
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            last_n: Últimos N registros (opcional)

        Returns:
            SGSSeries com os dados da série
        """
        if series_key not in self.SERIES:
            raise ValueError(f"Série '{series_key}' não encontrada")

        series_info = self.SERIES[series_key]
        series_id = series_info["id"]

        # Monta URL da API
        url = self.BASE_URL.format(series_id)

        # Adiciona parâmetros de data
        params = {}
        if start_date:
            params["dataInicial"] = start_date.strftime("%d/%m/%Y")
        if end_date:
            params["dataFinal"] = end_date.strftime("%d/%m/%Y")
        if last_n:
            params["ultN"] = str(last_n)

        logger.info(f"Consultando SGS série {series_key} (ID: {series_id})")

        try:
            response = self.http_client.get(url, params=params)
            response.raise_for_status()

            raw_data = response.json()
            logger.debug(f"Recebidos {len(raw_data)} pontos de dados para série {series_key}")

            # Converte dados brutos para SGSSeries
            data_points = []
            for item in raw_data:
                try:
                    # Formato esperado: {"data": "01/01/2023", "valor": "12.25"}
                    date_str = item.get("data", "")
                    value_str = item.get("valor", "")

                    if not date_str or not value_str:
                        continue

                    # Converte data
                    data_date = datetime.strptime(date_str, "%d/%m/%Y").date()

                    # Converte valor (pode ser string ou número)
                    try:
                        value = float(str(value_str).replace(",", "."))
                    except (ValueError, TypeError):
                        logger.warning(f"Valor inválido ignorado: {value_str}")
                        continue

                    data_points.append(SGSDataPoint(
                        date=data_date,
                        value=value,
                        metadata={"original_value": value_str}
                    ))

                except Exception as e:
                    logger.warning(f"Erro ao processar ponto de dados: {item} - {e}")
                    continue

            # Ordena por data
            data_points.sort(key=lambda x: x.date)

            return SGSSeries(
                series_id=series_id,
                name=series_info["name"],
                unit=series_info["unit"],
                frequency=series_info["frequency"],
                last_update=datetime.now(),
                data=data_points
            )

        except httpx.HTTPError as e:
            logger.error(f"Erro HTTP ao consultar SGS: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar SGS: {e}")
            raise

    def get_current_selic(self) -> Optional[float]:
        """Retorna a taxa SELIC mais recente."""
        try:
            series = self.get_series_data("selic", last_n=1)
            if series.data:
                return series.data[-1].value
        except Exception as e:
            logger.error(f"Erro ao obter SELIC atual: {e}")

        return None

    def get_current_cdi(self) -> Optional[float]:
        """Retorna a taxa CDI mais recente."""
        try:
            series = self.get_series_data("cdi", last_n=1)
            if series.data:
                return series.data[-1].value
        except Exception as e:
            logger.error(f"Erro ao obter CDI atual: {e}")

        return None

    def get_ipca_last_12_months(self) -> List[SGSDataPoint]:
        """Retorna os últimos 12 meses do IPCA."""
        try:
            # Calcula data de 12 meses atrás
            end_date = date.today()
            start_date = date(end_date.year - 1, end_date.month + 1, 1)

            series = self.get_series_data("ipca", start_date=start_date, end_date=end_date)
            return series.data
        except Exception as e:
            logger.error(f"Erro ao obter IPCA últimos 12 meses: {e}")
            return []

    def get_exchange_rate_history(
        self,
        days: int = 30
    ) -> List[SGSDataPoint]:
        """Retorna histórico da taxa de câmbio PTAX."""
        try:
            series = self.get_series_data("dolar_ptax", last_n=days)
            return series.data
        except Exception as e:
            logger.error(f"Erro ao obter histórico PTAX: {e}")
            return []

    def get_available_series(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todas as séries disponíveis."""
        return self.SERIES.copy()


# Função de conveniência para obter cliente
def get_bacen_client() -> BacenSGSClient:
    """Retorna instância do cliente BACEN SGS."""
    return BacenSGSClient()