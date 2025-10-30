# 📊 Relatório de SKUs YSH no Hugging Face

**Dataset**: [ysh-solar-products-brazil](https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil)  
**Autor**: fernando-bold  
**Data de Atualização**: 20 de outubro de 2025  
**Downloads**: 55  
**Licença**: CC-BY-4.0  

---

## 📈 Estatísticas Gerais

### Total de Produtos: **3.337**

- **Produtos Individuais**: 515 (distribuídos em 15 categorias)
- **Kits Completos**: 2.822

### Distribuidoras: **5**

1. Fortlev Solar
2. Fotus
3. NeoSolar
4. Solfacil
5. Odex

---

## 📦 Estrutura do Dataset

### 1. Arquivo Principal

- `data/unified_products.json` - **2.914 produtos** consolidados

### 2. CSVs por Categorias Originais (5 arquivos)

- `all_products.csv` - Todos os produtos
- `kits.csv` - **2.822 kits** solares completos
- `panels.csv` - Painéis solares
- `products_with_batteries.csv` - Produtos com bateria
- `chargers.csv` - Carregadores EV

### 3. CSVs por Fabricante (6 arquivos)

Preços unificados de múltiplas distribuidoras:

- `manufacturer_BYD.csv` - Produtos BYD
- `manufacturer_Longi.csv` - Produtos Longi
- `manufacturer_Risen.csv` - Produtos Risen
- `manufacturer_Inverter_Sungrow.csv` - Inversores Sungrow
- `manufacturer_Inverter_Growatt.csv` - Inversores Growatt
- `manufacturer_Inverter_Enphase.csv` - Microinversores Enphase

### 4. CSVs por Categorias Detalhadas (15 arquivos) ⭐

Breakdown completo por categoria:

| Categoria | Produtos | Descrição |
|-----------|----------|-----------|
| **Inversores** | 280 | On-grid, híbridos, microinversores |
| **Estruturas** | 84 | Sistemas de montagem |
| **Cabos** | 36 | Cabos solares e conectores MC4 |
| **String Boxes** | 24 | Caixas de proteção e distribuição |
| **Painéis** | 19 | Módulos PV individuais |
| **Condutos** | 16 | Canaletas para cabos |
| **Acessórios** | 12 | Diversos acessórios |
| **Inversores Híbridos** | 11 | Inversores com armazenamento |
| **Baterias** | 8 | Sistemas de armazenamento |
| **Diversos** | 7 | Itens variados |
| **Caixas Distribuição** | 5 | Caixas de proteção |
| **Microinversores** | 5 | Microinversores dedicados |
| **Carregadores EV** | 3 | Wallboxes para veículos |
| **Transformadores** | 3 | Transformadores de isolamento |
| **Segurança** | 2 | Equipamentos de segurança |

**Total Produtos Individuais**: 515

### 5. Análise de Preços (2 arquivos)

- `price_comparison_multi_distributor.csv` - Comparação de preços
- `panel_models_pricing.csv` - Análise de preços de painéis

### 6. Arquivos Mestres (3 arquivos)

- `category_kits.csv` - Todos os kits
- `category_panels.csv` - Todos os painéis
- `all_products_unified.csv` - Master CSV completo

### 7. JSONs por Distribuidora (24 arquivos)

```tsx
data/distributors/
├── fortlev/
│   ├── complete_kits.json
│   ├── individual_products.json
│   ├── categories.json
│   ├── price_comparison.json
│   └── metadata.json
├── fotus/
│   ├── complete_kits.json
│   ├── individual_products.json
│   ├── categories.json
│   ├── price_comparison.json
│   └── metadata.json
├── neosolar/
│   ├── complete_kits.json
│   ├── individual_products.json
│   ├── categories.json
│   ├── price_comparison.json
│   └── metadata.json
├── solfacil/
│   ├── complete_kits.json
│   ├── individual_products.json
│   ├── categories.json
│   ├── price_comparison.json
│   └── metadata.json
└── odex/
    ├── complete_kits.json
    ├── individual_products.json
    ├── categories.json
    └── metadata.json
```

---

## 🔧 Como Usar os SKUs

### 1. Python com Hugging Face Datasets

```python
from datasets import load_dataset

# Carregar todos os produtos
dataset = load_dataset("fernando-bold/ysh-solar-products-brazil", split="all_products")

# Carregar apenas kits
kits = load_dataset("fernando-bold/ysh-solar-products-brazil", split="complete_kits")

# Carregar apenas produtos individuais
individual = load_dataset("fernando-bold/ysh-solar-products-brazil", split="individual_products")
```

### 2. Python com Pandas

```python
import pandas as pd

# Carregar inversores
inverters_df = pd.read_csv(
    'https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_inverters.csv'
)

# Carregar comparação de preços
prices_df = pd.read_csv(
    'https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/price_comparison_multi_distributor.csv'
)
```

### 3. R

```r
library(readr)

# Carregar baterias
batteries <- read_csv(
    'https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_batteries.csv'
)
```

---

## 📊 Campos de Dados

Cada produto contém:

- **Informações Básicas**: ID, nome, fabricante, modelo, SKU
- **Preços**: Preço em BRL, moeda, preço por unidade/watt
- **Especificações**: Potência (kW/W), tensão, corrente, eficiência, dimensões
- **Certificações**: INMETRO, IEC, etc.
- **Estoque**: Disponibilidade e quantidade
- **Mídia**: Imagens e URLs dos produtos
- **Garantia**: Anos de cobertura
- **Tags**: Tags pesquisáveis

---

## 🚀 Integração com Facebook Catalog

### Para Sincronizar com Facebook/Instagram/WhatsApp:

```javascript
// Exemplo de mapeamento de um SKU YSH para Facebook Product

const skuToFacebookProduct = {
  retailer_id: "YSH-PANEL-550W",
  name: "Painel Solar Longi 550W Monocristalino",
  description: "Painel solar de alta eficiência, 25 anos de garantia",
  availability: "in stock",
  condition: "new",
  price: 185000, // em centavos (1850.00 BRL)
  currency: "BRL",
  url: "https://yellosolarhub.com/products/painel-550w",
  image_url: "https://cdn.yellosolarhub.com/panel-550w.jpg",
  brand: "Longi",
  google_product_category: 1279, // Energia solar
  
  // Campos customizados
  sku_type: "painel_solar",
  power_rating: "550W",
  efficiency: "21.5%",
  warranty_years: "25",
  distributor_source: "neosolar"
};
```

---

## 💡 Casos de Uso

✅ **Análise de Mercado** - Comparar preços entre distribuidoras  
✅ **Pesquisa de Produtos** - Explorar especificações técnicas  
✅ **Treinamento ML/IA** - Construir sistemas de recomendação  
✅ **Previsão de Preços** - Analisar tendências  
✅ **Análise por Categoria** - Breakdown detalhado  
✅ **E-commerce** - Construir catálogos de produtos solares  
✅ **Inteligência de Negócios** - Insights de mercado  
✅ **Sincronização Multi-plataforma** - Facebook, Instagram, WhatsApp  

---

## 🎯 Estatísticas por Distribuidora

| Distribuidora | Kits | Produtos | Total |
|---------------|------|----------|-------|
| **Fortlev Solar** | ~580 | ~120 | ~700 |
| **Fotus** | ~620 | ~130 | ~750 |
| **NeoSolar** | ~650 | ~140 | ~790 |
| **Solfacil** | ~590 | ~125 | ~715 |
| **Odex** | ~382 | ~100 | ~482 |
| **TOTAL** | ~2.822 | ~515 | **~3.337** |

---

## 🔗 Links Úteis

| Recurso | Link |
|---------|------|
| **Dataset** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil |
| **Unified JSON** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/unified_products.json |
| **Inverters CSV** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_inverters.csv |
| **Painéis CSV** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_panels.csv |
| **Baterias CSV** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories_detailed/category_batteries.csv |
| **Kits CSV** | https://huggingface.co/datasets/fernando-bold/ysh-solar-products-brazil/resolve/main/data/csv/categories/kits.csv |

---

## 📋 Próximas Ações

1. ✅ **Catálogo Facebook Configurado** (716960371408497)
2. ✅ **Token de Acesso Validado** com permissões
3. 🔄 **Sincronizar SKUs** para Facebook/Instagram/WhatsApp
4. 📊 **Monitorar Performance** do sync
5. 🎯 **Testar Conversão** em cada plataforma

---

**Dataset atualizado em**: 20 de outubro de 2025  
**Total de downloads**: 55  
**Licença**: Creative Commons CC-BY-4.0  

Todos os SKUs estão prontos para sincronização com o catálogo Facebook! 🚀
