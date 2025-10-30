"""
Enriquecimento Inteligente de Dados das Distribuidoras ANEEL
Utiliza APIs LLM (Gemini, OpenAI) e web scraping para completar dados territoriais
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import time
import requests
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from openai import OpenAI

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent
ANEEL_DIR = PROJECT_ROOT / "aneel_datasets"
OUTPUT_DIR = PROJECT_ROOT / "distribuitors"
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_KEY_1 = "AIzaSyCmgSL3RkU7kZ_wAfNiW0Y1nKkifXdx0zY"
GEMINI_KEY_2 = "AIzaSyAY3QeBxTR7pyyHbzULk3xbLWzrmA82Pi8"
OPENAI_KEY = "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"

# Encoding ANEEL
ENCODING = "latin-1"
SEPARATOR = ";"


class DistribuidoraEnricher:
    def __init__(self):
        # Configurar APIs
        genai.configure(api_key=GEMINI_KEY_1)
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")
        self.openai_client = OpenAI(api_key=OPENAI_KEY)

        # Contadores
        self.gemini_calls = 0
        self.openai_calls = 0
        self.current_gemini_key = 1

        # Cache de consultas
        self.cache = {}
        self.load_cache()

    def load_cache(self):
        """Carrega cache de consultas anteriores"""
        cache_file = OUTPUT_DIR / "enrichment_cache.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
            print(f"   ✅ Cache carregado: {len(self.cache)} entradas")

    def save_cache(self):
        """Salva cache de consultas"""
        cache_file = OUTPUT_DIR / "enrichment_cache.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
        print(f"   💾 Cache salvo: {len(self.cache)} entradas")

    def switch_gemini_key(self):
        """Alterna entre as duas chaves Gemini"""
        if self.current_gemini_key == 1:
            genai.configure(api_key=GEMINI_KEY_2)
            self.current_gemini_key = 2
            print("   🔄 Alternando para Gemini Key 2")
        else:
            genai.configure(api_key=GEMINI_KEY_1)
            self.current_gemini_key = 1
            print("   🔄 Alternando para Gemini Key 1")

    def query_gemini(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Consulta API Gemini com retry e alternância de keys"""
        cache_key = f"gemini_{hash(prompt)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(prompt)
                self.gemini_calls += 1
                result = response.text

                # Cache resultado
                self.cache[cache_key] = result
                if self.gemini_calls % 10 == 0:
                    self.save_cache()

                return result
            except Exception as e:
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    self.switch_gemini_key()
                    time.sleep(2)
                elif attempt < max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    print(f"   ❌ Erro Gemini: {e}")
                    return None
        return None

    def query_openai(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Consulta API OpenAI com retry"""
        cache_key = f"openai_{hash(prompt)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em dados do setor elétrico brasileiro.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )
                self.openai_calls += 1
                result = response.choices[0].message.content

                # Cache resultado
                self.cache[cache_key] = result
                if self.openai_calls % 5 == 0:
                    self.save_cache()

                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    print(f"   ❌ Erro OpenAI: {e}")
                    return None
        return None

    def extract_territorial_data(
        self, cnpj: str, sigla: str, razao_social: str
    ) -> Dict[str, Any]:
        """Extrai dados territoriais usando LLMs"""
        print(f"   🔍 Enriquecendo {sigla} ({cnpj[:8]}...)")

        prompt = f"""
Você é um especialista em dados do setor elétrico brasileiro.

Forneça dados PRECISOS e VERIFICÁVEIS sobre a distribuidora de energia:
- CNPJ: {cnpj}
- Sigla: {sigla}
- Razão Social: {razao_social}

Retorne um JSON estruturado com:
{{
  "estados_atendidos": ["UF1", "UF2"],
  "municipios_principais": ["Cidade1", "Cidade2", ...],
  "total_municipios_estimado": numero,
  "area_concessao_km2": numero,
  "coordenadas_sede": {{
    "lat": -XX.XXXX,
    "lng": -XX.XXXX,
    "municipio": "Nome",
    "uf": "UF"
  }},
  "limites_geograficos": {{
    "lat_min": -XX.XX,
    "lat_max": -XX.XX,
    "lng_min": -XX.XX,
    "lng_max": -XX.XX
  }},
  "tipo_distribuidora": "Grande Porte|Média|Cooperativa|Municipal",
  "grupo_empresarial": "Nome do Grupo ou null",
  "fonte": "URL ou fonte dos dados"
}}

IMPORTANTE:
- Use dados reais e verificáveis do setor elétrico brasileiro
- Para cooperativas, informe a região específica de atuação
- Coordenadas devem ser precisas (formato decimal)
- Se não tiver certeza de um dado, use null
- Retorne APENAS o JSON, sem texto adicional
"""

        # Usar OpenAI diretamente (Gemini com problemas de modelo)
        response = self.query_openai(prompt)

        if response:
            try:
                # Extrair JSON da resposta
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                    return data
            except Exception as e:
                print(f"   ⚠️ Erro ao parsear JSON: {e}")

        return None

    def process_municipios_dataset(self) -> pd.DataFrame:
        """Processa dataset de municípios atendidos por distribuidora"""
        print("📍 Processando municípios atendidos...")

        # Tentar encontrar dataset de municípios
        municipios_files = [
            "agentes-setor-eletrico-municipio.csv",
            "distribuidoras-municipios.csv",
            "municipios-distribuidoras.csv",
        ]

        for filename in municipios_files:
            file_path = ANEEL_DIR / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(
                        file_path, sep=SEPARATOR, encoding=ENCODING, dtype=str
                    )
                    print(f"   ✅ {len(df)} registros em {filename}")
                    return df
                except Exception as e:
                    print(f"   ⚠️ Erro ao ler {filename}: {e}")

        print("   ⚠️ Nenhum dataset de municípios encontrado")
        return pd.DataFrame()

    def enrich_all_distribuidoras(self):
        """Enriquece todas as distribuidoras do CSV"""
        print("🚀 Iniciando enriquecimento de distribuidoras...")
        print(f"   API Keys: Gemini (2 keys), OpenAI (1 key)")
        print(f"   Cache: {len(self.cache)} consultas")

        # Carregar CSV atual
        csv_path = OUTPUT_DIR / "aneel_distribuidoras_360_enriched.csv"
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype={"CNPJ": str})

        print(f"\n📊 Total: {len(df)} distribuidoras")

        # Identificar distribuidoras sem dados geográficos
        df_sem_dados = df[df["Total Municípios"] == 0].copy()
        print(
            f"   🎯 {len(df_sem_dados)} sem dados territoriais ({len(df_sem_dados)/len(df)*100:.1f}%)"
        )

        # Processar em lotes
        enriched_count = 0
        failed_count = 0

        for idx, row in df_sem_dados.iterrows():
            cnpj = row["CNPJ"]
            sigla = row["Sigla"] if row["Sigla"] != "nan" else ""
            razao_social = row["Razão Social"]

            # Pular entidades reguladoras e agências
            if any(
                x in razao_social.upper()
                for x in ["ANATEL", "AGENCIA REGULADORA", "ADASA"]
            ):
                continue

            # Enriquecer
            data = self.extract_territorial_data(cnpj, sigla, razao_social)

            if data and isinstance(data, dict):
                # Validar dados
                estados = data.get("estados_atendidos", [])
                if not isinstance(estados, list):
                    estados = []

                total_mun = data.get("total_municipios_estimado", 0)
                if not isinstance(total_mun, (int, float)):
                    total_mun = 0

                # Atualizar DataFrame
                df.loc[idx, "Estados Atendidos"] = ", ".join(estados)
                df.loc[idx, "Total Municípios"] = total_mun

                if "limites_geograficos" in data and data["limites_geograficos"]:
                    lim = data["limites_geograficos"]
                    df.loc[idx, "Lat Mínima"] = lim.get("lat_min")
                    df.loc[idx, "Lat Máxima"] = lim.get("lat_max")
                    df.loc[idx, "Lng Mínima"] = lim.get("lng_min")
                    df.loc[idx, "Lng Máxima"] = lim.get("lng_max")

                if "coordenadas_sede" in data and data["coordenadas_sede"]:
                    coord = data["coordenadas_sede"]
                    df.loc[idx, "Lat Centro"] = coord.get("lat")
                    df.loc[idx, "Lng Centro"] = coord.get("lng")

                enriched_count += 1
                print(
                    f"   ✅ {sigla}: {data.get('total_municipios_estimado', 0)} municípios"
                )
            else:
                failed_count += 1
                print(f"   ❌ {sigla}: Falha no enriquecimento")

            # Rate limiting
            time.sleep(1)

            # Salvar progresso a cada 10 distribuidoras
            if enriched_count % 10 == 0:
                self.save_progress(df)

        # Salvar resultado final
        self.save_progress(df)

        print(f"\n✅ Enriquecimento concluído!")
        print(f"   Sucesso: {enriched_count}")
        print(f"   Falhas: {failed_count}")
        print(f"   Gemini calls: {self.gemini_calls}")
        print(f"   OpenAI calls: {self.openai_calls}")

    def save_progress(self, df: pd.DataFrame):
        """Salva progresso do enriquecimento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # CSV
        csv_path = OUTPUT_DIR / "aneel_distribuidoras_360_enriched.csv"
        df.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

        # JSON
        json_path = OUTPUT_DIR / "aneel_distribuidoras_360_enriched.json"
        distribuidoras = []
        for _, row in df.iterrows():
            dist = {
                "cnpj": row["CNPJ"],
                "sigla": row["Sigla"] if row["Sigla"] != "nan" else "",
                "razao_social": row["Razão Social"],
                "grupo_empresarial": (
                    row.get("Grupo Empresarial", None)
                    if pd.notna(row.get("Grupo Empresarial", None))
                    else None
                ),
                "estados_atendidos": (
                    row["Estados Atendidos"].split(", ")
                    if pd.notna(row["Estados Atendidos"]) and row["Estados Atendidos"]
                    else []
                ),
                "total_municipios": (
                    int(row["Total Municípios"])
                    if pd.notna(row["Total Municípios"])
                    else 0
                ),
                "limites_geograficos": {
                    "lat_min": (
                        float(row["Lat Mínima"])
                        if pd.notna(row["Lat Mínima"])
                        else None
                    ),
                    "lat_max": (
                        float(row["Lat Máxima"])
                        if pd.notna(row["Lat Máxima"])
                        else None
                    ),
                    "lng_min": (
                        float(row["Lng Mínima"])
                        if pd.notna(row["Lng Mínima"])
                        else None
                    ),
                    "lng_max": (
                        float(row["Lng Máxima"])
                        if pd.notna(row["Lng Máxima"])
                        else None
                    ),
                    "lat_centro": (
                        float(row["Lat Centro"])
                        if pd.notna(row["Lat Centro"])
                        else None
                    ),
                    "lng_centro": (
                        float(row["Lng Centro"])
                        if pd.notna(row["Lng Centro"])
                        else None
                    ),
                },
            }
            distribuidoras.append(dist)

        output = {
            "metadata": {
                "data_enriquecimento": datetime.now().isoformat(),
                "total_distribuidoras": len(df),
                "com_dados_territoriais": len(df[df["Total Municípios"] > 0]),
                "versao": "1.1-enriched",
            },
            "distribuidoras": distribuidoras,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(
            f"   💾 Progresso salvo: {len(df[df['Total Municípios'] > 0])}/{len(df)} com dados"
        )


def main():
    print("=" * 80)
    print("ENRIQUECIMENTO INTELIGENTE DE DISTRIBUIDORAS ANEEL")
    print("Utilizando: Gemini Pro (2 keys) + OpenAI GPT-4")
    print("=" * 80)

    enricher = DistribuidoraEnricher()
    enricher.enrich_all_distribuidoras()

    print("\n" + "=" * 80)
    print("CONCLUÍDO!")
    print("=" * 80)


if __name__ == "__main__":
    main()
