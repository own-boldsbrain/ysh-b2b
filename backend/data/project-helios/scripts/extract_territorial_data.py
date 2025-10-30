"""
Extração Avançada de Dados Territoriais dos Datasets ANEEL
Processa múltiplos datasets para completar informações das distribuidoras
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Set
import re

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent
ANEEL_DIR = PROJECT_ROOT / "aneel_datasets"
OUTPUT_DIR = PROJECT_ROOT / "distribuitors"

ENCODING = "latin-1"
SEPARATOR = ";"


class ANEELTerritorialExtractor:
    def __init__(self):
        self.distribuidoras = {}
        self.municipios_by_dist = {}
        self.estados_by_dist = {}
        
    def load_current_data(self):
        """Carrega dados atuais do CSV"""
        print("📂 Carregando dados existentes...")
        csv_path = OUTPUT_DIR / "aneel_distribuidoras_360.csv"
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')
        
        for _, row in df.iterrows():
            cnpj = row['CNPJ']
            self.distribuidoras[cnpj] = {
                'cnpj': cnpj,
                'sigla': row['Sigla'] if row['Sigla'] != 'nan' else '',
                'razao_social': row['Razão Social'],
                'estados': set(),
                'municipios': set(),
                'lat_min': None,
                'lat_max': None,
                'lng_min': None,
                'lng_max': None,
                'lat_centro': None,
                'lng_centro': None
            }
        
        print(f"   ✅ {len(self.distribuidoras)} distribuidoras carregadas")

    def extract_from_gd_empreendimentos(self):
        """Extrai municípios de projetos de geração distribuída"""
        print("\n🏭 Processando empreendimentos de geração distribuída...")
        
        try:
            # Processar em chunks
            chunks_processed = 0
            total_municipios = 0
            
            for chunk in pd.read_csv(
                ANEEL_DIR / "empreendimento-geracao-distribuida.csv",
                sep=SEPARATOR,
                encoding=ENCODING,
                dtype=str,
                chunksize=100000
            ):
                chunks_processed += 1
                
                # Colunas relevantes: CodCEG (distribuidora), MdaMunicipio, SigUF
                if 'CodCEG' in chunk.columns and 'MdaMunicipio' in chunk.columns:
                    for _, row in chunk.iterrows():
                        cod_ceg = str(row.get('CodCEG', '')).strip()
                        municipio = str(row.get('MdaMunicipio', '')).strip()
                        uf = str(row.get('SigUF', '')).strip()
                        
                        # Encontrar distribuidora por código CEG
                        dist_cnpj = self.find_distribuidora_by_ceg(cod_ceg)
                        
                        if dist_cnpj and municipio and municipio != 'nan':
                            if dist_cnpj not in self.municipios_by_dist:
                                self.municipios_by_dist[dist_cnpj] = set()
                            if dist_cnpj not in self.estados_by_dist:
                                self.estados_by_dist[dist_cnpj] = set()
                            
                            self.municipios_by_dist[dist_cnpj].add(f"{municipio}-{uf}")
                            self.estados_by_dist[dist_cnpj].add(uf)
                            total_municipios += 1
                
                if chunks_processed >= 5:  # Limitar para não sobrecarregar
                    break
            
            print(f"   ✅ {len(self.municipios_by_dist)} distribuidoras mapeadas")
            print(f"   ✅ {total_municipios} associações município-distribuidora")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    def find_distribuidora_by_ceg(self, cod_ceg: str) -> str:
        """Encontra CNPJ da distribuidora pelo código CEG"""
        # Mapeamento conhecido de códigos CEG
        ceg_map = {
            '1': '33050071000158',  # ENEL RJ
            '2': '08336783000190',  # CELESC
            '6': '06981180000116',  # CEMIG-D
            '15': '15139629000194', # COELBA
            '17': '04368898000106', # COPEL
            # Adicionar mais conforme necessário
        }
        return ceg_map.get(cod_ceg)

    def extract_from_indicadores_municipio(self):
        """Extrai dados de indicadores por município"""
        print("\n📊 Processando indicadores por município...")
        
        try:
            df = pd.read_csv(
                ANEEL_DIR / "indqual-municipio.csv",
                sep=SEPARATOR,
                encoding=ENCODING,
                dtype=str
            )
            
            print(f"   📄 {len(df)} registros encontrados")
            
            # Colunas: Distribuidora, Município, UF, DEC, FEC
            if 'Distribuidora' in df.columns and 'Município' in df.columns:
                for _, row in df.iterrows():
                    dist_nome = str(row.get('Distribuidora', '')).strip().upper()
                    municipio = str(row.get('Município', '')).strip()
                    uf = str(row.get('UF', '')).strip()
                    
                    # Encontrar CNPJ por nome da distribuidora
                    dist_cnpj = self.find_distribuidora_by_name(dist_nome)
                    
                    if dist_cnpj and municipio and municipio != 'nan':
                        if dist_cnpj not in self.municipios_by_dist:
                            self.municipios_by_dist[dist_cnpj] = set()
                        if dist_cnpj not in self.estados_by_dist:
                            self.estados_by_dist[dist_cnpj] = set()
                        
                        self.municipios_by_dist[dist_cnpj].add(f"{municipio}-{uf}")
                        self.estados_by_dist[dist_cnpj].add(uf)
            
            print(f"   ✅ Dados de municípios extraídos")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    def find_distribuidora_by_name(self, nome: str) -> str:
        """Encontra CNPJ da distribuidora pelo nome"""
        nome = nome.upper().strip()
        
        for cnpj, data in self.distribuidoras.items():
            razao = data['razao_social'].upper()
            sigla = data['sigla'].upper()
            
            # Busca por sigla exata
            if sigla and sigla == nome:
                return cnpj
            
            # Busca por nome contido
            if nome in razao or razao in nome:
                return cnpj
        
        return None

    def calculate_geographic_bounds(self):
        """Calcula limites geográficos baseado nos municípios"""
        print("\n🗺️  Calculando limites geográficos...")
        
        # Coordenadas aproximadas de capitais e principais cidades (para estimativa)
        municipios_coords = self.load_municipios_coordinates()
        
        for cnpj, municipios in self.municipios_by_dist.items():
            if cnpj in self.distribuidoras:
                coords = []
                
                for mun_uf in municipios:
                    mun = mun_uf.split('-')[0] if '-' in mun_uf else mun_uf
                    if mun in municipios_coords:
                        coords.append(municipios_coords[mun])
                
                if coords:
                    lats = [c[0] for c in coords]
                    lngs = [c[1] for c in coords]
                    
                    margin = 0.5  # Margem de ~55km
                    
                    self.distribuidoras[cnpj].update({
                        'lat_min': min(lats) - margin,
                        'lat_max': max(lats) + margin,
                        'lng_min': min(lngs) - margin,
                        'lng_max': max(lngs) + margin,
                        'lat_centro': sum(lats) / len(lats),
                        'lng_centro': sum(lngs) / len(lngs)
                    })
        
        print(f"   ✅ Limites calculados para distribuidoras com municípios mapeados")

    def load_municipios_coordinates(self) -> Dict[str, tuple]:
        """Carrega coordenadas de municípios brasileiros"""
        # Base simplificada com principais cidades de cada estado
        return {
            # Norte
            'MANAUS': (-3.1190, -60.0217),
            'BELÉM': (-1.4558, -48.5039),
            'BOA VISTA': (2.8235, -60.6758),
            'MACAPÁ': (0.0349, -51.0694),
            'PALMAS': (-10.1847, -48.3336),
            'PORTO VELHO': (-8.7612, -63.9004),
            'RIO BRANCO': (-9.9747, -67.8243),
            
            # Nordeste
            'SALVADOR': (-12.9718, -38.5011),
            'FORTALEZA': (-3.7327, -38.5270),
            'SÃO LUÍS': (-2.5307, -44.3068),
            'JOÃO PESSOA': (-7.1219, -34.8450),
            'RECIFE': (-8.0476, -34.8770),
            'TERESINA': (-5.0919, -42.8034),
            'NATAL': (-5.7945, -35.2110),
            'ARACAJU': (-10.9162, -37.0772),
            'MACEIÓ': (-9.6498, -35.7089),
            
            # Centro-Oeste
            'BRASÍLIA': (-15.7942, -47.8825),
            'GOIÂNIA': (-16.6864, -49.2643),
            'CUIABÁ': (-15.6014, -56.0979),
            'CAMPO GRANDE': (-20.4697, -54.6201),
            
            # Sudeste
            'BELO HORIZONTE': (-19.9167, -43.9345),
            'RIO DE JANEIRO': (-22.9099, -43.1729),
            'SÃO PAULO': (-23.5505, -46.6333),
            'VITÓRIA': (-20.3155, -40.3128),
            
            # Sul
            'CURITIBA': (-25.4296, -49.2713),
            'FLORIANÓPOLIS': (-27.5954, -48.5480),
            'PORTO ALEGRE': (-30.0346, -51.2177)
        }

    def export_enriched_data(self):
        """Exporta dados enriquecidos"""
        print("\n💾 Exportando dados enriquecidos...")
        
        # Preparar DataFrame
        rows = []
        for cnpj, data in self.distribuidoras.items():
            municipios = list(self.municipios_by_dist.get(cnpj, set()))
            estados = list(self.estados_by_dist.get(cnpj, set()))
            
            row = {
                'CNPJ': cnpj,
                'Sigla': data['sigla'],
                'Razão Social': data['razao_social'],
                'Estados Atendidos': ', '.join(sorted(estados)) if estados else '',
                'Total Municípios': len(municipios),
                'Municípios (Lista Completa)': '; '.join(sorted(municipios)),
                'Lat Mínima': data.get('lat_min'),
                'Lat Máxima': data.get('lat_max'),
                'Lng Mínima': data.get('lng_min'),
                'Lng Máxima': data.get('lng_max'),
                'Lat Centro': data.get('lat_centro'),
                'Lng Centro': data.get('lng_centro')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Mesclar com dados originais
        csv_original = OUTPUT_DIR / "aneel_distribuidoras_360.csv"
        df_original = pd.read_csv(csv_original, sep=';', encoding='utf-8-sig')
        
        # Atualizar apenas campos territoriais
        for idx, row in df.iterrows():
            cnpj = row['CNPJ']
            mask = df_original['CNPJ'] == cnpj
            
            if row['Total Municípios'] > 0:
                df_original.loc[mask, 'Estados Atendidos'] = row['Estados Atendidos']
                df_original.loc[mask, 'Total Municípios'] = row['Total Municípios']
                df_original.loc[mask, 'Lat Mínima'] = row['Lat Mínima']
                df_original.loc[mask, 'Lat Máxima'] = row['Lat Máxima']
                df_original.loc[mask, 'Lng Mínima'] = row['Lng Mínima']
                df_original.loc[mask, 'Lng Máxima'] = row['Lng Máxima']
                df_original.loc[mask, 'Lat Centro'] = row['Lat Centro']
                df_original.loc[mask, 'Lng Centro'] = row['Lng Centro']
        
        # Exportar CSV enriquecido
        output_csv = OUTPUT_DIR / "aneel_distribuidoras_360_v2.csv"
        df_original.to_csv(output_csv, sep=';', index=False, encoding='utf-8-sig')
        print(f"   ✅ CSV: {output_csv}")
        
        # Exportar JSON detalhado com lista de municípios
        output_json = OUTPUT_DIR / "aneel_distribuidoras_360_v2.json"
        distribuidoras_json = []
        
        for _, row in df.iterrows():
            dist = {
                'cnpj': row['CNPJ'],
                'sigla': row['Sigla'],
                'razao_social': row['Razão Social'],
                'estados_atendidos': row['Estados Atendidos'].split(', ') if row['Estados Atendidos'] else [],
                'total_municipios': int(row['Total Municípios']),
                'municipios': [m.strip() for m in row['Municípios (Lista Completa)'].split(';') if m.strip()] if row['Municípios (Lista Completa)'] else [],
                'limites_geograficos': {
                    'lat_min': float(row['Lat Mínima']) if pd.notna(row['Lat Mínima']) else None,
                    'lat_max': float(row['Lat Máxima']) if pd.notna(row['Lat Máxima']) else None,
                    'lng_min': float(row['Lng Mínima']) if pd.notna(row['Lng Mínima']) else None,
                    'lng_max': float(row['Lng Máxima']) if pd.notna(row['Lng Máxima']) else None,
                    'lat_centro': float(row['Lat Centro']) if pd.notna(row['Lat Centro']) else None,
                    'lng_centro': float(row['Lng Centro']) if pd.notna(row['Lng Centro']) else None
                }
            }
            distribuidoras_json.append(dist)
        
        output_data = {
            'metadata': {
                'data_extracao': datetime.now().isoformat(),
                'versao': '2.0-territorial-complete',
                'total_distribuidoras': len(distribuidoras_json),
                'com_dados_territoriais': len([d for d in distribuidoras_json if d['total_municipios'] > 0]),
                'fonte': 'ANEEL Datasets + Geração Distribuída + Indicadores Municipais'
            },
            'distribuidoras': distribuidoras_json
        }
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ JSON: {output_json}")
        
        # Estatísticas
        total = len(df)
        com_dados = len(df[df['Total Municípios'] > 0])
        print(f"\n📈 Cobertura:")
        print(f"   Total: {total} distribuidoras")
        print(f"   Com dados territoriais: {com_dados} ({com_dados/total*100:.1f}%)")
        print(f"   Sem dados: {total - com_dados} ({(total-com_dados)/total*100:.1f}%)")


def main():
    print("=" * 80)
    print("EXTRAÇÃO AVANÇADA DE DADOS TERRITORIAIS - ANEEL")
    print("=" * 80)
    
    extractor = ANEELTerritorialExtractor()
    extractor.load_current_data()
    extractor.extract_from_gd_empreendimentos()
    extractor.extract_from_indicadores_municipio()
    extractor.calculate_geographic_bounds()
    extractor.export_enriched_data()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO CONCLUÍDA!")
    print("=" * 80)


if __name__ == "__main__":
    main()
