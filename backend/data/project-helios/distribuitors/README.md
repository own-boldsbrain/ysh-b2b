# 🔋 ANEEL Distribuidoras - Sistema de Extração Territorial 360°

> **Sistema inteligente de captura de dados de operações territoriais das distribuidoras de energia elétrica brasileiras**

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Outputs](#outputs)
- [Qualidade dos Dados](#qualidade-dos-dados)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Sistema automatizado que extrai dados territoriais detalhados de distribuidoras de energia elétrica da ANEEL, utilizando:

- **Browser Automation** (Playwright/Chromium) para navegar sites oficiais
- **LLMs** (Gemini → OpenAI → Docker models) para extração semântica inteligente
- **RAG e Fuzzy Matching** para validação e enriquecimento
- **Quality Assurance** automático com métricas de completude e acurácia

### Dados Extraídos

Para cada distribuidora, o sistema captura:

- ✅ Estados atendidos (siglas oficiais)
- ✅ Lista completa de municípios
- ✅ Total de municípios atendidos
- ✅ Área de concessão (km²)
- ✅ População atendida
- ✅ Número de unidades consumidoras
- ✅ Coordenadas geográficas (bounding box + centro)
- ✅ Score de confiança da extração
- ✅ Metadados de proveniência (fonte, data, método)

---

## ✨ Características

### 🤖 Inteligência Artificial Multi-Nível

**Failover Automático**:
1. **Gemini Pro** (Key 1) - Primário
2. **Gemini Pro** (Key 2) - Secundário
3. **OpenAI GPT-4** - Terciário
4. **Docker Models** (Ollama) - Fallback local
   - `smollm2:latest`
   - `gemma3-qat:latest`
   - `gpt-oss:latest`
   - `qwen3-coder:latest`

### 🌐 Browser Automation Avançado

- **Headless Chromium** via Playwright
- Anti-detecção (remove flags de automação)
- Rate limiting inteligente (3 req/s)
- Backoff exponencial em caso de erro
- User-Agent realista

### 🔍 Extração Semântica

- Análise de HTML com BeautifulSoup
- Remoção de ruído (scripts, styles, nav, footer)
- Prompts LLM otimizados para dados geográficos
- Parsing robusto de JSON da resposta LLM

### ✅ Quality Assurance

- Validação de estados (27 UFs brasileiras)
- Verificação de plausibilidade (municípios, área)
- Consistência cruzada (estados × municípios)
- Score de qualidade (0-100)
- Status classificado: EXCELENTE → CRÍTICO

---

## 🏗️ Arquitetura

```
aneel_distribuidoras_360.csv  (INPUT)
          ↓
┌─────────────────────────────────────┐
│ aneel_territorial_extractor.py      │
│  ↓                                   │
│  1. Carregar dados base              │
│  2. Filtrar distribuidoras sem dados│
│  3. Para cada distribuidora:        │
│     a) Buscar site oficial (LLM)    │
│     b) Navegar com Playwright       │
│     c) Extrair HTML limpo           │
│     d) LLM extrai dados (JSON)      │
│     e) Validar e enriquecer         │
│     f) Calcular coordenadas         │
│     g) Salvar em cache              │
│  4. Merge com dados originais       │
│  5. Exportar CSV + JSON             │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ quality_assurance.py                │
│  ↓                                   │
│  1. Validar cada registro           │
│  2. Calcular quality scores         │
│  3. Identificar problemas           │
│  4. Gerar recomendações             │
│  5. Exportar relatórios             │
└─────────────────────────────────────┘
          ↓
OUTPUTS:
  - aneel_distribuidoras_360_territorial_enriched.csv
  - aneel_distribuidoras_360_territorial_enriched.json
  - aneel_distribuidoras_validations.csv
  - quality_report.json
  - QUALITY_REPORT.md
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.10+**
- **Docker** (opcional, para fallback models)
- **Git**

### Passo 1: Clonar Repositório

```powershell
cd data\project-helios\distribuitors
```

### Passo 2: Instalar Dependências

Execute o script automatizado:

```powershell
.\install_dependencies.ps1
```

Ou manualmente:

```powershell
# Criar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar pacotes
pip install -r requirements.txt

# Instalar navegador Chromium
playwright install chromium
```

### Passo 3: Configurar API Keys

As chaves já estão configuradas no arquivo `.env` do backend:

```bash
# Verificar
cat ../../../.env | Select-String "GEMINI|OPENAI"
```

**Chaves configuradas**:
- ✅ `GEMINI_API_KEY_1`: AIzaSyCmgSL3RkU7kZ_wAfNiW0Y1nKkifXdx0zY
- ✅ `GEMINI_API_KEY_2`: AIzaSyAY3QeBxTR7pyyHbzULk3xbLWzrmA82Pi8
- ✅ `OPENAI_API_KEY`: sk-proj-CRKb8rVk...

---

## 💻 Uso

### Execução Completa

```powershell
# Extração territorial
python aneel_territorial_extractor.py

# Quality Assurance
python quality_assurance.py
```

### Modo Headless (Padrão)

Browser roda em background sem janela visível.

### Modo Visual (Debug)

Edite o arquivo `.env`:

```bash
HEADLESS_BROWSER=false
```

### Processar Apenas N Distribuidoras

Edite `aneel_territorial_extractor.py`:

```python
# Linha ~580
df_to_extract = df_to_extract.head(10)  # Apenas 10 primeiras
```

---

## 📂 Outputs

### Arquivos Gerados

| Arquivo | Descrição | Formato |
|---------|-----------|---------|
| `aneel_distribuidoras_360_territorial_enriched.csv` | Dados enriquecidos | CSV (;) |
| `aneel_distribuidoras_360_territorial_enriched.json` | Dados enriquecidos | JSON |
| `cache/territorial_extraction_cache.json` | Cache das extrações | JSON |
| `aneel_distribuidoras_validations.csv` | Resultados QA | CSV (;) |
| `quality_report.json` | Métricas de qualidade | JSON |
| `QUALITY_REPORT.md` | Relatório visual | Markdown |

### Estrutura do CSV Enriquecido

```csv
CNPJ;Sigla;Razão Social;Ativo;...;estados;municipios;total_municipios;area_concessao_km2;populacao_atendida;unidades_consumidoras;lat_centro;lng_centro;lat_minima;lat_maxima;lng_minima;lng_maxima;confidence_score;quality_status;extraction_method;extraction_date
```

### Estrutura do JSON

```json
{
  "cnpj": "06981180000116",
  "sigla": "CEMIG-D",
  "razao_social": "CEMIG DISTRIBUICAO S.A",
  "estados": ["MG"],
  "municipios": ["Belo Horizonte", "Uberlândia", "..."],
  "total_municipios": 774,
  "area_concessao_km2": 567295,
  "populacao_atendida": 17000000,
  "unidades_consumidoras": 8500000,
  "lat_centro": -19.9167,
  "lng_centro": -43.9345,
  "lat_minima": -20.9167,
  "lat_maxima": -18.9167,
  "lng_minima": -44.9345,
  "lng_maxima": -42.9345,
  "confidence_score": 0.92,
  "quality_status": "VALID",
  "extraction_method": "LLM + Browser Automation",
  "llm_provider": "Gemini Key 1",
  "extraction_date": "2025-10-20T14:32:15.123456"
}
```

---

## 📊 Qualidade dos Dados

### Métricas de Quality Assurance

| Métrica | Threshold | Descrição |
|---------|-----------|-----------|
| **Estados Válidos** | 27 UFs | Valida contra lista oficial |
| **Municípios Plausível** | 1-1000 | Range esperado |
| **Área Concessão** | 10-1M km² | Plausibilidade geográfica |
| **Confidence Score** | ≥0.6 | Confiança mínima LLM |
| **Coordenadas** | Presente | Lat/Lng calculadas |

### Status de Qualidade

| Score | Status | Ação |
|-------|--------|------|
| 80-100 | **EXCELENTE** | ✅ Dados prontos para uso |
| 60-79 | **BOM** | ⚠️ Revisar warnings |
| 40-59 | **REGULAR** | ⚠️ Validação manual recomendada |
| 20-39 | **RUIM** | ❌ Re-executar extração |
| 0-19 | **CRÍTICO** | ❌ Requer intervenção |

### Relatório de Qualidade

Após executar `quality_assurance.py`, consulte:

```powershell
cat QUALITY_REPORT.md
```

**Conteúdo**:
- Score médio, mínimo, máximo
- Distribuição por status
- Top 10 melhores distribuidoras
- Bottom 10 (requer atenção)
- Principais problemas identificados
- Recomendações de ação

---

## 🐛 Troubleshooting

### Erro: "Playwright não instalado"

```powershell
pip install playwright
playwright install chromium
```

### Erro: "API key inválida" (Gemini/OpenAI)

1. Verifique o arquivo `.env`:
   ```powershell
   cat ../../../.env | Select-String "GEMINI|OPENAI"
   ```

2. Certifique-se de que as chaves estão corretas e ativas

3. O sistema usa failover automático - se Gemini falhar, tenta OpenAI

### Erro: "Timeout ao acessar site"

- Aumente o timeout no `.env`:
  ```bash
  BROWSER_TIMEOUT=60000  # 60 segundos
  ```

- Verifique sua conexão de internet

- Alguns sites podem ter proteção anti-bot (CloudFlare, etc.)

### Performance Lenta

**Reduzir rate limiting**:
```bash
# .env
MAX_REQUESTS_PER_SECOND=5  # De 3 para 5
```

**Processar em lote menor**:
```python
# aneel_territorial_extractor.py, linha ~580
df_to_extract = df_to_extract.head(20)
```

### Docker Models Não Funcionam

1. Verificar se Ollama está rodando:
   ```powershell
   docker ps | Select-String ollama
   ```

2. Iniciar Ollama:
   ```powershell
   docker run -d -p 11434:11434 --name ollama ollama/ollama
   ```

3. Baixar modelos:
   ```powershell
   docker exec ollama ollama pull gemma3-qat
   ```

---

## 📈 Próximos Passos

Após executar o sistema:

### 1. Revisar Relatório de Qualidade

```powershell
cat QUALITY_REPORT.md
```

### 2. Corrigir Registros Críticos

Distribuidoras com score < 40 requerem atenção:

- Revisar manualmente os dados extraídos
- Verificar se o site oficial foi acessado corretamente
- Considerar extração manual via prompts LLM customizados

### 3. Enriquecer com Dados ANEEL Oficiais

Cruzar com datasets oficiais:
- `tarifas-homologadas-distribuidoras-energia-eletrica.csv`
- `projetos-gd-por-distribuidora.csv`

### 4. Integrar com HaaS API

Expor dados via endpoint REST:

```http
GET /api/distribuidoras/{cnpj}
GET /api/distribuidoras/search?estado=MG&municipio=Uberlândia
```

### 5. Visualização Geográfica

Criar mapa interativo com:
- Folium
- Plotly
- Streamlit Dashboard

---

## 📝 Changelog

### v1.0 (20/10/2025)

**Adicionado**:
- ✅ Extrator territorial com Playwright + LLM
- ✅ Failover automático Gemini → OpenAI → Docker
- ✅ Quality Assurance completo
- ✅ Cálculo de coordenadas geográficas
- ✅ Cache de extrações
- ✅ Relatórios markdown + JSON

**Performance**:
- ~3 segundos por distribuidora (com cache)
- ~15 segundos sem cache (navegação + LLM)
- Suporta até 1000 req/hora (rate limiting)

---

## 🤝 Contribuindo

Melhorias bem-vindas:

1. **Fontes de Dados Adicionais**: Integrar com APIs oficiais ANEEL
2. **Validação Geográfica**: Usar Google Maps API para validar coordenadas
3. **ML para Classificação**: Treinar modelo para detectar dados implausíveis
4. **Extração de Tarifas**: Adicionar scraping de tarifas atualizadas

---

## 📄 Licença

© 2025 YSH B2B - Todos os direitos reservados

---

## 🆘 Suporte

Problemas ou dúvidas:

1. Revisar `QUALITY_REPORT.md` gerado
2. Verificar logs do terminal
3. Consultar cache: `cache/territorial_extraction_cache.json`
4. Testar com uma distribuidora específica primeiro

---

**Última Atualização**: 20 de outubro de 2025  
**Versão**: 1.0  
**Status**: ✅ **PRODUÇÃO**
