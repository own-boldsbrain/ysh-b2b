"""
Database-backed repository for INMETRO equipment records.

Replaces the JSON file storage with PostgreSQL database persistence.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime, timezone, date
from typing import TypeAlias, cast, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.database import get_db
from app.database.models import EquipmentRecord
from validators.inmetro.models import EquipmentRecord as PydanticEquipmentRecord, EquipmentBatch

logger = logging.getLogger(__name__)

RecordPayload: TypeAlias = dict[str, object]


class DatabaseInmetroRepository:
    """Database-backed storage for INMETRO equipment records."""

    def __init__(self) -> None:
        """Initialize repository with database session management."""
        pass

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def upsert_record(self, record: PydanticEquipmentRecord) -> PydanticEquipmentRecord:
        """Insere ou atualiza um registro preservando unicidade."""
        db = next(get_db())
        try:
            # Check if record exists
            existing = db.query(EquipmentRecord).filter(
                and_(
                    EquipmentRecord.categoria == record.categoria,
                    EquipmentRecord.fabricante == record.fabricante,
                    EquipmentRecord.modelo == record.modelo,
                )
            ).first()

            if existing:
                # Update existing record
                self._update_from_pydantic(existing, record)
                existing.updated_at = datetime.now(timezone.utc)
            else:
                # Create new record
                db_record = self._pydantic_to_db(record)
                db.add(db_record)

            db.commit()
            logger.info(f"Equipment record upserted: {record.categoria} - {record.fabricante} {record.modelo}")
            return record

        except Exception as e:
            db.rollback()
            logger.error(f"Error upserting equipment record: {e}")
            raise
        finally:
            db.close()

    def upsert_batch(self, batch: EquipmentBatch) -> EquipmentBatch:
        """Persiste todos os equipamentos de um lote."""
        db = next(get_db())
        try:
            for equipment in batch.equipamentos:
                # Check if record exists
                existing = db.query(EquipmentRecord).filter(
                    and_(
                        EquipmentRecord.categoria == equipment.categoria,
                        EquipmentRecord.fabricante == equipment.fabricante,
                        EquipmentRecord.modelo == equipment.modelo,
                    )
                ).first()

                if existing:
                    # Update existing record
                    self._update_from_pydantic(existing, equipment)
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    # Create new record
                    db_record = self._pydantic_to_db(equipment)
                    db.add(db_record)

            db.commit()
            logger.info(f"Equipment batch upserted: {len(batch.equipamentos)} records")
            return batch

        except Exception as e:
            db.rollback()
            logger.error(f"Error upserting equipment batch: {e}")
            raise
        finally:
            db.close()

    def list_records(
        self,
        *,
        categoria: str | None = None,
        fabricante: str | None = None,
        modelo: str | None = None,
        limit: int | None = None,
        valid_only: bool = False,
    ) -> list[PydanticEquipmentRecord]:
        """Retorna registros aplicando filtros opcionais."""
        db = next(get_db())
        try:
            query = db.query(EquipmentRecord)

            # Apply filters
            if categoria:
                query = query.filter(EquipmentRecord.categoria.ilike(f"%{categoria}%"))
            if fabricante:
                query = query.filter(EquipmentRecord.fabricante.ilike(f"%{fabricante}%"))
            if modelo:
                query = query.filter(EquipmentRecord.modelo.ilike(f"%{modelo}%"))

            # Filter valid records only
            if valid_only:
                today = date.today()
                query = query.filter(
                    and_(
                        EquipmentRecord.data_validade.isnot(None),
                        EquipmentRecord.data_validade >= today
                    )
                )

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            db_records = query.all()
            results = [self._db_to_pydantic(record) for record in db_records]

            logger.info(f"Retrieved {len(results)} equipment records")
            return results

        except Exception as e:
            logger.error(f"Error listing equipment records: {e}")
            return []
        finally:
            db.close()

    def get_record(
        self,
        *,
        categoria: str,
        fabricante: str,
        modelo: str,
    ) -> PydanticEquipmentRecord | None:
        """Obtém um registro específico pelo identificador composto."""
        db = next(get_db())
        try:
            db_record = db.query(EquipmentRecord).filter(
                and_(
                    EquipmentRecord.categoria == categoria,
                    EquipmentRecord.fabricante == fabricante,
                    EquipmentRecord.modelo == modelo,
                )
            ).first()

            if db_record:
                return self._db_to_pydantic(db_record)

            return None

        except Exception as e:
            logger.error(f"Error getting equipment record: {e}")
            return None
        finally:
            db.close()

    def get_by_certificate(self, certificate_number: str) -> PydanticEquipmentRecord | None:
        """Get record by certificate number."""
        db = next(get_db())
        try:
            db_record = db.query(EquipmentRecord).filter(
                EquipmentRecord.certificado_numero == certificate_number
            ).first()

            if db_record:
                return self._db_to_pydantic(db_record)

            return None

        except Exception as e:
            logger.error(f"Error getting record by certificate: {e}")
            return None
        finally:
            db.close()

    def metadata(self) -> dict[str, object]:
        """Return repository metadata."""
        db = next(get_db())
        try:
            total_count = db.query(func.count(EquipmentRecord.id)).scalar() or 0

            # Count by category
            category_counts = db.query(
                EquipmentRecord.categoria,
                func.count(EquipmentRecord.id)
            ).group_by(EquipmentRecord.categoria).all()

            # Count valid records
            today = date.today()
            valid_count = db.query(func.count(EquipmentRecord.id)).filter(
                and_(
                    EquipmentRecord.data_validade.isnot(None),
                    EquipmentRecord.data_validade >= today
                )
            ).scalar() or 0

            latest_update = db.query(func.max(EquipmentRecord.updated_at)).scalar()

            return {
                "total_equipamentos": total_count,
                "equipamentos_validos": valid_count,
                "categorias": dict(category_counts),
                "ultima_atualizacao": latest_update.isoformat() if latest_update else None,
                "fonte": "database",
            }

        except Exception as e:
            logger.error(f"Error getting repository metadata: {e}")
            return {}
        finally:
            db.close()

    def clear_all(self) -> int:
        """Remove all records (for testing/admin purposes)."""
        db = next(get_db())
        try:
            deleted_count = db.query(EquipmentRecord).delete()
            db.commit()
            logger.warning(f"Cleared {deleted_count} equipment records from database")
            return deleted_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing records: {e}")
            raise
        finally:
            db.close()

    def ingest_records(self, records: Iterable[PydanticEquipmentRecord]) -> int:
        """Insert a collection of records (for testing/scripts)."""
        db = next(get_db())
        try:
            inserted_count = 0
            for record in records:
                # Check if record exists
                existing = db.query(EquipmentRecord).filter(
                    and_(
                        EquipmentRecord.categoria == record.categoria,
                        EquipmentRecord.fabricante == record.fabricante,
                        EquipmentRecord.modelo == record.modelo,
                    )
                ).first()

                if not existing:
                    db_record = self._pydantic_to_db(record)
                    db.add(db_record)
                    inserted_count += 1

            db.commit()
            logger.info(f"Ingested {inserted_count} new equipment records")
            return inserted_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error ingesting records: {e}")
            raise
        finally:
            db.close()

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------
    def _pydantic_to_db(self, pydantic_record: PydanticEquipmentRecord) -> EquipmentRecord:
        """Convert Pydantic model to database model."""
        return EquipmentRecord(
            categoria=pydantic_record.categoria,
            fabricante=pydantic_record.fabricante,
            modelo=pydantic_record.modelo,
            familia=pydantic_record.familia,
            normas_ensaios=pydantic_record.certificacao.normas_ensaios,
            ocp=pydantic_record.certificacao.ocp,
            certificado_numero=pydantic_record.certificacao.certificado_numero,
            registro_inmetro=pydantic_record.certificacao.registro_inmetro,
            laboratorio_ensaio=pydantic_record.certificacao.laboratorio_ensaio,
            data_emissao=pydantic_record.certificacao.data_emissao,
            data_validade=pydantic_record.certificacao.data_validade,
            atributos_tecnicos=pydantic_record.datasheet.atributos,
            arquivos_datasheet=pydantic_record.datasheet.arquivos,
            raw_payload=pydantic_record.raw_payload,
            fonte=pydantic_record.referencia.fonte if pydantic_record.referencia else "INMETRO",
            ultima_atualizacao=pydantic_record.referencia.ultima_atualizacao if pydantic_record.referencia else datetime.now(timezone.utc),
            responsavel=pydantic_record.referencia.responsavel if pydantic_record.referencia else None,
            extra_metadata=pydantic_record.referencia.extra if pydantic_record.referencia else {},
        )

    def _update_from_pydantic(self, db_record: EquipmentRecord, pydantic_record: PydanticEquipmentRecord) -> None:
        """Update database record from Pydantic model."""
        db_record.familia = pydantic_record.familia
        db_record.normas_ensaios = pydantic_record.certificacao.normas_ensaios
        db_record.ocp = pydantic_record.certificacao.ocp
        db_record.certificado_numero = pydantic_record.certificacao.certificado_numero
        db_record.registro_inmetro = pydantic_record.certificacao.registro_inmetro
        db_record.laboratorio_ensaio = pydantic_record.certificacao.laboratorio_ensaio
        db_record.data_emissao = pydantic_record.certificacao.data_emissao
        db_record.data_validade = pydantic_record.certificacao.data_validade
        db_record.atributos_tecnicos = pydantic_record.datasheet.atributos
        db_record.arquivos_datasheet = pydantic_record.datasheet.arquivos
        db_record.raw_payload = pydantic_record.raw_payload

        if pydantic_record.referencia:
            db_record.fonte = pydantic_record.referencia.fonte
            db_record.ultima_atualizacao = pydantic_record.referencia.ultima_atualizacao
            db_record.responsavel = pydantic_record.referencia.responsavel
            db_record.extra_metadata = pydantic_record.referencia.extra

    def _db_to_pydantic(self, db_record: EquipmentRecord) -> PydanticEquipmentRecord:
        """Convert database model to Pydantic model."""
        from validators.inmetro.models import ReferenceInfo, CertificationInfo, DatasheetInfo

        referencia = ReferenceInfo(
            fonte=db_record.fonte,
            ultima_atualizacao=db_record.ultima_atualizacao,
            responsavel=db_record.responsavel,
            extra=db_record.extra_metadata or {},
        )

        certificacao = CertificationInfo(
            normas_ensaios=db_record.normas_ensaios or [],
            ocp=db_record.ocp,
            certificado_numero=db_record.certificado_numero,
            registro_inmetro=db_record.registro_inmetro,
            laboratorio_ensaio=db_record.laboratorio_ensaio,
            data_emissao=db_record.data_emissao,
            data_validade=db_record.data_validade,
        )

        datasheet = DatasheetInfo(
            atributos=db_record.atributos_tecnicos or {},
            arquivos=db_record.arquivos_datasheet or [],
        )

        return PydanticEquipmentRecord(
            categoria=db_record.categoria,
            fabricante=db_record.fabricante,
            modelo=db_record.modelo,
            familia=db_record.familia,
            datasheet=datasheet,
            certificacao=certificacao,
            raw_payload=db_record.raw_payload or {},
            referencia=referencia,
        )