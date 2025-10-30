# Huginn Scenarios para HaaS Platform

Este diretório contém cenários e configurações de agentes Huginn para automação de processos do HaaS.

## Estrutura de Diretórios

```
huginn/scenarios/
├── README.md                          # Este arquivo
├── monitoring/                        # Cenários de monitoramento
│   ├── concessionarias-status.json   # Monitorar status de concessionárias
│   └── inmetro-updates.json          # Alertas de atualizações INMETRO
├── integration/                       # Cenários de integração
│   ├── haas-webhooks.json            # Integração com webhooks HaaS
│   └── notification-pipelines.json   # Pipelines de notificação
└── data-collection/                   # Cenários de coleta de dados
    ├── market-intelligence.json      # Inteligência de mercado
    └── regulatory-updates.json       # Atualizações regulatórias
```

## Jobs To Be Done - Casos de Uso HaaS

### 1. Monitoramento de Homologações (JTBD #1)

**Objetivo**: Alertar quando o status de uma homologação muda ou quando há atrasos.

**Agentes Necessários**:
- `WebsiteAgent` ou `WebhookAgent`: Recebe eventos da API HaaS
- `TriggerAgent`: Detecta mudanças de status ou atrasos
- `EmailAgent` / `SlackAgent`: Envia notificações

**Exemplo de Fluxo**:
```
HaaS API → Webhook → Trigger (detecta mudança) → Email/Slack
```

### 2. Agregação de Informações Regulatórias (JTBD #2)

**Objetivo**: Coletar atualizações de normas ANEEL, INMETRO e concessionárias.

**Agentes Necessários**:
- `RssAgent`: Monitora feeds de ANEEL/INMETRO
- `WebsiteAgent`: Scraping de páginas de concessionárias
- `DigestEmailAgent`: Consolida em relatório diário
- `DataOutputAgent`: Exporta para JSON/RSS

**Exemplo de Fluxo**:
```
RSS ANEEL → Filter → 
Website Concessionárias → Extract Data → 
INMETRO API → Transform → Digest → Email Diário
```

### 3. Automação de Workflows (JTBD #3)

**Objetivo**: Automatizar ações quando eventos ocorrem no HaaS.

**Agentes Necessários**:
- `WebhookAgent`: Recebe eventos do HaaS (novo projeto, aprovação, etc.)
- `EventFormattingAgent`: Formata dados para sistemas externos
- `PostAgent`: Envia para sistemas integrados (CRM, Slack, etc.)
- `JavaScriptAgent`: Lógica customizada quando necessário

**Exemplo de Fluxo**:
```
HaaS Webhook (Novo Projeto) → Format Data → 
  ├→ Post to CRM
  ├→ Send Slack Message
  └→ Create Task in Project Management
```

### 4. Extração e Transformação de Dados (JTBD #4)

**Objetivo**: Extrair dados de portais de concessionárias e APIs públicas.

**Agentes Necessários**:
- `WebsiteAgent`: Scraping com CSS/XPath
- `JavaScriptAgent`: Transformação e limpeza de dados
- `DataOutputAgent`: Estrutura em JSON
- `PostAgent`: Envia para API HaaS

**Exemplo de Fluxo**:
```
Scrape Portal Concessionária → Extract with CSS → 
Clean Data (JavaScript) → Transform to JSON → 
POST to HaaS API (atualizar banco de dados)
```

## Cenários Piloto Recomendados

### Piloto 1: Monitor de Status INMETRO
- **Valor**: Alto - crítico para validação de equipamentos
- **Complexidade**: Média
- **Arquivo**: `monitoring/inmetro-updates.json`

### Piloto 2: Relatório Diário de Homologações
- **Valor**: Alto - visibilidade operacional
- **Complexidade**: Baixa
- **Arquivo**: `data-collection/daily-homologation-report.json`

### Piloto 3: Webhook para Notificações
- **Valor**: Médio - melhora comunicação com clientes
- **Complexidade**: Baixa
- **Arquivo**: `integration/haas-webhooks.json`

## Como Importar Cenários

1. Acesse Huginn em `http://localhost:3000`
2. Login com credenciais configuradas no `.env`
3. Vá em `Scenarios` → `Import Scenario`
4. Cole o conteúdo JSON do arquivo do cenário
5. Ajuste credenciais e URLs conforme seu ambiente

## Boas Práticas

### Configuração de Agentes
- Use **Liquid templates** (`{{ }}`) para dados dinâmicos
- Armazene credenciais em **Credentials** (não hardcode)
- Nomeie agentes de forma descritiva: `[Categoria] Nome do Agente`

### Schedules
- Use `cron` para agendamentos precisos
- Evite schedules muito frequentes (sobrecarrega sistema)
- Sincronize horários com timezone do Brasil (`America/Sao_Paulo`)

### Debugging
- Use `Log Event` para inspecionar payloads
- Configure `dry_run` para testar sem executar ações
- Monitore logs em `logs/huginn/`

### Performance
- Limite `expected_update_period_in_days` de forma realista
- Use `keep_events_for` para limpar eventos antigos
- Evite chains muito longas (divida em cenários menores)

## Integração com HaaS API

### Recebendo Eventos do HaaS

Configure um `WebhookAgent` no Huginn:

```json
{
  "secret": "your-webhook-secret",
  "expected_receive_period_in_days": 1,
  "payload_path": "."
}
```

No HaaS, configure o webhook para apontar para:
```
http://huginn:3000/users/1/web_requests/{agent_id}/{secret}
```

### Enviando Dados para o HaaS

Use um `PostAgent`:

```json
{
  "post_url": "http://haas-api:8000/api/v1/endpoint",
  "expected_receive_period_in_days": 1,
  "headers": {
    "Authorization": "Bearer {% credential haas_api_token %}"
  },
  "payload": {
    "data": "{{ data }}"
  }
}
```

## Recursos Adicionais

- [Documentação Oficial Huginn](https://github.com/huginn/huginn/wiki)
- [Lista de Agentes Disponíveis](https://github.com/huginn/huginn/wiki/Agent-Types)
- [Liquid Template Language](https://shopify.github.io/liquid/)
- [Exemplos de Cenários](https://github.com/huginn/huginn/wiki/Scenarios)

## Suporte

Para questões sobre automação no projeto HaaS, consulte:
- Documentação do projeto em `PROJECT_ROOT/README.md`
- API docs em `http://localhost:8000/docs`
- Logs do Huginn em `logs/huginn/`
