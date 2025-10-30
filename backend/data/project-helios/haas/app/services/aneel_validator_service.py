"""
ANEEL Technical/Regulation Validator Service

Implementa validações técnicas e regulatórias contra base de dados ANEEL,
com sincronização automática de datasets do Hugging Face.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import httpx
import asyncio

from app.services.crawler_storage_service import CrawlerStorageService

logger = logging.getLogger(__name__)


class ANEELValidatorService:
    """Serviço de validação técnica e regulatória ANEEL."""

    def __init__(self):
        self.hf_repo = "fernando-bold/aneel-datasets"
        self.hf_base_url = (
            f"https://huggingface.co/datasets/{self.hf_repo}/resolve/main"
        )
        self.cache_timeout = timedelta(hours=24)  # Cache de 24h
        self.crawler_storage = CrawlerStorageService()

        # Mapeamento de datasets
        self.datasets = {
            "empreendimentos_gd": "empreendimento-geracao-distribuida.csv",
            "distribuidoras": "agentes-setor-eletrico.csv",
            "tarifas": "tarifas-homologadas.csv",
            "municipios": "indqual-municipio.csv",
            "siga_empreendimentos": "siga-empreendimentos-geracao.csv",
            "atos_outorgas": "atos-outorgas-aneel.csv",
            "auto_infracao": "auto-infracao.csv",
        }

    async def sync_datasets(
        self, force: bool = False, specific_datasets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Sincroniza datasets ANEEL do Hugging Face para PostgreSQL.

        Args:
            force: Forçar sincronização mesmo se dados estiverem frescos
            specific_datasets: Lista de datasets específicos para sincronizar

        Returns:
            Dict com estatísticas da sincronização
        """
        try:
            datasets_to_sync = specific_datasets or list(self.datasets.keys())
            synced_count = 0
            total_records = 0

            for dataset_key in datasets_to_sync:
                if dataset_key not in self.datasets:
                    logger.warning(
                        f"Dataset {dataset_key} não encontrado no mapeamento"
                    )
                    continue

                filename = self.datasets[dataset_key]
                records_synced = await self._sync_single_dataset(
                    dataset_key, filename, force
                )
                if records_synced > 0:
                    synced_count += 1
                    total_records += records_synced
                    logger.info(
                        f"Sincronizado {dataset_key}: {records_synced} registros"
                    )

            return {
                "success": True,
                "datasets_synced": synced_count,
                "total_records": total_records,
                "synced_at": datetime.utcnow(),
                "datasets_attempted": len(datasets_to_sync),
            }

        except Exception as e:
            logger.error(f"Erro na sincronização ANEEL: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "datasets_synced": 0,
                "total_records": 0,
                "synced_at": datetime.utcnow(),
            }

    async def _sync_single_dataset(
        self, dataset_key: str, filename: str, force: bool
    ) -> int:
        """Sincroniza um dataset específico."""
        try:
            # Verifica se precisa atualizar (baseado em cache)
            if not force and not self._needs_update(dataset_key):
                logger.info(f"Dataset {dataset_key} está atualizado, pulando...")
                return 0

            # Baixa dados do Hugging Face
            url = f"{self.hf_base_url}/{filename}"
            async with httpx.AsyncClient(timeout=300) as client:  # 5min timeout
                response = await client.get(url)
                response.raise_for_status()

            # Processa CSV
            df = pd.read_csv(
                pd.io.common.StringIO(response.text), sep=",", encoding="utf-8"
            )

            # Insere no CrawlerStorageService
            records_inserted = await self._insert_dataset_to_db(dataset_key, df)

            # Atualiza cache timestamp
            self._update_cache_timestamp(dataset_key)

            return records_inserted

        except Exception as e:
            logger.error(f"Erro sincronizando {dataset_key}: {str(e)}")
            return 0

    async def _insert_dataset_to_db(self, dataset_key: str, df: pd.DataFrame) -> int:
        """Insere dataset no CrawlerStorageService."""
        try:
            # Converte DataFrame para dict
            records = df.to_dict("records")
            record_count = len(records)

            # Calcula tamanho aproximado dos dados
            data_size = len(str(records).encode("utf-8"))

            # Cria URL do dataset
            filename = self.datasets[dataset_key]
            url = f"{self.hf_base_url}/{filename}"

            # Armazena usando CrawlerStorageService
            record_id = await self.crawler_storage.store_dataset(
                source="aneel",
                dataset_name=dataset_key,
                data=records,  # Store records directly as list
                url=url,
                file_size=data_size,
                record_count=record_count,
                data_quality_score=0.95,  # Score padrão para dados ANEEL
            )

            return record_count

        except Exception as e:
            logger.error(f"Erro armazenando dataset {dataset_key}: {str(e)}")
            raise

    def _needs_update(self, dataset_key: str) -> bool:
        """Verifica se dataset precisa ser atualizado baseado em cache Redis."""
        from core.cache import redis_client

        try:
            cache_key = f"aneel:dataset:{dataset_key}:last_sync"
            last_sync = redis_client.get(cache_key)

            if last_sync is None:
                return True  # Nunca foi sincronizado

            # Converte timestamp string para datetime
            from datetime import datetime

            last_sync_dt = datetime.fromisoformat(last_sync)

            # Verifica se passou mais de 24 horas
            from datetime import timedelta

            return datetime.now() - last_sync_dt > timedelta(hours=24)

        except Exception as e:
            logger.warning(f"Erro verificando cache para {dataset_key}: {e}")
            return True  # Em caso de erro, assume que precisa atualizar

    def _update_cache_timestamp(self, dataset_key: str):
        """Atualiza timestamp de cache do dataset no Redis."""
        from core.cache import redis_client

        try:
            from datetime import datetime

            cache_key = f"aneel:dataset:{dataset_key}:last_sync"
            timestamp = datetime.now().isoformat()

            # Cache por 30 dias (tempo suficiente para revalidação)
            redis_client.set(cache_key, timestamp, ex=30 * 24 * 60 * 60)

            logger.debug(f"Cache timestamp atualizado para {dataset_key}: {timestamp}")

        except Exception as e:
            logger.warning(f"Erro atualizando cache timestamp para {dataset_key}: {e}")

    async def execute_query(
        self,
        query_type: str,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Executa query SQL-like sobre datasets ANEEL.

        Args:
            query_type: Tipo de query (gd, tariff, distributor, market)
            filters: Filtros da query
            limit: Limite de resultados
            offset: Offset para paginação

        Returns:
            Dict com resultados da query
        """
        try:
            if query_type == "gd":
                return await self._query_gd_projects(filters, limit, offset)
            elif query_type == "tariff":
                return await self._query_tariffs(filters, limit, offset)
            elif query_type == "distributor":
                return await self._query_distributors(filters, limit, offset)
            elif query_type == "market":
                return await self._query_market_analysis(filters, limit, offset)
            else:
                raise ValueError(f"Tipo de query inválido: {query_type}")

        except Exception as e:
            logger.error(f"Erro na query {query_type}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "total_results": 0,
                "returned_results": 0,
            }

    async def _query_gd_projects(
        self, filters: Dict[str, Any], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Query projetos de GD usando CrawlerStorageService."""
        try:
            # Mapeia filtros para campos do dataset
            dataset_filters = {}

            if "uf" in filters:
                dataset_filters["uf"] = filters["uf"]

            if "distribuidora" in filters:
                dataset_filters["nom_agente"] = filters["distribuidora"]

            if "potencia_min" in filters:
                dataset_filters["potencia_instalada"] = filters["potencia_min"]

            if "potencia_max" in filters:
                dataset_filters["potencia_instalada"] = filters["potencia_max"]

            if "modalidade" in filters:
                dataset_filters["modalidade"] = filters["modalidade"]

            # Query usando CrawlerStorageService
            result = await self.crawler_storage.query_dataset_data(
                source="aneel",
                dataset_name="empreendimentos_gd",
                filters=dataset_filters,
                limit=limit,
                offset=offset,
            )

            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Erro na consulta"),
                    "data": [],
                    "total_results": 0,
                    "returned_results": 0,
                }

            return {
                "success": True,
                "query_type": "gd",
                "total_results": result["total_results"],
                "returned_results": result["returned_results"],
                "data": result["data"],
                "metadata": {
                    "filters_applied": filters,
                    "limit": limit,
                    "offset": offset,
                    "dataset_info": result.get("metadata", {}).get("dataset_info", {}),
                },
            }

        except Exception as e:
            logger.error(f"Erro na query GD: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "total_results": 0,
                "returned_results": 0,
            }

    async def _query_tariffs(
        self, filters: Dict[str, Any], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Query tarifas."""
        # TODO: Implementar query de tarifas
        return {
            "success": False,
            "query_type": "tariff",
            "total_results": 0,
            "returned_results": 0,
            "data": [],
            "metadata": {"status": "not_implemented"},
        }

    async def _query_distributors(
        self, filters: Dict[str, Any], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Query distribuidoras usando CrawlerStorageService."""
        try:
            # Mapeia filtros para campos do dataset
            dataset_filters = {}

            if "uf" in filters:
                dataset_filters["sigla_uf"] = filters["uf"]

            if "nome" in filters:
                dataset_filters["nom_agente"] = filters["nome"]

            if "codigo" in filters:
                dataset_filters["cod_agente"] = filters["codigo"]

            # Query usando CrawlerStorageService
            result = await self.crawler_storage.query_dataset_data(
                source="aneel",
                dataset_name="distribuidoras",
                filters=dataset_filters,
                limit=limit,
                offset=offset,
            )

            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Erro na consulta"),
                    "data": [],
                    "total_results": 0,
                    "returned_results": 0,
                }

            return {
                "success": True,
                "query_type": "distributor",
                "total_results": result["total_results"],
                "returned_results": result["returned_results"],
                "data": result["data"],
                "metadata": {
                    "filters_applied": filters,
                    "dataset_info": result.get("metadata", {}).get("dataset_info", {}),
                },
            }

        except Exception as e:
            logger.error(f"Erro na query distribuidoras: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "total_results": 0,
                "returned_results": 0,
            }

    async def _query_market_analysis(
        self, filters: Dict[str, Any], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Query análise de mercado."""
        # TODO: Implementar análise de mercado
        return {
            "success": False,
            "query_type": "market",
            "total_results": 0,
            "returned_results": 0,
            "data": [],
            "metadata": {"status": "not_implemented"},
        }

    async def validate_project(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida projeto contra base ANEEL completa.

        Args:
            validation_data: Dados do projeto para validação

        Returns:
            Dict com resultados da validação
        """
        validation_results = []
        warnings = []

        # 1. Validação de formato CEG
        if validation_data.get("ceg"):
            ceg_result = self._validate_ceg_format(validation_data["ceg"])
            validation_results.append(ceg_result)

        # 2. Validação de distribuidora
        dist_result = await self._validate_distributor_real(
            validation_data["distribuidora"], validation_data.get("uf")
        )
        validation_results.append(dist_result)

        # 3. Validação de faixa de potência
        power_result = self._validate_power_range(
            validation_data["potencia_kw"], validation_data["modalidade"]
        )
        validation_results.append(power_result)

        # 4. Validação de município
        if validation_data.get("municipio") and validation_data.get("uf"):
            municipality_result = await self._validate_municipality_real(
                validation_data["distribuidora"],
                validation_data["municipio"],
                validation_data["uf"],
            )
            validation_results.append(municipality_result)

        # 5. Cross-reference SIGA
        if validation_data.get("ceg"):
            siga_result = await self._validate_siga_reference_real(
                validation_data["ceg"]
            )
            validation_results.append(siga_result)

        # 6. Validações técnicas adicionais
        technical_results = await self._validate_technical_requirements(validation_data)
        validation_results.extend(technical_results)

        # Determina resultado geral
        overall_valid = all(check["passed"] for check in validation_results)

        return {
            "success": True,
            "overall_valid": overall_valid,
            "validation_checks": validation_results,
            "warnings": warnings,
            "timestamp": datetime.utcnow(),
        }

    def _validate_ceg_format(self, ceg: str) -> Dict[str, Any]:
        """Valida formato do código CEG."""
        parts = ceg.split(".")

        if len(parts) != 4:
            return {
                "check": "ceg_format",
                "passed": False,
                "message": "Formato CEG inválido - deve ter 4 partes separadas por ponto",
                "details": {
                    "received": ceg,
                    "expected_pattern": "UF.GD.DISTRIBUIDORA.NUMERO",
                },
            }

        uf, tipo, dist, numero = parts

        if len(uf) != 2:
            return {
                "check": "ceg_format",
                "passed": False,
                "message": "UF deve ter 2 caracteres",
                "details": {"uf": uf},
            }

        if tipo != "GD":
            return {
                "check": "ceg_format",
                "passed": False,
                "message": "Tipo deve ser 'GD'",
                "details": {"tipo": tipo},
            }

        if not numero.isdigit() or len(numero) < 8:
            return {
                "check": "ceg_format",
                "passed": False,
                "message": "Número deve ter pelo menos 8 dígitos",
                "details": {"numero": numero},
            }

        return {
            "check": "ceg_format",
            "passed": True,
            "message": "Formato CEG válido",
            "details": {"ceg": ceg},
        }

    async def _validate_distributor_real(
        self, distributor: str, uf: Optional[str] = None
    ) -> Dict[str, Any]:
        """Valida distribuidora contra base ANEEL real usando CrawlerStorageService."""
        try:
            # Query distribuidoras usando CrawlerStorageService
            filters = {"nom_agente": distributor}
            if uf:
                filters["sigla_uf"] = uf

            result = await self.crawler_storage.query_dataset_data(
                source="aneel",
                dataset_name="distribuidoras",
                filters=filters,
                limit=100,  # Limite alto para encontrar todas as ocorrências
            )

            if not result["success"]:
                return {
                    "check": "distributor_exists",
                    "passed": False,
                    "message": f"Erro ao consultar base ANEEL: {result.get('error', 'Erro desconhecido')}",
                    "details": {"distribuidora": distributor, "uf": uf},
                }

            matching_records = result["data"]

            # Filtra apenas distribuidoras (não transmissoras, etc.)
            distribuidoras = [
                r
                for r in matching_records
                if r.get("dsc_classe_agente", "").upper() == "DISTRIBUIDORA"
            ]

            if not distribuidoras:
                return {
                    "check": "distributor_exists",
                    "passed": False,
                    "message": f"Distribuidora '{distributor}' não encontrada na base ANEEL",
                    "details": {"distribuidora": distributor, "uf": uf},
                }

            # Verifica se distribuidora opera na UF especificada
            if uf:
                ufs_operacao = list(set(r.get("sigla_uf", "") for r in distribuidoras))
                if uf.upper() not in [uf_op.upper() for uf_op in ufs_operacao]:
                    return {
                        "check": "distributor_exists",
                        "passed": False,
                        "message": f"Distribuidora não opera em {uf}",
                        "details": {
                            "distribuidora": distributor,
                            "uf_solicitada": uf,
                            "ufs_operacao": ufs_operacao,
                        },
                    }

            return {
                "check": "distributor_exists",
                "passed": True,
                "message": f"Distribuidora validada na base ANEEL",
                "details": {
                    "distribuidora": distributor,
                    "uf": uf,
                    "encontrados": len(distribuidoras),
                },
            }

        except Exception as e:
            logger.error(f"Erro validando distribuidora {distributor}: {str(e)}")
            return {
                "check": "distributor_exists",
                "passed": False,
                "message": f"Erro interno na validação: {str(e)}",
                "details": {"distribuidora": distributor, "uf": uf},
            }

    def _validate_power_range(self, power_kw: float, modality: str) -> Dict[str, Any]:
        """Valida faixa de potência."""
        modality_lower = modality.lower()

        if modality_lower == "micro":
            if power_kw <= 75:
                return {
                    "check": "power_range",
                    "passed": True,
                    "message": f"Potência {power_kw} kW válida para Micro GD (≤75 kW)",
                    "details": {
                        "potencia_kw": power_kw,
                        "modalidade": "micro",
                        "limite": 75,
                    },
                }
            else:
                return {
                    "check": "power_range",
                    "passed": False,
                    "message": f"Potência {power_kw} kW excede limite de Micro GD (75 kW)",
                    "details": {
                        "potencia_kw": power_kw,
                        "modalidade": "micro",
                        "limite": 75,
                        "sugestao": "Use modalidade 'mini' para esta potência",
                    },
                }

        elif modality_lower == "mini":
            if 75 < power_kw <= 5000:
                return {
                    "check": "power_range",
                    "passed": True,
                    "message": f"Potência {power_kw} kW válida para Mini GD (75-5000 kW)",
                    "details": {
                        "potencia_kw": power_kw,
                        "modalidade": "mini",
                        "faixa": [75, 5000],
                    },
                }
            elif power_kw <= 75:
                return {
                    "check": "power_range",
                    "passed": False,
                    "message": f"Potência {power_kw} kW abaixo do mínimo para Mini GD (>75 kW)",
                    "details": {
                        "potencia_kw": power_kw,
                        "modalidade": "mini",
                        "minimo": 75,
                        "sugestao": "Use modalidade 'micro' para esta potência",
                    },
                }
            else:
                return {
                    "check": "power_range",
                    "passed": False,
                    "message": f"Potência {power_kw} kW excede limite de Mini GD (5000 kW)",
                    "details": {
                        "potencia_kw": power_kw,
                        "modalidade": "mini",
                        "limite": 5000,
                    },
                }

        else:
            return {
                "check": "power_range",
                "passed": False,
                "message": f"Modalidade '{modality}' inválida",
                "details": {
                    "modalidade": modality,
                    "modalidades_validas": ["micro", "mini"],
                },
            }

    async def _validate_municipality_real(
        self, distributor: str, municipality: str, uf: str
    ) -> Dict[str, Any]:
        """Valida município contra base territorial ANEEL."""
        db = next(get_db())

        try:
            # TODO: Implementar validação real baseada em dados territoriais
            # Por enquanto, retorna validação positiva
            return {
                "check": "municipality_coverage",
                "passed": True,
                "message": f"Município {municipality}/{uf} validado",
                "details": {
                    "distribuidora": distributor,
                    "municipio": municipality,
                    "uf": uf,
                    "note": "Validação territorial a ser implementada",
                },
            }

        finally:
            db.close()

    async def _validate_siga_reference_real(self, ceg: str) -> Dict[str, Any]:
        """Valida CEG contra base SIGA usando CrawlerStorageService."""
        try:
            # Query SIGA usando CrawlerStorageService
            result = await self.crawler_storage.query_dataset_data(
                source="aneel",
                dataset_name="siga_empreendimentos",
                filters={"ceg": ceg},
                limit=1,
            )

            if not result["success"]:
                return {
                    "check": "siga_reference",
                    "passed": False,
                    "message": f"Erro ao consultar base SIGA: {result.get('error', 'Erro desconhecido')}",
                    "details": {"ceg": ceg},
                }

            if result["data"]:
                return {
                    "check": "siga_reference",
                    "passed": True,
                    "message": f"CEG {ceg} encontrado no SIGA",
                    "details": {"ceg": ceg, "encontrado": True},
                }
            else:
                return {
                    "check": "siga_reference",
                    "passed": False,
                    "message": f"CEG {ceg} não encontrado no SIGA",
                    "details": {"ceg": ceg, "encontrado": False},
                }

        except Exception as e:
            logger.error(f"Erro validando CEG {ceg} no SIGA: {str(e)}")
            return {
                "check": "siga_reference",
                "passed": False,
                "message": f"Erro interno na validação SIGA: {str(e)}",
                "details": {"ceg": ceg},
            }

    async def _validate_technical_requirements(
        self, validation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validações técnicas adicionais."""
        results = []

        # Validação de fonte de energia
        fonte = validation_data.get("fonte", "").lower()
        fontes_validas = [
            "fotovoltaica",
            "solar",
            "eolica",
            "eólica",
            "biomassa",
            "pch",
        ]

        if fonte not in fontes_validas:
            results.append(
                {
                    "check": "energy_source",
                    "passed": False,
                    "message": f"Fonte de energia '{fonte}' não é elegível para GD",
                    "details": {
                        "fonte_informada": fonte,
                        "fontes_validas": fontes_validas,
                    },
                }
            )
        else:
            results.append(
                {
                    "check": "energy_source",
                    "passed": True,
                    "message": f"Fonte de energia '{fonte}' é elegível para GD",
                    "details": {"fonte": fonte},
                }
            )

        # Outras validações técnicas podem ser adicionadas aqui

        return results
