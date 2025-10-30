# 📊 Guia Prático - Uso dos CSVs Exportados

**Público**: Equipe Comercial, Analistas de Dados, Desenvolvedores  
**Data**: 20 de Outubro de 2025

---

## 🎯 Quick Start

### Arquivos Disponíveis

```
exports/csv/
├── all_products.csv    (2.915 linhas | 683 KB) - Todos os produtos
├── kits.csv           (2.823 linhas | 666 KB) - Kits solares
└── panels.csv         (93 linhas   | 18 KB)  - Painéis individuais
```

---

## 💼 Para Equipe Comercial

### Abrir no Excel

1. **Método 1 - Duplo Clique**
   - Simplesmente dê duplo clique no arquivo `.csv`
   - O Excel abrirá automaticamente com encoding correto

2. **Método 2 - Importação Avançada**
   ```
   Excel → Dados → Obter Dados Externos → De Texto/CSV
   → Selecione o arquivo
   → Encoding: UTF-8
   → Delimitador: Vírgula
   → Importar
   ```

### Consultas Rápidas no Excel

#### Encontrar Kits por Fabricante de Painel
```
1. Abra kits.csv
2. Clique em qualquer célula com dados
3. Ctrl + Shift + L (ativar filtros)
4. Na coluna "panel_manufacturer", selecione "Longi"
```

#### Kits por Faixa de Preço
```
1. Filtro avançado na coluna "price_brl"
2. Selecione: "Entre" → 5000 e 10000
```

#### Ordenar por Melhor Preço/Wp
```
1. Selecione coluna "price_per_wp"
2. Dados → Classificar → Menor para Maior
```

### Criar Tabela Dinâmica

```
1. Selecione todos os dados (Ctrl + A)
2. Inserir → Tabela Dinâmica
3. Arraste campos:
   - Linhas: distributor, panel_manufacturer
   - Valores: Contagem de id, Média de price_per_wp
```

---

## 📊 Para Analistas (Power BI)

### Importar no Power BI

```
1. Power BI Desktop → Obter Dados → Texto/CSV
2. Selecione: all_products.csv
3. Transformar Dados (Power Query)
4. Verificar tipos de dados:
   - price_brl → Número Decimal
   - power_kwp → Número Decimal
   - total_panels → Número Inteiro
5. Fechar e Aplicar
```

### Medidas DAX Sugeridas

```dax
// Preço Médio por Watt
Preço Médio Wp = 
AVERAGE(products[price_per_wp])

// Total de Kits Disponíveis
Total Kits = 
COUNTROWS(FILTER(products, products[category] = "kits"))

// Potência Total Instalável
Potência Total = 
SUM(products[power_kwp])

// Ticket Médio por Distribuidor
Ticket Médio = 
AVERAGEX(
    VALUES(products[distributor]),
    CALCULATE(AVERAGE(products[price_brl]))
)
```

### Visuais Recomendados

1. **Gráfico de Barras**: Distribuidores x Quantidade de SKUs
2. **Gráfico de Dispersão**: Potência (kWp) x Preço (R$)
3. **Cartão**: Total de SKUs, Preço Médio, Potência Total
4. **Matriz**: Fabricante Painel x Fabricante Inversor (contagem)

---

## 💻 Para Desenvolvedores (Python)

### Instalar Dependências

```bash
pip install pandas numpy openpyxl
```

### Carregar e Explorar Dados

```python
import pandas as pd
import numpy as np

# Carregar CSVs
df_all = pd.read_csv('all_products.csv', encoding='utf-8-sig')
df_kits = pd.read_csv('kits.csv', encoding='utf-8-sig')
df_panels = pd.read_csv('panels.csv', encoding='utf-8-sig')

# Informações básicas
print(f"Total de produtos: {len(df_all)}")
print(f"\nColunas disponíveis:\n{df_all.columns.tolist()}")
print(f"\nCategorias: {df_all['category'].unique()}")
print(f"\nDistribuidores: {df_all['distributor'].unique()}")

# Estatísticas descritivas
print(df_kits[['power_kwp', 'price_brl', 'price_per_wp']].describe())
```

### Análises Práticas

#### 1. Top 10 Kits Mais Baratos por Wp

```python
top10_cheap = df_kits.nsmallest(10, 'price_per_wp')[
    ['name', 'power_kwp', 'price_brl', 'price_per_wp', 'distributor']
]
print(top10_cheap)
```

#### 2. Distribuição de Kits por Faixa de Potência

```python
# Criar bins de potência
bins = [0, 3, 5, 10, 20, 50, 100, 1000]
labels = ['0-3kWp', '3-5kWp', '5-10kWp', '10-20kWp', '20-50kWp', '50-100kWp', '100+kWp']

df_kits['power_range'] = pd.cut(df_kits['power_kwp'], bins=bins, labels=labels)

# Contar por faixa
distribution = df_kits['power_range'].value_counts().sort_index()
print(distribution)

# Plotar
import matplotlib.pyplot as plt
distribution.plot(kind='bar', title='Distribuição de Kits por Potência')
plt.ylabel('Quantidade de Kits')
plt.tight_layout()
plt.show()
```

#### 3. Análise de Preços por Fabricante de Painel

```python
# Filtrar kits com fabricante conhecido
df_with_manufacturer = df_kits[df_kits['panel_manufacturer'].notna()]

# Agrupar e calcular estatísticas
price_analysis = df_with_manufacturer.groupby('panel_manufacturer').agg({
    'price_per_wp': ['mean', 'median', 'min', 'max', 'count']
}).round(2)

price_analysis.columns = ['Média R$/Wp', 'Mediana R$/Wp', 'Mín R$/Wp', 'Máx R$/Wp', 'Qtd Kits']
print(price_analysis.sort_values('Média R$/Wp'))
```

#### 4. Matriz de Combinações (Painel x Inversor)

```python
# Criar tabela cruzada
combination_matrix = pd.crosstab(
    df_kits['panel_manufacturer'], 
    df_kits['inverter_manufacturer'],
    margins=True,
    margins_name='Total'
)

print("\n=== Combinações Painel x Inversor ===")
print(combination_matrix)

# Salvar em Excel
combination_matrix.to_excel('combination_matrix.xlsx')
```

#### 5. Análise de Competitividade

```python
# Calcular percentil de preços por faixa de potência
df_kits['price_percentile'] = df_kits.groupby('power_range')['price_per_wp'].rank(pct=True)

# Classificar competitividade
def classify_competitiveness(percentile):
    if percentile <= 0.25:
        return 'Muito Competitivo'
    elif percentile <= 0.50:
        return 'Competitivo'
    elif percentile <= 0.75:
        return 'Médio'
    else:
        return 'Alto'

df_kits['competitiveness'] = df_kits['price_percentile'].apply(classify_competitiveness)

# Produtos mais competitivos
competitive = df_kits[df_kits['competitiveness'] == 'Muito Competitivo']
print(f"\n{len(competitive)} kits muito competitivos encontrados")
print(competitive[['name', 'power_kwp', 'price_per_wp', 'distributor']].head(20))
```

### Exportar Análises

```python
# Criar Excel com múltiplas abas
with pd.ExcelWriter('analises_produtos.xlsx', engine='openpyxl') as writer:
    top10_cheap.to_excel(writer, sheet_name='Top 10 Baratos', index=False)
    distribution.to_excel(writer, sheet_name='Distribuição Potência')
    price_analysis.to_excel(writer, sheet_name='Preços por Fabricante')
    combination_matrix.to_excel(writer, sheet_name='Matriz Combinações')
    competitive.to_excel(writer, sheet_name='Mais Competitivos', index=False)

print("✅ Análises exportadas para analises_produtos.xlsx")
```

---

## 🗄️ Para Banco de Dados

### PostgreSQL

```sql
-- Criar tabela
CREATE TABLE products (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(500),
    distributor VARCHAR(50),
    category VARCHAR(50),
    type VARCHAR(100),
    power_kwp DECIMAL(10,2),
    power_watts DECIMAL(10,2),
    price_brl DECIMAL(10,2),
    price_per_wp DECIMAL(10,3),
    panel_manufacturer VARCHAR(100),
    panel_power_w INTEGER,
    inverter_manufacturer VARCHAR(100),
    inverter_power_kw DECIMAL(10,2),
    total_panels INTEGER,
    total_inverters INTEGER,
    total_batteries INTEGER,
    status VARCHAR(20),
    tags TEXT
);

-- Importar CSV
\COPY products FROM 'all_products.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- Criar índices
CREATE INDEX idx_category ON products(category);
CREATE INDEX idx_distributor ON products(distributor);
CREATE INDEX idx_price ON products(price_per_wp);
CREATE INDEX idx_power ON products(power_kwp);

-- Consultas úteis
-- Top 10 kits mais baratos
SELECT name, power_kwp, price_brl, price_per_wp, distributor
FROM products
WHERE category = 'kits'
ORDER BY price_per_wp ASC
LIMIT 10;

-- Estatísticas por distribuidor
SELECT 
    distributor,
    COUNT(*) as total_produtos,
    AVG(price_per_wp) as preco_medio_wp,
    MIN(price_brl) as preco_min,
    MAX(price_brl) as preco_max
FROM products
WHERE category = 'kits'
GROUP BY distributor
ORDER BY total_produtos DESC;
```

### MySQL

```sql
-- Criar tabela
CREATE TABLE products (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(500),
    distributor VARCHAR(50),
    category VARCHAR(50),
    type VARCHAR(100),
    power_kwp DECIMAL(10,2),
    power_watts DECIMAL(10,2),
    price_brl DECIMAL(10,2),
    price_per_wp DECIMAL(10,3),
    panel_manufacturer VARCHAR(100),
    panel_power_w INT,
    inverter_manufacturer VARCHAR(100),
    inverter_power_kw DECIMAL(10,2),
    total_panels INT,
    total_inverters INT,
    total_batteries INT,
    status VARCHAR(20),
    tags TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Importar (via terminal MySQL)
LOAD DATA LOCAL INFILE 'all_products.csv'
INTO TABLE products
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Fulltext search
ALTER TABLE products ADD FULLTEXT(name, tags);

-- Buscar kits LONGi
SELECT * FROM products
WHERE MATCH(name, tags) AGAINST('LONGi' IN NATURAL LANGUAGE MODE)
AND category = 'kits'
LIMIT 20;
```

---

## 🔍 Consultas SQL Avançadas

### 1. Kits com Melhor ROI por Faixa de Potência

```sql
WITH power_ranges AS (
    SELECT 
        *,
        CASE 
            WHEN power_kwp <= 3 THEN '0-3kWp'
            WHEN power_kwp <= 5 THEN '3-5kWp'
            WHEN power_kwp <= 10 THEN '5-10kWp'
            WHEN power_kwp <= 20 THEN '10-20kWp'
            ELSE '20+kWp'
        END as power_range
    FROM products
    WHERE category = 'kits'
),
ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY power_range ORDER BY price_per_wp) as rank
    FROM power_ranges
)
SELECT 
    power_range,
    name,
    power_kwp,
    price_brl,
    price_per_wp,
    distributor,
    panel_manufacturer,
    inverter_manufacturer
FROM ranked
WHERE rank <= 5
ORDER BY power_range, rank;
```

### 2. Análise de Mix de Produtos

```sql
SELECT 
    panel_manufacturer,
    inverter_manufacturer,
    COUNT(*) as qty_kits,
    AVG(power_kwp) as avg_power,
    AVG(price_per_wp) as avg_price_wp,
    MIN(price_per_wp) as best_price_wp,
    STRING_AGG(DISTINCT distributor, ', ') as distributors
FROM products
WHERE category = 'kits'
    AND panel_manufacturer IS NOT NULL
    AND inverter_manufacturer IS NOT NULL
GROUP BY panel_manufacturer, inverter_manufacturer
HAVING COUNT(*) >= 3
ORDER BY qty_kits DESC, avg_price_wp ASC
LIMIT 20;
```

---

## 📱 Para Aplicações Web

### Node.js + Express

```javascript
const fs = require('fs');
const csv = require('csv-parser');

// Carregar produtos em memória
let products = [];

fs.createReadStream('all_products.csv')
  .pipe(csv())
  .on('data', (row) => {
    products.push(row);
  })
  .on('end', () => {
    console.log(`✅ ${products.length} produtos carregados`);
  });

// API Endpoint: Buscar kits
app.get('/api/kits', (req, res) => {
  const { 
    minPower, 
    maxPower, 
    maxPrice, 
    distributor, 
    manufacturer 
  } = req.query;

  let filtered = products.filter(p => p.category === 'kits');

  if (minPower) {
    filtered = filtered.filter(p => parseFloat(p.power_kwp) >= parseFloat(minPower));
  }
  if (maxPower) {
    filtered = filtered.filter(p => parseFloat(p.power_kwp) <= parseFloat(maxPower));
  }
  if (maxPrice) {
    filtered = filtered.filter(p => parseFloat(p.price_brl) <= parseFloat(maxPrice));
  }
  if (distributor) {
    filtered = filtered.filter(p => p.distributor === distributor);
  }
  if (manufacturer) {
    filtered = filtered.filter(p => 
      p.panel_manufacturer === manufacturer || 
      p.inverter_manufacturer === manufacturer
    );
  }

  res.json(filtered);
});

// Endpoint: Estatísticas
app.get('/api/stats', (req, res) => {
  const kits = products.filter(p => p.category === 'kits');
  
  const stats = {
    total_kits: kits.length,
    distributors: [...new Set(kits.map(k => k.distributor))],
    avg_price_wp: (kits.reduce((sum, k) => sum + parseFloat(k.price_per_wp || 0), 0) / kits.length).toFixed(2),
    power_range: {
      min: Math.min(...kits.map(k => parseFloat(k.power_kwp || 0))),
      max: Math.max(...kits.map(k => parseFloat(k.power_kwp || 0)))
    }
  };

  res.json(stats);
});
```

---

## 🎯 Casos de Uso Práticos

### 1. Cotação Rápida para Cliente

**Cenário**: Cliente quer kit de 5kWp, até R$ 15.000

```python
# Python
filtered = df_kits[
    (df_kits['power_kwp'] >= 4.5) & 
    (df_kits['power_kwp'] <= 5.5) & 
    (df_kits['price_brl'] <= 15000)
].sort_values('price_per_wp')

print(filtered[['name', 'power_kwp', 'price_brl', 'distributor']].head(10))
```

### 2. Análise de Estoque Estratégico

**Objetivo**: Identificar gaps no portfolio

```python
# Analisar cobertura por faixa de potência
coverage = df_kits.groupby(['power_range', 'distributor']).size().unstack(fill_value=0)
print("\nCobertura por Faixa de Potência:")
print(coverage)

# Identificar faixas com baixa cobertura
low_coverage = coverage[coverage.sum(axis=1) < 50]
print(f"\n⚠️ Faixas com baixa cobertura (<50 SKUs):")
print(low_coverage)
```

### 3. Benchmarking de Preços

**Objetivo**: Comparar preços do distribuidor X vs mercado

```python
distributor = 'Fortlev'

benchmark = df_kits.groupby('power_range').agg({
    'price_per_wp': ['mean', 'median']
}).round(2)

distributor_prices = df_kits[df_kits['distributor'] == distributor].groupby('power_range').agg({
    'price_per_wp': 'mean'
}).round(2)

comparison = benchmark.join(distributor_prices, rsuffix='_fortlev')
print(comparison)
```

---

## ✅ Checklist de Qualidade

Antes de usar os dados, verifique:

- [ ] Encoding UTF-8 configurado corretamente
- [ ] Colunas numéricas reconhecidas como números
- [ ] Valores nulos tratados adequadamente
- [ ] Duplicatas removidas (se necessário)
- [ ] Filtros aplicados corretamente

---

**Atualizado em**: 20 de Outubro de 2025  
**Versão**: 1.0.0  
**Suporte**: Equipe YSH B2B Platform
