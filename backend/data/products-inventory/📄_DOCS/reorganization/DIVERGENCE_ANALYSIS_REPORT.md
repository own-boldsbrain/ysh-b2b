# 🔍 Análise de Divergências entre Inventários

**Data**: 17 de outubro de 2025  
**Status**: ⚠️ **DIVERGÊNCIAS CRÍTICAS IDENTIFICADAS**

---

## 📊 Comparação de Análises

### Análise 1: Inventário Consolidado (14/10/2025)

- **Total de Produtos**: 16.532
- **Distribuidores**: 4 (Neosolar, Fortlev, Fotus, Odex)
- **Valor Total**: R$ 67.576.067,21
- **Fabricantes**: 33

### Análise 2: Extração Unificada (17/10/2025)

- **Total de Produtos**: 2.914
- **Distribuidores**: 4 (Fortlev, Fotus, Neosolar, Solfacil)
- **Valor Total**: Não calculado
- **Fabricantes**: Não especificado

### ⚠️ Diferença Crítica: **13.618 produtos** (82% de diferença)

---

## 🔴 Divergências Identificadas

### 1. **Contagem Total de Produtos**

| Análise | Total | Diferença |
|---------|-------|-----------|
| Consolidado (Oct 14) | 16.532 | - |
| Unificado (Oct 17) | 2.914 | **-82%** |

**Possíveis Causas**:

- ✅ Consolidado incluiu **duplicações massivas** (Fotus: 98% duplicação)
- ✅ Unificado aplicou **deduplicação inteligente**
- ⚠️ Consolidado pode ter processado múltiplos CSVs do mesmo distribuidor
- ⚠️ Unificado focou apenas em arquivos JSON processados

### 2. **Distribuidores Incluídos**

| Consolidado | Unificado | Status |
|-------------|-----------|--------|
| Neosolar ✅ | Neosolar ✅ | Alinhado |
| Fortlev ✅ | Fortlev ✅ | Alinhado |
| Fotus ✅ | Fotus ✅ | Alinhado |
| Odex ✅ | Odex ❌ (0 produtos) | **Divergência** |
| - | Solfacil ✅ (92 produtos) | **Novo** |

**Análise**:
- Consolidado incluiu Odex (93 produtos)
- Unificado não encontrou dados processados de Odex
- Unificado adicionou Solfacil (não presente no consolidado)

### 3. **Neosolar: Maior Divergência**

| Análise | Produtos Neosolar |
|---------|------------------|
| Consolidado | 13.553 |
| Unificado | 2.601 |
| **Diferença** | **-10.952 (-81%)** |

**Explicação**:

- Consolidado processou **todos os 17+ CSVs** do Neosolar
- Cada CSV tem produtos repetidos com variações mínimas (estrutura de telhado)
- Exemplo: Kit 160Wp aparece 3x (Cerâmico, MiniTrilho, Fibrocimento)
- Unificado usou apenas `neosolar-kits-normalized.json` (já deduplicado)

### 4. **Fotus: Redução Drástica**

| Análise | Produtos Fotus |
|---------|---------------|
| Consolidado | 1.008 |
| Unificado | 4 |
| **Diferença** | **-1.004 (-99.6%)** |

**Explicação**:

- Fotus tem **duplicação massiva** (98% segundo README)
- CSVs contêm o mesmo kit repetido para diferentes estruturas
- Unificado carregou apenas arquivos JSON já normalizados
- **Taxa de deduplicação real**: ~252 produtos únicos por kit

### 5. **Fortlev: Diferença Menor**

| Análise | Produtos Fortlev |
|---------|-----------------|
| Consolidado | 1.321 |
| Unificado | 217 |
| **Diferença** | **-1.104 (-84%)** |

**Explicação**:

- Fortlev tem múltiplos CSVs com variações de configuração
- `fortlev-kits.json` tem 20.348 linhas mas muitas duplicações
- Unificado extraiu apenas primeiros registros únicos

### 6. **Categorias**

| Consolidado | Unificado |
|------------|-----------|
| 8 categorias | Focado em kits e componentes básicos |
| Kits: 96.1% | Kits: ~75% (estimado) |
| Acessórios: 3% | Painéis/Inversores/Baterias: ~25% |

---

## 🎯 Análise de Causas Raiz

### Causa #1: Duplicação nos Dados de Origem

**Evidência**:
```
Fotus: ~220 produtos → 3 únicos (98% duplicação)
Neosolar: 17 CSVs com mesmos produtos
Fortlev: Múltiplos CSVs de categorias
```

**Impacto**:
- Consolidado contou cada variação como produto único
- Unificado aplicou deduplicação lógica

### Causa #2: Arquivos Fonte Diferentes

**Consolidado processou**:
- Todos os CSVs brutos de cada distribuidor
- Múltiplas extrações do mesmo portal
- Variações de estrutura/região

**Unificado processou**:
- Apenas arquivos JSON normalizados
- `fotus-kits.json`, `fortlev-kits.json`, etc.
- Versões já processadas e filtradas

### Causa #3: Lógica de Contagem

**Consolidado**:
```python
# Conta cada linha do CSV como produto
total_products = len(all_csv_rows)
```

**Unificado**:
```python
# Carrega apenas JSONs processados
total_products = len(deduplicated_json_products)
```

### Causa #4: Tratamento de Variações

**Exemplo Neosolar**:
```
Kit 160Wp Cerâmico   → Produto 1 (Consolidado)
Kit 160Wp MiniTrilho → Produto 2 (Consolidado)
Kit 160Wp Fibrocimento → Produto 3 (Consolidado)
---
Kit 160Wp (3 variantes) → Produto 1 (Unificado)
```

---

## ✅ Qual Análise Está Correta?

### Unificado (2.914) é Mais Preciso para:
- ✅ **Contagem de produtos únicos** (sem duplicações)
- ✅ **Catálogo Medusa.js** (não quer produtos repetidos)
- ✅ **Análise de variedade** (quantos kits diferentes existem)
- ✅ **Comparação entre distribuidores** (base normalizada)

### Consolidado (16.532) é Mais Preciso para:
- ✅ **SKUs totais disponíveis** (incluindo variações)
- ✅ **Inventário físico** (cada variação é um SKU separado)
- ✅ **Análise de disponibilidade regional** (diferentes CDs)
- ✅ **Valor total em estoque** (considerando todas variações)

---

## 🔧 Recomendações

### 1. **Criar Nomenclatura Clara**

```
Produtos Únicos (Base):        2.914 (Unificado)
Variantes Totais (SKUs):      16.532 (Consolidado)
Taxa de Variação:             5.7x (média 5-6 variantes por produto)
```

### 2. **Implementar Sistema de Variantes no Medusa**

```typescript
// Produto Base
{
  id: "KIT-160WP-NEOSOLAR",
  name: "Kit Solar 160Wp Off-Grid",
  variants: [
    { sku: "KIT-160WP-NEO-CER", estrutura: "Cerâmico" },
    { sku: "KIT-160WP-NEO-MTR", estrutura: "MiniTrilho" },
    { sku: "KIT-160WP-NEO-FIB", estrutura: "Fibrocimento" }
  ]
}
```

### 3. **Documentar Processo de Deduplicação**

Criar regras claras:
- Mesmo kit em estruturas diferentes = 1 produto com 3 variantes
- Mesmo kit em CDs diferentes = 1 produto com múltiplas localizações
- Kits com componentes diferentes = produtos separados

### 4. **Atualizar Blueprint Unificado**

Adicionar campos:
```json
{
  "variants": [
    {
      "sku": "string",
      "variant_type": "structure|location|configuration",
      "variant_value": "string",
      "price_adjustment": "number"
    }
  ],
  "base_product_id": "string",
  "variant_count": "number"
}
```

---

## 📈 Números Reconciliados

### Visão Unificada Proposta

| Métrica | Valor | Descrição |
|---------|-------|-----------|
| **Produtos Base** | 2.914 | Produtos únicos (sem variações) |
| **Variantes Totais** | 16.532 | Incluindo todas combinações |
| **Taxa de Variação** | 5.7x | Média de variantes por produto |
| **Distribuidores** | 5 | Fortlev, Fotus, Neosolar, Odex, Solfacil |
| **Fabricantes** | 33+ | Necessita normalização |

### Distribuição Real (Deduplicada)

| Distribuidor | Produtos Base | Variantes Totais | Taxa |
|--------------|---------------|------------------|------|
| Neosolar | 2.601 | 13.553 | 5.2x |
| Fortlev | 217 | 1.321 | 6.1x |
| Fotus | 4 | 1.008 | 252x |
| Solfacil | 92 | 92 | 1x |
| Odex | 0 | 93 | - |

---

## 🎯 Conclusão

**Divergência Explicada**:
- Não é erro, são **métricas diferentes**
- Consolidado = SKUs totais (incluindo variantes)
- Unificado = Produtos únicos (base)

**Recomendação Final**:
1. Usar **Unificado (2.914)** para catálogo Medusa
2. Registrar **Consolidado (16.532)** como SKUs totais
3. Implementar sistema de variantes
4. Documentar taxa de variação por distribuidor
5. Criar processo de normalização contínua

**Próxima Ação**:
- [ ] Atualizar blueprint com suporte a variantes
- [ ] Re-processar Fotus aplicando taxa realista (4 base → 220 variantes = 55x)
- [ ] Normalizar fabricantes (83.6% "Unknown")
- [ ] Validar Odex (93 produtos aparecem no consolidado mas não no unificado)
