# Scripts de Gerenciamento de Imagens de SKUs

Este diretório contém scripts para garantir, auditar e validar imagens dos SKUs no catálogo de produtos.

## Scripts Disponíveis

### 1. `ensure-sku-images.js`
**Propósito**: Preencher `image_url` e `images` em SKUs usando múltiplas fontes de dados locais.

**Uso**:
```powershell
node scripts/ensure-sku-images.js
```

**Fontes de dados** (em ordem de prioridade):
- `imgs-index.json` — mapeamento direto SKU → cdn_url/filename
- `products-detailed-catalog.json` — catálogo com `image_url` e `sku`
- `product_image_map.json` — map SKU → array de imagens
- `sku-images-sync.json` — resumo com `primary_url`/`all_urls`
- `products-fully-priced-catalog.json` — preços + imagens
- `equipamentos.json` e `store-ready-skus.json` (fallback)
- Token-match em filenames quando necessário

**Outputs**:
- `backend/enriched-skus-for-dynamodb-images-fixed.json`
- `backend/ENRICHED_SKUS_DYNAMIC_PRICING_REPORT-images-fixed.json`

---

### 2. `generate-sku-image-audit-enhanced.js`
**Propósito**: Gerar CSV de auditoria com informações de pricing/kpi/candidatos de imagem e top-250 SKUs por valor.

**Uso**:
```powershell
node scripts/generate-sku-image-audit-enhanced.js
```

**Colunas do CSV**:
- `sku` — identificador único
- `primary_image` — URL da imagem primária
- `all_images` — todas as imagens (pipe-separated)
- `source` — origem do match (imgs-index, product_image_map, etc)
- `score` — confiança do match (0-100)
- `price_brl` — preço final em BRL
- `gross_margin_percent` — margem bruta %
- `weight_kg` — peso do produto
- `candidate_urls` — top-5 candidatos de imagem (pipe-separated)

**Outputs**:
- `backend/sku-image-audit-enhanced.csv` — auditoria completa (1138 linhas)
- `backend/sku-image-audit-top250.csv` — top-250 por preço para revisão manual

---

### 3. `validate-image-urls.js`
**Propósito**: Testar URLs de imagem (200/404/Timeout) e gerar relatório de status.

**Uso**:
```powershell
node scripts/validate-image-urls.js
```

**O que faz**:
- Extrai todas as URLs de imagem dos SKUs enriquecidos
- Filtra apenas URLs absolutas (http/https)
- Executa requests HEAD em batches de 50
- Detecta status: OK (200-299), 404, Timeout, Error
- Identifica SKUs com imagens quebradas

**Outputs**:
- `backend/image-url-validation-report.csv` — lista todas as URLs com status
- `backend/image-url-validation-report.json` — relatório JSON com summary e SKUs afetados

**Estatísticas** (última execução):
- Total URLs testadas: 1138
- OK (200-299): 1128
- 404 Not Found: 0
- Timeout: 0
- Outros Erros: 10
- SKUs com imagens quebradas: 10

---

### 4. `upload-enriched-skus-to-dynamodb.js`
**Propósito**: Fazer upload de SKUs enriquecidos para a tabela DynamoDB `ysh-products-catalog`.

**Uso**:
```powershell
# Usar arquivo padrão (enriched-skus-for-dynamodb.json)
node scripts/upload-enriched-skus-to-dynamodb.js

# Usar arquivo customizado
node scripts/upload-enriched-skus-to-dynamodb.js --file enriched-skus-for-dynamodb-images-fixed.json
```

**Argumento CLI**:
- `--file <path>` — especifica arquivo customizado (absoluto ou relativo a `backend/`)

**Configuração** (via env vars):
- `AWS_REGION` — região AWS (padrão: us-east-1)
- `AWS_ACCESS_KEY_ID` — credencial AWS
- `AWS_SECRET_ACCESS_KEY` — credencial AWS
- `DYNAMODB_TABLE_NAME` — nome da tabela (padrão: ysh-products-catalog)

**Features**:
- Batch write com retry automático (3 tentativas)
- Backoff exponencial em caso de erro
- Progresso em tempo real
- Estatísticas de sucesso/erro ao final

---

## Workflow Automatizado (GitHub Actions)

**Arquivo**: `.github/workflows/reconcile-imgs-index.yml`

**Quando executa**:
- Diariamente às 02:00 UTC (cron)
- Manual via `workflow_dispatch`

**O que faz**:
1. Executa `ensure-sku-images.js` para atualizar imagens
2. Commita arquivos `*-images-fixed.json` se houver mudanças
3. (Opcional) Upload para DynamoDB se `do_upload=true` no workflow_dispatch

**Configuração de Secrets** (necessário para upload):
- `AWS_REGION`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**Permissions**:
- `contents: write` — para commit automático

---

## Fluxo Completo Recomendado

1. **Garantir imagens**:
```powershell
node scripts/ensure-sku-images.js
```

2. **Auditar qualidade**:
```powershell
node scripts/generate-sku-image-audit-enhanced.js
```

3. **Validar URLs** (opcional, leva ~2-3 min):
```powershell
node scripts/validate-image-urls.js
```

4. **Revisar manualmente** (se necessário):
- Abrir `sku-image-audit-top250.csv` no Excel
- Revisar SKUs de maior valor
- Corrigir imagens faltantes/incorretas nos arquivos-fonte

5. **Upload para DynamoDB**:
```powershell
node scripts/upload-enriched-skus-to-dynamodb.js --file enriched-skus-for-dynamodb-images-fixed.json
```

---

## Observações Técnicas

### Heurísticas de Match
- Exact match por SKU (prioridade máxima)
- Match por model/part_number
- Token overlap em nome/título
- Levenshtein fuzzy matching (threshold >= 15)
- Filename token matching (fallback)

### Performance
- `ensure-sku-images.js`: ~1-2s (leitura/escrita de arquivos)
- `generate-sku-image-audit-enhanced.js`: ~1-2s
- `validate-image-urls.js`: ~2-3 min (1138 URLs em batches de 50)
- `upload-enriched-skus-to-dynamodb.js`: ~30-60s (1138 SKUs em batches de 25)

### Troubleshooting
- **Erro "ENOENT"**: verifique caminhos absolutos para arquivos YSH-HELIO
- **Erro "ResourceNotFoundException"**: tabela DynamoDB não existe
- **Timeout em validate-image-urls**: ajustar timeout (padrão: 5000ms) na linha 53
- **Lint warnings**: são avisos de estilo; não bloqueiam execução

---

## Manutenção

Para manter o catálogo atualizado:
1. Re-executar `ensure-sku-images.js` quando novos assets forem adicionados ao CDN
2. Rodar `validate-image-urls.js` periodicamente para detectar URLs quebradas
3. Usar workflow GitHub Action para automatizar reconciliação diária
4. Revisar `sku-image-audit-top250.csv` mensalmente para garantir qualidade dos SKUs de maior valor
