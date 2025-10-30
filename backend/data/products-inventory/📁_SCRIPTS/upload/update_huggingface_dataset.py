#!/usr/bin/env python3
"""
Atualizador do Dataset Hugging Face
Adiciona os novos CSVs de categorias ao dataset existente
"""

import os
import time
from pathlib import Path
from huggingface_hub import HfApi, login
from typing import List, Tuple


class HuggingFaceUpdater:
    """Atualiza dataset no Hugging Face com novos arquivos"""

    def __init__(self, repo_id: str = "fernando-bold/ysh-solar-products-brazil"):
        self.repo_id = repo_id
        self.api = HfApi()
        self.base_dir = Path(__file__).parent
        self.categories_dir = self.base_dir / "exports" / "unified_categories"

        # Login
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN não encontrado nas variáveis de ambiente")
        login(token=token)

    def scan_new_files(self) -> List[Tuple[Path, str]]:
        """Escaneia novos CSVs de categorias"""
        files_to_upload = []

        if not self.categories_dir.exists():
            print("⚠️  Diretório de categorias não encontrado")
            return files_to_upload

        for csv_file in sorted(self.categories_dir.glob("*.csv")):
            # Path no HF será: data/csv/categories_detailed/category_*.csv
            path_in_repo = f"data/csv/categories_detailed/{csv_file.name}"
            files_to_upload.append((csv_file, path_in_repo))

        return files_to_upload

    def upload_files(self, files: List[Tuple[Path, str]]):
        """Faz upload dos arquivos para o HF"""
        print(f"\n{'='*80}")
        print(f"📤 INICIANDO UPLOAD DE {len(files)} ARQUIVOS")
        print(f"{'='*80}\n")

        total_size = sum(f[0].stat().st_size for f in files)
        total_size_mb = total_size / (1024 * 1024)

        print(f"📊 Tamanho total: {total_size_mb:.2f} MB")
        print(f"🎯 Repositório: {self.repo_id}\n")

        success_count = 0
        failed_count = 0

        for i, (local_path, repo_path) in enumerate(files, 1):
            try:
                file_size_kb = local_path.stat().st_size / 1024
                print(
                    f"[{i}/{len(files)}] Enviando: {local_path.name} ({file_size_kb:.2f} KB)"
                )
                print(f"           → {repo_path}")

                self.api.upload_file(
                    path_or_fileobj=str(local_path),
                    path_in_repo=repo_path,
                    repo_id=self.repo_id,
                    repo_type="dataset",
                    commit_message=f"Add {local_path.name} - Categoria detalhada",
                )

                print(f"           ✅ Upload concluído\n")
                success_count += 1

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"           ❌ Erro: {e}\n")
                failed_count += 1

        # Sumário
        print(f"\n{'='*80}")
        print(f"✅ UPLOAD FINALIZADO")
        print(f"{'='*80}")
        print(f"\n📊 RESULTADOS:")
        print(f"  • Sucesso: {success_count} arquivos")
        print(f"  • Falhas: {failed_count} arquivos")
        print(f"  • Total: {len(files)} arquivos")

        if failed_count == 0:
            print(f"\n🎉 TODOS OS ARQUIVOS FORAM ENVIADOS COM SUCESSO!")

        print(f"\n🔗 Dataset: https://huggingface.co/datasets/{self.repo_id}")

    def update_readme(self):
        """Atualiza README.md com informações das novas categorias"""
        print(f"\n{'='*80}")
        print(f"📝 ATUALIZANDO README.md")
        print(f"{'='*80}\n")

        readme_content = f"""# YSH Solar Products - Brazil Market Dataset

Comprehensive dataset of solar energy products from major Brazilian distributors.

**Last Updated:** 2025-10-20

## 📊 Dataset Overview

This dataset contains **3,337 solar products** from **5 major Brazilian distributors**:
- Fortlev Solar
- Fotus
- NeoSolar  
- Solfacil
- Odex

## 📦 Dataset Structure

### 1. Main Files
- `data/unified_products.json` - Complete consolidated product database (2,914 products)

### 2. CSV by Original Categories (5 files)
- `data/csv/categories/all_products.csv` - All products flattened
- `data/csv/categories/kits.csv` - Complete solar kits (2,822 products)
- `data/csv/categories/panels.csv` - Solar panels
- `data/csv/categories/products_with_batteries.csv` - Products with battery storage
- `data/csv/categories/chargers.csv` - EV chargers

### 3. CSV by Manufacturers (6 files)
Unified CSVs organized by manufacturer with multi-distributor pricing:
- `data/csv/manufacturers/manufacturer_BYD.csv`
- `data/csv/manufacturers/manufacturer_Longi.csv`
- `data/csv/manufacturers/manufacturer_Risen.csv`
- `data/csv/manufacturers/manufacturer_Inverter_Sungrow.csv`
- `data/csv/manufacturers/manufacturer_Inverter_Growatt.csv`
- `data/csv/manufacturers/manufacturer_Inverter_Enphase.csv`

### 4. CSV by Detailed Categories (15 files) - NEW! 🆕
Comprehensive breakdown by product category:

- `data/csv/categories_detailed/category_inverters.csv` - **280 products** - On-grid inverters
- `data/csv/categories_detailed/category_structures.csv` - **84 products** - Mounting systems
- `data/csv/categories_detailed/category_cables.csv` - **36 products** - Solar cables & connectors
- `data/csv/categories_detailed/category_stringboxes.csv` - **24 products** - String protection boxes
- `data/csv/categories_detailed/category_panels.csv` - **19 products** - Individual PV modules
- `data/csv/categories_detailed/category_conduits.csv` - **16 products** - Cable conduits
- `data/csv/categories_detailed/category_accessories.csv` - **12 products** - Various accessories
- `data/csv/categories_detailed/category_hybrid_inverters.csv` - **11 products** - Hybrid inverters
- `data/csv/categories_detailed/category_batteries.csv` - **8 products** - Energy storage systems
- `data/csv/categories_detailed/category_miscellaneous.csv` - **7 products** - Miscellaneous items
- `data/csv/categories_detailed/category_boxes.csv` - **5 products** - Distribution boxes
- `data/csv/categories_detailed/category_microinverters.csv` - **5 products** - Microinverters
- `data/csv/categories_detailed/category_ev_chargers.csv` - **3 products** - EV wallboxes
- `data/csv/categories_detailed/category_transformers.csv` - **3 products** - Isolation transformers
- `data/csv/categories_detailed/category_security.csv` - **2 products** - Security equipment

**Total Individual Products: 515 across 15 categories**

### 5. Price Analysis (2 files)
- `data/csv/price_comparison_multi_distributor.csv` - Multi-distributor price comparison
- `data/csv/panel_models_pricing.csv` - Panel models pricing analysis

### 6. Master Files (2 files)
- `data/csv/category_kits.csv` - All kits unified
- `data/csv/category_panels.csv` - All panels unified
- `data/csv/all_products_unified.csv` - Complete master CSV

### 7. Distributor JSONs (24 files)
Individual JSON files organized by distributor in `data/distributors/`:
- **Fortlev** (5 files)
- **Fotus** (5 files)
- **NeoSolar** (5 files)
- **Solfacil** (5 files)
- **Odex** (4 files)

## 🎯 Use Cases

- **Market Analysis**: Compare prices across distributors
- **Product Research**: Explore solar equipment specifications
- **ML/AI Training**: Build recommendation systems
- **Price Prediction**: Analyze pricing trends
- **Category Analysis**: Detailed breakdown by product type

## 📊 Statistics

- **Total Products**: 3,337
  - Individual Products: 515 (15 categories)
  - Complete Kits: 2,822
- **Distributors**: 5
- **CSV Files**: 31 total
  - Original categories: 5
  - Manufacturers: 6
  - Detailed categories: 15 (NEW!)
  - Price analysis: 2
  - Master files: 3
- **JSON Files**: 25 (1 unified + 24 distributor-specific)

## 🔧 Usage Examples

### Python (Pandas)
```python
import pandas as pd

# Load inverters category
inverters_df = pd.read_csv('hf://datasets/fernando-bold/ysh-solar-products-brazil/data/csv/categories_detailed/category_inverters.csv')

# Load complete kits
kits_df = pd.read_csv('hf://datasets/fernando-bold/ysh-solar-products-brazil/data/csv/categories/kits.csv')

# Load multi-distributor price comparison
prices_df = pd.read_csv('hf://datasets/fernando-bold/ysh-solar-products-brazil/data/csv/price_comparison_multi_distributor.csv')
```

### R
```r
library(readr)

# Load batteries category
batteries <- read_csv('https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_batteries.csv')

# Load panels
panels <- read_csv('https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_panels.csv')
```

### Direct JSON Access
```python
import json
import requests

url = 'https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/unified_products.json'
response = requests.get(url)
products = response.json()
```

## 📝 Data Schema

Each product contains:
- **Basic Info**: ID, name, manufacturer, model, SKU
- **Pricing**: BRL price, currency, price per unit
- **Specifications**: Power, voltage, current, efficiency, dimensions
- **Certifications**: INMETRO, etc.
- **Stock**: Availability and quantity
- **Media**: Product images
- **Warranty**: Years of coverage

## 🏷️ Categories

### Equipment Categories
- **Inverters**: On-grid, hybrid, and microinverters
- **Solar Panels**: Monocrystalline and polycrystalline modules
- **Batteries**: Lithium and lead-acid storage systems
- **Structures**: Roof and ground mounting systems
- **String Boxes**: Protection and distribution
- **Cables**: Solar cables and MC4 connectors
- **EV Chargers**: Wallboxes for electric vehicles
- **Accessories**: Tools, conduits, boxes, security

### System Types
- **Complete Kits**: Ready-to-install solar systems
- **Individual Components**: Standalone products

## 📄 License

**CC-BY-4.0** - Attribution required

## 🤝 Contributing

Contributions welcome! Please ensure data quality and consistency.

## 📧 Contact

For questions or suggestions, open an issue on the dataset repository.

---

**Note**: Prices and availability subject to change. Always verify with distributors.
"""

        try:
            # Upload README
            self.api.upload_file(
                path_or_fileobj=readme_content.encode("utf-8"),
                path_in_repo="README.md",
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message="Update README with detailed categories information",
            )

            print("✅ README.md atualizado com sucesso!")

        except Exception as e:
            print(f"❌ Erro ao atualizar README: {e}")

    def run(self):
        """Executa atualização completa"""
        print("\n" + "=" * 80)
        print("🚀 ATUALIZADOR DE DATASET - HUGGING FACE")
        print("=" * 80)
        print(f"📦 Repositório: {self.repo_id}\n")

        # Escanear arquivos
        files = self.scan_new_files()

        if not files:
            print("⚠️  Nenhum arquivo novo encontrado")
            return

        print(f"📋 Arquivos encontrados: {len(files)}\n")
        for local_path, repo_path in files:
            size_kb = local_path.stat().st_size / 1024
            print(f"  • {local_path.name:35} → {repo_path} ({size_kb:.2f} KB)")

        # Confirmar upload
        print(f"\n{'='*80}")
        response = input("Deseja prosseguir com o upload? (s/n): ")

        if response.lower() != "s":
            print("\n❌ Upload cancelado pelo usuário")
            return

        # Upload files
        self.upload_files(files)

        # Update README
        self.update_readme()

        print(f"\n{'='*80}")
        print("✅ ATUALIZAÇÃO COMPLETA!")
        print(f"{'='*80}")
        print(f"\n🔗 Acesse: https://huggingface.co/datasets/{self.repo_id}\n")


def main():
    updater = HuggingFaceUpdater()
    updater.run()


if __name__ == "__main__":
    main()
