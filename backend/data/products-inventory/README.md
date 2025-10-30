---
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
