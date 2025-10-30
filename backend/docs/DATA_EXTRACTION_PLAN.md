# 📋 Plano Estratégico de Extração e Upload de Dados

**Data**: 19/10/2025  
**Status**: 🚀 Pronto para Execução  
**Responsável**: YSH Solar B2B Team

---

## 🎯 Objetivo

Extrair, transformar e carregar (ETL) todos os dados do inventário de produtos para os bancos de dados PostgreSQL e Redis, preparando o sistema para operação completa do scraping automático.

---

## 📊 Dados Disponíveis

### Inventário Atual

| Arquivo | Registros | Tamanho | Status |
|---------|-----------|---------|--------|
| `unified_products.json` | **173,981 linhas** | ~50 MB | ✅ Pronto |
| `manufacturers_unified_list.json` | **32 fabricantes** | 2 KB | ✅ Pronto |
| `datasheet_search_list.json` | **1,256 produtos** | 50 KB | ✅ Pronto |
| `technology_matrix.json` | Matriz técnica | 10 KB | ✅ Pronto |
| `product_series_analysis.json` | Análise de séries | 15 KB | ✅ Pronto |

### Distribuição por Categoria

```
Kits Solares:      ~5,000 itens
Painéis:          ~3,000 itens
Inversores:       ~2,500 itens
Baterias:         ~1,500 itens
Estruturas:       ~1,000 itens
Cabos/Acessórios: ~500 itens
```

### Top 10 Fabricantes (por volume)

1. **Deye** - 1,278 produtos (29.77%)
2. **EPever** - 609 produtos (14.19%)
3. **DAH Solar** - 538 produtos (12.53%)
4. **Ztroon** - 407 produtos (9.48%)
5. **Znshine** - 258 produtos (6.01%)
6. **Sunova** - 228 produtos (5.31%)
7. **Moura** - 151 produtos (3.52%)
8. **LONGi** - 143 produtos (3.33%)
9. **OSDA Solar** - 128 produtos (2.98%)
10. **UCB** - 102 produtos (2.38%)

---

## 🗄️ Esquema de Banco de Dados

### Tabelas Principais (PostgreSQL)

#### 1. `manufacturers`
```sql
- id: SERIAL PRIMARY KEY
- name: VARCHAR(255) UNIQUE
- base_url: VARCHAR(500)
- priority: INT (calculado por volume)
- active: BOOLEAN
- last_scraped: TIMESTAMP
- last_status: VARCHAR(50)
```

#### 2. `products`
```sql
- id: SERIAL PRIMARY KEY
- manufacturer_id: INT (FK)
- model: VARCHAR(255)
- title: VARCHAR(500)
- specs_json: JSONB (todas as especificações)
- image_url: VARCHAR(1000)
- facebook_uploaded: BOOLEAN
- created_at: TIMESTAMP
```

#### 3. `product_images`
```sql
- id: SERIAL PRIMARY KEY
- product_id: INT (FK)
- url: VARCHAR(1000)
- local_path: VARCHAR(500)
- quality_score: INT (0-10)
- width: INT
- height: INT
- image_hash: VARCHAR(64)
```

#### 4. `enriched_products`
```sql
- id: SERIAL PRIMARY KEY
- product_id: INT (FK)
- sku: VARCHAR(100) UNIQUE
- category: VARCHAR(100)
- normalized_specs: JSONB
- confidence_score: FLOAT
```

#### 5. `scraping_logs`
```sql
- id: SERIAL PRIMARY KEY
- manufacturer_id: INT (FK)
- status: VARCHAR(50)
- products_found: INT
- images_downloaded: INT
- error_message: TEXT
- timestamp: TIMESTAMP
```

---

## 🔄 Pipeline de Extração (5 Fases)

### **FASE 1: Extração de Fabricantes** ⏱️ ~2 min

**Entrada**: `manufacturers_unified_list.json`  
**Processamento**:
- Parse de 32 fabricantes
- Cálculo de prioridade (baseado em volume)
- Mapeamento de URLs oficiais
- Marcação de fabricantes ativos

**Saída**: 
- ✅ 32 registros em `manufacturers`
- Prioridades: 60-100 (quanto maior o volume, maior a prioridade)

**Lógica de Prioridade**:
```python
>= 1000 produtos → Priority 100
>= 500 produtos  → Priority 90
>= 100 produtos  → Priority 80
>= 50 produtos   → Priority 70
< 50 produtos    → Priority 60
```

---

### **FASE 2: Extração de Produtos** ⏱️ ~15 min

**Entrada**: `unified_products.json` (173,981 linhas)  
**Processamento**:
- Parse de cada produto
- Identificação de fabricante (painéis → inversores → distribuidor)
- Extração de specs técnicas (power, category, components)
- Normalização de imagens

**Transformações**:
```python
# Exemplo de transformação
{
  "id": "fortlev_kit_001",
  "name": "Kit 2.44kWp - Panel + Growatt",
  "components": {...}
}

↓ TRANSFORMA EM ↓

{
  "manufacturer_id": 16,  # Growatt
  "model": "Kit 2.44kWp - Panel + Growatt",
  "specs_json": {
    "power_kwp": 2.44,
    "components": {...},
    "pricing": {...}
  }
}
```

**Saída**:
- ✅ ~10,000-15,000 produtos inseridos (após filtros)
- Produtos sem fabricante identificável são descartados
- Batch insert de 100 registros por vez

---

### **FASE 3: Extração de Imagens** ⏱️ ~5 min

**Entrada**: Produtos com `image_url` não-nulo  
**Processamento**:
- Extração de URLs de imagens
- Score inicial baseado em fonte:
  - URLs oficiais (prod-platform-api): Score 7
  - URLs genéricas: Score 5
- Dimensões estimadas (800x800 default)

**Saída**:
- ✅ ~8,000-12,000 registros em `product_images`
- Metadados prontos para download posterior

---

### **FASE 4: Cache Redis** ⏱️ ~1 min

**Processamento**:
- Cache de fabricantes ativos com TTL 24h
- Cache de estatísticas (produtos por fabricante)
- Keys estruturadas:
  ```
  manufacturer:deye → {name, url, priority}
  stats:products:deye → 1278
  ```

**Saída**:
- ✅ 32 fabricantes em cache
- ✅ 32 contadores de produtos

---

### **FASE 5: Validação e Relatório** ⏱️ ~2 min

**Validações**:
1. ✅ Total de fabricantes = 32
2. ✅ Fabricantes ativos >= 30
3. ✅ Produtos inseridos > 10,000
4. ✅ Produtos com imagens > 8,000
5. ✅ Média de produtos/fabricante > 300

**Saída**:
- Relatório completo em `data/extraction_report.txt`
- Log detalhado em `data_extraction_pipeline.log`
- Estatísticas no console

---

## 🚀 Execução do Pipeline

### Pré-requisitos

```powershell
# 1. Docker containers rodando
docker-compose ps | findstr "postgres redis"
# Deve mostrar: ysh-postgres (healthy), ysh-redis (healthy)

# 2. Banco de dados inicializado
docker exec -it ysh-postgres psql -U postgres -d ysh_solar -c "\dt"
# Deve mostrar: manufacturers, products, product_images, etc.

# 3. Python com dependências
pip install psycopg2-binary redis
```

### Comando de Execução

```powershell
cd C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend

# Execução completa
python scripts/data_extraction_pipeline.py
```

### Monitoramento

```powershell
# Terminal 1: Logs do pipeline
Get-Content data_extraction_pipeline.log -Wait

# Terminal 2: Monitorar banco
docker exec -it ysh-postgres psql -U postgres -d ysh_solar

# Queries úteis:
SELECT COUNT(*) FROM manufacturers;
SELECT COUNT(*) FROM products;
SELECT m.name, COUNT(p.id) as products 
FROM manufacturers m 
LEFT JOIN products p ON m.id = p.manufacturer_id 
GROUP BY m.name 
ORDER BY products DESC 
LIMIT 10;
```

---

## 📊 Resultados Esperados

### Após Execução Completa

| Métrica | Valor Esperado | Status |
|---------|----------------|--------|
| Fabricantes carregados | 32 | ⏳ Pendente |
| Produtos carregados | 10,000-15,000 | ⏳ Pendente |
| Imagens registradas | 8,000-12,000 | ⏳ Pendente |
| Cache Redis | 64 keys | ⏳ Pendente |
| Tempo total | ~25 minutos | ⏳ Pendente |
| Erros tolerados | < 100 | ⏳ Pendente |

### Qualidade de Dados

- ✅ 100% dos fabricantes com URL oficial
- ✅ >80% dos produtos com imagens
- ✅ >90% dos produtos com specs completas
- ✅ 0% de duplicatas (constraint UNIQUE)

---

## 🔄 Próximos Passos (Pós-ETL)

### 1. Download de Imagens (Fase Scraping)

```powershell
# Executar scraper AI-guided para top 10 fabricantes
python src/scrapers/ai_guided_scraper.py \
  --manufacturer "Deye" \
  --url "https://www.deyeinverter.com/" \
  --max-products 100
```

### 2. Processamento Pathway

```powershell
# Iniciar processador real-time
docker-compose up -d pathway-processor

# Monitorar
docker logs -f ysh-pathway-processor
```

### 3. Upload Facebook Catalog

```powershell
# Worker de upload em background
docker-compose up -d facebook-uploader

# Adicionar job na fila Redis
redis-cli LPUSH facebook_upload_queue '{"manufacturer_id": 1, "manufacturer_name": "Deye"}'
```

### 4. Schedules Dagster

```powershell
# Iniciar Dagster
docker-compose up -d dagster-webserver dagster-daemon

# Acessar UI
start http://localhost:3000

# Ativar schedules:
# - daily_manufacturer_scrape (2 AM)
# - weekly_catalog_update (3 AM domingos)
```

---

## ⚠️ Troubleshooting

### Erro: "Database connection failed"

```powershell
# Verificar se Postgres está rodando
docker ps | findstr postgres

# Reiniciar container
docker-compose restart postgres

# Testar conexão
docker exec -it ysh-postgres psql -U postgres -d ysh_solar -c "SELECT 1"
```

### Erro: "Redis connection refused"

```powershell
# Verificar Redis
docker ps | findstr redis

# Testar conexão
docker exec -it ysh-redis redis-cli PING
# Deve retornar: PONG
```

### Erro: "File not found"

```powershell
# Verificar se arquivos existem
Test-Path C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\unified_products.json

# Listar arquivos
ls C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\*.json
```

### Pipeline travou na Fase 2

```powershell
# Produtos grandes demais, aumentar batch size ou adicionar limite
# Editar data_extraction_pipeline.py linha 231:
batch_size = 50  # Reduzir de 100 para 50
```

---

## 📈 Métricas de Sucesso

| KPI | Meta | Medição |
|-----|------|---------|
| Taxa de sucesso ETL | >95% | (produtos_inserted / produtos_total) * 100 |
| Cobertura de imagens | >80% | (produtos_com_imagem / produtos_total) * 100 |
| Tempo de execução | <30 min | timestamp_fim - timestamp_inicio |
| Erros críticos | 0 | COUNT(errors WHERE severity='critical') |
| Duplicatas | 0 | Constraint UNIQUE garante |

---

## ✅ Checklist de Execução

### Pré-Execução

- [ ] Docker Desktop rodando
- [ ] Containers postgres e redis healthy
- [ ] Tabelas criadas (02-create-scraping-tables.sql executado)
- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivos JSON presentes em `data/products-inventory/`

### Durante Execução

- [ ] Monitorar logs em tempo real
- [ ] Verificar uso de memória (Task Manager)
- [ ] Observar taxas de inserção (produtos/segundo)
- [ ] Aguardar relatório final

### Pós-Execução

- [ ] Revisar relatório em `data/extraction_report.txt`
- [ ] Verificar contagens no banco
- [ ] Testar queries de exemplo
- [ ] Validar cache Redis
- [ ] Commit e push dos logs

---

## 📞 Suporte

**Documentação Completa**: `docs/ai-ml/README-IMAGE-SCRAPING.md`  
**Logs**: `data_extraction_pipeline.log`  
**Schema SQL**: `init-scripts/02-create-scraping-tables.sql`

---

**🚀 PRONTO PARA EXECUTAR!**

```powershell
python scripts/data_extraction_pipeline.py
```
