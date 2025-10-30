# Huginn Integration - Quick Start Guide

## 🚀 Início Rápido

### 1. Iniciar o Stack Completo

```bash
cd haas
docker-compose up -d
```

Aguarde todos os serviços iniciarem (pode levar 1-2 minutos na primeira vez).

### 2. Acessar o Huginn

Abra o navegador em: **http://localhost:3000**

**Credenciais padrão** (configure no `.env`):
- Username: `admin`
- Password: `password`
- Invitation Code: `try-huginn`

### 3. Configurar Credenciais

Antes de importar cenários, configure as credenciais necessárias:

1. Acesse: **Settings → Credentials**
2. Adicione as seguintes credenciais:

   - **haas_api_token**
     - Name: `haas_api_token`
     - Value: `seu-token-jwt-aqui`
     
   - **slack_webhook_url** (opcional)
     - Name: `slack_webhook_url`
     - Value: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

### 4. Importar Cenário Piloto

1. Acesse: **Scenarios → Import**
2. Cole o conteúdo de um dos arquivos:
   - `monitoring/inmetro-updates.json` (Recomendado para começar)
   - `integration/haas-webhooks.json`
3. Clique em **Import**
4. Revise os agentes importados
5. Ative o cenário

### 5. Testar Integração

#### Teste do Monitor INMETRO:

```bash
# Trigger manual do scheduler
curl -X POST http://localhost:3000/users/1/agents/{scheduler-agent-id}/run
```

#### Teste do Webhook:

```bash
curl -X POST http://localhost:3000/users/1/web_requests/{webhook-agent-id}/haas-webhook-secret-2025 \
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

## 📊 Verificar Status dos Serviços

```bash
# Ver status de todos os containers
docker-compose ps

# Ver logs do Huginn
docker-compose logs -f huginn

# Ver logs da API HaaS
docker-compose logs -f haas-api
```

## 🔧 Configuração de Produção

### Variáveis Essenciais no `.env`:

```bash
# Segurança
HUGINN_SECRET_KEY_BASE=$(openssl rand -hex 64)
HUGINN_INVITATION_CODE=seu-codigo-secreto

# Credenciais admin
HUGINN_SEED_USERNAME=seu-admin
HUGINN_SEED_PASSWORD=senha-forte-aqui
HUGINN_SEED_EMAIL=admin@sua-empresa.com

# Domínio (produção)
HUGINN_DOMAIN=huginn.sua-empresa.com
HUGINN_PROTOCOL=https

# Email SMTP (para notificações)
HUGINN_SMTP_SERVER=smtp.gmail.com
HUGINN_SMTP_PORT=587
HUGINN_SMTP_USER=seu-email@gmail.com
HUGINN_SMTP_PASSWORD=sua-senha-app
HUGINN_EMAIL_FROM=noreply@sua-empresa.com
```

## 🎯 Próximos Passos

1. **Customize os cenários** para suas necessidades específicas
2. **Configure webhooks** na API HaaS para enviar eventos ao Huginn
3. **Crie novos agentes** para automações específicas do seu negócio
4. **Configure backups** do volume `huginn_data`
5. **Monitore logs** regularmente para garantir operação correta

## 📚 Recursos

- [Documentação Huginn](https://github.com/huginn/huginn/wiki)
- [Tipos de Agentes](https://github.com/huginn/huginn/wiki/Agent-Types)
- [Cenários de Exemplo](scenarios/README.md)
- [API HaaS Docs](http://localhost:8000/docs)

## ⚠️ Troubleshooting

### Huginn não inicia

```bash
# Verificar logs
docker-compose logs huginn

# Recriar container
docker-compose down
docker-compose up -d huginn
```

### Erro de conexão com banco de dados

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Recriar banco do Huginn
docker-compose exec postgres psql -U haas_user -c "DROP DATABASE IF EXISTS huginn_production;"
docker-compose exec postgres psql -U haas_user -c "CREATE DATABASE huginn_production;"
docker-compose restart huginn
```

### Agentes não executam

1. Verifique se o scheduler está rodando: **Settings → Background Jobs**
2. Confirme credenciais configuradas corretamente
3. Revise logs do agente específico na interface web
4. Teste manualmente: clique no agente → **Run**

## 🔒 Segurança

- ✅ Sempre use HTTPS em produção
- ✅ Altere senha padrão imediatamente
- ✅ Use secrets fortes para webhooks
- ✅ Limite acesso ao Huginn via firewall/VPN
- ✅ Faça backup regular do volume `huginn_data`
- ✅ Rotacione tokens de API periodicamente

## 💡 Dicas de Performance

- Configure `keep_events_for` adequadamente (7-30 dias)
- Use schedules espaçados (evite executar muitos agentes simultaneamente)
- Monitore uso de recursos com `docker stats`
- Limite `events_to_show` em DataOutputAgents
- Archive cenários não utilizados
