# 📑 Índice Completo - Products Inventory

## 🚀 Quick Start

**Novo aqui?** Comece por:

1. **README.md** - Visão geral do dataset
2. **START_HERE.md** - Guia completo de início
3. **📊_DATA/unified/unified_products.json** - Arquivo principal de dados

## 📁 Estrutura Organizacional

### 🔧 Scripts (`📁_SCRIPTS/`)

Todas as ferramentas de processamento organizadas por função:

#### Exportação (`export/`)

- `export_to_csv.py` - Exporta para CSV por categoria
- `create_unified_csvs.py` - CSVs unificados por fabricante

#### Upload (`upload/`)

- `upload_to_huggingface.py` - Upload inicial completo
- `update_huggingface_dataset.py` - Atualizações incrementais
- `check_upload_preparation.py` - Validação pré-upload
- `fix_huggingface_readme.py` - Correção de metadata YAML

#### Extração (`extraction/`)

- `extract_datasheet_models.py` - Extrai modelos de datasheets
- `extract_manufacturers.py` - Extrai fabricantes únicos
- `extract_technical_specs.py` - Extrai specs técnicas
- `unified_product_extractor.py` - Extrator completo unificado

#### Unificação (`unification/`)

- `unify_all_categories.py` - Unifica todas as 15 categorias
- `unify_distributors.py` - Unifica dados entre distribuidores

#### Análise (`analysis/`)
- `generate_360_stats.py` - Estatísticas 360° completas

### 📚 Documentação (`📄_DOCS/`)

#### Inventários (`inventories/`)

**Kits Solares:**

- `KITS_INVENTORY.md` - Inventário completo (2.822 kits)
- `KITS_README.md` - Guia detalhado de kits

**Inversores:**

- `INVERSORES_README.md` - Guia completo
- `INVERSORES_INDEX.md` - Índice alfabético
- `INVERSORES_QUICK_REFERENCE.md` - Referência rápida
- `INVERSORES_CONSOLIDADO_360.md` - Análise 360° (280 inversores)

**Painéis Solares:**

- `PAINEIS_README.md` - Guia completo
- `PAINEIS_SOLARES_INDEX.md` - Índice alfabético
- `PAINEIS_QUICK_REFERENCE.md` - Referência rápida
- `PAINEIS_SOLARES_CONSOLIDADO_360.md` - Análise 360° (92 painéis)

**Geral:**
- `INDEX.md` - Índice geral

#### Reorganização (`reorganization/`)

- `REORGANIZATION_PLAN.md` - Plano original
- `REORGANIZATION_SUMMARY.md` - Resumo executivo
- `REORGANIZATION_EXECUTION_COMPLETE.md` - Execução completa
- `REORGANIZATION_FINAL_REVIEW.md` - Revisão final
- `REVIEW_SUMMARY.md` - Sumário de revisão
- `UNIFIED_EXTRACTION_REPORT.md` - Relatório de extração
- `DIVERGENCE_ANALYSIS_REPORT.md` - Análise de divergências

#### Técnica (`technical/`)

- `MANUFACTURERS_360_COMPLETE.md` - Análise 360° de fabricantes
- `MANUFACTURERS_360_REPORT.txt` - Relatório de fabricantes

### 📊 Dados (`📊_DATA/`)

#### Unificados (`unified/`)

- **`unified_products.json`** (4.6 MB) - **ARQUIVO PRINCIPAL**
  - 2.914 produtos consolidados
  - 5 distribuidores
  - Schema completo

#### Metadados (`metadata/`)
- `manufacturers_unified_list.json` - Lista de fabricantes (3.6 KB)
- `product_series_analysis.json` - Análise de séries (7.1 KB)
- `technology_matrix.json` - Matriz tecnológica (0.2 KB)
- `unified_product_blueprint.json` - Blueprint do schema (4.7 KB)
- `datasheet_search_list.json` - Lista de datasheets (39.1 KB)
- `datasheet_search_list.csv` - Lista em CSV (14.5 KB)

### 📤 Exports (`exports/`)

#### CSVs Originais (`csv/`)

- `all_products.csv` - Todos os produtos
- `kits.csv` - Kits solares
- `panels.csv` - Painéis
- `inverters.csv` - Inversores
- `batteries.csv` - Baterias

#### CSVs Unificados (`unified/`)

11 CSVs por distribuidor/fabricante/preço

#### CSVs por Categoria (`unified_categories/`)

15 categorias detalhadas:
- Inversores (280)
- Estruturas (84)
- Cabos (36)
- String Boxes (24)
- Painéis (19)
- Eletrodutos (16)
- Acessórios (12)
- Inversores Híbridos (11)
- Baterias (8)
- Diversos (7)
- Caixas (5)
- Microinversores (5)
- Carregadores EV (3)
- Transformadores (3)
- Segurança (2)

### 🏢 Distribuidores (`distributors/`)
JSONs originais de:
- Fortlev Solar
- Fotus
- NeoSolar
- Odex
- Solfacil

### 🔍 Schemas (`schemas/`)
- `unified_product_schema.json` - Schema JSON completo

### 📊 Analysis (`analysis/`)
Scripts de análise e estatísticas

### 🛠️ Scripts Utilitários (`scripts/`)
Scripts auxiliares diversos

## 📈 Estatísticas Rápidas

### Produtos
- **Total**: 3.337 produtos
  - Kits completos: 2.822
  - Produtos individuais: 515

### Categorias (15)
1. Inversores: 280
2. Estruturas: 84
3. Cabos: 36
4. String Boxes: 24
5. Painéis: 19
6. Eletrodutos: 16
7. Acessórios: 12
8. Inversores Híbridos: 11
9. Baterias: 8
10. Diversos: 7
11. Caixas: 5
12. Microinversores: 5
13. Carregadores EV: 3
14. Transformadores: 3
15. Segurança: 2

### Distribuidores (5)
- Fortlev Solar
- Fotus
- NeoSolar
- Solfacil
- Odex

## 🔗 Links Externos

- **Dataset Público**: [Hugging Face](https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil)

## 🗂️ Por Tipo de Tarefa

### Quero exportar dados
→ `📁_SCRIPTS/export/`

### Quero fazer upload
→ `📁_SCRIPTS/upload/`

### Quero extrair novos dados
→ `📁_SCRIPTS/extraction/`

### Quero unificar catálogos
→ `📁_SCRIPTS/unification/`

### Quero analisar dados
→ `📁_SCRIPTS/analysis/` e `📄_DOCS/inventories/`

### Quero os dados brutos
→ `📊_DATA/unified/unified_products.json`

### Quero CSVs prontos
→ `exports/unified_categories/`

## 📅 Última Atualização

**20 de Outubro de 2025**

---

**Navegação:**
- [⬆️ Voltar ao README](./README.md)
- [▶️ Começar Aqui](./START_HERE.md)
