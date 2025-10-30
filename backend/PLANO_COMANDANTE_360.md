# Plano Comandante 360: Estratégia de Cobertura Total

**Data:** 21 de outubro de 2025  
**Versão:** 1.0  
**Objetivo:** Alcançar máxima performance e eficácia na cobertura de dados de produtos, garantindo uma visão 360º (imagens, datasheets, especificações) de ponta a ponta.

---

## 🎯 Diagnóstico Atual

O sistema atual é funcional, mas sua eficácia é limitada por dois fatores principais:
1.  **Inteligência de Alvo Fraca:** O RAG frequentemente seleciona páginas genéricas (homepages) com baixo score, resultando em falhas na extração.
2.  **Extração Estática:** O sistema não consegue lidar com sites modernos (SPAs) que carregam conteúdo dinamicamente via JavaScript.

Este plano aborda diretamente esses pontos, introduzindo uma arquitetura mais robusta e adaptativa.

---

## 🚀 A Estratégia: 3 Fases para a Cobertura Total

### Fase 1: Inteligência de Alvos Otimizada (Target Intelligence)

**Meta:** Garantir que o sistema sempre analise a página de maior relevância para o produto.

#### **Ação 1.1: Enriquecimento da Knowledge Base (KB) com Seed URLs**
- **Problema:** O crawling a partir da homepage é lento e nem sempre encontra as páginas de produto.
- **Solução:** Pré-popular a KB com URLs de alto valor.
  - **Implementação:**
    1.  Analisar `robots.txt` para encontrar `sitemap.xml`.
    2.  Extrair todas as URLs do sitemap e priorizar aquelas com palavras-chave de produto (`/product/`, `/series/`, `/modelo/`).
    3.  Adicionar uma lista de `seed_urls` conhecidas no `orchestrator.py` para cada fabricante.
    4.  O `KnowledgeBaseBuilder` deverá priorizar o crawling a partir dessas seeds.

#### **Ação 1.2: RAG com Múltiplas Queries (Multi-Query RAG)**
- **Problema:** Uma única query de busca pode ser ambígua.
- **Solução:** Gerar múltiplas queries para "triangular" o melhor resultado.
  - **Implementação:**
    1.  No `sku_parser.py`, gerar um array de queries:
        - Query base: `"JINKO TGR 585W"`
        - Query de datasheet: `"JINKO TGR 585W datasheet"`
        - Query de especificações: `"JINKO TGR 585W specifications"`
    2.  No `rag_finder.py`, executar todas as queries em paralelo.
    3.  Consolidar os resultados, somando os scores para URLs que aparecem em múltiplas buscas. A URL com o maior score consolidado é a vencedora.

#### **Ação 1.3: Google Search API como Fallback Inteligente**
- **Problema:** A KB interna pode não conter a página do produto.
- **Solução:** Usar a busca do Google como a "knowledge base definitiva".
  - **Implementação:**
    1.  No `orchestrator.py`, após a busca RAG, verificar o score do melhor resultado.
    2.  **Se `score < 0.5` (limiar de confiança baixo):**
        - Acionar uma busca na Google Search API com uma query precisa: `site:jinkosolar.com "JKM585N-72HL4-V" filetype:pdf OR "datasheet"`
        - O primeiro resultado dessa busca se torna a URL alvo, pulando a extração semântica e indo direto para o download/processamento.

---

### Fase 2: Extração Adaptativa Multi-Método (Adaptive Extraction)

**Meta:** Extrair dados com sucesso de qualquer tipo de site (estático ou dinâmico).

#### **Ação 2.1: Arquitetura de Extração em Camadas (Layered Extraction)**
- **Problema:** Usar browser automation (lento) para todos os sites é ineficiente.
- **Solução:** Criar um fluxo que só recorre a métodos lentos quando necessário.
  - **Implementação:**
    1.  **Camada 1 (Fast Path):** Sempre iniciar com `requests` + `BeautifulSoup`.
    2.  **Análise e Decisão:** Usar o `advanced_scraper` para analisar a estrutura da página.
    3.  **Se `spa_detected` for `True` OU se a Camada 1 retornar 0 imagens:**
        - **Camada 2 (Slow Path):** Automaticamente acionar um segundo passe usando **Playwright** para renderizar o JavaScript da página.
        - O HTML renderizado pelo Playwright é então passado para o `BeautifulSoup` para extração.

#### **Ação 2.2: Scraping Direto de API (API-First Scraping)**
- **Problema:** Em SPAs, os dados de produtos geralmente vêm de uma API interna.
- **Solução:** Capturar e usar essas chamadas de API diretamente.
  - **Implementação:**
    1.  No `advanced_scraper`, aprimorar a detecção de `ajax_endpoints`.
    2.  Ao usar Playwright (Camada 2), interceptar as respostas de rede.
    3.  Se uma resposta JSON contiver os dados do produto (identificados por palavras-chave como "sku", "power", "model"), extrair os dados diretamente do JSON.
    4.  Isso é **muito mais rápido e confiável** do que parsear o HTML renderizado.

---

### Fase 3: Ciclo de Melhoria Contínua (Flywheel)

**Meta:** Usar os dados de cada execução para tornar o sistema mais inteligente e eficaz ao longo do tempo.

#### **Ação 3.1: Banco de Dados de Seletores (Selector Database)**
- **Problema:** Seletores CSS mudam e são específicos para cada site.
- **Solução:** Criar um banco de dados que armazena seletores bem-sucedidos.
  - **Implementação:**
    1.  Criar um banco de dados (JSON ou SQLite) `selectors_db.json`.
    2.  Sempre que a extração de um campo (ex: `product_title`) for bem-sucedida, salvar:
        - `fabricante`
        - `tipo_de_dado` (ex: 'product_title')
        - `seletor_css` (ex: `'h1.product-title'`)
        - `score` (inicialmente 1)
    3.  Na próxima vez que for raspar o mesmo fabricante, o sistema primeiro tenta os seletores salvos com maior score, antes de usar a heurística geral.

#### **Ação 3.2: Auto-Tuning de Limiares (Threshold Auto-Tuning)**
- **Problema:** Limiares como `RAG_SCORE_THRESHOLD` e `IMAGE_MIN_WIDTH` são definidos manualmente.
- **Solução:** Ajustá-los dinamicamente com base na taxa de sucesso.
  - **Implementação:**
    1.  No final de cada execução do `orchestrator`, calcular a taxa de sucesso geral (ex: 85% dos SKUs tiveram packshot aprovado).
    2.  Se a taxa de sucesso cair abaixo de um alvo (ex: 80%), o sistema pode:
        - **Reduzir o `RAG_SCORE_THRESHOLD`** para permitir que mais URLs sejam consideradas.
        - **Ajustar os parâmetros de QA de imagem** se muitas imagens estiverem sendo rejeitadas.

---

## 📈 Métricas de Sucesso Esperadas

| Métrica | Antes da Estratégia | Após a Estratégia |
| :--- | :--- | :--- |
| **Taxa de Sucesso (End-to-End)** | ~50% | **> 90%** |
| **Necessidade de Intervenção Manual** | Alta | **Mínima** |
| **Cobertura de SPAs/Sites Dinâmicos** | 0% | **~95%** |
| **Velocidade Média por SKU** | Rápida (mas ineficaz) | **Adaptativa** (rápida para sites simples, lenta apenas quando necessário) |
| **Inteligência do Sistema** | Estática | **Evolutiva (Flywheel)** |

---

## 🗺️ Roadmap de Implementação

1.  **Sprint 1 (Urgente):**
    - [ ] **Ação 1.1:** Implementar `sitemap.xml` e `seed_urls` no `KnowledgeBaseBuilder`.
    - [ ] **Ação 1.3:** Implementar fallback com Google Search API para RAG com score baixo.
    - [ ] **Ação 2.1:** Integrar Playwright como Camada 2 de extração.

2.  **Sprint 2 (Curto Prazo):**
    - [ ] **Ação 1.2:** Implementar Multi-Query RAG.
    - [ ] **Ação 3.1:** Criar a primeira versão do `selectors_db.json`.
    - [ ] **Ação 2.2:** Adicionar interceptação de rede no Playwright para capturar APIs.

3.  **Sprint 3 (Médio Prazo):**
    - [ ] **Ação 3.2:** Implementar o mecanismo de auto-tuning de limiares.
    - [ ] Refinar e otimizar todos os módulos anteriores.
