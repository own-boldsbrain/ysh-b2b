# 🚀 Huginn + HaaS - Guia de Implementação Rápida

## ⏱️ Tempo Estimado: 2 horas

Este guia detalha os passos para implementar o **Piloto 1: Monitor de Certificados INMETRO** em produção.

---

## 📋 Pré-requisitos

### Infraestrutura
- [ ] Servidor com Docker e Docker Compose instalados
- [ ] 2 vCPUs, 4 GB RAM, 20 GB SSD disponíveis
- [ ] Acesso SSH ao servidor
- [ ] Domínio configurado (ex: `huginn.haas.ysh.com.br`)

### Credenciais e Acessos
- [ ] Token de administrador do HaaS
- [ ] Acesso ao Slack (webhook URL do canal #homologacoes)
- [ ] Credenciais SMTP para envio de emails

### Conhecimentos Técnicos
- [ ] Básico de Docker
- [ ] Básico de JSON
- [ ] Básico de HTTP/REST APIs

---

## 🔧 Parte 1: Deploy do Huginn (30 min)

### Passo 1.1: Criar `docker-compose.huginn.yml`

```bash
# Conectar ao servidor
ssh user@huginn.haas.ysh.com.br

# Criar diretório do projeto
mkdir -p /opt/huginn
cd /opt/huginn
```

```yaml
# docker-compose.huginn.yml
version: '3.8'

services:
  huginn:
    image: huginn/huginn:latest
    container_name: huginn_app
    ports:
      - "3000:3000"
    environment:
      DATABASE_ADAPTER: postgresql
      DATABASE_HOST: postgres
      DATABASE_NAME: huginn_production
      DATABASE_USERNAME: huginn
      DATABASE_PASSWORD: ${HUGINN_DB_PASSWORD}
      
      # Application Settings
      INVITATION_CODE: ${HUGINN_INVITATION_CODE}
      DOMAIN: huginn.haas.ysh.com.br
      FORCE_SSL: 'true'
      
      # Email Settings (SMTP)
      SMTP_DOMAIN: ysh.com.br
      SMTP_USER_NAME: ${SMTP_USERNAME}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_AUTHENTICATION: plain
      SMTP_ENABLE_STARTTLS_AUTO: 'true'
      EMAIL_FROM_ADDRESS: no-reply-huginn@ysh.com.br
      
      # Timezone
      TIMEZONE: America/Sao_Paulo
      
      # Memory Limits
      WEB_CONCURRENCY: 2
      RAILS_MAX_THREADS: 5
    
    volumes:
      - huginn-data:/var/lib/huginn
    
    depends_on:
      postgres:
        condition: service_healthy
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: huginn_postgres
    environment:
      POSTGRES_DB: huginn_production
      POSTGRES_USER: huginn
      POSTGRES_PASSWORD: ${HUGINN_DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8"
    
    volumes:
      - huginn-postgres:/var/lib/postgresql/data
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U huginn"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  huginn-data:
    driver: local
  huginn-postgres:
    driver: local

networks:
  default:
    name: huginn_network
```

### Passo 1.2: Criar arquivo `.env`

```bash
# .env
HUGINN_DB_PASSWORD=seu_password_seguro_aqui_123
HUGINN_INVITATION_CODE=convite_ysh_2025
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua_senha_app_gmail
```

**⚠️ IMPORTANTE**: Use uma **senha de app** do Gmail, não sua senha principal!

Como gerar senha de app Gmail:
1. Acesse https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Em "Senhas de app", gere uma nova senha
4. Copie e cole em `SMTP_PASSWORD`

### Passo 1.3: Iniciar o Huginn

```bash
# Iniciar containers
docker-compose -f docker-compose.huginn.yml up -d

# Verificar logs
docker-compose -f docker-compose.huginn.yml logs -f huginn

# Aguardar mensagem: "Listening on tcp://0.0.0.0:3000"
```

### Passo 1.4: Acessar Interface Web

1. Abra o navegador: `http://huginn.haas.ysh.com.br:3000`
2. **Primeiro Acesso**: Criar conta admin
   - Email: `admin@ysh.com.br`
   - Username: `admin`
   - Password: (escolha uma senha forte)
   - Invitation Code: `convite_ysh_2025` (do `.env`)
3. Login

✅ **Checkpoint**: Huginn rodando e acessível!

---

## 🔑 Parte 2: Configurar Credenciais (15 min)

### Passo 2.1: Gerar Token de Serviço no HaaS

```bash
# Via cURL (substituir ADMIN_TOKEN pelo seu token de admin)
curl -X POST https://haas.ysh.com.br/api/auth/service-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "service_name": "huginn",
    "scopes": ["webhooks:write", "monitoring:read"],
    "expires_in_days": 365
  }'

# Resposta:
# {
#   "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "expires_at": "2026-10-18T00:00:00Z"
# }
```

**Salve o token retornado!**

### Passo 2.2: Configurar Credenciais no Huginn

**Interface Web → Credentials → New Credential**

**Credencial 1: HaaS API Token**
- **Name**: `haas_api_token`
- **Value**: `Bearer eyJ0eXAiOiJKV1QiLCJhbGc...` (cole o token completo)
- **Description**: Token JWT do HaaS para autenticação de webhooks

**Credencial 2: Slack Webhook**
- **Name**: `slack_webhook_haas`
- **Value**: `https://hooks.slack.com/services/T00000000/B00000000/XXXX` (obter do Slack)
- **Description**: Webhook do canal #homologacoes

Como obter Slack Webhook:
1. Acesse https://api.slack.com/apps
2. Selecione seu workspace → "Incoming Webhooks"
3. Ative "Activate Incoming Webhooks"
4. "Add New Webhook to Workspace"
5. Selecione `#homologacoes`
6. Copie a Webhook URL

✅ **Checkpoint**: Credenciais configuradas no Huginn!

---

## 📦 Parte 3: Importar Cenário INMETRO (10 min)

### Passo 3.1: Copiar JSON do Cenário

```bash
# No servidor, baixar o cenário
cd /opt/huginn
curl -O https://raw.githubusercontent.com/own-boldsbrain/ysh-b2b/main/backend/data/project-helios/huginn-scenarios/inmetro-monitor.json
```

Ou copie o conteúdo do arquivo `huginn-scenarios/inmetro-monitor.json` do repositório.

### Passo 3.2: Importar via Interface Web

1. **Huginn → Scenarios → Import Scenario**
2. Cole o JSON completo
3. Clique em **"Import Scenario"**
4. Aguarde confirmação: "Scenario imported successfully"

### Passo 3.3: Verificar Agentes Criados

**Huginn → Agents**

Você deve ver 7 agentes:
1. ✅ INMETRO Watcher
2. ✅ Detect INMETRO Changes
3. ✅ Format HaaS Payload
4. ✅ Notify HaaS API (webhook receiver - NÃO USAR)
5. ✅ Send to HaaS Endpoint
6. ✅ Notify Team Slack
7. ✅ Email Alert Technical Team

**⚠️ IMPORTANTE**: Desative o agente #4 (Notify HaaS API) - é um webhook RECEIVER, não usaremos neste fluxo.

**Agents → Notify HaaS API → Edit → Marcar "Disabled"**

✅ **Checkpoint**: Cenário importado e agentes configurados!

---

## 🔌 Parte 4: Implementar Endpoint no HaaS (45 min)

### Passo 4.1: Criar Schema JSON

```bash
# No workspace do HaaS
cd haas/schemas
```

Criar arquivo `huginn_event.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://haas.ysh.com.br/schemas/huginn_event.schema.json",
  "title": "HuginEventPayload",
  "description": "Schema para eventos recebidos do Huginn",
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
      ],
      "description": "Tipo do evento"
    },
    "source": {
      "type": "string",
      "description": "Nome do agente Huginn que gerou o evento",
      "minLength": 1,
      "maxLength": 255
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp de criação do evento (ISO 8601)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confiabilidade dos dados extraídos (0-1)"
    },
    "data": {
      "type": "object",
      "description": "Payload específico do evento"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "scrape_url": {
          "type": "string",
          "format": "uri"
        },
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

### Passo 4.2: Criar Modelos Pydantic

Editar `haas/app/models/webhooks.py`:

```python
# Adicionar ao final do arquivo

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class HuginnEventType(str, Enum):
    """Tipos de eventos do Huginn."""
    INMETRO_CERTIFICATE_CHANGE = "inmetro_certificate_change"
    REGULATORY_CHANGE = "regulatory_change"
    TARIFF_UPDATE = "tariff_update"
    DISTRIBUTOR_PORTAL_CHANGE = "distributor_portal_change"
    CERTIFICATE_REVOCATION = "certificate_revocation"

class HuginnExtractionMethod(str, Enum):
    """Métodos de extração de dados."""
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    REGEX = "regex"
    API = "api"

class HuginnValidationStatus(str, Enum):
    """Status de validação."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    PENDING = "pending"

class HuginnEventMetadata(BaseModel):
    """Metadados do evento Huginn."""
    scrape_url: Optional[str] = None
    extraction_method: Optional[HuginnExtractionMethod] = None
    validation_status: Optional[HuginnValidationStatus] = None

class HuginnEventPayload(BaseModel):
    """Payload de evento recebido do Huginn."""
    event_type: HuginnEventType
    source: str = Field(..., min_length=1, max_length=255)
    timestamp: datetime
    confidence: Optional[float] = Field(None, ge=0, le=1)
    data: Dict[str, Any]
    metadata: Optional[HuginnEventMetadata] = None

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "inmetro_certificate_change",
                "source": "huginn_inmetro_watcher",
                "timestamp": "2025-10-18T14:30:00Z",
                "confidence": 0.95,
                "data": {
                    "last_update_date": "17/10/2025",
                    "page_hash": "a3f5c8d2e1b4",
                    "certificate_count": 1547
                },
                "metadata": {
                    "scrape_url": "https://www.gov.br/inmetro/...",
                    "extraction_method": "css_selector",
                    "validation_status": "automatic"
                }
            }
        }
```

### Passo 4.3: Criar Migration do Banco

```bash
# Gerar migration
cd haas
alembic revision -m "add huginn events table"
```

Editar o arquivo gerado em `haas/alembic/versions/xxx_add_huginn_events_table.py`:

```python
"""add huginn events table

Revision ID: xxx
Revises: yyy
Create Date: 2025-10-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'huginn_events',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('source_agent', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=True),
        sa.Column('data', JSONB, nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('processed', sa.Boolean, default=False, nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )
    
    # Indexes
    op.create_index('idx_huginn_events_type', 'huginn_events', ['event_type'])
    op.create_index('idx_huginn_events_timestamp', 'huginn_events', [sa.text('timestamp DESC')])
    op.create_index('idx_huginn_events_processed', 'huginn_events', ['processed'], postgresql_where=sa.text('NOT processed'))
    op.execute('CREATE INDEX idx_huginn_events_data_gin ON huginn_events USING GIN(data)')

def downgrade() -> None:
    op.drop_index('idx_huginn_events_data_gin')
    op.drop_index('idx_huginn_events_processed')
    op.drop_index('idx_huginn_events_timestamp')
    op.drop_index('idx_huginn_events_type')
    op.drop_table('huginn_events')
```

Aplicar migration:

```bash
alembic upgrade head
```

### Passo 4.4: Criar Endpoint no Router

Editar `haas/app/routers/webhooks.py`, adicionar ao final:

```python
# Importações adicionais no topo do arquivo
from app.models.webhooks import HuginnEventPayload
from sqlalchemy import text
import uuid

# Adicionar ao final do arquivo, antes de fechar o router

@router.post("/huginn/inmetro")
async def receive_huginn_inmetro_event(
    payload: HuginnEventPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_service_user)
):
    """
    Recebe eventos do Huginn sobre mudanças na base INMETRO.
    Requer autenticação de serviço (service account).
    """
    logger.info(f"Received Huginn event from {payload.source}: {payload.event_type}")
    
    try:
        # Validar tipo de evento
        if payload.event_type != "inmetro_certificate_change":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type for this endpoint: {payload.event_type}"
            )
        
        # Inserir no banco de dados
        insert_query = text("""
            INSERT INTO huginn_events (
                event_type, source_agent, timestamp, confidence, data, metadata, processed
            ) VALUES (
                :event_type, :source, :timestamp, :confidence, :data, :metadata, :processed
            ) RETURNING id
        """)
        
        result = db.execute(insert_query, {
            "event_type": payload.event_type.value,
            "source": payload.source,
            "timestamp": payload.timestamp,
            "confidence": payload.confidence,
            "data": payload.data,
            "metadata": payload.metadata.dict() if payload.metadata else None,
            "processed": False
        })
        db.commit()
        
        event_id = result.fetchone()[0]
        
        logger.info(f"Stored Huginn event with ID: {event_id}")
        
        # TODO: Processar evento (validar certificados afetados, notificar projetos)
        # Por enquanto, apenas armazena
        
        return {
            "status": "received",
            "event_id": str(event_id),
            "timestamp": datetime.utcnow().isoformat(),
            "message": "INMETRO change event stored successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing Huginn event: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process event: {str(e)}"
        )
```

**⚠️ IMPORTANTE**: Verifique se a função `get_current_service_user` existe em `app/auth/dependencies.py`. Se não existir, veja a seção de Segurança na proposta principal.

### Passo 4.5: Reiniciar HaaS

```bash
# Se usando Docker
docker-compose -f docker-compose.yml restart haas-api

# Se rodando localmente
# Ctrl+C e depois:
python haas/run.py
```

### Passo 4.6: Testar Endpoint

```bash
# Testar endpoint HaaS
curl -X POST https://haas.ysh.com.br/api/webhooks/huginn/inmetro \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_HUGINN" \
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
#   "event_id": "uuid-aqui",
#   "timestamp": "2025-10-18T14:30:05Z",
#   "message": "INMETRO change event stored successfully"
# }
```

✅ **Checkpoint**: Endpoint HaaS funcionando!

---

## 🧪 Parte 5: Teste End-to-End (20 min)

### Passo 5.1: Atualizar URL do Endpoint no Huginn

1. **Huginn → Agents → Send to HaaS Endpoint → Edit**
2. Localizar opção `post_url`
3. Verificar se está: `https://haas.ysh.com.br/api/webhooks/huginn/inmetro`
4. **Save**

### Passo 5.2: Executar Teste Manual

**Opção A: Forçar Execução do Primeiro Agente**

1. **Huginn → Agents → INMETRO Watcher**
2. Clicar em **"Run this Agent"**
3. Aguardar execução (pode demorar 10-30s)
4. Verificar em **Activity** se há eventos criados

**Opção B: Injetar Evento de Teste**

1. **Huginn → Agents → Format HaaS Payload → Edit**
2. Clicar em **"Dry Run"**
3. Cole um evento de exemplo:

```json
{
  "last_update_date": "17/10/2025",
  "page_hash": "a3f5c8d2e1b4test",
  "certificate_count": 1547
}
```

4. **Run** → Verificar output

### Passo 5.3: Verificar Fluxo Completo

**Checklist de Verificação**:

- [ ] **Huginn Activity**: Ver eventos fluindo entre agentes
- [ ] **Slack**: Mensagem apareceu no canal #homologacoes
- [ ] **Email**: Email recebido pela equipe técnica
- [ ] **HaaS Database**: Verificar registro inserido

```bash
# Verificar no banco HaaS
docker exec -it haas-postgres psql -U haas_user -d haas_platform

SELECT * FROM huginn_events ORDER BY created_at DESC LIMIT 1;
```

### Passo 5.4: Configurar Schedule Automático

Por padrão, o agente roda a cada 6h. Para alterar:

1. **Huginn → Agents → INMETRO Watcher → Edit**
2. Localizar campo `schedule`
3. Opções:
   - `every_2h`: A cada 2 horas
   - `every_6h`: A cada 6 horas (padrão)
   - `every_12h`: A cada 12 horas
   - `midnight`: Diariamente à meia-noite
4. **Save**

✅ **Checkpoint**: Sistema funcionando end-to-end!

---

## 🎉 Conclusão

### ✅ O que você implementou:

1. ✅ Huginn rodando em produção (Docker)
2. ✅ Credenciais configuradas (HaaS + Slack)
3. ✅ Cenário INMETRO Monitor importado
4. ✅ Endpoint HaaS `/api/webhooks/huginn/inmetro` funcional
5. ✅ Banco de dados PostgreSQL com tabela `huginn_events`
6. ✅ Notificações Slack + Email funcionando
7. ✅ Teste end-to-end validado

### 📊 Próximos Passos

**Imediato (Próximas 24h)**:
- [ ] Configurar monitoramento (Uptime Kuma, Grafana, etc)
- [ ] Criar alerta se o agente falhar 3x consecutivas
- [ ] Documentar processo para equipe

**Curto Prazo (Próxima Semana)**:
- [ ] Implementar processamento dos eventos INMETRO (validar certificados de projetos ativos)
- [ ] Criar dashboard de eventos Huginn no HaaS admin
- [ ] Adicionar logs estruturados (JSON) para debugging

**Médio Prazo (Próximo Mês)**:
- [ ] Implementar JTBD 2 (Regulatory Digest)
- [ ] Implementar JTBD 4 (Tariff Scraper)
- [ ] Criar testes automatizados de integração

### 📚 Recursos

- **Documentação Huginn**: https://github.com/huginn/huginn/wiki
- **Troubleshooting**: Ver `huginn-scenarios/README.md`
- **Suporte**: devops@ysh.com.br

---

**Parabéns!** 🎊 Você implementou com sucesso a integração **Huginn + HaaS** e automatizou o monitoramento de certificados INMETRO!

**Tempo Real vs. Estimado**: _________  
**Issues Encontrados**: _________  
**Feedback**: _________

---

**Preparado por**: GitHub Copilot  
**Data**: 18/10/2025  
**Versão**: 1.0
