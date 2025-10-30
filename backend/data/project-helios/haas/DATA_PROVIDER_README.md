# Sistema de Provedor de Dados Inteligente - HaaS Platform

## Visão Geral

O **Sistema de Provedor de Dados Inteligente** é uma plataforma avançada projetada para fornecer dados e inteligência em tempo real para MCPs (Model Context Protocols), ferramentas e agentes A2A (Agent-to-Agent). O sistema combina cache inteligente, alertas automáticos, streaming em tempo real e APIs RESTful para oferecer uma experiência de consumo de dados de alta performance.

## Componentes Principais

### 1. Data Provider Service (`app/services/data_provider_service.py`)
Serviço principal que gerencia consultas de dados, cache e notificações.

**Funcionalidades:**
- Consultas de dados com filtros avançados
- Cache inteligente com prefetching
- Sistema de assinaturas para notificações em tempo real
- Integração com alertas inteligentes

### 2. Intelligent Cache Service (`app/services/intelligent_cache_service.py`)
Sistema de cache avançado com prefetching preditivo e analytics.

**Funcionalidades:**
- Cache com TTL configurável
- Prefetching automático de dados relacionados
- Estatísticas de uso e performance
- Invalidação inteligente por padrões

### 3. Intelligent Alert Service (`app/services/intelligent_alert_service.py`)
Sistema de alertas que detecta anomalias e eventos críticos automaticamente.

**Funcionalidades:**
- Regras de alerta configuráveis
- Detecção de anomalias em dados
- Notificações automáticas via webhooks
- Sistema de cooldown para evitar spam

### 4. Data Streaming Router (`app/routers/data_stream.py`)
WebSocket API para streaming de dados em tempo real.

**Funcionalidades:**
- Conexões WebSocket persistentes
- Streaming de dados em tempo real
- Gerenciamento de conexões e assinaturas
- Simulação de atualizações contínuas

## APIs Disponíveis

### REST API Endpoints

#### Consultas de Dados
```
POST /api/data/query
```
Consulta dados coletados com filtros avançados e paginação.

**Exemplo de Request:**
```json
{
  "data_type": "bacen",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "filters": {"region": "MG"},
  "limit": 100,
  "include_metadata": true
}
```

#### Tipos de Dados Disponíveis
```
GET /api/data/types
```
Lista todos os tipos de dados disponíveis para consumo.

#### Saúde dos Dados
```
GET /api/data/health/{data_type}
```
Verifica o status de saúde de um tipo específico de dados.

#### Schema dos Dados
```
GET /api/data/schema/{data_type}
```
Obtém a definição de schema para um tipo de dados.

#### Assinaturas
```
POST /api/data/subscribe/{data_type}
DELETE /api/data/subscribe/{subscription_id}
GET /api/data/subscriptions
```
Gerenciamento de assinaturas para notificações em tempo real.

#### Cache Management
```
GET /api/data/cache/stats
POST /api/data/cache/invalidate
POST /api/data/cache/warm
```
Gerenciamento do sistema de cache inteligente.

#### Alertas
```
GET /api/data/alerts/active
GET /api/data/alerts/history
POST /api/data/alerts/{alert_id}/resolve
```
Gerenciamento do sistema de alertas inteligentes.

### WebSocket Streaming
```
WS /api/stream/{data_type}
```
Streaming de dados em tempo real via WebSocket.

**Protocolo:**
```json
// Ping/Pong
{"type": "ping"}
{"type": "pong", "timestamp": "2025-10-22T10:00:00Z"}

// Subscription
{"type": "subscribe", "filters": {"min_rate": 12.0}}
{"type": "subscription_confirmed", "data_type": "bacen", "filters": {...}}

// Data Updates
{"type": "data_update", "data_type": "bacen", "data": {...}, "timestamp": "..."}
```

## Tipos de Dados Suportados

### 1. BACEN (`bacen`)
Dados econômicos e taxas de juros.
- `selic_rate`: Taxa SELIC
- `cdi_rate`: Taxa CDI
- `spread`: Spread SELIC-CDI
- `date`: Data da taxa

### 2. Distribuidoras (`distributor`)
Informações sobre concessionárias de energia.
- `distributor`: Nome da distribuidora
- `requirements`: Requisitos necessários
- `deadlines`: Prazos estabelecidos
- `fees`: Taxas aplicáveis

### 3. Mercado (`market`)
Inteligência de mercado e preços.
- `inverters_avg`: Preço médio inversores
- `panels_avg`: Preço médio painéis
- `trends`: Tendências de mercado

### 4. Regulatório (`regulatory`)
Atualizações regulatórias e normas.
- `changes`: Mudanças detectadas
- `documents`: Documentos regulatórios
- `deadlines`: Prazos importantes

### 5. Conformidade (`compliance`)
Dados de conformidade e certificações.
- `certificates`: Status de certificações
- `issues`: Problemas de conformidade
- `expirations`: Vencimentos próximos

## Sistema de Alertas

### Regras de Alerta Pré-configuradas

1. **Anomalia BACEN**: Detecta taxas SELIC fora do intervalo esperado (>15% ou <8%)
2. **Volatilidade de Mercado**: Identifica mudanças significativas nos preços
3. **Vencimento de Certificados**: Alerta sobre certificados próximos do vencimento
4. **Mudanças Regulatórias**: Notifica sobre alterações em normas

### Severidades
- `LOW`: Baixa prioridade
- `MEDIUM`: Média prioridade
- `HIGH`: Alta prioridade
- `CRITICAL`: Crítica - ação imediata necessária

## Cache Inteligente

### Funcionalidades
- **Prefetching**: Carrega automaticamente dados relacionados
- **Analytics**: Rastreia padrões de acesso
- **Invalidação**: Limpeza seletiva por padrões
- **Warm-up**: Pré-carregamento de dados frequentes

### Estatísticas Disponíveis
- Taxa de acerto do cache
- Top chaves mais acessadas
- Uso de memória
- Tempo de atividade

## Como Usar

### 1. Consulta Básica
```python
import aiohttp
import json

async with aiohttp.ClientSession() as session:
    query = {
        "data_type": "bacen",
        "limit": 10,
        "include_metadata": True
    }

    async with session.post(
        "http://localhost:8000/api/data/query",
        json=query,
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    ) as response:
        data = await response.json()
        print(f"Received {len(data['records'])} records")
```

### 2. Streaming em Tempo Real
```python
import websockets
import json

async with websockets.connect(
    "ws://localhost:8000/api/stream/bacen?token=YOUR_TOKEN"
) as websocket:

    # Subscribe to data
    await websocket.send(json.dumps({
        "type": "subscribe",
        "filters": {"min_rate": 12.0}
    }))

    # Listen for updates
    async for message in websocket:
        data = json.loads(message)
        if data["type"] == "data_update":
            print(f"New data: {data['data']}")
```

### 3. Assinatura para Notificações
```python
subscription = {
    "webhook_url": "https://your-app.com/webhook",
    "filters": {"region": "MG"}
}

# Subscribe
response = await session.post(
    "http://localhost:8000/api/data/subscribe/bacen",
    json=subscription,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
subscription_id = (await response.json())["subscription_id"]
```

## Testes

Execute o script de teste para verificar todas as funcionalidades:

```bash
cd haas
python test_data_provider.py
```

O script testa:
- Consultas de dados
- Estatísticas de cache
- Sistema de alertas
- Integração completa do sistema
- Streaming WebSocket

## Monitoramento

### Health Checks
```
GET /health
```
Verifica saúde geral do sistema incluindo banco de dados e Redis.

### Métricas de Cache
```
GET /api/data/cache/stats
```
Estatísticas detalhadas do sistema de cache.

### Alertas Ativos
```
GET /api/data/alerts/active
```
Lista todos os alertas ativos no sistema.

## Configuração

### Variáveis de Ambiente
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://user:pass@localhost/haas

# Security
SECRET_KEY=your-secret-key
```

### Inicialização
O sistema inicializa automaticamente com:
- Regras de alerta padrão
- Cache vazio (warm-up pode ser executado manualmente)
- Conexões WebSocket disponíveis

## Extensibilidade

### Adicionando Novos Tipos de Dados
1. Atualizar `data_provider_service.py` com novos tipos
2. Adicionar schemas em `get_data_schema()`
3. Implementar lógica de consulta em `_query_database()`

### Criando Novas Regras de Alerta
1. Definir função de condição
2. Criar `AlertRule` com parâmetros apropriados
3. Adicionar ao sistema via `add_alert_rule()`

### Canais de Notificação Customizados
1. Implementar função de callback
2. Registrar via `add_notification_channel()`

## Performance

### Otimizações Implementadas
- Cache inteligente com prefetching
- Consultas assíncronas
- Conexões WebSocket eficientes
- Sistema de cooldown para alertas

### Recomendações
- Use filtros específicos para reduzir carga
- Implemente paginação para grandes datasets
- Monitore estatísticas de cache regularmente
- Configure alertas apropriados para seu caso de uso

## Segurança

### Autenticação
Todos os endpoints requerem autenticação via JWT token no header `Authorization`.

### Autorização
Usuários só podem acessar dados de suas próprias assinaturas e alertas.

### Rate Limiting
Implementado no nível de middleware com limites configuráveis.

---

**Nota**: Este sistema foi projetado para ser altamente escalável e adaptável às necessidades específicas de MCPs e agentes A2A no ecossistema de energia solar brasileiro.</content>
<parameter name="filePath">c:\Users\fjuni\ysh-b2b\backend\data\project-helios\haas\DATA_PROVIDER_README.md