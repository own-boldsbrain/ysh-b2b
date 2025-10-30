# 📊 Dados

Dados processados e consolidados do catálogo.

## 📂 Estrutura

### 🔗 unified/

Dados unificados consolidados.

- **`unified_products.json`** (4.6 MB) - **Arquivo principal**
  - 2.914 produtos consolidados
  - 5 distribuidores
  - Schema completo
  - Formato: JSON array

### 📋 metadata/

Metadados e índices auxiliares.

- `manufacturers_unified_list.json` - Lista de fabricantes (3.6 KB)
- `product_series_analysis.json` - Análise de séries (7.1 KB)
- `technology_matrix.json` - Matriz tecnológica (0.2 KB)
- `unified_product_blueprint.json` - Blueprint do schema (4.7 KB)
- `datasheet_search_list.json` - Lista de datasheets (39.1 KB)
- `datasheet_search_list.csv` - Lista em CSV (14.5 KB)

## 📊 Estatísticas

### unified_products.json

```json
{
  "total_products": 2914,
  "distributors": 5,
  "categories": {
    "kits": 2822,
    "panels": 92
  },
  "file_size": "4.6 MB",
  "encoding": "UTF-8"
}
```

### Metadados

- **Fabricantes**: ~50 manufacturers
- **Séries de Produtos**: Análise completa
- **Datasheets**: 127 modelos identificados

## 🔧 Uso

### Carregar JSON Principal

```python
import json

with open('unified/unified_products.json', encoding='utf-8') as f:
    products = json.load(f)

# Total de produtos
print(f"Total: {len(products)}")

# Produtos por distribuidor
from collections import Counter
dist_count = Counter(p['distributor'] for p in products)
print(dist_count)
```

### Carregar Metadados

```python
# Fabricantes
with open('metadata/manufacturers_unified_list.json') as f:
    manufacturers = json.load(f)

# Séries
with open('metadata/product_series_analysis.json') as f:
    series = json.load(f)

# Datasheets
import pandas as pd
datasheets = pd.read_csv('metadata/datasheet_search_list.csv')
```

## 📝 Schema de Dados

### Produto Base

```json
{
  "id": "string",
  "name": "string",
  "distributor": "string",
  "category": "string",
  "type": "string",
  "pricing": {
    "price_brl": "float",
    "price_per_wp": "float",
    "currency": "string"
  },
  "power": {
    "kwp": "float",
    "watts": "float"
  },
  "components": {
    "panels": [],
    "inverters": [],
    "batteries": [],
    "structures": []
  },
  "specifications": {},
  "media": {},
  "metadata": {}
}
```

## 🔄 Atualização

Dados atualizados em: **20/10/2025**

Para atualizar:

```bash
# Re-executar extração
python ../📁_SCRIPTS/extraction/unified_product_extractor.py

# Re-gerar unificação
python ../📁_SCRIPTS/unification/unify_all_categories.py
```
