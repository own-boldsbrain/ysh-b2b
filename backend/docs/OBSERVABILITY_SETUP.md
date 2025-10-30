# Intelligent Fallback Orchestrator - Observabilidade

## 📊 Dashboard Grafana Criado

Dashboard completo configurado em:
- **Arquivo:** `config/grafana/dashboards/intelligent-fallback-dashboard.json`
- **UID:** `intelligent-fallback-dashboard`
- **Refresh:** 10s automático

### Painéis Implementados

#### 1. Volume de Requisições por Camada
- **Tipo:** Time Series
- **Métricas:** `rate(fallback_requests_total[5m]) * 60`
- **Layers:** RAG (verde), SearxNG (azul), Ollama (laranja)
- **Agregações:** Média + Máximo na legenda
- **Objetivo:** Visualizar carga de trabalho por camada

#### 2. Taxa de Sucesso por Camada
- **Tipo:** Gauge
- **Métrica:** `fallback_success_rate`
- **Thresholds:**
  - 🔴 Vermelho: < 70%
  - 🟡 Amarelo: 70-90%
  - 🟢 Verde: > 90%
- **Objetivo:** Monitorar health de cada fallback

#### 3. Latência Média por Camada
- **Tipo:** Time Series
- **Métrica:** `fallback_latency_ms`
- **Thresholds:**
  - 🟢 < 500ms
  - 🟡 500-2000ms
  - 🔴 > 2000ms
- **Agregações:** Média, Máximo, Mínimo
- **Objetivo:** Identificar gargalos de performance

#### 4. Status Circuit Breaker
- **Tipo:** Donut Chart
- **Métrica:** `fallback_circuit_open`
- **Valores:**
  - 🟢 0 = Fechado (operacional)
  - 🔴 1 = Aberto (bloqueado)
- **Objetivo:** Alertar sobre circuit breakers ativos

#### 5. Evolução de Thresholds Adaptativos
- **Tipo:** Time Series (step-after)
- **Métricas:** `fallback_threshold_adaptive{layer="rag|searx"}`
- **Range:** 0-1
- **Agregações:** Último, Mínimo, Máximo
- **Objetivo:** Acompanhar ajustes dinâmicos de thresholds

#### 6. Logs Estruturados (Loki)
- **Tipo:** Logs Panel
- **Query:** `{job="intelligent-fallback"} |= ""`
- **Features:** Log details habilitado, ordem descendente
- **Objetivo:** Investigar eventos com contexto completo

#### 7-8. Amostras Adaptativas
- **Tipo:** Stat Panel
- **Métricas:** `fallback_adaptive_samples{layer="rag|searx"}`
- **Thresholds:**
  - 🔴 < 5 (dados insuficientes)
  - 🟡 5-10 (coletando)
  - 🟢 ≥ 10 (threshold confiável)
- **Objetivo:** Validar confiabilidade de thresholds

#### 9. Status de Saúde das Camadas
- **Tipo:** Stat Panel
- **Métrica:** `fallback_health`
- **Valores:**
  - 🟢 1 = Healthy
  - 🔴 0 = Unhealthy
- **Objetivo:** Visão geral de disponibilidade

---

## 🔧 Como Importar no Grafana

### Via UI (Manual)
1. Acesse Grafana: http://localhost:3000
2. Menu: **Dashboards** → **Import**
3. Upload `intelligent-fallback-dashboard.json`
4. Configure datasources:
   - **Prometheus UID:** `prometheus`
   - **Loki UID:** `loki`
5. Clique em **Import**

### Via Provisioning (Automático)
Adicione ao `docker-compose.yml`:

```yaml
grafana:
  volumes:
    - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
  environment:
    - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/intelligent-fallback-dashboard.json
```

Crie `config/grafana/provisioning/dashboards.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'Intelligent Fallback'
    orgId: 1
    folder: 'Observability'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

---

## 📈 Métricas Prometheus Disponíveis

Todas expostas via `http://localhost:9090/metrics`:

```prometheus
# Contador de requisições por camada
fallback_requests_total{layer="rag|searx|ollama"}

# Taxa de sucesso (0-1)
fallback_success_rate{layer="rag|searx|ollama"}

# Latência média em ms
fallback_latency_ms{layer="rag|searx|ollama"}

# Circuit breaker status (0=closed, 1=open)
fallback_circuit_open{layer="rag|searx|ollama"}

# Health status (0=unhealthy, 1=healthy)
fallback_health{layer="rag|searx|ollama"}

# Threshold adaptativo atual
fallback_threshold_adaptive{layer="rag|searx"}

# Número de amostras coletadas
fallback_adaptive_samples{layer="rag|searx"}
```

---

## 🔍 Queries Loki Úteis

### Erros de Circuit Breaker
```logql
{job="intelligent-fallback"} |= "circuit_action"
```

### Queries com alta latência
```logql
{job="intelligent-fallback"} | json | latency_ms > 1000
```

### Falhas por camada
```logql
{job="intelligent-fallback"} | json | status="not_found"
| unwrap latency_ms | quantile_over_time(0.95, [5m]) by (fallback_layer)
```

### Taxa de sucesso por manufacturer
```logql
rate({job="intelligent-fallback"} | json | status="success" [5m])
```

---

## 🚀 Próximos Passos

1. **Alertas Prometheus** - Criar regras para:
   - Circuit breaker aberto > 5min
   - Success rate < 80% em 15min
   - Latency p95 > 5s

2. **Benchmarks** - Executar `test_fallback_system.py` com dados reais:
   ```bash
   python scripts/test_fallback_system.py
   ```

3. **Tuning Adaptativo** - Ajustar percentis baseado em métricas:
   - Analisar histogramas de score no Grafana
   - Modificar `AdaptiveConfig.percentile` se necessário
   - Ajustar `cache_ttl` baseado em hit rates

---

## ✅ Status de Implementação

- [x] Handler Loki estruturado (`structured_logging.py`)
- [x] Integração logging em Ollama fallback
- [x] Integração logging em SearxNG fallback
- [x] Integração logging em Orchestrator
- [x] Dashboard Grafana com 9 painéis
- [x] Métricas Prometheus expostas (port 9090)
- [x] Documentação de observabilidade

**Próximo:** Executar benchmarks e tunning adaptativos! 🎯
