# 🚀 ANEEL Data MCP Server - Guia de Configuração

Este documento descreve como configurar e importar o cenário Huginn **ANEEL Data MCP Server** na sua instância Huginn.

## 📋 Pré-requisitos

✅ **Instância Huginn rodando** (Docker, Heroku, ou manual)  
✅ **HaaS API acessível** (endpoints `/api/aneel/*` implementados)  
✅ **Dataset ANEEL no Hugging Face**: https://huggingface.co/datasets/fernando-bold/aneel-datasets  
✅ **Slack Workspace** (para notificações) - Opcional

---

## 🔧 Passo 1: Configurar Credenciais

Antes de importar o cenário, você precisa configurar as seguintes credenciais na sua instância Huginn:

### 1.1 HaaS API Token

```json
{
  "credential_name": "haas_api_token",
  "credential_value": "your-haas-api-bearer-token-here"
}
```

**Como obter**:
1. Acesse sua API HaaS
2. Faça login via `/auth/login`
3. Copie o token JWT retornado
4. No Huginn: **Credentials → New Credential**
   - Name: `haas_api_token`
   - Value: Cole o token JWT

### 1.2 Slack Webhook (Opcional)

```json
{
  "credential_name": "slack_webhook_haas",
  "credential_value": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

**Como obter**:
1. Acesse https://api.slack.com/apps
2. Crie um novo app ou selecione existente
3. Vá em **Incoming Webhooks**
4. Ative e crie um novo webhook para o canal `#aneel-data`
5. Copie a Webhook URL
6. No Huginn: **Credentials → New Credential**
   - Name: `slack_webhook_haas`
   - Value: Cole a webhook URL

---

## 📦 Passo 2: Importar o Cenário

### Método 1: Via Interface Web (Recomendado)

1. Acesse sua instância Huginn
2. Vá em **Scenarios → Import Scenario**
3. Cole o conteúdo do arquivo `aneel-data-mcp.json`
4. Clique em **Import**

### Método 2: Via API

```bash
curl -X POST https://your-huginn-instance.com/scenarios \
  -H "Authorization: Bearer YOUR_HUGINN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @aneel-data-mcp.json
```

---

## 🎯 Passo 3: Configurar URLs

Após importar, você precisa atualizar as URLs nos agentes para apontarem para sua infraestrutura:

### 3.1 Atualizar HaaS API URL

Edite os seguintes agentes:

#### Agent 7: **Sync to HaaS API**
```json
{
  "post_url": "https://YOUR-HAAS-API.com/api/aneel/sync",
  "headers": {
    "Authorization": "Bearer {% credential haas_api_token %}"
  }
}
```

### 3.2 Atualizar ANEEL Dados Abertos URL

#### Agent 4: **ANEEL Data Freshness Monitor**
```json
{
  "url": "https://dadosabertos.aneel.gov.br/dataset/empreendimento-geracao-distribuida",
  "expected_update_period_in_days": "1"
}
```

---

## ⚙️ Passo 4: Configurar Agendamentos

Configure os schedules para execução automática:

### Agent 0-3: **Query/Calculation Engines**
- **Schedule**: On-demand (via webhook ou manual)
- **Keep events**: 7 days

### Agent 4: **ANEEL Data Freshness Monitor**
- **Schedule**: Every 12 hours
- **Keep events**: 7 days

### Agent 5: **Detect ANEEL Data Updates**
- **Schedule**: Imediato (triggered)
- **Keep events**: 7 days

### Agent 7: **Sync to HaaS API**
- **Schedule**: Diário (1x por dia às 3am)
- **Keep events**: 30 days

### Agent 8: **Notify Data Team**
- **Schedule**: Imediato (triggered)
- **Keep events**: 7 days

---

## 🧪 Passo 5: Testar o Cenário

### 5.1 Teste Manual de Query

1. Acesse **Agent 0: ANEEL GD Data Query Engine**
2. Clique em **Run**
3. Cole o seguinte evento de teste:

```json
{
  "query": {
    "type": "gd_projects",
    "filters": {
      "uf": "MG",
      "distribuidora": "CEMIG",
      "potencia_min": 75,
      "potencia_max": 5000
    },
    "limit": 10
  }
}
```

4. Verifique a saída no **Agent 9: Cache Query Results**

### 5.2 Teste de Validação de Projeto

1. Acesse **Agent 2: ANEEL Project Validator**
2. Clique em **Run**
3. Cole o seguinte evento de teste:

```json
{
  "project": {
    "ceg": "MG.GD.CEMIG-D.00012345",
    "distribuidora": "CEMIG",
    "potencia_kw": 150.5,
    "modalidade": "mini",
    "municipio": "Belo Horizonte",
    "uf": "MG"
  }
}
```

4. Verifique a saída com resultados de validação

### 5.3 Teste de Sincronização

1. Acesse **Agent 7: Sync to HaaS API**
2. Clique em **Run**
3. Verifique nos logs da HaaS API se a sincronização foi iniciada
4. Confirme a notificação no Slack (se configurado)

---

## 📊 Passo 6: Monitorar Operação

### Dashboard de Monitoramento

Crie um dashboard no Huginn para acompanhar:

1. **Taxa de sucesso** de queries (Agent 0-3)
2. **Última atualização** ANEEL (Agent 4)
3. **Sincronizações** executadas (Agent 7)
4. **Alertas** enviados (Agent 8)

### Logs Importantes

Verifique regularmente:

```bash
# Logs Huginn
docker logs huginn_web_1 --tail 100 -f

# Logs HaaS API
docker logs haas_api_1 --tail 100 -f

# Métricas de cache (Agent 9)
# Verificar eventos armazenados e TTL
```

---

## 🔍 Troubleshooting

### Problema: Agentes não executam

**Solução**:
1. Verifique se credenciais estão configuradas
2. Confirme schedules ativos
3. Verifique logs: `docker logs huginn_web_1`

### Problema: Erro 401 na HaaS API

**Solução**:
1. Verifique se token está válido
2. Regenere token se expirado
3. Atualize credential `haas_api_token`

### Problema: Slack não recebe notificações

**Solução**:
1. Teste webhook URL diretamente:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```
2. Verifique se canal `#aneel-data` existe
3. Confirme permissões do app Slack

### Problema: Dados não atualizam

**Solução**:
1. Verifique Agent 4 (Freshness Monitor)
2. Confirme que ANEEL Dados Abertos está acessível
3. Force execução do Agent 7 (Sync)

---

## 📈 Métricas de Performance

### Targets de Performance

| Métrica | Target | Como Medir |
|---------|--------|------------|
| **Query Time** | < 50ms (cached) | Agent 9 logs |
| **Tariff Calculation** | < 100ms | Agent 1 execution time |
| **Project Validation** | < 200ms | Agent 2 execution time |
| **Market Analysis** | < 500ms | Agent 3 execution time |
| **Sync Frequency** | 1x / dia | Agent 7 schedule |
| **Freshness Check** | 2x / dia | Agent 4 schedule |

### Monitoramento Contínuo

Configure alertas para:
- ❌ Falhas de sincronização > 2 consecutivas
- ⚠️ Query time > 200ms (cached)
- ⚠️ Freshness check sem atualização > 7 dias

---

## 🎓 Casos de Uso

### Caso 1: Validação de Projeto CEMIG

```bash
# Via Huginn Agent 2
{
  "ceg": "MG.GD.CEMIG-D.00012345",
  "distribuidora": "CEMIG",
  "potencia_kw": 150.5,
  "modalidade": "mini",
  "municipio": "Belo Horizonte",
  "uf": "MG"
}

# Resultado esperado:
# ✅ CEG format válido
# ✅ Distribuidora existe
# ✅ Potência dentro da faixa
# ✅ Município na área de concessão
# ⚠️ Projeto não encontrado no SIGA (novo projeto)
```

### Caso 2: Análise de Mercado Sudeste

```bash
# Via Huginn Agent 3
{
  "region": "sudeste",
  "metric": "gd_penetration",
  "period": "2024"
}

# Resultado esperado:
# - SP: 45% penetração
# - MG: 38% penetração
# - RJ: 32% penetração
# - ES: 28% penetração
# - Oportunidades: RJ e ES (menor saturação)
```

### Caso 3: Cálculo de Tarifa CEMIG

```bash
# Via Huginn Agent 1
{
  "distribuidora": "CEMIG",
  "classe": "B1",
  "consumo_kwh": 500,
  "bandeira": "verde"
}

# Resultado esperado:
# - TUSD: R$ 0.45/kWh
# - TE: R$ 0.38/kWh
# - Total base: R$ 0.83/kWh
# - Bandeira verde: R$ 0.00
# - Total final: R$ 415.00
```

---

## 🔄 Atualizações Futuras

### Roadmap de Melhorias

**v1.1 (Próxima release)**:
- [ ] Parser CSV real com DuckDB
- [ ] Cache distribuído Redis
- [ ] API REST para queries diretas
- [ ] Dashboard Grafana

**v1.2**:
- [ ] Machine Learning para previsão de demanda
- [ ] Alertas preditivos de mudanças regulatórias
- [ ] Integração com SIGA em tempo real

**v1.3**:
- [ ] Análise geoespacial com PostGIS
- [ ] Recomendações de localização de projetos
- [ ] Otimização de rota para engenheiros

---

## 📞 Suporte

### Problemas ou Dúvidas?

1. **Documentação**: Veja `DELIVERABLES_SUMMARY.md`
2. **Issues**: Abra issue no GitHub
3. **Email**: contact@projecthelios.com (exemplo)

### Recursos Adicionais

- [Huginn Documentation](https://github.com/huginn/huginn/wiki)
- [ANEEL Dados Abertos](https://dadosabertos.aneel.gov.br/)
- [HaaS API Docs](http://localhost:8000/docs)
- [Dataset Hugging Face](https://huggingface.co/datasets/fernando-bold/aneel-datasets)

---

**Status**: ✅ Produção Ready (após configuração)  
**Última Atualização**: 20/10/2025  
**Versão**: 1.0.0
