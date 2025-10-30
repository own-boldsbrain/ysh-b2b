"""
Enriquecimento com OpenAI apenas - Versão Simplificada e Robusta
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
from openai import OpenAI

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "distribuitors"
OUTPUT_DIR.mkdir(exist_ok=True)

OPENAI_KEY = "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"


class SimpleEnricher:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_KEY)
        self.calls = 0
        self.cache = self.load_cache()

    def load_cache(self):
        cache_file = OUTPUT_DIR / "enrichment_cache.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_cache(self):
        cache_file = OUTPUT_DIR / "enrichment_cache.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def query_openai(self, cnpj, sigla, razao_social):
        """Consulta OpenAI para obter dados territoriais"""
        cache_key = f"openai_{cnpj}"
        if cache_key in self.cache:
            print(f"      💾 Cache hit")
            return self.cache[cache_key]

        prompt = f"""Você é especialista no setor elétrico brasileiro.

Distribuidora:
- CNPJ: {cnpj}
- Sigla: {sigla}
- Nome: {razao_social}

Retorne APENAS um JSON com dados reais e verificáveis:
{{
  "estados_atendidos": ["UF1", "UF2"],
  "total_municipios_estimado": numero,
  "limites_geograficos": {{
    "lat_min": -XX.XX,
    "lat_max": -XX.XX,
    "lng_min": -XX.XX,
    "lng_max": -XX.XX
  }},
  "lat_centro": -XX.XX,
  "lng_centro": -XX.XX,
  "grupo_empresarial": "Grupo" ou null
}}

Seja preciso. Para cooperativas, use dados da região de atuação."""

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Modelo mais rápido e barato
                    messages=[
                        {"role": "system", "content": "Especialista setor elétrico BR"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=500,
                )
                self.calls += 1
                result = response.choices[0].message.content

                # Parse JSON
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    data = json.loads(json_str)

                    # Cache
                    self.cache[cache_key] = data
                    if self.calls % 5 == 0:
                        self.save_cache()

                    return data
            except Exception as e:
                if attempt < 2:
                    time.sleep(2**attempt)
                else:
                    print(f"      ❌ Erro: {str(e)[:50]}")
        return None

    def enrich(self, batch_size=20):
        """Enriquece distribuidoras em lotes"""
        print("🚀 ENRIQUECIMENTO SIMPLIFICADO - OPENAI GPT-4o-mini")
        print(f"   Batch size: {batch_size}")

        # Carregar CSV
        csv_path = OUTPUT_DIR / "aneel_distribuidoras_360_enriched.csv"
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype={"CNPJ": str})

        print(f"\n📊 Total: {len(df)} distribuidoras")

        # Identificar sem dados
        df_sem_dados = df[
            (df["Total Municípios"] == 0) | (df["Total Municípios"].isna())
        ].copy()

        print(f"   🎯 {len(df_sem_dados)} sem dados territoriais")

        enriched = 0
        failed = 0

        for idx, row in df_sem_dados.head(batch_size).iterrows():
            cnpj = str(row["CNPJ"])
            sigla = str(row["Sigla"]) if pd.notna(row["Sigla"]) else ""
            razao_social = str(row["Razão Social"])

            # Pular agências reguladoras
            if any(
                x in razao_social.upper()
                for x in ["ANATEL", "AGENCIA REGULADORA", "ADASA", "COMPLEXO SOLAR"]
            ):
                print(f"\n   ⏭️ {sigla or cnpj[:8]}: Pulando (não é distribuidora)")
                continue

            print(f"\n   🔍 {sigla or cnpj[:8]}: {razao_social[:50]}...")

            data = self.query_openai(cnpj, sigla, razao_social)

            if data and isinstance(data, dict):
                try:
                    # Validar e extrair dados
                    estados = data.get("estados_atendidos", [])
                    if not isinstance(estados, list):
                        estados = []

                    total_mun = data.get("total_municipios_estimado", 0)
                    if not isinstance(total_mun, (int, float)):
                        total_mun = 0

                    grupo = data.get("grupo_empresarial")

                    # Atualizar
                    if estados:
                        df.loc[idx, "Estados Atendidos"] = ", ".join(estados)
                    if total_mun > 0:
                        df.loc[idx, "Total Municípios"] = int(total_mun)
                    if grupo and grupo != "null":
                        df.loc[idx, "Grupo Empresarial"] = grupo

                    # Limites geográficos
                    lim = data.get("limites_geograficos", {})
                    if lim and isinstance(lim, dict):
                        if lim.get("lat_min"):
                            df.loc[idx, "Lat Mínima"] = float(lim["lat_min"])
                        if lim.get("lat_max"):
                            df.loc[idx, "Lat Máxima"] = float(lim["lat_max"])
                        if lim.get("lng_min"):
                            df.loc[idx, "Lng Mínima"] = float(lim["lng_min"])
                        if lim.get("lng_max"):
                            df.loc[idx, "Lng Máxima"] = float(lim["lng_max"])

                    # Centro
                    if data.get("lat_centro"):
                        df.loc[idx, "Lat Centro"] = float(data["lat_centro"])
                    if data.get("lng_centro"):
                        df.loc[idx, "Lng Centro"] = float(data["lng_centro"])

                    # Atualizar status
                    if total_mun > 0 and estados:
                        df.loc[idx, "Tem Dados Completos"] = "Sim"
                        df.loc[idx, "Fonte Dados"] = "OpenAI GPT-4o-mini"

                    enriched += 1
                    print(f"      ✅ {total_mun} municípios em {', '.join(estados)}")

                except Exception as e:
                    print(f"      ⚠️ Erro ao processar: {e}")
                    failed += 1
            else:
                failed += 1
                print(f"      ❌ Sem dados válidos")

            # Salvar a cada 5
            if (enriched + failed) % 5 == 0:
                self.save_progress(df)

            # Rate limit
            time.sleep(1.5)

        # Salvar final
        self.save_progress(df)

        print(f"\n✅ CONCLUÍDO!")
        print(f"   Enriquecidas: {enriched}")
        print(f"   Falhas: {failed}")
        print(f"   Chamadas OpenAI: {self.calls}")
        print(f"   Total com dados: {len(df[df['Total Municípios'] > 0])}/{len(df)}")

        return df

    def save_progress(self, df):
        """Salva progresso"""
        csv_path = OUTPUT_DIR / "aneel_distribuidoras_360_enriched.csv"
        df.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

        total_com_dados = len(df[df["Total Municípios"] > 0])
        print(f"\n      💾 Progresso salvo: {total_com_dados}/{len(df)} com dados")

        self.save_cache()


def main():
    enricher = SimpleEnricher()
    enricher.enrich(batch_size=30)  # Processar 30 por vez


if __name__ == "__main__":
    main()
