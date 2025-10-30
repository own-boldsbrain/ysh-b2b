# Teste de Fluxo Semântico - Plano Comandante A

Sistema de scraping inteligente para captura de imagens de produtos solares usando:
- **Knowledge Base Builder**: Crawl de sites de fabricantes
- **RAG Finder**: Busca semântica de produtos com TF-IDF
- **Semantic Scraper**: Extração inteligente de imagens com LLM

## Estrutura dos Módulos

```
orchestrator.py          # Coordenador principal (INTEGRADO ✅)
├── knowledge_base_builder.py  # Construção de KB
├── rag_finder.py               # Busca semântica
├── semantic_scraper.py         # Extração de imagens
├── image_processor.py          # Normalização 1024x1024 + 600x600
└── quality_assurance.py        # Validação de qualidade
```

## Fluxo Completo

```
SKU (ex: "PNL-JINKO-TGR-585W-NTYPE")
  ↓
1. Parse SKU → {manufacturer, series, power, search_query}
  ↓
2. Ensure Knowledge Base
   - Verifica se KB existe
   - Se não: crawl do site (max_depth=2)
   - Salva JSON em output/knowledge_bases/
  ↓
3. RAG Search
   - TF-IDF vectorization
   - Cosine similarity
   - Retorna top_k URLs com scores
  ↓
4. Semantic Scraping
   - Fetch página do produto
   - Extrai candidatos de imagem
   - LLM seleciona melhores
   - Fallback heurístico (size, alt, src patterns)
  ↓
5. Download & Process
   - Download paralelo
   - Normalização 1024x1024 (primária)
   - Normalização 600x600 (secundária)
   - Letterbox branco mantendo aspect ratio
  ↓
6. Quality Assurance
   - Dimensões mínimas
   - Formato correto
   - Background detection
   - Score 0-100
  ↓
7. Relatórios
   - CSV com resultados
   - Estatísticas de aprovação
```

## Arquitetura Semântica

### 1. Knowledge Base Builder
- **Input**: URL base do fabricante (ex: jinkosolar.com)
- **Processamento**: 
  - BFS crawling com rate limiting
  - Extração de text + links
  - Filtragem de URLs válidas
- **Output**: JSON com {url: {title, content}}

### 2. RAG Finder
- **Input**: manufacturer + search_query (ex: "JINKO Tiger Neo 585W N-Type")
- **Processamento**:
  - TF-IDF vectorization (1000 features, bigrams)
  - Cosine similarity entre query e KB
- **Output**: Lista de (url, score) ordenada

### 3. Semantic Scraper
- **Input**: product_url + sku_info
- **Processamento**:
  - Fetch HTML
  - Extrai candidatos (img src/srcset/data-src)
  - LLM scoring (Gemini/OpenAI)
  - Fallback heurístico (size, keywords)
- **Output**: Lista de image_urls ordenada por relevância

## URLs Configuradas (Wave 1)

```python
manufacturer_urls = {
    "JINKO": "https://www.jinkosolar.com",
    "TRINA": "https://www.trinasolar.com",
    "JA": "https://www.jasolar.com",
    "LONGI": "https://www.longi.com",
    "CANADIAN": "https://www.canadiansolar.com",
    "DEYE": "https://www.deyeinverter.com",
    "GROWATT": "https://www.growatt.com",
    "FRONIUS": "https://www.fronius.com",
    "GOODWE": "https://www.goodwe.com",
    "SOLIS": "https://www.solisinverters.com",
}
```

## Wave 1 - SKUs Piloto (6 produtos)

1. **PNL-JINKO-TGR-585W-NTYPE** - Painel Jinko Tiger Neo 585W
2. **PNL-TRINA-VERTEX-670W** - Painel Trina Vertex 670W
3. **PNL-JA-JAM72-550W** - Painel JA Solar JAM72 550W
4. **PNL-LONGI-HMO6-665W** - Painel Longi Hi-MO 6 665W
5. **PNL-CANA-CS7N-550W** - Painel Canadian Solar CS7N 550W
6. **INV-DEYE-SUN-8KW-SG** - Inversor Deye SUN-8K

## Como Testar

### Teste Individual (test_semantic_flow.py)
```bash
cd backend/scripts
python test_semantic_flow.py
```

**O que faz:**
1. Prompt interativo para escolher SKU
2. Executa fluxo completo para 1 SKU
3. Output detalhado de cada etapa
4. QA report no final

### Teste Wave 1 Completa (orchestrator.py)
```bash
cd backend/scripts
python orchestrator.py
```

**O que faz:**
1. Carrega todos os SKUs do inventário
2. Processa Wave 1 (6 SKUs)
3. Paraleliza quando possível
4. Gera relatórios CSV completos

## Outputs Esperados

```
output/
├── knowledge_bases/
│   ├── jinko_kb.json          # KB do Jinko (100-500 URLs)
│   ├── trina_kb.json          # KB do Trina
│   └── ...
├── images/
│   ├── jinko/
│   │   └── PNL-JINKO-TGR-585W-NTYPE/
│   │       ├── PNL-JINKO-TGR-585W-NTYPE_primary.jpg (1024x1024)
│   │       ├── PNL-JINKO-TGR-585W-NTYPE_primary_600x600.jpg
│   │       ├── PNL-JINKO-TGR-585W-NTYPE_add_1.jpg
│   │       └── ...
│   └── ...
└── reports/
    └── qa_report_YYYYMMDD_HHMMSS.csv
```

## Métricas de Sucesso

- **Taxa de KB construída**: 100% (todos os 10 fabricantes)
- **Taxa de URL encontrada**: >80% (RAG match score >0.1)
- **Taxa de imagens extraídas**: >90% (pelo menos 1 imagem/SKU)
- **Taxa de QA aprovada**: >70% (score ≥60)

## Próximos Passos

1. ✅ Integração completa no orchestrator.py
2. 🔄 Teste Wave 1 (6 SKUs)
3. ⏳ Ajustar thresholds baseado em resultados
4. ⏳ Wave 2 (painéis restantes ~20 SKUs)
5. ⏳ Wave 3 (inversores restantes ~15 SKUs)
6. ⏳ Geração de feed Meta Commerce

## Troubleshooting

### KB não constrói
- Verificar URL base acessível
- Verificar rate limiting (default: 2s entre requests)
- Verificar max_depth (default: 2)

### RAG não encontra produto
- Verificar KB construída corretamente
- Ajustar threshold (default: 0.1)
- Melhorar search_query no SKU parser

### Semantic scraper não encontra imagens
- Verificar LLM keys configuradas (Gemini/OpenAI)
- Fallback heurístico sempre ativo
- Verificar se página tem imagens válidas

### QA reprova muitas imagens
- Ajustar MIN_WIDTH/MIN_HEIGHT em config.py
- Ajustar background threshold
- Revisar process_image() letterbox
