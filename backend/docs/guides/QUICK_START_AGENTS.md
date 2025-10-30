# 🚀 Quick Start: Deploy de Agentes YSH em 15 Minutos

**Data**: 19 de Outubro de 2025

---

## 📋 Pré-requisitos

```bash
# Verificar instalações
node --version  # >= 20.0.0
docker --version  # >= 24.0.0
docker-compose --version  # >= 2.20.0
git --version  # >= 2.40.0
```

---

## ⚡ Deploy Rápido

### Passo 1: Clone e Setup (2 minutos)

```bash
# Clone o repositório
git clone https://github.com/own-boldsbrain/ysh-b2b.git
cd ysh-b2b/backend

# Copiar variáveis de ambiente
cp .env.example .env

# Editar credenciais (use seu editor favorito)
code .env
```

### Passo 2: Configure Credenciais no `.env`

```bash
# ==================== DISTRIBUIDORES ====================
FORTLEV_URL=https://fortlevsolar.app/
FORTLEV_EMAIL=fernando.teixeira@yello.cash
FORTLEV_PASSWORD=@Botapragirar2025

NEOSOLAR_URL=https://portalb2b.neosolar.com.br/
NEOSOLAR_EMAIL=product@boldsbrain.ai
NEOSOLAR_PASSWORD=Rookie@010100

SOLFACIL_URL=https://sso.solfacil.com.br/
SOLFACIL_EMAIL=fernando.teixeira@yello.cash
SOLFACIL_PASSWORD=Rookie@010100

FOTUS_URL=https://app.fotus.com.br/
FOTUS_EMAIL=fernando@yellosolarhub.com
FOTUS_PASSWORD=Rookie@010100

ODEX_URL=https://plataforma.odex.com.br/
ODEX_EMAIL=fernando@yellosolarhub.com
ODEX_PASSWORD=Rookie@010100

EDELTEC_URL=https://edeltecsolar.com.br/
EDELTEC_EMAIL=fernando@yellosolarhub.com
EDELTEC_PASSWORD=010100@Rookie

DYNAMIS_URL=https://app.dynamisimportadora.com.br/
DYNAMIS_EMAIL=fernando@yellosolarhub.com
DYNAMIS_PASSWORD=Rookie@010100

# ==================== SERVICES ====================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<will be generated>
SUPABASE_SERVICE_ROLE_KEY=<will be generated>

REDIS_URL=redis://localhost:6379
TEMPORAL_ADDRESS=localhost:7233
KAFKA_BROKERS=localhost:19092
```

### Passo 3: Deploy Stack Completo (10 minutos)

```bash
# Subir todos os serviços
docker-compose -f docker-compose.agents.yml up -d

# Aguardar inicialização (2-3 minutos)
echo "⏳ Aguardando serviços..."
sleep 180

# Verificar status
docker-compose -f docker-compose.agents.yml ps
```

### Passo 4: Migrations e Seeds (2 minutos)

```bash
# Instalar dependências
npm install

# Rodar migrations
npx supabase db push

# Seed inicial
npm run seed:distributors
npm run seed:agents

# Verificar banco
npx supabase db remote:status
```

### Passo 5: Deploy Workers (1 minuto)

```bash
# Build workers
npm run build:workers

# Deploy workers do Temporal
npm run worker:start

# Verificar workers
curl http://localhost:8080/api/v1/namespaces/default/workers
```

---

## ✅ Verificação de Instalação

```bash
# Script de health check
npm run health-check
```

Saída esperada:

```
🏥 YSH Agents Health Check
==========================

✅ Temporal Server: http://localhost:8080 [OK]
✅ Supabase: http://localhost:54321 [OK]
✅ Redis: redis://localhost:6379 [OK]
✅ Redpanda: localhost:19092 [OK]
✅ Grafana: http://localhost:3000 [OK]
✅ Prometheus: http://localhost:9090 [OK]

📊 Agents Status:
✅ Catalog Extractor: Ready
✅ Price Intelligence: Ready
✅ Product Enricher: Ready
✅ SKU Governor: Ready

🎉 All systems operational!
```

---

## 🎮 Interfaces Web

Após deploy, acesse:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Temporal UI** | http://localhost:8080 | - |
| **Supabase Studio** | http://localhost:54321 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Redis Commander** | http://localhost:8081 | - |

---

## 🚦 Executar Primeiro Workflow

### Extração de Catálogo Manual

```bash
# Trigger workflow manualmente
npm run workflow:extract -- --distributor neosolar

# Ou via API
curl -X POST http://localhost:3001/api/workflows/extract \
  -H "Content-Type: application/json" \
  -d '{
    "distributorId": "neosolar",
    "options": {
      "downloadImages": true,
      "downloadDatasheets": true
    }
  }'
```

### Acompanhar Execução

```bash
# Via Temporal UI
open http://localhost:8080

# Via CLI
npm run workflow:status -- --workflow-id <WORKFLOW_ID>

# Ver logs em tempo real
npm run logs:follow -- --service catalog-extractor
```

---

## 📅 Schedule Automático

```bash
# Schedule diário (2 AM)
npm run schedule:catalog-extraction

# Schedule de preços (a cada 15 minutos)
npm run schedule:price-sync

# Verificar schedules ativos
npm run schedule:list
```

---

## 🐛 Troubleshooting

### Problema: Serviços não sobem

```bash
# Verificar logs
docker-compose -f docker-compose.agents.yml logs

# Restart específico
docker-compose -f docker-compose.agents.yml restart temporal-server

# Limpar e recriar
docker-compose -f docker-compose.agents.yml down -v
docker-compose -f docker-compose.agents.yml up -d
```

### Problema: Workflow falha

```bash
# Ver detalhes do erro
npm run workflow:describe -- --workflow-id <WORKFLOW_ID>

# Retry manual
npm run workflow:retry -- --workflow-id <WORKFLOW_ID>
```

### Problema: Credenciais inválidas

```bash
# Testar login manual
npm run test:login -- --distributor neosolar

# Ver logs de autenticação
npm run logs:auth
```

---

## 📊 Monitoramento

### Métricas em Tempo Real

```bash
# Dashboard Grafana pré-configurado
open http://localhost:3000/d/ysh-agents

# Metrics via Prometheus
curl http://localhost:9090/api/v1/query?query=products_extracted_total
```

### Alertas

```bash
# Configurar Slack webhook
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Testar alerta
npm run test:alert -- --type extraction_failed
```

---

## 🔄 Atualização

```bash
# Pull latest changes
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.agents.yml down
docker-compose -f docker-compose.agents.yml build
docker-compose -f docker-compose.agents.yml up -d

# Migrations
npx supabase db push
```

---

## 🗑️ Cleanup

```bash
# Parar todos os serviços
docker-compose -f docker-compose.agents.yml down

# Remover volumes (⚠️ apaga dados)
docker-compose -f docker-compose.agents.yml down -v

# Limpar cache
npm run clean
docker system prune -a
```

---

## 📚 Próximos Passos

1. ✅ Ler documentação completa: `AGENTES_SWARM_ESTRATEGIA_DEFINITIVA.md`
2. ✅ Explorar Temporal UI para entender workflows
3. ✅ Analisar produtos extraídos no Supabase Studio
4. ✅ Configurar alertas no Grafana
5. ✅ Implementar agentes customizados

---

## 💡 Comandos Úteis

```bash
# Ver todos os produtos extraídos
npm run query:products -- --limit 10

# Estatísticas de extração
npm run stats:extraction

# Reprocessar produtos sem preço
npm run reprocess:missing-prices

# Backup do banco
npm run backup:db -- --output ./backups/$(date +%Y%m%d).sql

# Restore
npm run restore:db -- --input ./backups/20251019.sql
```

---

**Suporte**: product@boldsbrain.ai  
**Documentação**: https://github.com/own-boldsbrain/ysh-b2b/wiki  
**Status**: https://status.yellosolarhub.com
