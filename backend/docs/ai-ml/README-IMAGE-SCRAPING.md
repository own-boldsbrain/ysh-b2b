# YSH Solar B2B - Sistema de Captura Automática de Imagens

Sistema completo de scraping inteligente guiado por IA (Gemini + OpenAI) para captura automática de imagens de produtos solares de fabricantes brasileiros e internacionais.

## 🚀 Stack Tecnológica

### IA & Automação
- **Google Gemini Pro**: Navegação inteligente e identificação de produtos
- **OpenAI GPT-4/Codex**: Geração de código de scraping
- **GitHub Copilot CLI**: Assistente de linha de comando
- **Playwright**: Automação de navegador headless

### Orquestração & Processamento
- **Dagster**: Orquestração de pipelines (agendamento, DAGs, monitoring)
- **Pathway**: Processamento de streams em tempo real
- **Docker Compose**: Orquestração de containers

### Dados & Filas
- **PostgreSQL 15**: Banco de dados principal
- **Redis**: Cache e message queue

### Monitoramento
- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards e visualizações

### Integrações
- **Facebook Catalog API**: Upload em lote de produtos

## 📋 Pré-requisitos

- **Python 3.11+**
- **Docker Desktop** (com WSL2 no Windows)
- **Node.js 18+** (opcional, para GitHub Copilot CLI)
- **PowerShell 7+** (no Windows)

### API Keys Necessárias

Você precisa das seguintes chaves de API:

1. **Google Gemini API** (2 keys para failover)
   - Obtenha em: https://makersuite.google.com/app/apikey
   
2. **OpenAI API**
   - Obtenha em: https://platform.openai.com/api-keys
   
3. **Facebook Marketing API** (opcional, para upload de catálogo)
   - App ID, App Secret, Access Token
   - Configure em: https://developers.facebook.com/apps

## 🛠️ Setup e Instalação

### 1. Clone o repositório

```powershell
git clone https://github.com/own-boldsbrain/ysh-b2b.git
cd ysh-b2b/backend
```

### 2. Configure as variáveis de ambiente

O arquivo `.env` já está configurado com suas API keys:

```
GEMINI_API_KEY_1=AIzaSyCmgSL3RkU7kZ_wAfNiW0Y1nKkifXdx0zY
GEMINI_API_KEY_2=AIzaSyAY3QeBxTR7pyyHbzULk3xbLWzrmA82Pi8
OPENAI_API_KEY=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
```

### 3. Execute o setup master (Método Recomendado)

```powershell
cd scripts
.\setup_all.ps1
```

Este script faz:
- ✅ Verifica pré-requisitos (Python, Docker, Git)
- ✅ Valida API keys no .env
- ✅ Configura GitHub Copilot CLI
- ✅ Configura Gemini CLI com dual-key failover
- ✅ Configura OpenAI/Codex
- ✅ Instala dependências Python
- ✅ Instala navegadores Playwright
- ✅ Cria diretórios de output
- ✅ Inicia PostgreSQL
- ✅ Testa APIs

**Após o setup, REINICIE o PowerShell** para carregar as novas funções.

### 4. Build e Start dos containers

```powershell
cd ..  # volta para backend/
docker-compose build
docker-compose up -d
```

Verificar status:
```powershell
docker-compose ps
```

Você deverá ver 10 containers rodando:
- `ysh-postgres` (porta 5432)
- `ysh-redis` (porta 6379)
- `ysh-dagster-webserver` (porta 3000)
- `ysh-dagster-daemon`
- `ysh-pathway-processor` (porta 8080)
- `ysh-image-scraper`
- `ysh-facebook-uploader`
- `ysh-prometheus` (porta 9090)
- `ysh-grafana` (porta 3001)
- `ysh-mcp-server` (porta 8000)

## 🎯 Uso

### CLI Tools (após reiniciar PowerShell)

```powershell
# Gemini CLI (com failover automático entre 2 keys)
gemini "Liste os principais fabricantes de painéis solares no Brasil"

# OpenAI Codex (geração de código)
codex "Create a Playwright script to scrape product images from a gallery"

# GitHub Copilot CLI
ghcs "start docker compose services"  # suggest
ghce "docker-compose up -d"           # explain
```

### Acessar Interfaces Web

- **Dagster UI**: http://localhost:3000
  - Visualizar pipelines, schedules, execuções
  
- **Grafana**: http://localhost:3001
  - Login: admin / admin
  - Dashboard: "YSH Solar - Image Scraping System"
  
- **Prometheus**: http://localhost:9090
  - Métricas raw, queries PromQL

### Executar Scraping Manual

```powershell
# Scraping de um fabricante específico
python src/scrapers/ai_guided_scraper.py `
  --manufacturer "Jinko Solar" `
  --url "https://www.jinkosolar.com/en/site/products" `
  --output-dir "./output/images/jinkosolar" `
  --max-products 50

# Ver resultados
ls output/images/jinkosolar/
cat output/images/jinkosolar/metadata.json
```

### Agendar Scraping Automático

O Dagster já tem schedules configurados:

1. **Daily Scrape**: 2 AM todos os dias
   - Scraping dos 50 fabricantes com maior prioridade
   
2. **Weekly Update**: 3 AM aos domingos
   - Re-scrape completo de todos os fabricantes

Para forçar execução manual:
- Acesse http://localhost:3000
- Vá em "Jobs" → "daily_manufacturer_scrape"
- Clique em "Launchpad" → "Launch Run"

## 📊 Monitoramento

### Logs em Tempo Real

```powershell
# Todos os serviços
docker-compose logs -f

# Apenas scraper
docker-compose logs -f image-scraper

# Apenas Dagster
docker-compose logs -f dagster-webserver dagster-daemon

# Apenas Pathway
docker-compose logs -f pathway-processor
```

### Métricas no Grafana

Dashboard "YSH Solar - Image Scraping System" mostra:

- **Success Rate**: Taxa de sucesso de scraping (últimas 24h)
- **Images/Hour**: Imagens baixadas por hora
- **API Quota**: Uso das APIs Gemini e OpenAI
- **Products by Manufacturer**: Produtos coletados por fabricante
- **Error Log**: Últimos 100 erros
- **Pathway Lag**: Latência do processamento em tempo real

### Verificar Banco de Dados

```powershell
# Conectar ao PostgreSQL
docker exec -it ysh-postgres psql -U postgres -d ysh_solar

# Queries úteis
SELECT * FROM v_scraping_dashboard;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM product_images;
SELECT * FROM scraping_logs ORDER BY timestamp DESC LIMIT 10;
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      DAGSTER WEBSERVER                      │
│          (Orquestração, Schedules, Monitoring)              │
└─────────────────────────────────────────────────────────────┘
                             │
                             ↓
           ┌─────────────────────────────────┐
           │   DAGSTER DAEMON (Executor)     │
           └─────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Scraper    │    │   Scraper    │    │   Scraper    │
│  (Jinko)     │    │  (Canadian)  │    │  (Fronius)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ↓
                  ┌─────────────────────┐
                  │   PATHWAY PROCESSOR  │
                  │  (Real-Time Stream)  │
                  └─────────────────────┘
                             │
                ┌────────────┼────────────┐
                ↓            ↓            ↓
         ┌───────────┐  ┌────────┐  ┌────────────┐
         │ PostgreSQL│  │ Redis  │  │  Facebook  │
         │ (Storage) │  │(Queue) │  │  Catalog   │
         └───────────┘  └────────┘  └────────────┘
                             │
                             ↓
                  ┌─────────────────────┐
                  │  PROMETHEUS/GRAFANA │
                  │    (Monitoring)     │
                  └─────────────────────┘
```

## 📁 Estrutura do Projeto

```
backend/
├── config/                         # Configurações
│   ├── prometheus.yml              # Scrape configs
│   └── grafana/dashboards/         # Dashboards JSON
├── data-platform/                  # Pipelines e processamento
│   ├── dagster/pipelines/          # Jobs Dagster
│   │   ├── __init__.py
│   │   └── image_capture.py        # Pipeline principal
│   └── pathway/                    # Stream processing
│       └── product_stream_processor.py
├── docker/                         # Dockerfiles
│   ├── Dockerfile.dagster
│   ├── Dockerfile.pathway
│   ├── Dockerfile.scraper
│   ├── Dockerfile.facebook
│   └── Dockerfile.mcp
├── docs/ai-ml/                     # Documentação IA
│   └── mega-prompt-image-capture.md  # Contexto para LLMs
├── init-scripts/                   # SQL de inicialização
│   └── 02-create-scraping-tables.sql
├── output/                         # Resultados
│   ├── images/                     # Imagens baixadas
│   ├── metadata/                   # JSON de produtos
│   └── logs/                       # Logs de scraping
├── scripts/                        # Scripts de setup
│   ├── setup_all.ps1               # Master setup
│   ├── setup_copilot_cli.ps1
│   ├── setup_gemini.ps1
│   └── setup_openai.ps1
├── src/                            # Código fonte
│   ├── api/
│   │   └── facebook_catalog_uploader.py
│   └── scrapers/
│       └── ai_guided_scraper.py    # Scraper principal
├── docker-compose.yml              # Orquestração
├── requirements.txt                # Dependências Python
└── .env                            # Variáveis de ambiente
```

## 🔧 Troubleshooting

### Container não inicia

```powershell
# Ver logs de erro
docker-compose logs [service-name]

# Rebuild do container
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### Scraper falha com erro de API

- **Gemini Rate Limit**: O scraper automaticamente faz failover para GEMINI_API_KEY_2
- **OpenAI Quota**: Verifique créditos em https://platform.openai.com/usage
- **Verificar keys**: Execute `python scripts/test_gemini.py` ou `python scripts/test_openai.py`

### Playwright não encontra navegador

```powershell
# Reinstalar navegadores
playwright install chromium
```

### Banco de dados não inicializa

```powershell
# Reset do banco (CUIDADO: apaga todos os dados)
docker-compose down -v
docker-compose up -d postgres

# Aguarde 10 segundos, então:
docker exec -it ysh-postgres psql -U postgres -d ysh_solar -f /docker-entrypoint-initdb.d/02-create-scraping-tables.sql
```

## 📚 Documentação Adicional

- **Mega Prompt**: `docs/ai-ml/mega-prompt-image-capture.md` - Instruções completas para os LLMs
- **Dagster Docs**: https://docs.dagster.io/
- **Pathway Docs**: https://pathway.com/developers/
- **Playwright Docs**: https://playwright.dev/python/
- **Facebook Catalog API**: https://developers.facebook.com/docs/marketing-api/catalog/

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é propriedade da YSH Solar B2B.

## 👨‍💻 Autores

- **YSH Solar B2B Team**
- Desenvolvido com assistência de GitHub Copilot

## 🙏 Agradecimentos

- Google Gemini Pro
- OpenAI GPT-4
- Comunidades open-source: Dagster, Pathway, Playwright

---

**Status do Projeto**: ✅ Produção (Phase 5 Complete)

Para suporte: contato@yshsolar.com.br
