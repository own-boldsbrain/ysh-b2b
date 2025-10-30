# YSH Solar Data Pipeline - Meta Commerce Integration

## 🚀 Stack FOSS de Máxima Performance

Sistema completo open-source para extração automatizada de dados de fabricantes de equipamentos solares e sincronização com **Meta Commerce Platform** (Facebook/Instagram).

---

## 📋 Visão Geral

Esta stack foi projetada para máxima performance, escalabilidade e compliance com os padrões da Meta Commerce Platform. O sistema extrai automaticamente datasheets, imagens e especificações técnicas de fabricantes solares e sincroniza com catálogos do Facebook/Instagram.

### Principais Características

✅ **Extração Automatizada**: Web scraping de alta performance com Crawlee + Playwright  
✅ **Processamento AI**: Extração de specs técnicas com Ollama (local) ou OpenAI  
✅ **Compliance Meta**: 100% aderente aos campos da Meta Commerce Platform  
✅ **High Performance**: Processamento paralelo com Polars, Celery e async  
✅ **Observabilidade**: Monitoramento completo com Prometheus + Grafana + Loki  
✅ **Escalável**: Arquitetura distribuída com Airflow + Redis + PostgreSQL  

---

## 🛠️ Stack Tecnológica

### **Orchestration & Workflows**

- **Apache Airflow 2.7+** com Celery Executor
- DAGs para extração, transformação e sincronização
- Retry automático e monitoramento de falhas

### **Web Scraping**

- **Crawlee** + **Playwright** (headless browser)
- Suporte a JavaScript-rendered pages
- Rate limiting e proxy rotation

### **Data Processing**

- **Polars** (dataframes ultra-rápidos)
- **Pandas** (compatibilidade)
- **Pydantic** (validação de schemas)

### **AI/ML**

- **Ollama** (LLM local para extração de specs)
- **OpenAI GPT-4** (opcional, para tarefas avançadas)
- **pdfplumber** + **PyMuPDF** (parsing de PDFs)

### **Storage**

- **PostgreSQL** (database principal)
- **Redis** (cache e queue)
- **MinIO** (S3-compatible object storage)
- **Qdrant** (vector database para busca semântica)

### **Monitoring**

- **Prometheus** (coleta de métricas)
- **Grafana** (dashboards)
- **Loki** (log aggregation)
- **Promtail** (log shipper)

### **Meta Commerce Integration**

- **Facebook Graph API v18.0**
- **Batch API** para bulk uploads
- Geração de feeds CSV/XML
- Compliance com [Meta Commerce Catalog Fields](https://developers.facebook.com/docs/commerce-platform/catalog/fields)

---

## 📁 Estrutura do Projeto

```tsx
data-pipeline/
├── workflows/
│   ├── dags/
│   │   ├── manufacturer_data_extraction_dag.py   # Extração de fabricantes
│   │   ├── meta_commerce_sync_dag.py             # Sync com Meta
│   │   └── image_enrichment_dag.py               # Processamento de imagens
│   └── README.md
├── services/
│   ├── meta_commerce_sync_service.py             # Serviço de sync Meta
│   └── README.md
├── infrastructure/
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── airflow/
├── docker-compose.yml                            # Stack completa
├── requirements-full.txt                         # Dependências Python
├── .env.example                                  # Template de variáveis
└── README_META_COMMERCE.md                       # Esta documentação
```

---

## 🚦 Quick Start

### 1. Pré-requisitos

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+ (opcional, para scripts auxiliares)
- Conta Facebook Business Manager
- Catálogo criado no Commerce Manager

### 2. Configuração Inicial

```bash
# Clone o repositório
cd backend/data/products-inventory/data-pipeline

# Copie o arquivo de environment
cp .env.example .env

# Edite as variáveis (especialmente Meta Commerce)
nano .env
```

**Configurações críticas no `.env`:**

```bash
# Meta Commerce (obrigatório)
FACEBOOK_CATALOG_ID=your_catalog_id_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
BASE_PRODUCT_URL=https://ysh.solar/products

# Database
DATABASE_URL=postgresql://ysh_admin:ysh_secure_2025@postgres:5432/ysh_pipeline

# Storage
MINIO_ENDPOINT=http://minio:9000
```

### 3. Obter Access Token do Facebook

1. Acesse [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Selecione seu App
3. Adicione permissões: `catalog_management`, `pages_manage_metadata`
4. Clique em "Generate Access Token"
5. Copie o token para `.env`

### 4. Criar Catálogo no Commerce Manager

1. Acesse [Facebook Commerce Manager](https://business.facebook.com/commerce/)
2. Clique em "Criar Catálogo"
3. Selecione "E-commerce"
4. Copie o **Catalog ID** (número longo) para `.env`

### 5. Iniciar a Stack

```bash
# Suba toda a infraestrutura
docker-compose up -d

# Verifique os serviços
docker-compose ps

# Logs em tempo real
docker-compose logs -f
```

### 6. Acessar Interfaces

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin / admin_2025 |
| **Grafana** | http://localhost:3000 | admin / grafana_2025 |
| **Prometheus** | http://localhost:9090 | - |
| **MinIO** | http://localhost:9001 | ysh_admin / ysh_minio_2025 |
| **Flower** (Celery) | http://localhost:5555 | - |

---

## 🔄 Workflows Disponíveis

### 1. **manufacturer_data_extraction** (Semanal)

Extrai catálogo completo de fabricantes:

- Acessa websites dos fabricantes (Jinko, Growatt, Canadian Solar, etc.)
- Extrai informações de produtos
- Baixa datasheets (PDFs)
- Baixa imagens de produtos
- Extrai specs técnicas com AI
- Salva na staging table

**Execução:** Domingos às 2h  
**Duração:** ~2-4 horas (dependendo do volume)

### 2. **meta_commerce_product_sync** (A cada 2 horas)

Sincroniza produtos com Meta Commerce:

- Lê produtos pending da staging table
- Transforma para schema Meta Commerce
- Upload via Graph API Batch
- Marca como synced

**Execução:** A cada 2 horas  
**Duração:** ~10-30 minutos

### 3. **image_enrichment** (A cada 4 horas)

Processa e otimiza imagens:

- Gera múltiplas resoluções (thumbnail, web, high-res)
- Converte para WebP
- Remove backgrounds (opcional)
- Gera captions com AI

**Execução:** A cada 4 horas  
**Duração:** ~15-45 minutos

---

## 📊 Schema Meta Commerce

### Campos Obrigatórios

```python
{
    "id": "JKO-tiger-neo-620w",           # SKU único
    "title": "Jinko Tiger Neo 620W",      # Máx 150 chars
    "description": "...",                  # Máx 5000 chars
    "availability": "in stock",            # ou "out of stock"
    "condition": "new",                    # ou "refurbished", "used"
    "price": "1299.99 BRL",               # Formato: "valor CURRENCY"
    "link": "https://ysh.solar/products/jinko-tiger-neo-620w",
    "image_link": "https://cdn.ysh.solar/jinko-tiger-neo-620w.webp",
    "brand": "Jinko Solar",
    "google_product_category": "Electronics > Components > Solar Panels"
}
```

### Campos Recomendados

```python
{
    "additional_image_link": ["url1", "url2", "url3"],  # Até 10 imagens
    "item_group_id": "JKO-tiger-neo",                   # Para variantes
    "inventory": 50,                                    # Estoque disponível
    "sale_price": "1099.99 BRL",                        # Preço promocional
    "custom_label_0": "Jinko Solar",                    # Filtros customizados
    "custom_label_1": "module",
    "custom_label_2": "620W"
}
```

### Campos Específicos Solares

```python
{
    "material": "solar-grade",
    "shipping_weight_value": 32.5,
    "shipping_weight_unit": "kg",
    "mpn": "JKM620N-78HL4-V",                          # Manufacturer Part Number
    "rich_text_description": "<p>Specs: ...</p>"       # HTML permitido
}
```

---

## 🔧 Configurações Avançadas

### Adicionar Novo Fabricante

Edite `workflows/dags/manufacturer_data_extraction_dag.py`:

```python
MANUFACTURERS.append({
    'name': 'Novo Fabricante',
    'website': 'https://www.fabricante.com',
    'product_categories': ['modules', 'inverters'],
    'selectors': {
        'product_list': '.product-card',
        'datasheet': 'a[href$=".pdf"]',
        'images': 'img.product-image'
    }
})
```

### Customizar Google Product Category

Edite `services/meta_commerce_sync_service.py`:

```python
self.solar_categories = {
    'module': 'Electronics > Components > Solar Panels',
    'inverter': 'Electronics > Components > Power Inverters',
    'battery': 'Electronics > Components > Batteries',
    'novo_tipo': 'Sua Categoria Aqui',
}
```

### Ajustar Batch Size

No `.env`:

```bash
SYNC_BATCH_SIZE=200        # Produtos por batch (padrão: 100)
SCRAPING_BATCH_SIZE=100    # Páginas por scraping (padrão: 50)
```

---

## 📈 Monitoramento

### Dashboards Grafana

1. **Pipeline Overview**: Visão geral de todos os workflows
2. **Meta Commerce Sync**: Métricas de sincronização
3. **Scraping Performance**: Taxa de sucesso, erros, tempo
4. **Storage Metrics**: Uso de disco, objetos em MinIO

### Alertas Configurados

- ❌ Falha em sync com Meta Commerce
- 🐌 Scraping com >30% de falhas
- 💾 Disco acima de 80%
- ⚠️ Airflow tasks com >3 retries

---

## 🧪 Testes

```bash
# Teste de conexão com Meta Commerce
python services/meta_commerce_sync_service.py --test-connection

# Teste de scraping (dry-run)
python workflows/dags/manufacturer_data_extraction_dag.py --dry-run

# Teste de transformação de schema
pytest tests/test_meta_commerce_schema.py
```

---

## 📝 Manutenção

### Atualizar Access Token

Tokens do Facebook expiram. Para renovar:

```bash
# 1. Gere novo token no Graph API Explorer
# 2. Atualize o .env
FACEBOOK_ACCESS_TOKEN=new_token_here

# 3. Reinicie o serviço
docker-compose restart ysh-worker
```

### Limpar Cache

```bash
# Redis
docker exec ysh-redis redis-cli FLUSHALL

# PostgreSQL staging table
docker exec ysh-postgres psql -U ysh_admin -d ysh_pipeline \
  -c "TRUNCATE product_staging CASCADE;"
```

### Backup

```bash
# Backup PostgreSQL
docker exec ysh-postgres pg_dump -U ysh_admin ysh_pipeline > backup_$(date +%Y%m%d).sql

# Backup MinIO
docker exec ysh-minio mc mirror local/ysh-datasheets /backup/datasheets/
```

---

## 🔒 Segurança

1. **Nunca** commitar `.env` com valores reais
2. Use **secrets manager** em produção (AWS Secrets Manager, Vault)
3. Rotacione **tokens e senhas** a cada 90 dias
4. Restrinja **IPs** no firewall (whitelist)
5. Use **HTTPS** em produção
6. Ative **2FA** no Facebook Business Manager

---

## 🐛 Troubleshooting

### Erro: "Invalid OAuth access token"

**Solução:** Token expirado ou sem permissões corretas. Gere novo token com scopes `catalog_management`.

### Erro: "Catalog not found"

**Solução:** Verifique se `FACEBOOK_CATALOG_ID` está correto. Acesse Commerce Manager e copie o ID novamente.

### Erro: "Image URL not accessible"

**Solução:** Imagens devem estar publicamente acessíveis via HTTPS. Verifique permissões do MinIO ou CDN.

### Scraping falha com timeout

**Solução:** Aumente `SCRAPING_TIMEOUT` no `.env` ou reduza `SCRAPING_BATCH_SIZE`.

---

## 📚 Referências

- [Meta Commerce Platform Docs](https://developers.facebook.com/docs/commerce-platform/)
- [Catalog Fields Reference](https://developers.facebook.com/docs/commerce-platform/catalog/fields)
- [Graph API Batch Requests](https://developers.facebook.com/docs/graph-api/making-multiple-requests)
- [Google Product Categories](https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt)
- [Apache Airflow Docs](https://airflow.apache.org/docs/)

---

## 🤝 Suporte

- 📧 Email: data-engineering@ysh.solar
- 💬 Slack: #data-pipeline
- 📖 Wiki: https://wiki.ysh.solar/data-pipeline

---

## 📄 Licença

Proprietary - YSH Solar Platform © 2025

---

**Built with ❤️ by YSH Data Engineering Team**
