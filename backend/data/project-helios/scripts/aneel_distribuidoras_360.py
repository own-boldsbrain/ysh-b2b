"""
ANEEL Distribuidoras 360º - Cobertura Completa
Extrai dados consolidados de todas distribuidoras de energia do Brasil
"""

import pandas as pd
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

# Configuração
ANEEL_DIR = Path(
    "C:/Users/fjuni/OneDrive/Documentos/GitHub/ysh-b2b/backend/data/project-helios/aneel_datasets"
)
OUTPUT_DIR = Path(
    "C:/Users/fjuni/OneDrive/Documentos/GitHub/ysh-b2b/backend/data/project-helios/distribuitors"
)
OUTPUT_DIR.mkdir(exist_ok=True)

# Encoding comum em CSVs ANEEL
ENCODING = "latin-1"
SEPARATOR = ";"


class ANEELDistribuidoras360:
    def __init__(self):
        self.distribuidoras = {}
        self.agentes = pd.DataFrame()
        self.tarifas = pd.DataFrame()
        self.gd_empreendimentos = pd.DataFrame()
        self.indicadores_continuidade = []
        self.municipios = pd.DataFrame()

    def load_agentes_setor_eletrico(self):
        """Carrega agentes do setor elétrico (base de distribuidoras)"""
        print("📊 Carregando agentes do setor elétrico...")
        try:
            df = pd.read_csv(
                ANEEL_DIR / "agentes-setor-eletrico.csv",
                sep=SEPARATOR,
                encoding=ENCODING,
                dtype=str,
            )

            # Filtrar apenas distribuidoras ativas
            self.agentes = df[
                (df["IdcDistribuicao"] == "1") & (df["IdcAtivo"] == "A")
            ].copy()

            print(f"   ✅ {len(self.agentes)} distribuidoras ativas encontradas")

            # Criar estrutura base
            for _, row in self.agentes.iterrows():
                cnpj = str(row["NumCnpj"]).strip()
                self.distribuidoras[cnpj] = {
                    "cnpj": cnpj,
                    "sigla": str(row.get("SigPessoa", "")).strip(),
                    "razao_social": str(row["NomRazaoSocial"]).strip(),
                    "ativo": row["IdcAtivo"] == "A",
                    "atividades": {
                        "distribuicao": row["IdcDistribuicao"] == "1",
                        "geracao": row.get("IdcGeracao", "0") == "1",
                        "transmissao": row.get("IdcTransmissao", "0") == "1",
                        "comercializacao": row.get("IdcComercializacao", "0") == "1",
                    },
                    "tarifas": {},
                    "municipios_atendidos": [],
                    "area_concessao": {},
                    "indicadores_qualidade": {},
                    "projetos_gd": {},
                    "kpis": {},
                }

            return True
        except Exception as e:
            print(f"   ❌ Erro ao carregar agentes: {e}")
            return False

    def load_tarifas_homologadas(self):
        """Carrega tarifas homologadas (arquivo grande, processamento parcial)"""
        print("💰 Carregando tarifas homologadas...")
        try:
            # Ler em chunks para arquivos grandes
            chunks = []
            for chunk in pd.read_csv(
                ANEEL_DIR / "tarifas-homologadas-distribuidoras-energia-eletrica.csv",
                sep=SEPARATOR,
                encoding=ENCODING,
                dtype=str,
                chunksize=50000,
            ):
                chunks.append(chunk)
                if len(chunks) >= 5:  # Limitar para não sobrecarregar memória
                    break

            self.tarifas = pd.concat(chunks, ignore_index=True)
            print(f"   ✅ {len(self.tarifas)} registros de tarifas carregados")

            # Processar tarifas por distribuidora
            for cnpj in self.distribuidoras.keys():
                tarifas_distrib = self.tarifas[
                    self.tarifas["NumCnpjDistribuidora"] == cnpj
                ].copy()

                if len(tarifas_distrib) > 0:
                    # Pegar tarifa mais recente
                    tarifas_distrib["DatInicioVigencia"] = pd.to_datetime(
                        tarifas_distrib["DatInicioVigencia"], errors="coerce"
                    )
                    tarifa_atual = tarifas_distrib.sort_values(
                        "DatInicioVigencia", ascending=False
                    ).iloc[0]

                    self.distribuidoras[cnpj]["tarifas"] = {
                        "vigencia_inicio": str(
                            tarifa_atual.get("DatInicioVigencia", "")
                        ),
                        "vigencia_fim": str(tarifa_atual.get("DatFimVigencia", "")),
                        "modalidade": str(
                            tarifa_atual.get("SigModalidadeTarifaria", "")
                        ),
                        "classe": str(tarifa_atual.get("SigClasse", "")),
                        "subgrupo": str(tarifa_atual.get("SigSubGrupoTarifario", "")),
                        "valor_kwh": str(tarifa_atual.get("VlrTarifa", "")),
                        "unidade": str(tarifa_atual.get("SigUnidade", "R$/kWh")),
                    }

            return True
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar tarifas (continuando sem tarifas): {e}")
            return False

    def load_geracao_distribuida(self):
        """Carrega empreendimentos de geração distribuída"""
        print("⚡ Carregando projetos de Geração Distribuída...")
        try:
            # Ler em chunks
            chunks = []
            for chunk in pd.read_csv(
                ANEEL_DIR / "empreendimento-geracao-distribuida.csv",
                sep=SEPARATOR,
                encoding=ENCODING,
                dtype=str,
                chunksize=100000,
            ):
                chunks.append(chunk)
                if len(chunks) >= 3:  # Limitar
                    break

            self.gd_empreendimentos = pd.concat(chunks, ignore_index=True)
            print(f"   ✅ {len(self.gd_empreendimentos)} projetos GD carregados")

            # Contar projetos por distribuidora
            if "CodCEG" in self.gd_empreendimentos.columns:
                projetos_por_distrib = (
                    self.gd_empreendimentos.groupby("CodCEG")
                    .agg(
                        {
                            "CodCEG": "count",
                            "NumCodigoClasseConsumo": lambda x: (
                                x.mode()[0] if len(x) > 0 else ""
                            ),
                            "SigTipoGeracao": lambda x: ", ".join(x.unique()[:5]),
                        }
                    )
                    .rename(columns={"CodCEG": "total_projetos"})
                )

                # Associar aos CNPJs (se tivermos mapeamento)
                # Por ora, adicionar contagem geral
                for cnpj in self.distribuidoras.keys():
                    sigla = self.distribuidoras[cnpj]["sigla"]
                    if sigla:
                        matching = projetos_por_distrib[
                            projetos_por_distrib.index.str.contains(
                                sigla, case=False, na=False
                            )
                        ]
                        if len(matching) > 0:
                            self.distribuidoras[cnpj]["projetos_gd"] = {
                                "total_projetos": int(
                                    matching.iloc[0]["total_projetos"]
                                ),
                                "classe_predominante": str(
                                    matching.iloc[0]["NumCodigoClasseConsumo"]
                                ),
                                "tipos_geracao": str(
                                    matching.iloc[0]["SigTipoGeracao"]
                                ),
                            }

            return True
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar GD (continuando sem GD): {e}")
            return False

    def load_indicadores_qualidade(self):
        """Carrega indicadores de qualidade (DEC, FEC, etc)"""
        print("📈 Carregando indicadores de qualidade...")
        try:
            # Tentar carregar indicadores de continuidade mais recentes
            anos = [2025, 2024, 2023, 2022]
            loaded = False

            for ano in anos:
                file_path = (
                    ANEEL_DIR
                    / f"indicadores-continuidade-coletivos-{ano//10*10}-{ano//10*10+9}.csv"
                )
                if file_path.exists():
                    df = pd.read_csv(
                        file_path,
                        sep=SEPARATOR,
                        encoding=ENCODING,
                        dtype=str,
                        nrows=10000,  # Limitar
                    )
                    self.indicadores_continuidade.append(df)
                    loaded = True
                    print(f"   ✅ Indicadores {ano//10*10}-{ano//10*10+9} carregados")
                    break

            if not loaded:
                print("   ⚠️  Nenhum indicador de continuidade encontrado")

            return loaded
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar indicadores: {e}")
            return False

    def load_componentes_tarifarias(self):
        """Carrega componentes tarifárias mais recentes"""
        print("💵 Carregando componentes tarifárias...")
        try:
            anos = [2025, 2024, 2023]
            for ano in anos:
                file_path = ANEEL_DIR / f"componentes-tarifarias-{ano}.csv"
                if file_path.exists():
                    df = pd.read_csv(
                        file_path,
                        sep=SEPARATOR,
                        encoding=ENCODING,
                        dtype=str,
                        nrows=5000,
                    )

                    # Processar componentes por distribuidora
                    for cnpj in self.distribuidoras.keys():
                        sigla = self.distribuidoras[cnpj]["sigla"]
                        if sigla and "SigAgente" in df.columns:
                            comps = df[df["SigAgente"] == sigla]
                            if len(comps) > 0:
                                self.distribuidoras[cnpj]["kpis"][
                                    "componentes_tarifarias"
                                ] = {"ano": ano, "registros": len(comps)}

                    print(f"   ✅ Componentes tarifárias {ano} carregadas")
                    return True

            print("   ⚠️  Nenhum componente tarifária encontrado")
            return False
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar componentes: {e}")
            return False

    def enrich_with_conhecidas(self):
        """Enriquece com dados conhecidos das distribuidoras principais"""
        print("🗺️  Enriquecendo com dados geográficos conhecidos...")

        # Mapping de distribuidoras conhecidas (das que já trabalhamos)
        distribuidoras_conhecidas = {
            "ENEL": {
                "estados": ["SP", "CE", "RJ", "GO"],
                "area_concessao": {
                    "SP": {
                        "municipios": 28,
                        "lat_centro": -23.5505,
                        "lng_centro": -46.6333,
                    },
                    "CE": {
                        "municipios": 184,
                        "lat_centro": -3.7172,
                        "lng_centro": -38.5434,
                    },
                    "RJ": {
                        "municipios": 66,
                        "lat_centro": -22.9068,
                        "lng_centro": -43.1729,
                    },
                    "GO": {
                        "municipios": 237,
                        "lat_centro": -16.6869,
                        "lng_centro": -49.2648,
                    },
                },
                "projetos_gd_estimado": 45000,
                "mercado_anual": "R$ 20.25M",
            },
            "CEMIG": {
                "estados": ["MG"],
                "area_concessao": {
                    "MG": {
                        "municipios": 774,
                        "lat_centro": -19.9167,
                        "lng_centro": -43.9345,
                    }
                },
                "projetos_gd_estimado": 38000,
                "mercado_anual": "R$ 17.1M",
            },
            "CPFL": {
                "estados": ["SP"],
                "area_concessao": {
                    "SP": {
                        "municipios": 234,
                        "lat_centro": -22.9099,
                        "lng_centro": -47.0626,
                    }
                },
                "projetos_gd_estimado": 32000,
                "mercado_anual": "R$ 14.4M",
            },
            "COELBA": {
                "estados": ["BA"],
                "area_concessao": {
                    "BA": {
                        "municipios": 415,
                        "lat_centro": -12.9777,
                        "lng_centro": -38.5016,
                    }
                },
                "projetos_gd_estimado": 24000,
                "mercado_anual": "R$ 10.8M",
            },
            "COPEL": {
                "estados": ["PR"],
                "area_concessao": {
                    "PR": {
                        "municipios": 399,
                        "lat_centro": -25.4296,
                        "lng_centro": -49.2713,
                    }
                },
                "projetos_gd_estimado": 28000,
                "mercado_anual": "R$ 12.6M",
            },
            "CELESC": {
                "estados": ["SC"],
                "area_concessao": {
                    "SC": {
                        "municipios": 295,
                        "lat_centro": -27.5954,
                        "lng_centro": -48.5480,
                    }
                },
                "projetos_gd_estimado": 18000,
                "mercado_anual": "R$ 8.1M",
            },
            "RGE": {
                "estados": ["RS"],
                "area_concessao": {
                    "RS": {
                        "municipios": 381,
                        "lat_centro": -30.0346,
                        "lng_centro": -51.2177,
                    }
                },
                "projetos_gd_estimado": 16000,
                "mercado_anual": "R$ 7.2M",
            },
            "EQUATORIAL": {
                "estados": ["MA", "PA", "PI", "AL"],
                "area_concessao": {
                    "MA": {
                        "municipios": 217,
                        "lat_centro": -2.5387,
                        "lng_centro": -44.2825,
                    },
                    "PA": {
                        "municipios": 144,
                        "lat_centro": -1.4554,
                        "lng_centro": -48.4898,
                    },
                    "PI": {
                        "municipios": 224,
                        "lat_centro": -5.0892,
                        "lng_centro": -42.8034,
                    },
                    "AL": {
                        "municipios": 102,
                        "lat_centro": -9.6658,
                        "lng_centro": -35.7353,
                    },
                },
                "projetos_gd_estimado": 41000,
                "mercado_anual": "R$ 18.5M",
            },
            "ENERGISA": {
                "estados": [
                    "MT",
                    "MS",
                    "TO",
                    "RO",
                    "AC",
                    "SE",
                    "PB",
                    "MG",
                    "SP",
                    "RJ",
                    "PR",
                ],
                "area_concessao": {
                    "MT": {
                        "municipios": 141,
                        "lat_centro": -15.6014,
                        "lng_centro": -56.0979,
                    },
                    "MS": {
                        "municipios": 79,
                        "lat_centro": -20.4428,
                        "lng_centro": -54.6464,
                    },
                    "TO": {
                        "municipios": 139,
                        "lat_centro": -10.1753,
                        "lng_centro": -48.2982,
                    },
                    "RO": {
                        "municipios": 52,
                        "lat_centro": -8.7612,
                        "lng_centro": -63.9039,
                    },
                    "AC": {
                        "municipios": 22,
                        "lat_centro": -9.0238,
                        "lng_centro": -70.8120,
                    },
                    "SE": {
                        "municipios": 75,
                        "lat_centro": -10.9091,
                        "lng_centro": -37.0677,
                    },
                    "PB": {
                        "municipios": 223,
                        "lat_centro": -7.1219,
                        "lng_centro": -34.8450,
                    },
                    "MG": {
                        "municipios": 95,
                        "lat_centro": -19.9167,
                        "lng_centro": -43.9345,
                    },
                    "SP": {
                        "municipios": 45,
                        "lat_centro": -23.5505,
                        "lng_centro": -46.6333,
                    },
                    "RJ": {
                        "municipios": 12,
                        "lat_centro": -22.9068,
                        "lng_centro": -43.1729,
                    },
                    "PR": {
                        "municipios": 18,
                        "lat_centro": -25.4296,
                        "lng_centro": -49.2713,
                    },
                },
                "projetos_gd_estimado": 78000,
                "mercado_anual": "R$ 35.1M",
            },
        }

        # Enriquecer distribuidoras encontradas
        for cnpj, data in self.distribuidoras.items():
            sigla = data["sigla"].upper()
            razao_social = data["razao_social"].upper()

            # Procurar match nas conhecidas
            for key, info in distribuidoras_conhecidas.items():
                if key in sigla or key in razao_social:
                    data["area_concessao"] = info["area_concessao"]
                    data["estados_atendidos"] = info["estados"]
                    data["kpis"]["projetos_gd_estimado"] = info["projetos_gd_estimado"]
                    data["kpis"]["mercado_anual_estimado"] = info["mercado_anual"]
                    print(
                        f"   ✅ {sigla}: {len(info['estados'])} estados, {info['projetos_gd_estimado']} projetos/ano"
                    )
                    break

        return True

    def calculate_geographic_bounds(self):
        """Calcula limites geográficos (bounding box) para cada distribuidora"""
        print("🌎 Calculando limites geográficos...")

        for cnpj, data in self.distribuidoras.items():
            if data.get("area_concessao"):
                # Calcular bounding box a partir dos centros dos estados
                lats = []
                lngs = []

                for estado, info in data["area_concessao"].items():
                    if "lat_centro" in info and "lng_centro" in info:
                        lats.append(info["lat_centro"])
                        lngs.append(info["lng_centro"])

                if lats and lngs:
                    # Expandir ~100km em cada direção (aproximado: 1 grau = ~111km)
                    margin = 1.0
                    data["limites_geograficos"] = {
                        "lat_min": min(lats) - margin,
                        "lat_max": max(lats) + margin,
                        "lng_min": min(lngs) - margin,
                        "lng_max": max(lngs) + margin,
                        "lat_centro": sum(lats) / len(lats),
                        "lng_centro": sum(lngs) / len(lngs),
                    }

        return True

    def export_to_json(self):
        """Exporta para JSON"""
        output_file = OUTPUT_DIR / "aneel_distribuidoras_360.json"

        print(f"\n💾 Exportando para JSON: {output_file}")

        export_data = {
            "metadata": {
                "data_extracao": datetime.now().isoformat(),
                "total_distribuidoras": len(self.distribuidoras),
                "fonte": "ANEEL Datasets",
                "cobertura": "360º - Dados cadastrais, tarifas, área concessão, KPIs",
                "versao": "1.0",
            },
            "distribuidoras": list(self.distribuidoras.values()),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"   ✅ {len(self.distribuidoras)} distribuidoras exportadas para JSON")
        return output_file

    def export_to_csv(self):
        """Exporta para CSV"""
        output_file = OUTPUT_DIR / "aneel_distribuidoras_360.csv"

        print(f"\n💾 Exportando para CSV: {output_file}")

        # Flatten data para CSV
        rows = []
        for cnpj, data in self.distribuidoras.items():
            row = {
                "CNPJ": cnpj,
                "Sigla": data["sigla"],
                "Razão Social": data["razao_social"],
                "Ativo": "Sim" if data["ativo"] else "Não",
                "Distribuição": "Sim" if data["atividades"]["distribuicao"] else "Não",
                "Geração": "Sim" if data["atividades"]["geracao"] else "Não",
                "Transmissão": "Sim" if data["atividades"]["transmissao"] else "Não",
                "Comercialização": (
                    "Sim" if data["atividades"]["comercializacao"] else "Não"
                ),
                "Estados Atendidos": ", ".join(data.get("estados_atendidos", [])),
                "Total Municípios": sum(
                    info.get("municipios", 0)
                    for info in data.get("area_concessao", {}).values()
                ),
                "Lat Mínima": data.get("limites_geograficos", {}).get("lat_min", ""),
                "Lat Máxima": data.get("limites_geograficos", {}).get("lat_max", ""),
                "Lng Mínima": data.get("limites_geograficos", {}).get("lng_min", ""),
                "Lng Máxima": data.get("limites_geograficos", {}).get("lng_max", ""),
                "Lat Centro": data.get("limites_geograficos", {}).get("lat_centro", ""),
                "Lng Centro": data.get("limites_geograficos", {}).get("lng_centro", ""),
                "Tarifa Vigência Início": data.get("tarifas", {}).get(
                    "vigencia_inicio", ""
                ),
                "Tarifa Vigência Fim": data.get("tarifas", {}).get("vigencia_fim", ""),
                "Tarifa Modalidade": data.get("tarifas", {}).get("modalidade", ""),
                "Tarifa Valor kWh": data.get("tarifas", {}).get("valor_kwh", ""),
                "Projetos GD Total": data.get("projetos_gd", {}).get(
                    "total_projetos",
                    data.get("kpis", {}).get("projetos_gd_estimado", ""),
                ),
                "Projetos GD Classe": data.get("projetos_gd", {}).get(
                    "classe_predominante", ""
                ),
                "Projetos GD Tipos": data.get("projetos_gd", {}).get(
                    "tipos_geracao", ""
                ),
                "Mercado Anual Estimado": data.get("kpis", {}).get(
                    "mercado_anual_estimado", ""
                ),
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False, encoding="utf-8-sig", sep=";")

        print(f"   ✅ {len(rows)} distribuidoras exportadas para CSV")
        return output_file

    def generate_summary_report(self):
        """Gera relatório resumido"""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO COBERTURA 360º - DISTRIBUIDORAS ANEEL")
        print("=" * 70)

        total = len(self.distribuidoras)
        com_area = sum(
            1 for d in self.distribuidoras.values() if d.get("area_concessao")
        )
        com_tarifas = sum(
            1
            for d in self.distribuidoras.values()
            if d.get("tarifas", {}).get("valor_kwh")
        )
        com_gd = sum(
            1
            for d in self.distribuidoras.values()
            if d.get("projetos_gd") or d.get("kpis", {}).get("projetos_gd_estimado")
        )
        com_limites = sum(
            1 for d in self.distribuidoras.values() if d.get("limites_geograficos")
        )

        print(f"\n✅ Total Distribuidoras Ativas: {total}")
        print(f"🗺️  Com Área de Concessão: {com_area} ({com_area/total*100:.1f}%)")
        print(f"💰 Com Tarifas: {com_tarifas} ({com_tarifas/total*100:.1f}%)")
        print(f"⚡ Com Dados GD: {com_gd} ({com_gd/total*100:.1f}%)")
        print(
            f"🌍 Com Limites Geográficos: {com_limites} ({com_limites/total*100:.1f}%)"
        )

        # Top 10 por projetos GD
        print("\n🏆 TOP 10 DISTRIBUIDORAS POR PROJETOS GD:")
        print("-" * 70)

        top_distribuidoras = sorted(
            [
                (
                    d["sigla"] or d["razao_social"][:20],
                    d.get("projetos_gd", {}).get("total_projetos")
                    or d.get("kpis", {}).get("projetos_gd_estimado", 0),
                    d.get("kpis", {}).get("mercado_anual_estimado", "N/A"),
                )
                for d in self.distribuidoras.values()
            ],
            key=lambda x: (
                int(str(x[1]).replace("k", "000"))
                if str(x[1]).replace("k", "").isdigit()
                else 0
            ),
            reverse=True,
        )[:10]

        for i, (nome, projetos, mercado) in enumerate(top_distribuidoras, 1):
            print(f"{i:2d}. {nome:30s} | {str(projetos):>10s} projetos/ano | {mercado}")

        print("\n" + "=" * 70)

    def run(self):
        """Executa todo o pipeline"""
        print("\n🚀 INICIANDO EXTRAÇÃO COBERTURA 360º - DISTRIBUIDORAS ANEEL\n")

        # 1. Carregar agentes (base)
        if not self.load_agentes_setor_eletrico():
            print("❌ Erro crítico ao carregar agentes. Abortando.")
            return False

        # 2. Carregar tarifas
        self.load_tarifas_homologadas()

        # 3. Carregar GD
        self.load_geracao_distribuida()

        # 4. Carregar indicadores
        self.load_indicadores_qualidade()

        # 5. Carregar componentes tarifárias
        self.load_componentes_tarifarias()

        # 6. Enriquecer com dados conhecidos
        self.enrich_with_conhecidas()

        # 7. Calcular limites geográficos
        self.calculate_geographic_bounds()

        # 8. Exportar
        json_file = self.export_to_json()
        csv_file = self.export_to_csv()

        # 9. Relatório
        self.generate_summary_report()

        print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
        print(f"   📄 JSON: {json_file}")
        print(f"   📄 CSV:  {csv_file}\n")

        return True


if __name__ == "__main__":
    processor = ANEELDistribuidoras360()
    processor.run()
