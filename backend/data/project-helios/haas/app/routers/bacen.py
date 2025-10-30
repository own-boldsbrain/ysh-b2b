"""Router para APIs BACEN SGS - Sistema Gerenciador de Séries Temporais."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.bacen_service import BacenService, get_bacen_service

# Metrics decorators
from core.metrics import track_bacen_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bacen", tags=["bacen"])


# ==================== SCHEMAS ====================


class SeriesInfo(BaseModel):
    """Informações sobre uma série temporal."""

    id: str = Field(..., description="ID da série no SGS")
    name: str = Field(..., description="Nome da série")
    unit: str = Field(..., description="Unidade de medida")
    frequency: str = Field(..., description="Frequência (daily, monthly, quarterly)")


class RateResponse(BaseModel):
    """Resposta com taxa de juros."""

    rate: Optional[float] = Field(None, description="Valor da taxa")
    unit: str = Field(..., description="Unidade da taxa")
    description: str = Field(..., description="Descrição da taxa")
    timestamp: str = Field(..., description="Timestamp da consulta")
    source: str = Field(..., description="Fonte dos dados")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")


class SeriesDataPoint(BaseModel):
    """Ponto de dados de uma série temporal."""

    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    value: float = Field(..., description="Valor do indicador")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class SeriesResponse(BaseModel):
    """Resposta com dados de uma série temporal."""

    series_id: str = Field(..., description="ID da série")
    name: str = Field(..., description="Nome da série")
    unit: str = Field(..., description="Unidade de medida")
    frequency: str = Field(..., description="Frequência dos dados")
    data: List[SeriesDataPoint] = Field(..., description="Pontos de dados")
    count: int = Field(..., description="Número de pontos")
    last_update: str = Field(..., description="Última atualização")
    source: str = Field(..., description="Fonte dos dados")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")


class ExchangeRateResponse(BaseModel):
    """Resposta com taxa de câmbio."""

    rate: Optional[float] = Field(None, description="Valor da taxa USD/BRL")
    currency: str = Field(..., description="Par de moedas")
    description: str = Field(..., description="Descrição da taxa")
    date: Optional[str] = Field(None, description="Data da taxa")
    timestamp: str = Field(..., description="Timestamp da consulta")
    source: str = Field(..., description="Fonte dos dados")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")


class AvailableSeriesResponse(BaseModel):
    """Resposta com séries disponíveis."""

    series: Dict[str, SeriesInfo] = Field(..., description="Séries disponíveis por chave")


# ==================== ENDPOINTS ====================


@router.get(
    "/selic",
    response_model=RateResponse,
    summary="Taxa SELIC atual",
    description="Retorna a taxa SELIC (Sistema Especial de Liquidação e Custódia) mais recente.",
)
@track_bacen_request("selic")
async def get_selic_rate(
    service: BacenService = Depends(get_bacen_service),
) -> RateResponse:
    """
    Obtém taxa SELIC atual.

    Returns:
        RateResponse com taxa SELIC
    """
    data = service.get_selic_rate()
    return RateResponse(**data)


@router.get(
    "/cdi",
    response_model=RateResponse,
    summary="Taxa CDI atual",
    description="Retorna a taxa CDI (Certificado de Depósito Interbancário) mais recente.",
)
@track_bacen_request("cdi")
async def get_cdi_rate(
    service: BacenService = Depends(get_bacen_service),
) -> RateResponse:
    """
    Obtém taxa CDI atual.

    Returns:
        RateResponse com taxa CDI
    """
    data = service.get_cdi_rate()
    return RateResponse(**data)


@router.get(
    "/selic/history",
    response_model=SeriesResponse,
    summary="Histórico da taxa SELIC",
    description="Retorna histórico da taxa SELIC para os últimos N dias.",
)
@track_bacen_request("selic_history")
async def get_selic_history(
    days: int = Query(30, ge=1, le=365, description="Número de dias de histórico"),
    service: BacenService = Depends(get_bacen_service),
) -> SeriesResponse:
    """
    Obtém histórico da taxa SELIC.

    Args:
        days: Número de dias de histórico (1-365)

    Returns:
        SeriesResponse com histórico SELIC
    """
    data = service.get_selic_history(days=days)
    return SeriesResponse(**data)


@router.get(
    "/inflation/{indicator}",
    response_model=SeriesResponse,
    summary="Dados de inflação",
    description="Retorna dados de inflação (IPCA ou IGP-M) para os últimos N meses.",
)
@track_bacen_request("inflation")
async def get_inflation_data(
    indicator: str = Query(..., regex="^(ipca|igpm)$", description="Indicador: ipca ou igpm"),
    months: int = Query(12, ge=1, le=120, description="Número de meses de histórico"),
    service: BacenService = Depends(get_bacen_service),
) -> SeriesResponse:
    """
    Obtém dados de inflação.

    Args:
        indicator: Indicador de inflação ('ipca' ou 'igpm')
        months: Número de meses de histórico (1-120)

    Returns:
        SeriesResponse com dados de inflação
    """
    data = service.get_inflation_data(indicator=indicator, months=months)
    return SeriesResponse(**data)


@router.get(
    "/exchange-rate",
    response_model=ExchangeRateResponse,
    summary="Taxa de câmbio PTAX atual",
    description="Retorna a taxa de câmbio PTAX (Dólar Americano) mais recente.",
)
@track_bacen_request("exchange_rate")
async def get_exchange_rate(
    service: BacenService = Depends(get_bacen_service),
) -> ExchangeRateResponse:
    """
    Obtém taxa de câmbio PTAX atual.

    Returns:
        ExchangeRateResponse com taxa USD/BRL
    """
    data = service.get_exchange_rate()
    return ExchangeRateResponse(**data)


@router.get(
    "/exchange-rate/history",
    response_model=SeriesResponse,
    summary="Histórico da taxa de câmbio PTAX",
    description="Retorna histórico da taxa de câmbio PTAX para os últimos N dias.",
)
@track_bacen_request("exchange_rate_history")
async def get_exchange_rate_history(
    days: int = Query(30, ge=1, le=365, description="Número de dias de histórico"),
    service: BacenService = Depends(get_bacen_service),
) -> SeriesResponse:
    """
    Obtém histórico da taxa de câmbio PTAX.

    Args:
        days: Número de dias de histórico (1-365)

    Returns:
        SeriesResponse com histórico PTAX
    """
    data = service.get_exchange_rate_history(days=days)
    return SeriesResponse(**data)


@router.get(
    "/series",
    response_model=AvailableSeriesResponse,
    summary="Séries disponíveis",
    description="Lista todas as séries temporais disponíveis na API BACEN SGS.",
)
async def get_available_series(
    service: BacenService = Depends(get_bacen_service),
) -> AvailableSeriesResponse:
    """
    Lista séries disponíveis.

    Returns:
        AvailableSeriesResponse com séries disponíveis
    """
    series = service.get_available_series()

    # Convert to SeriesInfo objects
    series_info = {}
    for key, info in series.items():
        series_info[key] = SeriesInfo(**info)

    return AvailableSeriesResponse(series=series_info)


@router.get(
    "/series/{series_key}",
    response_model=SeriesResponse,
    summary="Dados de uma série específica",
    description="Retorna dados de uma série temporal específica do SGS.",
)
@track_bacen_request("series_data")
async def get_series_data(
    series_key: str,
    start_date: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    last_n: Optional[int] = Query(None, ge=1, le=1000, description="Últimos N registros"),
    service: BacenService = Depends(get_bacen_service),
) -> SeriesResponse:
    """
    Obtém dados de uma série específica.

    Args:
        series_key: Chave da série (selic, cdi, ipca, igpm, dolar_ptax, pib)
        start_date: Data inicial (opcional)
        end_date: Data final (opcional)
        last_n: Últimos N registros (opcional)

    Returns:
        SeriesResponse com dados da série
    """
    try:
        # This would require extending BacenService to support generic series queries
        # For now, return error
        return SeriesResponse(
            series_id="",
            name="",
            unit="",
            frequency="",
            data=[],
            count=0,
            last_update="",
            source="BACEN SGS",
            error=f"Série '{series_key}' não implementada. Use endpoints específicos."
        )
    except Exception as e:
        logger.error(f"Erro ao obter série {series_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/cache/invalidate",
    summary="Invalidar cache BACEN",
    description="Invalida o cache Redis para dados do BACEN.",
)
async def invalidate_bacen_cache(
    pattern: str = Query("*", description="Padrão para invalidar (default: todos)"),
    service: BacenService = Depends(get_bacen_service),
) -> Dict[str, Any]:
    """
    Invalida cache do BACEN.

    Args:
        pattern: Padrão Redis para invalidar

    Returns:
        Dict com resultado da operação
    """
    deleted = service.invalidate_cache(pattern)
    return {
        "message": f"Cache invalidado: {pattern}",
        "keys_deleted": deleted,
        "timestamp": service.get_cache_stats()["timestamp"]
    }


@router.get(
    "/cache/stats",
    summary="Estatísticas do cache BACEN",
    description="Retorna estatísticas do cache Redis para dados do BACEN.",
)
async def get_bacen_cache_stats(
    service: BacenService = Depends(get_bacen_service),
) -> Dict[str, Any]:
    """
    Estatísticas do cache BACEN.

    Returns:
        Dict com estatísticas do cache
    """
    return service.get_cache_stats()