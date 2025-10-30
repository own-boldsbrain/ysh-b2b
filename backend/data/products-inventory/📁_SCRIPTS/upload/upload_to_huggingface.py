#!/usr/bin/env python3
"""
Upload Estratégico para Hugging Face Hub
Envia JSONs e CSVs em lotes otimizados
"""
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo, login
import logging
from typing import List
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HuggingFaceUploader:
    """Upload estratégico para Hugging Face"""

    def __init__(self, repo_id: str, token: str = None):
        self.repo_id = repo_id
        self.api = HfApi()

        # Login
        if token:
            login(token=token)
        else:
            # Tenta usar token do ambiente
            logger.info("Usando token do ambiente HF_TOKEN")

        self.base_path = Path(__file__).parent

    def create_repository(self, repo_type: str = "dataset"):
        """Cria repositório no Hub"""
        try:
            logger.info(f"📦 Criando repositório: {self.repo_id}")
            create_repo(
                repo_id=self.repo_id, repo_type=repo_type, exist_ok=True, private=False
            )
            logger.info("✅ Repositório criado/verificado")
        except Exception as e:
            logger.error(f"❌ Erro ao criar repositório: {e}")
            raise

    def upload_batch(
        self, files: List[Path], path_in_repo: str = "", batch_name: str = "batch"
    ):
        """Upload de lote de arquivos"""
        logger.info(f"\n📤 Upload do lote: {batch_name}")
        logger.info(f"   Arquivos: {len(files)}")

        for file_path in files:
            if not file_path.exists():
                logger.warning(f"⚠️  Arquivo não encontrado: {file_path}")
                continue

            try:
                # Caminho relativo no repo
                file_name = file_path.name
                repo_path = f"{path_in_repo}/{file_name}" if path_in_repo else file_name

                # Upload
                logger.info(f"   Uploading: {file_name} → {repo_path}")

                self.api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=repo_path,
                    repo_id=self.repo_id,
                    repo_type="dataset",
                )

                logger.info(f"   ✓ {file_name} enviado com sucesso")

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"   ❌ Erro ao enviar {file_path.name}: {e}")

    def upload_strategic_batches(self):
        """Upload em lotes estratégicos"""
        logger.info("\n" + "=" * 80)
        logger.info("🚀 INICIANDO UPLOAD ESTRATÉGICO PARA HUGGING FACE")
        logger.info("=" * 80)

        # Lote 1: JSON Principal (unified_products.json)
        logger.info("\n📊 LOTE 1: JSON Principal")
        json_main = self.base_path / "unified_products.json"
        if json_main.exists():
            self.upload_batch(
                files=[json_main], path_in_repo="data", batch_name="JSON Principal"
            )

        # Lote 2: CSVs de Categorias (exports/csv/)
        logger.info("\n📊 LOTE 2: CSVs por Categoria")
        csv_dir = self.base_path / "exports" / "csv"
        if csv_dir.exists():
            csv_files = list(csv_dir.glob("*.csv"))
            self.upload_batch(
                files=csv_files,
                path_in_repo="data/csv/categories",
                batch_name="CSVs por Categoria",
            )

        # Lote 3: CSVs Unificados (exports/unified/)
        logger.info("\n📊 LOTE 3: CSVs Unificados Multi-Distribuidor")
        unified_dir = self.base_path / "exports" / "unified"
        if unified_dir.exists():
            # Dividir em sub-lotes

            # 3.1: CSVs de Fabricantes
            manufacturer_files = list(unified_dir.glob("manufacturer_*.csv"))
            if manufacturer_files:
                self.upload_batch(
                    files=manufacturer_files,
                    path_in_repo="data/csv/manufacturers",
                    batch_name="CSVs de Fabricantes",
                )

            # 3.2: CSVs de Categorias Unificadas
            category_files = list(unified_dir.glob("category_*.csv"))
            if category_files:
                self.upload_batch(
                    files=category_files,
                    path_in_repo="data/csv/unified_categories",
                    batch_name="CSVs de Categorias Unificadas",
                )

            # 3.3: CSVs de Comparação de Preços
            price_files = [
                unified_dir / "price_comparison_multi_distributor.csv",
                unified_dir / "panel_models_pricing.csv",
            ]
            price_files = [f for f in price_files if f.exists()]
            if price_files:
                self.upload_batch(
                    files=price_files,
                    path_in_repo="data/csv/price_analysis",
                    batch_name="CSVs de Análise de Preços",
                )

            # 3.4: CSV Mestre
            master_file = unified_dir / "all_products_unified.csv"
            if master_file.exists():
                self.upload_batch(
                    files=[master_file],
                    path_in_repo="data/csv",
                    batch_name="CSV Mestre Unificado",
                )

        # Lote 4: JSONs dos Distribuidores (opcional)
        logger.info("\n📊 LOTE 4: JSONs por Distribuidor")
        distributors = ["fortlev", "fotus", "neosolar", "solfacil", "odex"]

        for dist in distributors:
            dist_path = self.base_path / "distributors" / dist
            if not dist_path.exists():
                continue

            # Pegar JSONs principais (não backups)
            json_files = [
                f
                for f in dist_path.glob("*.json")
                if "backup" not in f.name.lower()
                and "mapping" not in f.name.lower()
                and f.stat().st_size < 10 * 1024 * 1024  # Menor que 10MB
            ]

            if json_files:
                # Limitar a 5 arquivos mais importantes
                json_files = sorted(
                    json_files, key=lambda f: f.stat().st_size, reverse=True
                )[:5]

                self.upload_batch(
                    files=json_files,
                    path_in_repo=f"data/distributors/{dist}",
                    batch_name=f"JSONs {dist.upper()}",
                )

        logger.info("\n" + "=" * 80)
        logger.info("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 80)
        logger.info(f"\n🔗 Repositório: https://huggingface.co/datasets/{self.repo_id}")

    def create_readme(self):
        """Cria README.md para o dataset"""
        readme_content = f"""---
license: cc-by-4.0
task_categories:
- tabular-classification
- tabular-regression
tags:
- solar-energy
- photovoltaic
- pricing
- brazil
- energy
size_categories:
- 1K<n<10K
---

# YSH Solar Products Dataset - Brazil

## Descrição

Dataset completo de produtos solares fotovoltaicos de múltiplos distribuidores brasileiros.

## Conteúdo

- **2.914 produtos** de 5 distribuidores
- **Kits solares**: on-grid, off-grid, híbridos
- **Painéis solares**: diversos fabricantes e potências
- **Inversores**: grid-tie, micro-inversores, híbridos
- **Baterias**: múltiplas capacidades e voltagens

## Estrutura

```
data/
├── unified_products.json          # JSON completo com todos os produtos
├── csv/
│   ├── all_products_unified.csv   # CSV mestre
│   ├── categories/                # CSVs por categoria
│   ├── manufacturers/             # CSVs por fabricante
│   ├── unified_categories/        # Categorias unificadas
│   └── price_analysis/            # Análise de preços
└── distributors/                  # Dados por distribuidor
```

## Campos Principais

- **id**: Identificador único
- **name**: Nome do produto
- **distributor**: Distribuidor (Fortlev, Fotus, NeoSolar, etc)
- **category**: Categoria (kits, panels, inverters, batteries)
- **power_kwp**: Potência em kWp
- **price_brl**: Preço em BRL
- **price_per_wp**: Custo por Wp
- **components**: Detalhes de painéis, inversores, baterias
- **manufacturer**: Fabricantes dos componentes

## Uso

### Python
```python
import pandas as pd

# Carregar CSV mestre
df = pd.read_csv('data/csv/all_products_unified.csv')

# Análise de preços
price_comparison = pd.read_csv('data/csv/price_analysis/price_comparison_multi_distributor.csv')
```

### R
```r
library(readr)

# Carregar dados
products <- read_csv("data/csv/all_products_unified.csv")
```

## Licença

CC-BY-4.0 - Atribuição requerida

## Fonte

Dados coletados de plataformas B2B de distribuidores solares brasileiros (Outubro 2025).

## Atualização

Última atualização: 20 de Outubro de 2025
"""

        readme_path = self.base_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        logger.info("📄 README.md criado")

        # Upload do README
        try:
            self.api.upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=self.repo_id,
                repo_type="dataset",
            )
            logger.info("✅ README.md enviado")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar README: {e}")


def main():
    """Função principal"""

    # Configuração
    REPO_ID = "fernando-bold/ysh-solar-products-brazil"

    # Token pode ser passado via env var HF_TOKEN
    token = os.getenv("HF_TOKEN")

    if not token:
        logger.warning(
            "⚠️  Token não encontrado!\n"
            "   Configure: export HF_TOKEN='seu_token_aqui'\n"
            "   Ou obtenha em: https://huggingface.co/settings/tokens"
        )
        return

    try:
        # Criar uploader
        uploader = HuggingFaceUploader(repo_id=REPO_ID, token=token)

        # Criar repositório
        uploader.create_repository()

        # Criar README
        uploader.create_readme()

        # Upload estratégico
        uploader.upload_strategic_batches()

    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        raise


if __name__ == "__main__":
    main()
