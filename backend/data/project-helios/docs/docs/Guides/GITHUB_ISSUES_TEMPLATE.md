# 🎯 GitHub Issues - Project Helios

> ⚠️ **IMPORTANTE**: O repositório `own-boldsbrain/ysh-b2b` está com Issues desabilitadas.

> **Para habilitar:**
>
> 1. Vá em: https://github.com/own-boldsbrain/ysh-b2b/settings
> 2. Em "Features", marque a opção "Issues"
> 3. Salve as configurações
> 4. Depois, copie e cole cada issue abaixo manualmente

---

## 🔴 P0 - BLOQUEADORES CRÍTICOS

### Issue #1: [P0] Database Setup - PostgreSQL + PostGIS + pgvector

**Labels**: `priority: critical`, `type: infrastructure`, `blocker`

**Descrição:**

```markdown
## 🎯 Objetivo
Configurar infraestrutura de banco de dados para persistência de dados do Project Helios.

## 📋 Tarefas
- [ ] Instalar PostgreSQL 15 com extensões PostGIS e pgvector
- [ ] Configurar variáveis de ambiente de conexão (.env)
- [ ] Executar migrations Alembic
- [ ] Criar seed data inicial (67 distribuidoras, tarifas ANEEL)
- [ ] Configurar Redis para cache
- [ ] Testar conexões database (PostgreSQL + Redis)

## 📥 Inputs
- Credenciais de banco de dados
- Scripts de migration em `haas/alembic/`
- Dados de distribuidoras em `schemas/distribuidoras_gd.schema.json`

## 📤 Outputs Esperados
- ✅ PostgreSQL rodando com extensões ativas
- ✅ 67 distribuidoras carregadas
- ✅ Tarifas ANEEL 2025 carregadas
- ✅ Redis configurado com TTL padrão
- ✅ Conexões testadas e validadas

## 🎯 Outcomes
- Sistema persiste dados entre restarts
- Queries otimizadas com índices
- Cache Redis reduz 80% de queries ao banco

## ⏱️ Estimativa
3 dias

## 🔗 Arquivos Relacionados
- `haas/alembic/env.py`
- `haas/app/database/connection.py`
- `haas/docker-compose.yml`
- `schemas/distribuidoras_gd.schema.json`
```

---

### Issue #2: [P0] INMETRO API Integration - Conectar Backend aos Endpoints REST

**Labels**: `priority: critical`, `type: backend`, `blocker`

**Descrição:**
```markdown
## 🎯 Objetivo
Expor validação de equipamentos INMETRO via REST API (backend 100% pronto, falta apenas exposição).

## 📋 Tarefas
- [ ] Criar singleton de `InmetroPipeline` no FastAPI (Dependency Injection)
- [ ] Substituir dict `_validation_status` por Redis com TTL 24h
- [ ] Implementar `_process_validation()` com background tasks
- [ ] Conectar `InmetroRepository` ao PostgreSQL
- [ ] Expor endpoint `POST /validation/inmetro/equipment`
- [ ] Expor endpoint `GET /validation/inmetro/equipment/{id}`
- [ ] Expor endpoint `POST /validation/inmetro/batch`
- [ ] Expor endpoint `GET /validation/inmetro/manufacturers`
- [ ] Expor endpoint `GET /validation/inmetro/models/{manufacturer}`
- [ ] Testar validação end-to-end

## 📥 Inputs
```json
POST /validation/inmetro/equipment
{
  "manufacturer": "Canadian Solar",
  "model": "CS7N-665MS",
  "type": "painel_solar",
  "certificate_number": "INMETRO/EB-XYZ/2024"
}
```

## 📤 Outputs Esperados

```json
{
  "is_valid": true,
  "certificate_status": "active",
  "expiration_date": "2029-12-31",
  "manufacturer": "Canadian Solar",
  "model": "CS7N-665MS",
  "power_wp": 665,
  "efficiency_percent": 21.5,
  "tier": 1,
  "technology": "N-Type TOPCon"
}
```

## 🎯 Outcomes

- Validação de 100+ equipamentos/minuto
- Resposta < 15 segundos (vs 3-5 dias manual)
- Diferencial competitivo #1 ativado

## 🔗 Dependências

- Issue #1: Database Setup (PostgreSQL + Redis)

## ⏱️ Estimativa

5 dias

## 🔗 Arquivos Relacionados

- `haas/validators/inmetro/pipeline.py`
- `haas/validators/inmetro/crawler.py`
- `haas/validators/inmetro/validator.py`
- `haas/validators/inmetro/repository.py`
- `haas/app/routers/inmetro.py` (criar)
- `haas/app/services/inmetro_service.py` (criar)

---

### Issue #3: [P0] Huginn Production Deployment - Deploy 12 Cenários

**Labels**: `priority: critical`, `type: devops`, `automation`

**Descrição:**

```markdown
## 🎯 Objetivo
Colocar em produção os 12 cenários Huginn (INMETRO, ANEEL, EPE, 9 distribuidoras) para monitoramento 24/7.

## 📋 Tarefas
- [ ] Provisionar VPS/Docker para Huginn
- [ ] Configurar SSL/HTTPS (Let's Encrypt)
- [ ] Importar cenário `inmetro-monitor.json`
- [ ] Importar cenário `aneel-data-mcp.json`
- [ ] Importar cenário `epe-consumo-monitor.json`
- [ ] Importar 9 cenários de distribuidoras (Enel SP, CEMIG, CPFL, Coelba, Copel, Celesc, RGE, Equatorial, Energisa)
- [ ] Configurar credencial `haas_api_token` (JWT)
- [ ] Configurar credencial `slack_webhook_haas`
- [ ] Testar integração com HaaS API
- [ ] Testar notificações Slack/Email
- [ ] Ativar monitoramento 24/7
- [ ] Configurar backups automáticos

## 📥 Inputs
- 12 arquivos JSON em `huginn-scenarios/`
- Token JWT do HaaS
- Webhook URL do Slack

## 📤 Outputs Esperados
- ✅ Huginn acessível via HTTPS
- ✅ 12 cenários ativos e funcionais
- ✅ Notificações sendo enviadas
- ✅ Webhooks chegando ao HaaS
- ✅ Logs estruturados

## 🎯 Outcomes
- Monitoramento 24/7 de R$ 144M de mercado
- Detecção automática de mudanças regulatórias
- Notificações proativas para equipes

## 📊 Mercado Coberto
- **Core**: INMETRO + ANEEL (207 datasets) + EPE
- **Tier 1**: Enel SP (45k proj/ano) + CEMIG (38k proj/ano)
- **Tier 2**: CPFL (32k proj/ano) + Coelba (24k proj/ano)
- **Tier 3**: Copel (28k proj/ano) + Celesc (18k proj/ano)
- **Tier 4**: RGE (16k) + Equatorial (41k) + Energisa (78k)
- **Total**: 320k projetos/ano | R$ 144M

## ⏱️ Estimativa
2 dias

## 🔗 Arquivos Relacionados
- `huginn-scenarios/*.json` (12 arquivos)
- `huginn-scenarios/README.md`
- `haas/docker-compose.yml`
```

---

## 🟡 P1 - IMPORTANTES

### Issue #4: [P1] Geração de Documentos - Memorial Descritivo + Templates

**Labels**: `priority: high`, `type: backend`, `feature`

**Descrição:**

```markdown
## 🎯 Objetivo
Implementar geração automática de memoriais descritivos e outros documentos necessários para homologação.

## 📋 Tarefas
- [ ] Criar templates Jinja2 para memorial descritivo
- [ ] Integrar WeasyPrint para renderização PDF
- [ ] Implementar endpoint `POST /documents/memorial`
- [ ] Implementar endpoint `GET /documents/templates`
- [ ] Implementar endpoint `GET /documents/download/{id}`
- [ ] Configurar storage S3 ou local para PDFs
- [ ] Adicionar marca d'água e metadados
- [ ] Testar geração com dados reais
- [ ] Validar conformidade com normas técnicas

## 📥 Inputs
```json
POST /documents/memorial
{
  "project_id": "proj_123abc",
  "client_name": "João Silva",
  "installation_address": "Rua das Flores, 123",
  "system_capacity_kwp": 5.2,
  "modules": [...],
  "inverter": {...},
  "distributor": "ENEL_SP"
}
```

## 📤 Outputs Esperados

```json
{
  "document_id": "doc_xyz789",
  "document_type": "memorial_descritivo",
  "format": "pdf",
  "size_bytes": 245678,
  "pages": 8,
  "download_url": "/documents/download/doc_xyz789",
  "generated_at": "2025-10-22T15:45:00Z",
  "expires_at": "2025-11-22T15:45:00Z"
}
```

## 🎯 Outcomes

- Memorial gerado em < 5 segundos (vs 2-4 horas manual)
- Documentos profissionais e padronizados
- Redução de erros em documentação

## ⏱️ Estimativa

10 dias

## 🔗 Arquivos Relacionados

- `haas/app/routers/documents.py` (criar)
- `haas/app/services/document_service.py` (criar)
- `haas/templates/memorial_descritivo.html` (criar)
- `haas/requirements.txt` (adicionar WeasyPrint)
```

---

### Issue #5: [P1] Endpoints de Monitoramento - Substituir Mocks por Implementação Real

**Labels**: `priority: high`, `type: backend`, `feature`

**Descrição:**
```markdown
## 🎯 Objetivo
Implementar endpoints de monitoramento de projetos com queries PostgreSQL otimizadas.

## 📋 Tarefas
- [ ] Implementar `GET /monitoring/projects` (substituir mock)
- [ ] Implementar `GET /monitoring/projects/{id}` (substituir mock)
- [ ] Implementar `GET /monitoring/statistics` (substituir mock)
- [ ] Criar queries PostgreSQL otimizadas
- [ ] Adicionar índices para performance
- [ ] Implementar cache Redis (TTL 5min)
- [ ] Adicionar filtros (status, distribuidora, período)
- [ ] Testar com 10.000+ projetos

## 📥 Inputs

```tsx
GET /monitoring/projects?status=under_review&distributor=ENEL_SP&limit=50
GET /monitoring/projects/proj_123abc
GET /monitoring/statistics?period=last_30_days
```

## 📤 Outputs Esperados

```json
{
  "projects": [
    {
      "id": "proj_123abc",
      "client_name": "João Silva",
      "status": "under_review",
      "distributor": "ENEL_SP",
      "submitted_at": "2025-10-15T10:00:00Z",
      "progress_percent": 45,
      "estimated_completion": "2025-11-20"
    }
  ],
  "total": 127,
  "page": 1,
  "limit": 50
}
```

## 🎯 Outcomes

- Dashboard em tempo real
- Transparência total de status
- Queries < 100ms com índices

## 🔗 Dependências

- Issue #1: Database Setup

## ⏱️ Estimativa

3 dias

## 🔗 Arquivos Relacionados

- `haas/app/routers/monitoring.py`
- `haas/app/database/models.py`
```

---

### Issue #6: [P1] Autenticação Completa - Refresh Token + Logout

**Labels**: `priority: high`, `type: backend`, `security`

**Descrição:**
```markdown
## 🎯 Objetivo
Completar sistema de autenticação com renovação de tokens e logout seguro.

## 📋 Tarefas
- [ ] Implementar `POST /auth/refresh` (renovação JWT)
- [ ] Implementar `POST /auth/logout` (blacklist de tokens)
- [ ] Configurar Redis para blacklist de tokens
- [ ] Adicionar testes de segurança (token expiration, rotation)
- [ ] Documentar fluxo de autenticação completo
- [ ] Testar cenários edge (token expirado, token inválido)

## 📥 Inputs
```json
POST /auth/refresh
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}

POST /auth/logout
Headers: Authorization: Bearer {access_token}
```

## 📤 Outputs Esperados

```json
// Refresh
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer"
}

// Logout
{
  "message": "Logged out successfully",
  "tokens_revoked": 2
}
```

## 🎯 Outcomes

- Segurança reforçada
- Experiência de usuário melhorada
- Conformidade com boas práticas OAuth2

## ⏱️ Estimativa

2 dias

## 🔗 Arquivos Relacionados

- `haas/app/routers/auth.py`
- `haas/app/core/security.py`
```

---

### Issue #7: [P1] Upload Datasets ANEEL para Hugging Face

**Labels**: `priority: high`, `type: data`, `documentation`

**Descrição:**
```markdown
## 🎯 Objetivo
Publicar os 207 datasets ANEEL no Hugging Face para acesso público e backup em nuvem.

## 📋 Tarefas
- [ ] Executar `huggingface-cli login`
- [ ] Executar `python upload_to_huggingface.py`
- [ ] Criar README.md do dataset com documentação completa
- [ ] Adicionar metadata (tags, license, size_categories)
- [ ] Testar download via `datasets` library
- [ ] Verificar URL pública: `https://huggingface.co/datasets/fernando-bold/aneel-datasets`
- [ ] Documentar exemplo de uso

## 📥 Inputs
- 207 arquivos CSV em `aneel_datasets/` (~500MB)
- Token Hugging Face com permissão write
- Script `upload_to_huggingface.py`

## 📤 Outputs Esperados
- ✅ Dataset público no Hugging Face
- ✅ README.md completo
- ✅ Download funcionando via `load_dataset()`
- ✅ Documentação de uso

## 🎯 Outcomes
- Backup em nuvem dos datasets ANEEL
- Acesso público para comunidade
- Facilita integração com outras ferramentas
- Aumenta visibilidade do projeto

## 📚 Exemplo de Uso
```python
from datasets import load_dataset

# Load specific file
dataset = load_dataset(
    "fernando-bold/aneel-datasets", 
    data_files="empreendimento-geracao-distribuida.csv"
)
```

## ⏱️ Estimativa

1 dia

## 🔗 Arquivos Relacionados

- `upload_to_huggingface.py`
- `HUGGINGFACE_UPLOAD_INSTRUCTIONS.md`
- `aneel_datasets/` (207 CSVs)
```

---

## 🟢 P2 - EXPANSÃO

### Issue #8: [P2] MCP Servers Adicionais - GitHub + PostgreSQL + Filesystem

**Labels**: `priority: medium`, `type: devops`, `tooling`

**Descrição:**
```markdown
## 🎯 Objetivo
Expandir capacidades de automação com servidores MCP adicionais.

## 📋 Tarefas
- [ ] Configurar GitHub MCP para gestão de repositório
- [ ] Configurar PostgreSQL MCP para queries diretas
- [ ] Configurar Filesystem MCP para operações avançadas
- [ ] Atualizar `.vscode/mcp.json` com novos servers
- [ ] Testar integração com VS Code
- [ ] Documentar casos de uso de cada MCP

## 📥 Inputs
- Tokens/credenciais necessárias
- Arquivo de configuração `.vscode/mcp.json`

## 📤 Outputs Esperados
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {"POSTGRES_CONNECTION_STRING": "postgresql://..."}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    }
  }
}
```

## 🎯 Outcomes
- Automação avançada de repositório
- Queries SQL diretas via MCP
- Operações de arquivo em batch
- Produtividade aumentada

## ⏱️ Estimativa
5 dias

## 🔗 Arquivos Relacionados
- `.vscode/mcp.json`
```

---

### Issue #9: [P2] Conectores Web Automáticos - Playwright para CPFL, Enel, CEMIG

**Labels**: `priority: medium`, `type: backend`, `automation`, `complex`

**Descrição:**
```markdown
## 🎯 Objetivo
Implementar submissão automática de projetos via browser automation (Playwright).

## 📋 Tarefas
- [ ] Instalar e configurar Playwright
- [ ] Criar conector para CPFL (NTC-905600)
- [ ] Criar conector para Enel SP
- [ ] Criar conector para CEMIG (ND-5.3)
- [ ] Implementar endpoint `POST /utilities/{code}/submit`
- [ ] Implementar endpoint `GET /utilities/submission/{id}/status`
- [ ] Implementar retry automático em caso de falha
- [ ] Testar preenchimento automático de formulários
- [ ] Adicionar captcha solver (se necessário)
- [ ] Configurar execução headless

## 📥 Inputs
```json
POST /utilities/CPFL_PAULISTA/submit
{
  "project_id": "proj_123abc",
  "consumer_unit": "12345678",
  "documents": [
    {"type": "memorial", "url": "https://..."},
    {"type": "art", "url": "https://..."}
  ]
}
```

## 📤 Outputs Esperados
```json
{
  "submission_id": "sub_xyz789",
  "distributor": "CPFL_PAULISTA",
  "protocol_number": "2024-CPFL-001234",
  "status": "submitted",
  "submitted_at": "2025-10-22T16:00:00Z",
  "tracking_url": "https://servicosonline.cpfl.com.br/..."
}
```

## 🎯 Outcomes
- Submissão automática para top 3 distribuidoras
- Redução de 100% do trabalho manual
- Padronização de processos
- Rastreabilidade completa

## 💡 Stack Técnico
- Playwright (Python)
- Headless browser automation
- Captcha solver (2captcha/anticaptcha)

## ⚠️ Riscos
- Mudanças frequentes nos portais
- Captchas
- Rate limiting
- Downtime de portais

## ⏱️ Estimativa
15 dias

## 🔗 Arquivos Relacionados
- `haas/app/services/connectors/` (criar)
- `haas/app/routers/utilities.py`
- `haas/requirements.txt` (adicionar playwright)
```

---

### Issue #10: [P2] Dashboard Frontend React - KPIs Financeiros + Rankings + Análise Regional

**Labels**: `priority: medium`, `type: frontend`, `ui/ux`

**Descrição:**
```markdown
## 🎯 Objetivo
Criar dashboard interativo para visualização de KPIs financeiros, rankings de equipamentos e análise regional.

## 📋 Tarefas
- [ ] Setup Next.js + React + TypeScript
- [ ] Criar componente `PersonaFinancialDashboard`
- [ ] Criar componente `MetricCard` (KPIs)
- [ ] Criar componente `LeaderboardView` (rankings)
- [ ] Criar componente `RegionalView` (análise regional)
- [ ] Integrar com API BACEN (`/bacen/kpis/persona`)
- [ ] Integrar com API EPE (`/epe/market-insights`)
- [ ] Implementar gráficos Recharts/D3.js
- [ ] Adicionar exportação PDF de relatórios
- [ ] Implementar comparação side-by-side de equipamentos
- [ ] Adicionar simulador interativo de oversizing
- [ ] Testar responsividade (mobile/tablet/desktop)

## 📥 Inputs
- APIs BACEN Realtime
- APIs EPE
- Dados de 185.000+ produtos
- 67 distribuidoras ANEEL

## 📤 Outputs Esperados
### Dashboard com 3 Tabs:
1. **KPIs Financeiros**: Payback, TIR, VPL, LCOE, Economia Projetada, Riscos Regulatórios
2. **Rankings de Equipamentos**: Top 10 por Score, LCOE, ROI, Payback
3. **Análise Regional**: HSP, Tarifas, Recomendações por UF

## 🎯 Outcomes
- Visualização instantânea de análises complexas
- Comparação interativa de equipamentos
- Insights regionais acionáveis
- Experiência de usuário premium

## 💡 Stack Técnico
- Next.js 14
- React 18
- TypeScript
- Recharts / D3.js
- TanStack Query
- Tailwind CSS

## ⏱️ Estimativa
12 dias

## 🔗 Arquivos Relacionados
- `storefront/src/components/PersonaFinancialDashboard.tsx`
- `storefront/src/lib/services/bacen-realtime-service.ts`
- `storefront/src/lib/services/epe-service.ts`
```

---

## 📊 RESUMO EXECUTIVO

### Por Prioridade
- **P0 (Bloqueadores)**: 3 issues - 10 dias úteis
- **P1 (Importantes)**: 4 issues - 16 dias úteis
- **P2 (Expansão)**: 3 issues - 32 dias úteis

### Por Categoria
- **Backend**: 5 issues
- **Infrastructure/DevOps**: 3 issues
- **Frontend**: 1 issue
- **Data**: 1 issue

### Estimativa Total
- **MVP Beta (P0 + P1)**: 26 dias úteis (~5-6 semanas)
- **Sistema Completo (P0 + P1 + P2)**: 58 dias úteis (~12 semanas)

---

## 🚀 PRÓXIMOS PASSOS

1. **Habilitar Issues no repositório GitHub**
2. **Copiar e colar cada issue acima manualmente**
3. **Criar labels necessárias**:
   - `priority: critical`
   - `priority: high`
   - `priority: medium`
   - `type: infrastructure`
   - `type: backend`
   - `type: frontend`
   - `type: devops`
   - `type: data`
   - `blocker`
   - `feature`
   - `security`
   - `automation`
   - `ui/ux`
   - `documentation`
   - `tooling`
   - `complex`

4. **Organizar em Project Board** (opcional mas recomendado):
   - Coluna: Backlog
   - Coluna: Sprint 1 (P0)
   - Coluna: Sprint 2-3 (P1)
   - Coluna: Sprint 4+ (P2)
   - Coluna: In Progress
   - Coluna: Done

---

**Gerado em**: 22 de outubro de 2025  
**Versão**: 1.0  
**Total de Issues**: 10
