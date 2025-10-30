"""Serviço de armazenamento e gerenciamento de dados coletados por crawler."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.database import get_db, SessionLocal
from app.database.models import CrawlerData
from core.cache import cache_result

logger = logging.getLogger(__name__)


class CrawlerStorageService:
    """Serviço para armazenar e gerenciar dados coletados por crawlers."""

    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        """Fecha conexão com banco ao destruir objeto."""
        if hasattr(self, 'db'):
            self.db.close()

    async def store_dataset(
        self,
        source: str,
        dataset_name: str,
        data: Dict[str, Any],
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        record_count: Optional[int] = None,
        data_quality_score: Optional[float] = None,
    ) -> int:
        """
        Armazena dataset coletado no banco de dados.

        Args:
            source: Fonte dos dados (aneel, bacen, etc.)
            dataset_name: Nome do dataset
            data: Dados do dataset (JSON serializable)
            url: URL de origem (opcional)
            file_path: Caminho do arquivo local (opcional)
            file_size: Tamanho do arquivo em bytes (opcional)
            record_count: Número de registros (opcional)
            data_quality_score: Score de qualidade dos dados (opcional)

        Returns:
            ID do registro criado
        """
        try:
            # Cria registro no banco
            crawler_record = CrawlerData(
                source=source,
                dataset_name=dataset_name,
                data=data,
                collection_date=datetime.utcnow(),
                url=url,
                file_path=str(file_path) if file_path else None,
                file_size=file_size,
                record_count=record_count,
                data_quality_score=data_quality_score,
                processed=False,
                processing_status="pending",
                processing_attempts=0,
            )

            self.db.add(crawler_record)
            self.db.commit()
            self.db.refresh(crawler_record)

            logger.info(f"Dataset armazenado: {source}/{dataset_name} (ID: {crawler_record.id})")
            return crawler_record.id

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro armazenando dataset {source}/{dataset_name}: {e}")
            raise

    async def update_processing_status(
        self,
        record_id: int,
        status: str,
        error: Optional[str] = None,
        increment_attempts: bool = True,
    ) -> bool:
        """
        Atualiza status de processamento de um dataset.

        Args:
            record_id: ID do registro
            status: Novo status (pending, processing, completed, failed)
            error: Mensagem de erro (opcional)
            increment_attempts: Se deve incrementar contador de tentativas

        Returns:
            True se atualizado com sucesso
        """
        try:
            record = self.db.query(CrawlerData).filter(CrawlerData.id == record_id).first()
            if not record:
                logger.warning(f"Registro {record_id} não encontrado para atualização")
                return False

            record.processing_status = status
            record.last_error = error

            if increment_attempts:
                record.processing_attempts += 1

            if status == "completed":
                record.processed = True
                record.processed_at = datetime.utcnow()
            elif status == "failed":
                record.processed = False

            record.updated_at = datetime.utcnow()
            self.db.commit()

            logger.info(f"Status atualizado para registro {record_id}: {status}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro atualizando status do registro {record_id}: {e}")
            return False

    async def get_dataset(
        self,
        source: str,
        dataset_name: str,
        include_processed: bool = True,
        include_failed: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera dataset mais recente por fonte e nome.

        Args:
            source: Fonte dos dados
            dataset_name: Nome do dataset
            include_processed: Incluir datasets já processados
            include_failed: Incluir datasets com falha

        Returns:
            Dados do dataset ou None se não encontrado
        """
        try:
            query = self.db.query(CrawlerData).filter(
                CrawlerData.source == source,
                CrawlerData.dataset_name == dataset_name
            )

            if not include_processed:
                query = query.filter(CrawlerData.processed == False)

            if not include_failed:
                query = query.filter(CrawlerData.processing_status != "failed")

            # Ordena por data de coleta (mais recente primeiro)
            record = query.order_by(CrawlerData.collection_date.desc()).first()

            if not record:
                return None

            return {
                "id": record.id,
                "source": record.source,
                "dataset_name": record.dataset_name,
                "data": record.data,
                "collection_date": record.collection_date.isoformat(),
                "url": record.url,
                "file_path": record.file_path,
                "file_size": record.file_size,
                "record_count": record.record_count,
                "data_quality_score": record.data_quality_score,
                "processed": record.processed,
                "processing_status": record.processing_status,
                "processing_attempts": record.processing_attempts,
                "last_error": record.last_error,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "processed_at": record.processed_at.isoformat() if record.processed_at else None,
            }

        except Exception as e:
            logger.error(f"Erro recuperando dataset {source}/{dataset_name}: {e}")
            return None

    async def list_datasets(
        self,
        source: Optional[str] = None,
        processed: Optional[bool] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Lista datasets armazenados com filtros.

        Args:
            source: Filtrar por fonte (opcional)
            processed: Filtrar por status de processamento (opcional)
            status: Filtrar por status de processamento (opcional)
            limit: Limite de resultados
            offset: Offset para paginação

        Returns:
            Dict com lista de datasets e metadados
        """
        try:
            query = self.db.query(CrawlerData)

            if source:
                query = query.filter(CrawlerData.source == source)

            if processed is not None:
                query = query.filter(CrawlerData.processed == processed)

            if status:
                query = query.filter(CrawlerData.processing_status == status)

            # Conta total
            total_count = query.count()

            # Aplica paginação e ordenação
            records = query.order_by(CrawlerData.collection_date.desc()).offset(offset).limit(limit).all()

            datasets = []
            for record in records:
                datasets.append({
                    "id": record.id,
                    "source": record.source,
                    "dataset_name": record.dataset_name,
                    "collection_date": record.collection_date.isoformat(),
                    "url": record.url,
                    "file_size": record.file_size,
                    "record_count": record.record_count,
                    "data_quality_score": record.data_quality_score,
                    "processed": record.processed,
                    "processing_status": record.processing_status,
                    "processing_attempts": record.processing_attempts,
                })

            return {
                "datasets": datasets,
                "total_count": total_count,
                "returned_count": len(datasets),
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
            }

        except Exception as e:
            logger.error(f"Erro listando datasets: {e}")
            return {
                "datasets": [],
                "total_count": 0,
                "returned_count": 0,
                "error": str(e),
            }

    async def delete_dataset(self, record_id: int) -> bool:
        """
        Remove dataset do banco de dados.

        Args:
            record_id: ID do registro a remover

        Returns:
            True se removido com sucesso
        """
        try:
            record = self.db.query(CrawlerData).filter(CrawlerData.id == record_id).first()
            if not record:
                logger.warning(f"Registro {record_id} não encontrado para remoção")
                return False

            # Remove arquivo físico se existir
            if record.file_path and Path(record.file_path).exists():
                try:
                    Path(record.file_path).unlink()
                    logger.info(f"Arquivo removido: {record.file_path}")
                except Exception as e:
                    logger.warning(f"Erro removendo arquivo {record.file_path}: {e}")

            self.db.delete(record)
            self.db.commit()

            logger.info(f"Dataset removido: ID {record_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro removendo dataset {record_id}: {e}")
            return False

    async def query_dataset_data(
        self,
        source: str,
        dataset_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Query data within a specific dataset with filters.

        Args:
            source: Data source (e.g., 'aneel')
            dataset_name: Name of the dataset
            filters: Dictionary of field filters
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Dict with query results and metadata
        """
        try:
            # Get the dataset
            dataset = await self.get_dataset(source, dataset_name)
            if not dataset:
                return {
                    "success": False,
                    "error": f"Dataset {source}/{dataset_name} not found",
                    "data": [],
                    "total_results": 0,
                    "returned_results": 0,
                }

            # Extract data records
            data_records = dataset.get("data", [])
            if not isinstance(data_records, list):
                return {
                    "success": False,
                    "error": "Dataset data is not in expected list format",
                    "data": [],
                    "total_results": 0,
                    "returned_results": 0,
                }

            # Apply filters
            filtered_records = data_records
            if filters:
                filtered_records = []
                for record in data_records:
                    if self._matches_filters(record, filters):
                        filtered_records.append(record)

            # Get total count before pagination
            total_results = len(filtered_records)

            # Apply pagination
            paginated_records = filtered_records[offset:offset + limit]

            return {
                "success": True,
                "source": source,
                "dataset_name": dataset_name,
                "total_results": total_results,
                "returned_results": len(paginated_records),
                "data": paginated_records,
                "metadata": {
                    "filters_applied": filters or {},
                    "limit": limit,
                    "offset": offset,
                    "dataset_info": {
                        "collection_date": dataset.get("collection_date"),
                        "record_count": dataset.get("record_count"),
                        "data_quality_score": dataset.get("data_quality_score"),
                    }
                }
            }

        except Exception as e:
            logger.error(f"Erro consultando dados do dataset {source}/{dataset_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "total_results": 0,
                "returned_results": 0,
            }

    def _matches_filters(self, record: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if a record matches the given filters.

        Args:
            record: Data record to check
            filters: Filter criteria

        Returns:
            True if record matches all filters
        """
        for field, value in filters.items():
            if field not in record:
                return False

            record_value = record[field]

            # Handle different filter types
            if isinstance(value, str):
                # Case-insensitive string matching
                if not str(record_value).upper().startswith(value.upper()):
                    return False
            elif isinstance(value, (int, float)):
                # Numeric comparison - exact match for now
                # Could be extended to support ranges like "min_power", "max_power"
                try:
                    record_num = float(record_value) if record_value else 0
                    if record_num != value:
                        return False
                except (ValueError, TypeError):
                    return False
            else:
                # Exact match for other types
                if record_value != value:
                    return False

        return True
        """
        Estatísticas de armazenamento de dados coletados.

        Returns:
            Dict com estatísticas
        """
        try:
            # Total de registros
            total_records = self.db.query(func.count(CrawlerData.id)).scalar() or 0

            # Por fonte
            source_stats = self.db.query(
                CrawlerData.source,
                func.count(CrawlerData.id).label('count'),
                func.sum(CrawlerData.file_size).label('total_size')
            ).group_by(CrawlerData.source).all()

            sources = {}
            for source, count, total_size in source_stats:
                sources[source] = {
                    "datasets_count": count,
                    "total_file_size": total_size or 0,
                }

            # Por status de processamento
            status_stats = self.db.query(
                CrawlerData.processing_status,
                func.count(CrawlerData.id).label('count')
            ).group_by(CrawlerData.processing_status).all()

            statuses = {status: count for status, count in status_stats}

            # Espaço total ocupado
            total_size = self.db.query(func.sum(CrawlerData.file_size)).scalar() or 0

            return {
                "total_datasets": total_records,
                "total_file_size_bytes": total_size,
                "sources": sources,
                "processing_statuses": statuses,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro obtendo estatísticas de armazenamento: {e}")
            return {
                "error": str(e),
                "total_datasets": 0,
                "total_file_size_bytes": 0,
                "sources": {},
                "processing_statuses": {},
            }

    async def cleanup_old_datasets(
        self,
        days_old: int = 30,
        source: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Remove datasets antigos (útil para limpeza de cache).

        Args:
            days_old: Remover datasets com mais de N dias
            source: Filtrar por fonte (opcional)
            dry_run: Se True, apenas simula a remoção

        Returns:
            Dict com resultados da limpeza
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            query = self.db.query(CrawlerData).filter(
                CrawlerData.collection_date < cutoff_date
            )

            if source:
                query = query.filter(CrawlerData.source == source)

            old_records = query.all()
            record_ids = [r.id for r in old_records]

            if dry_run:
                return {
                    "dry_run": True,
                    "records_to_delete": len(record_ids),
                    "cutoff_date": cutoff_date.isoformat(),
                    "source_filter": source,
                    "record_ids": record_ids,
                }

            # Remove registros
            deleted_count = 0
            for record_id in record_ids:
                if await self.delete_dataset(record_id):
                    deleted_count += 1

            return {
                "dry_run": False,
                "records_deleted": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "source_filter": source,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro na limpeza de datasets antigos: {e}")
            return {
                "error": str(e),
                "records_deleted": 0,
            }


# Função de conveniência para obter instância do serviço
def get_crawler_storage_service() -> CrawlerStorageService:
    """Retorna instância do serviço de armazenamento de crawler."""
    return CrawlerStorageService()