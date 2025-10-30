# 🏗️ Arquitetura de Integração: Huginn ↔ HaaS

## 📐 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HUGINN - Sistema de Automação Soberana                   │
│                              (Self-Hosted / On-Premises)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ Webhooks HTTP/HTTPS
                                         │ (Bidirectional)
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
┌───────────────┐              ┌───────────────┐               ┌──────────────┐
│  WebsiteAgent │              │ WebhookAgent  │               │  PostAgent   │
│  (Scraping)   │              │  (Receiver)   │               │  (Sender)    │
└───────┬───────┘              └───────┬───────┘               └──────┬───────┘
        │                              │                              │
        │ Extrai dados                 │ Recebe eventos               │ Envia dados
        │ de portais                   │ do HaaS                      │ para HaaS
        │                              │                              │
        ▼                              │                              ▼
┌───────────────┐                      │                      ┌──────────────┐
│ TriggerAgent  │                      │                      │  SlackAgent  │
│ (Detect)      │◄─────────────────────┘                      │ (Notify)     │
└───────┬───────┘                                             └──────────────┘
        │                                                              ▲
        │ Mudanças detectadas                                          │
        │                                                              │
        ▼                                                              │
┌─────────────────────────────────────────────────────────────────────┼──────┐
│                    EventFormattingAgent                             │      │
│                    (Transform to HaaS Schema)                       │      │
└─────────────────────────────────────────────────────────────────────┬──────┘
                                         │                            │
                                         │ JSON Payload               │
                                         │                            │
                                         ▼                            │
        ┌────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HaaS Platform - FastAPI Backend                          │
│                              (AWS / Self-Hosted)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ├─────────► POST /api/webhooks/huginn/inmetro
        │           ├── Autenticação: Bearer Token (Service Account)
        │           ├── Validação: Pydantic Schema (HuginnEventPayload)
        │           └── Response: {status, event_id, timestamp}
        │
        ├─────────► GET /api/health (healthcheck)
        │
        └─────────► POST /api/webhooks/haas/events (emissão de eventos)
                    └── Notifica Huginn sobre mudanças no HaaS
                        (ex: projeto aprovado, documento gerado)

┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Database (HaaS)                               │
│                              + PostGIS + pgvector                                │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ├─────────► huginn_events (tabela)
        │           ├── Columns: id, event_type, source_agent, timestamp,
        │           │            confidence, data (JSONB), metadata (JSONB),
        │           │            processed, processed_at, created_at
        │           └── Indexes: event_type, timestamp DESC, processed,
        │                        data (GIN for JSONB queries)
        │
        ├─────────► inmetro_certificates (validação futura)
        │
        └─────────► projects (vincular eventos a projetos ativos)

┌─────────────────────────────────────────────────────────────────────────────────┐
│                         Notificações Externas                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ├─────────► Slack (#homologacoes)
        │           └── Via SlackAgent do Huginn
        │
        ├─────────► Email (equipe técnica)
        │           └── Via EmailAgent do Huginn (SMTP)
        │
        └─────────► SMS/WhatsApp (futuro)
                    └── Via Twilio/MessageBird
```

---

## 🔄 Fluxos de Dados Principais

### Fluxo 1: Monitoramento INMETRO → Notificação HaaS

```
1. [Huginn] WebsiteAgent scrape https://www.gov.br/inmetro/... (a cada 6h)
   └─► Extrai: {last_update_date, page_hash, certificate_count}

2. [Huginn] TriggerAgent compara page_hash com execução anterior
   └─► Se mudou: emite evento

3. [Huginn] EventFormattingAgent formata para schema HaaS
   └─► Cria JSON:
       {
         "event_type": "inmetro_certificate_change",
         "source": "huginn_inmetro_watcher",
         "timestamp": "2025-10-18T14:30:00Z",
         "confidence": 0.95,
         "data": {...},
         "metadata": {...}
       }

4. [Huginn] PostAgent envia para HaaS
   └─► POST https://haas.ysh.com.br/api/webhooks/huginn/inmetro
       Headers: Authorization: Bearer <service_token>

5. [HaaS] Endpoint valida e armazena
   └─► INSERT INTO huginn_events
       └─► Retorna: {status: "received", event_id: "uuid"}

6. [Huginn] SlackAgent notifica canal
   └─► POST https://hooks.slack.com/services/T.../B.../XXX
       Message: "⚠️ INMETRO Database Updated..."

7. [Huginn] EmailAgent envia alerta
   └─► SMTP send to: equipe-tecnica@ysh.com.br
       Subject: "🚨 Alerta: Atualização Base INMETRO..."
```

**Tempo Total**: ~15-30 segundos (após detecção de mudança)

---

### Fluxo 2: HaaS Evento → Acionamento Huginn Workflow

```
1. [HaaS] Projeto aprovado em validação INMETRO
   └─► Evento interno: {project_id, status: "approved"}

2. [HaaS] Webhook emitido para Huginn
   └─► POST http://huginn.haas.ysh.com.br/users/1/webhooks/xyz/receive
       Payload: {
         "event_type": "project_approved",
         "project_id": "proj_12345",
         "distributor_code": "ENEL-SP",
         "timestamp": "2025-10-18T15:00:00Z"
       }

3. [Huginn] WebhookAgent recebe e valida
   └─► Verifica secret, extrai payload

4. [Huginn] TriggerAgent filtra por event_type
   └─► Se "project_approved": aciona fluxo de documentos

5. [Huginn] PostAgent → Gerar Memorial Descritivo
   └─► POST https://haas.ysh.com.br/api/documents/generate
       {project_id, document_type: "memorial_descritivo"}

6. [Huginn] DelayAgent aguarda processamento
   └─► Espera 60s para geração completa

7. [Huginn] PostAgent → Gerar Diagrama Unifilar
   └─► POST https://haas.ysh.com.br/api/documents/diagrams/generate
       {project_id, diagram_type: "unifilar"}

8. [Huginn] PostAgent → Submeter para Concessionária
   └─► POST https://haas.ysh.com.br/api/distributors/ENEL-SP/submit
       {project_id, documents: [...]}

9. [Huginn] SlackAgent notifica sucesso
   └─► "✅ Projeto proj_12345 submetido para ENEL-SP"
```

**Tempo Total**: ~2-3 minutos (incluindo geração de documentos)

---

## 🔐 Segurança e Autenticação

### Autenticação Huginn → HaaS

```python
# HaaS: Validação de Token de Serviço

@router.post("/webhooks/huginn/inmetro")
async def receive_huginn_event(
    payload: HuginnEventPayload,
    current_user: User = Depends(get_current_service_user)  # ← Service Account
):
    # current_user.type == "service_account"
    # current_user.service_name == "huginn"
    # current_user.scopes == ["webhooks:write", "monitoring:read"]
    ...
```

**Token JWT de Serviço**:
```json
{
  "sub": "service:huginn",
  "type": "service_account",
  "service_name": "huginn",
  "scopes": ["webhooks:write", "monitoring:read"],
  "iat": 1729267200,
  "exp": 1760803200
}
```

**Armazenamento no Huginn**:
```yaml
# Huginn Credentials Manager
credentials:
  - name: haas_api_token
    value: "Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
    description: "Token JWT do HaaS (válido até 2026-10-18)"
```

**Uso no PostAgent**:
```json
{
  "type": "Agents::PostAgent",
  "options": {
    "headers": {
      "Authorization": "{% credential haas_api_token %}"
    }
  }
}
```

---

### Autenticação HaaS → Huginn

```yaml
# Huginn: Webhook Receiver com Secret Validation

WebhookAgent:
  options:
    secret: "whsec_3f8a9b2c1d4e5f6g7h8i9j0k"
    verbs: ["post"]
    response: "Event received"
```

**HaaS enviando webhook**:
```python
import hmac
import hashlib

def send_webhook_to_huginn(payload: dict):
    secret = settings.HUGINN_WEBHOOK_SECRET
    signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Huginn-Signature": f"sha256={signature}"
    }
    
    requests.post(
        "http://huginn.haas.ysh.com.br/users/1/webhooks/xyz/receive",
        json=payload,
        headers=headers
    )
```

---

## 📊 Schema de Dados

### HuginnEventPayload (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HuginEventPayload",
  "type": "object",
  "required": ["event_type", "source", "timestamp", "data"],
  "properties": {
    "event_type": {
      "type": "string",
      "enum": [
        "inmetro_certificate_change",
        "regulatory_change",
        "tariff_update",
        "distributor_portal_change",
        "certificate_revocation"
      ]
    },
    "source": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "data": {
      "type": "object"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "scrape_url": {"type": "string", "format": "uri"},
        "extraction_method": {
          "type": "string",
          "enum": ["css_selector", "xpath", "regex", "api"]
        },
        "validation_status": {
          "type": "string",
          "enum": ["automatic", "manual", "pending"]
        }
      }
    }
  }
}
```

### PostgreSQL Schema

```sql
CREATE TABLE huginn_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    source_agent VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence DECIMAL(3,2),
    data JSONB NOT NULL,
    metadata JSONB,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_huginn_events_type ON huginn_events(event_type);
CREATE INDEX idx_huginn_events_timestamp ON huginn_events(timestamp DESC);
CREATE INDEX idx_huginn_events_processed ON huginn_events(processed) 
    WHERE NOT processed;
CREATE INDEX idx_huginn_events_data_gin ON huginn_events USING GIN(data);

-- Query de exemplo (buscar eventos não processados)
SELECT * FROM huginn_events
WHERE processed = FALSE
  AND event_type = 'inmetro_certificate_change'
ORDER BY timestamp DESC
LIMIT 10;

-- Query de exemplo (buscar por conteúdo no JSONB)
SELECT * FROM huginn_events
WHERE data @> '{"certificate_count": 1547}'::jsonb;
```

---

## 🧪 Testes de Integração

### Teste 1: Healthcheck HaaS

```bash
curl https://haas.ysh.com.br/api/health

# Resposta esperada:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-18T14:30:00Z",
#   "version": "1.0.0"
# }
```

---

### Teste 2: Enviar Evento de Teste (Huginn → HaaS)

```bash
curl -X POST https://haas.ysh.com.br/api/webhooks/huginn/inmetro \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "event_type": "inmetro_certificate_change",
    "source": "test_manual",
    "timestamp": "2025-10-18T14:30:00Z",
    "confidence": 0.95,
    "data": {
      "last_update_date": "17/10/2025",
      "page_hash": "test123",
      "certificate_count": 1547
    },
    "metadata": {
      "scrape_url": "https://www.gov.br/inmetro/...",
      "extraction_method": "css_selector",
      "validation_status": "automatic"
    }
  }'

# Resposta esperada:
# {
#   "status": "received",
#   "event_id": "550e8400-e29b-41d4-a716-446655440000",
#   "timestamp": "2025-10-18T14:30:05Z",
#   "message": "INMETRO change event stored successfully"
# }
```

---

### Teste 3: Verificar Armazenamento no Banco

```sql
-- Conectar ao PostgreSQL do HaaS
psql -h localhost -U haas_user -d haas_platform

-- Verificar último evento
SELECT 
    id,
    event_type,
    source_agent,
    timestamp,
    confidence,
    data->'certificate_count' as cert_count,
    processed
FROM huginn_events
ORDER BY created_at DESC
LIMIT 1;

-- Resultado esperado:
--                   id                  |       event_type           | source_agent |      timestamp      | confidence | cert_count | processed
-- -------------------------------------+---------------------------+--------------+---------------------+------------+------------+-----------
--  550e8400-e29b-41d4-a716-446655440000 | inmetro_certificate_change | test_manual  | 2025-10-18 14:30:00 |       0.95 | 1547       | f
```

---

## 📈 Monitoramento e Observabilidade

### Métricas Chave

| Métrica | Descrição | Threshold |
|---------|-----------|-----------|
| **Webhook Delivery Rate** | % de webhooks entregues com sucesso | >95% |
| **Average Response Time** | Tempo médio de resposta do endpoint HaaS | <500ms |
| **Event Processing Rate** | Eventos processados por hora | >100/h |
| **Error Rate** | % de erros 4xx/5xx | <5% |
| **Agent Uptime** | Disponibilidade dos agentes Huginn | >99% |

---

### Dashboard de Monitoramento

**Huginn Built-in Stats**: `http://huginn.haas.ysh.com.br/stats`

Gráficos disponíveis:
- Events created per day
- Agent execution status
- Memory usage per agent
- Webhook delivery success rate

**HaaS Custom Dashboard** (a implementar):
```sql
-- Query para dashboard
SELECT 
    event_type,
    COUNT(*) as total_events,
    AVG(confidence) as avg_confidence,
    COUNT(*) FILTER (WHERE processed = TRUE) as processed_count,
    COUNT(*) FILTER (WHERE processed = FALSE) as pending_count
FROM huginn_events
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY event_type
ORDER BY total_events DESC;
```

---

## 🚨 Alertas e Notificações

### Configuração de Alertas

```yaml
# Alerta: Huginn Agent Falhou 3x Consecutivas
Alert:
  type: AgentFailure
  threshold: 3
  window: 1h
  action: Email + Slack
  recipients:
    - devops@ysh.com.br
    - slack:#alerts-haas

# Alerta: Endpoint HaaS Retornando 5xx
Alert:
  type: EndpointError
  threshold: 10 errors in 5 min
  action: PagerDuty Incident
  severity: High

# Alerta: Evento INMETRO Não Processado em 1h
Alert:
  type: EventProcessingDelay
  threshold: 1h
  action: Slack
  channel: #homologacoes
```

---

## 📚 Recursos Adicionais

### Documentação Técnica
- [FastAPI Webhooks](https://fastapi.tiangolo.com/advanced/events/)
- [Huginn Agent Types](https://github.com/huginn/huginn/wiki/Agent-Types)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)

### Ferramentas
- **RequestBin**: https://requestbin.com (testar webhooks)
- **JSONPath Tester**: https://jsonpath.com (validar extrações)
- **CSS Selector Tester**: https://try.jsoup.org (validar scrapers)

---

**Preparado por**: GitHub Copilot  
**Data**: 18/10/2025  
**Versão**: 1.0
