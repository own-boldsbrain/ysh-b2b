# 🎯 QUICK START - ANEEL Distribuidoras 360°

> **Execute este comando para começar imediatamente**

```powershell
cd backend\data\project-helios\distribuitors
.\install_dependencies.ps1
.\run_pipeline.ps1
```

---

## 📋 O Que Foi Criado

```
distribuitors/
├── 📄 aneel_distribuidoras_360.csv          (INPUT - 176 registros, 69.3% incompletos)
├── 🤖 aneel_territorial_extractor.py        (Extrator com LLM + Browser)
├── ✅ quality_assurance.py                  (Sistema de QA)
├── 📦 requirements.txt                      (Dependências)
├── ⚙️  install_dependencies.ps1             (Setup automático)
├── 🚀 run_pipeline.ps1                      (Executor interativo)
├── 📚 README.md                             (Documentação completa)
├── 📊 SUMARIO_EXECUCAO.md                   (Guia executivo)
└── 🎯 QUICKSTART.md                         (Este arquivo)
```

---

## ⚡ Execução Rápida (3 Passos)

### 1️⃣ Instalar (5 min)

```powershell
.\install_dependencies.ps1
```

### 2️⃣ Executar (3-5 min para teste)

```powershell
.\run_pipeline.ps1
# Escolher opção 2 (10 primeiras distribuidoras)
```

### 3️⃣ Revisar

```powershell
cat QUALITY_REPORT.md
```

---

## 📊 Resultados Esperados

### Antes (Atual)

```
📂 aneel_distribuidoras_360.csv
├─ 176 distribuidoras
├─ 54 com dados territoriais (30.7%) ✅
└─ 122 sem dados (69.3%) ❌
```

### Depois (Com Sistema)

```
📂 aneel_distribuidoras_360_territorial_enriched.csv
├─ 176 distribuidoras
├─ 140-160 com dados territoriais (80-90%) ✅✅✅
└─ 16-36 sem dados (10-20%) ⚠️
```

**Melhoria**: +159-196% de cobertura

---

## 🤖 Tecnologias Usadas

- **Playwright** → Navegação automatizada (Chromium headless)
- **Gemini Pro** → Extração semântica com LLM
- **OpenAI GPT-4** → Fallback secundário
- **Docker/Ollama** → Fallback local (offline)
- **BeautifulSoup** → Parsing de HTML
- **Pandas** → Processamento de dados

---

## 🔑 API Keys (Já Configuradas)

```bash
GEMINI_API_KEY_1=AIzaSyCmgSL3RkU7kZ_wAfNiW0Y1nKkifXdx0zY
GEMINI_API_KEY_2=AIzaSyAY3QeBxTR7pyyHbzULk3xbLWzrmA82Pi8
OPENAI_API_KEY=sk-proj-CRKb8...
```

Localização: `backend\.env` ✅

---

## 📁 Outputs Gerados

| Arquivo | O Que Contém |
|---------|--------------|
| `aneel_distribuidoras_360_territorial_enriched.csv` | Dados completos de 176 distribuidoras |
| `aneel_distribuidoras_360_territorial_enriched.json` | Mesmos dados em JSON |
| `aneel_distribuidoras_validations.csv` | Resultados de QA |
| `quality_report.json` | Métricas agregadas |
| `QUALITY_REPORT.md` | Relatório visual |
| `cache/territorial_extraction_cache.json` | Cache (evita re-processar) |

---

## ⏱️ Tempo de Execução

| Modo | Distribuidoras | Tempo |
|------|---------------|-------|
| **Teste** | 10 | 3-5 min |
| **Incremental** | 122 | 60-90 min |
| **Completo** | 176 | 90-120 min |

---

## 💰 Custo Estimado

- **Gemini Pro**: $0.50 - $1.00 USD
- **OpenAI GPT-4**: $0 - $3.00 USD (apenas fallback)
- **Total**: $0.50 - $4.00 USD

---

## 🎯 Dados Extraídos por Distribuidora

```json
{
  "sigla": "CEMIG-D",
  "estados": ["MG"],
  "municipios": ["Belo Horizonte", "Uberlândia", "..."],
  "total_municipios": 774,
  "area_concessao_km2": 567295,
  "populacao_atendida": 17000000,
  "unidades_consumidoras": 8500000,
  "lat_centro": -19.9167,
  "lng_centro": -43.9345,
  "confidence_score": 0.92,
  "quality_status": "VALID"
}
```

---

## 🐛 Problemas? Soluções Rápidas

### "Playwright não instalado"
```powershell
pip install playwright
playwright install chromium
```

### "Timeout ao acessar site"
Edite `.env`:
```bash
BROWSER_TIMEOUT=60000  # 60 segundos
```

### "API key inválida"
```powershell
cat ..\..\..\..env | Select-String "GEMINI|OPENAI"
```
Sistema usa failover automático se uma key falhar

---

## 📚 Documentação Completa

- **README.md** → Documentação técnica completa
- **SUMARIO_EXECUCAO.md** → Guia executivo detalhado
- **QUICKSTART.md** → Este arquivo (início rápido)

---

## ✅ Checklist Pré-Execução

- [x] Python 3.10+ instalado
- [x] API keys configuradas no `.env`
- [x] Arquivo `aneel_distribuidoras_360.csv` presente
- [ ] Dependências instaladas → `.\install_dependencies.ps1`
- [ ] Internet estável

---

## 🚀 Comando Único (Copy-Paste)

```powershell
cd backend\data\project-helios\distribuitors; .\install_dependencies.ps1; .\run_pipeline.ps1
```

---

**🎉 Sistema Pronto! Basta executar.**

*20 de outubro de 2025 - v1.0*
