#!/usr/bin/env python3
"""
Fix Hugging Face README.md with proper YAML metadata
"""

import os
from huggingface_hub import HfApi, login


def create_readme_with_metadata():
    """Cria README com YAML metadata correto"""

    readme_content = """---
language:
- pt
- en
license: cc-by-4.0
size_categories:
- 1K<n<10K
task_categories:
- tabular-classification
- tabular-regression
tags:
- solar-energy
- renewable-energy
- brazil
- market-analysis
- price-comparison
- ecommerce
- photovoltaic
- inverters
- solar-panels
- batteries
pretty_name: YSH Solar Products - Brazil Market
dataset_info:
  features:
  - name: distributor
    dtype: string
  - name: id
    dtype: string
  - name: name
    dtype: string
  - name: manufacturer
    dtype: string
  - name: model
    dtype: string
  - name: category
    dtype: string
  - name: price_brl
    dtype: float64
  - name: power_kw
    dtype: float64
  splits:
  - name: all_products
    num_bytes: 4492800
    num_examples: 2914
  - name: individual_products
    num_bytes: 91615
    num_examples: 515
  - name: complete_kits
    num_bytes: 4401185
    num_examples: 2822
  download_size: 7220000
  dataset_size: 8985600
configs:
- config_name: default
  data_files:
  - split: all_products
    path: data/unified_products.json
  - split: individual_products
    path: data/csv/categories_detailed/*.csv
  - split: complete_kits
    path: data/csv/categories/kits.csv
---

# YSH Solar Products - Brazil Market Dataset

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

### 4. CSV by Detailed Categories (15 files) 🆕
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

### 6. Master Files (3 files)
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
- **E-commerce**: Build solar product catalogs
- **Business Intelligence**: Market insights and trends

## 📊 Statistics

- **Total Products**: 3,337
  - Individual Products: 515 (15 categories)
  - Complete Kits: 2,822
- **Distributors**: 5
- **CSV Files**: 31 total
  - Original categories: 5
  - Manufacturers: 6
  - Detailed categories: 15
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

### Using Hugging Face Datasets Library
```python
from datasets import load_dataset

# Load all products
dataset = load_dataset("fernando-bold/ysh-solar-products-brazil", split="all_products")

# Load individual products only
individual = load_dataset("fernando-bold/ysh-solar-products-brazil", split="individual_products")

# Load complete kits only
kits = load_dataset("fernando-bold/ysh-solar-products-brazil", split="complete_kits")
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
- **Pricing**: BRL price, currency, price per unit/watt
- **Specifications**: Power (kW/W), voltage, current, efficiency, dimensions
- **Certifications**: INMETRO, IEC, etc.
- **Stock**: Availability and quantity
- **Media**: Product images and URLs
- **Warranty**: Years of coverage
- **Tags**: Searchable product tags

## 🏷️ Categories

### Equipment Categories
- **Inverters**: On-grid, hybrid, and microinverters (296 total)
- **Solar Panels**: Monocrystalline and polycrystalline modules
- **Batteries**: Lithium and lead-acid storage systems
- **Structures**: Roof and ground mounting systems (84 products)
- **String Boxes**: Protection and distribution (24 products)
- **Cables**: Solar cables and MC4 connectors (36 products)
- **EV Chargers**: Wallboxes for electric vehicles
- **Accessories**: Tools, conduits, boxes, security

### System Types
- **Complete Kits**: Ready-to-install solar systems (2,822 products)
- **Individual Components**: Standalone products (515 products)

## 🌍 Geographic Coverage

**Primary Market**: Brazil
- All prices in Brazilian Real (BRL)
- Products comply with Brazilian regulations (INMETRO)
- Distributors located across Brazil

## 📄 License

**CC-BY-4.0** - Attribution required

When using this dataset, please cite:
```
YSH Solar Products - Brazil Market Dataset
Available at: https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil
```

## 🤝 Contributing

Contributions welcome! Please ensure data quality and consistency.

## 📧 Contact

For questions or suggestions, open an issue on the dataset repository.

## 🔄 Updates

- **2025-10-20**: Added 15 detailed category CSVs (515 individual products)
- **2025-10-19**: Initial release with kits and unified products

---

**Note**: Prices and availability subject to change. Always verify with distributors before making purchase decisions.
"""

    return readme_content


def main():
    """Atualiza README com metadata correto"""

    print("\n" + "=" * 80)
    print("🔧 CORRIGINDO YAML METADATA DO README.MD")
    print("=" * 80 + "\n")

    # Login
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN não encontrado")

    login(token=token)

    # Criar README
    readme = create_readme_with_metadata()

    # Upload
    api = HfApi()
    repo_id = "fernando-bold/ysh-solar-products-brazil"

    try:
        print("📤 Enviando README.md com YAML metadata...")

        api.upload_file(
            path_or_fileobj=readme.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Fix: Add proper YAML metadata to README",
        )

        print("✅ README.md atualizado com sucesso!")
        print(f"\n🔗 https://huggingface.co/datasets/{repo_id}\n")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
