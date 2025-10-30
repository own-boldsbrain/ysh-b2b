# Integração Huginn - HaaS Platform

## Visão Geral

O **Huginn** foi integrado ao stack do HaaS Platform para fornecer capacidades avançadas de automação de workflows, monitoramento proativo e integração entre sistemas.

## Por que Huginn?

- **Soberania de Dados**: Auto-hospedado, você controla 100% dos seus dados
- **Automação Determinística**: Lógica "se-então" confiável e previsível
- **Flexibilidade Total**: Configuração via JSON permite customização ilimitada
- **Integração Nativa**: Conecta facilmente com a API HaaS via webhooks e HTTP

## Casos de Uso no HaaS

### 1. Monitoramento Proativo
- Alertas quando certificados INMETRO são atualizados
- Notificações de mudanças de status em homologações
- Detecção de atrasos e gargalos no processo

### 2. Agregação de Informações
- Relatórios diários consolidados de homologações
- Coleta de atualizações regulatórias (ANEEL, INMETRO)
- Inteligência de mercado sobre concessionárias

### 3. Automação de Workflows
- Notificações automáticas para clientes via email/Slack
- Integração com sistemas externos (CRM, ferramentas de projeto)
- Gatilhos para ações baseadas em eventos do HaaS

### 4. Extração de Dados
- Web scraping de portais de concessionárias
- Transformação e estruturação de dados não estruturados
- Sincronização com base de dados do HaaS

## Arquitetura de Integração

```
┌─────────────────┐
│   HaaS API      │
│   (FastAPI)     │
└────────┬────────┘
         │
         │ Webhooks
         ▼
┌─────────────────┐      ┌──────────────┐
│     Huginn      │◄─────┤  PostgreSQL  │
│   (Workflows)   │      │  (Shared DB) │
└────────┬────────┘      └──────────────┘
         │
         │ Actions
         ▼
┌─────────────────┐
│  Email/Slack/   │
│  External APIs  │
└─────────────────┘
```

## Acesso e Configuração

### URLs de Acesso

- **Interface Web**: http://localhost:3000
- **Credenciais Padrão**: admin / password (configurável via `.env`)

### Variáveis de Ambiente Importantes

```bash
# No arquivo .env
HUGINN_PORT=3000
HUGINN_INVITATION_CODE=try-huginn
HUGINN_SEED_USERNAME=admin
HUGINN_SEED_PASSWORD=password
HUGINN_TIMEZONE=America/Sao_Paulo
```

## Cenários Pré-Configurados

### 1. Monitor INMETRO
**Arquivo**: `huginn/scenarios/monitoring/inmetro-updates.json`

Monitora atualizações de certificados INMETRO e envia alertas por email.

**Fluxo**:
```
Scheduler (diário) → API HaaS → Detecta mudanças → Formata email → Envia
```

### 2. HaaS Webhooks
**Arquivo**: `huginn/scenarios/integration/haas-webhooks.json`

Recebe eventos da API HaaS e distribui notificações.

**Eventos suportados**:
- `project.created` - Novo projeto criado
- `homologation.approved` - Homologação aprovada
- `homologation.delayed` - Atraso detectado

**Fluxo**:
```
Webhook Receiver → Filtros (por tipo de evento) → Formata → Email/Slack/Log
```

## Guia Rápido de Uso

### 1. Iniciar o Huginn

```bash
cd haas
docker-compose up -d huginn
```

### 2. Primeiro Acesso

1. Acesse http://localhost:3000
2. Use o código de convite configurado no `.env`
3. Crie sua conta ou faça login com admin/password

### 3. Configurar Credenciais

Antes de usar os cenários, configure:

**Settings → Credentials:**
- `haas_api_token`: Token JWT da API HaaS
- `slack_webhook_url`: URL do webhook Slack (opcional)

### 4. Importar Cenário

1. **Scenarios → Import**
2. Cole o JSON de `huginn/scenarios/`
3. Revise os agentes importados
4. Ative o cenário

### 5. Testar Webhook

```bash
# Obter ID do webhook agent na interface web
# URL: http://localhost:3000/users/1/web_requests/{agent_id}/{secret}

curl -X POST http://localhost:3000/users/1/web_requests/1/haas-webhook-secret-2025 \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "project.created",
    "timestamp": "2025-10-17T12:00:00Z",
    "project": {
      "id": "123",
      "name": "Projeto Solar Teste",
      "client": "Cliente ABC",
      "distributor": "CEMIG",
      "status": "pending"
    }
  }'
```

## Integração com a API HaaS

### Enviando Eventos do HaaS para Huginn

No código da API HaaS, adicione chamadas webhook:

```python
import httpx

async def notify_huginn(event_type: str, data: dict):
    webhook_url = "http://huginn:3000/users/1/web_requests/{agent_id}/{secret}"
    
    payload = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)

# Exemplo de uso
await notify_huginn("project.created", {
    "project": {
        "id": project.id,
        "name": project.name,
        "client": project.client,
        "distributor": project.distributor,
        "status": project.status
    }
})
```

### Consumindo API HaaS do Huginn

Use `WebsiteAgent` ou `PostAgent`:

```json
{
  "type": "Agents::WebsiteAgent",
  "options": {
    "url": "http://haas-api:8000/api/v1/projects",
    "type": "json",
    "headers": {
      "Authorization": "Bearer {% credential haas_api_token %}"
    },
    "extract": {
      "projects": { "path": "data" }
    }
  }
}
```

## Criando Novos Agentes

### Exemplo: Monitorar API Externa

```json
{
  "type": "Agents::WebsiteAgent",
  "name": "Monitor Concessionária XYZ",
  "options": {
    "url": "https://api.concessionaria.com/status",
    "type": "json",
    "mode": "on_change",
    "extract": {
      "status": { "path": "data.status" },
      "message": { "path": "data.message" }
    }
  },
  "schedule": "every_1h"
}
```

### Exemplo: Enviar Email

```json
{
  "type": "Agents::EmailAgent",
  "name": "Notificação Email",
  "options": {
    "subject": "Alerta: {{ status }}",
    "body": "Mensagem: {{ message }}\n\nTimestamp: {{ timestamp }}",
    "recipients": ["admin@haas.com"]
  }
}
```

## Boas Práticas

### Segurança
- ✅ Altere senha padrão do admin imediatamente
- ✅ Use secrets fortes nos webhooks
- ✅ Armazene tokens em **Credentials**, não em JSON
- ✅ Em produção, use HTTPS e restrinja acesso

### Performance
- ✅ Configure `keep_events_for` adequadamente (7-30 dias)
- ✅ Use schedules espaçados para evitar sobrecarga
- ✅ Limite `events_to_show` em feeds (10-100)
- ✅ Archive cenários não utilizados

### Manutenção
- ✅ Monitore logs regularmente: `docker-compose logs huginn`
- ✅ Faça backup do volume `huginn_data`
- ✅ Documente cenários customizados
- ✅ Teste cenários em dry-run antes de ativar

## Troubleshooting

### Huginn não inicia

```bash
# Ver logs
docker-compose logs huginn

# Recriar container
docker-compose restart huginn
```

### Erro de conexão com PostgreSQL

```bash
# Verificar se o banco existe
docker-compose exec postgres psql -U haas_user -l

# Recriar banco do Huginn
docker-compose exec postgres psql -U haas_user -c "CREATE DATABASE huginn_production;"
docker-compose restart huginn
```

### Webhook não recebe eventos

1. Verifique URL do webhook na interface Huginn
2. Confirme que o secret está correto
3. Teste com curl (veja exemplo acima)
4. Verifique logs: **Agent → Show → Recent Events**

### Emails não enviam

1. Configure SMTP no `.env`:
   ```bash
   HUGINN_SMTP_SERVER=smtp.gmail.com
   HUGINN_SMTP_PORT=587
   HUGINN_SMTP_USER=seu-email@gmail.com
   HUGINN_SMTP_PASSWORD=senha-app-google
   ```
2. Reinicie Huginn: `docker-compose restart huginn`
3. Teste com agente de email simples

## Recursos Adicionais

- **Documentação Completa**: [huginn/QUICKSTART.md](QUICKSTART.md)
- **Cenários Disponíveis**: [huginn/scenarios/README.md](scenarios/README.md)
- **Documentação Oficial**: https://github.com/huginn/huginn/wiki
- **Tipos de Agentes**: https://github.com/huginn/huginn/wiki/Agent-Types

## Próximos Passos

1. ✅ Importe e teste o cenário "Monitor INMETRO"
2. ✅ Configure webhooks na API HaaS
3. ✅ Customize notificações (email/Slack)
4. ✅ Crie cenários específicos para seu workflow
5. ✅ Configure backups automáticos

---

**Dúvidas?** Consulte a documentação completa em `huginn/scenarios/README.md` ou os logs em `logs/huginn/`.
