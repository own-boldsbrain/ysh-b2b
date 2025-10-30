# 🖼️ Blueprint da Infraestrutura de Imagens - YSH B2B

**Data de Criação:** 21 de Outubro de 2025  
**Versão:** 1.0  
**Autor:** GitHub Copilot

---

## 1. Resumo Executivo

Este documento fornece uma visão cronológica e arquitetônica completa da infraestrutura de gerenciamento de imagens de produtos na plataforma YSH B2B. O sistema evoluiu de um processo manual e estático para uma arquitetura multi-camada, incorporando scraping dinâmico, processamento avançado, otimização e análise por Inteligência Artificial.

O objetivo deste blueprint é consolidar o conhecimento sobre as ferramentas existentes, mapear o fluxo de dados, identificar o estado atual da infraestrutura, apontar gaps críticos e definir os próximos passos estratégicos para alcançar uma cobertura de imagens de 100% com alta qualidade.

Atualmente, o pipeline de **processamento e otimização** de imagens está maduro e robusto, porém, a camada de **captura (scraping)** enfrenta um desafio crítico: o novo scraper dinâmico (`scrape_dynamic_images.py`), apesar de implementado, não está retornando resultados, mantendo a cobertura de imagens de produtos em 0%. A resolução deste problema é a principal prioridade.

---

## 2. Introdução

A gestão de imagens de produtos é um pilar fundamental para a experiência do usuário e para o sucesso comercial da plataforma YSH B2B. Imagens de alta qualidade, otimizadas e corretamente associadas aos produtos são essenciais para catálogos online, marketing e vendas.

Ao longo do tempo, a complexidade dos sites de fabricantes e a necessidade de escalar a captura de recursos visuais levaram a uma evolução significativa de nossa infraestrutura. Este documento serve como um guia centralizado para entender essa jornada, detalhando cada componente, sua função e como eles se interconectam.

O blueprint está organizado nas seguintes seções:
- **Evolução da Captura de Imagens:** Da extração estática à automação com browsers headless.
- **Pipeline de Processamento e Otimização:** Como as imagens são normalizadas, redimensionadas e otimizadas para performance.
- **Camada de Inteligência Artificial (IA):** O uso de modelos de visão para análise e extração de metadados.
- **Fluxo de Dados e Monitoramento:** O ciclo de vida de uma imagem, do scraping ao armazenamento e monitoramento.
- **Estado Atual, Gaps e Recomendações:** Uma análise da situação atual e um plano de ação claro.

Este documento é destinado a desenvolvedores, arquitetos e stakeholders para fornecer uma fonte única de verdade sobre todo o ecossistema de imagens da YSH.

---

## 3. Evolução da Captura de Imagens (Scraping)

A capacidade de extrair imagens de produtos diretamente dos sites dos fabricantes é a primeira e mais crucial etapa de todo o pipeline. Essa capacidade evoluiu em três fases distintas, cada uma respondendo aos desafios da fase anterior.

### Fase 1: Scraper Estático (Onda 1) - `image_scraper.py`

A primeira abordagem foi um scraper simples e direto, projetado para a "Onda 1" de produtos.

- **Ferramenta:** `scripts/image_scraper.py`
- **Estratégia:** Utilizava um dicionário Python (`wave1_targets`) que mapeava SKUs de produtos diretamente para URLs de imagens ou PDFs conhecidas.
- **Tecnologia:** `requests` para downloads diretos.
- **Limitações:**
    - **Não escalável:** Exigia que cada URL fosse encontrada e adicionada manualmente ao código.
    - **Frágil:** Quebrava sempre que um fabricante alterava a URL de um recurso.
    - **Ineficaz para sites dinâmicos:** Incapaz de extrair imagens de sites que usam JavaScript para renderizar conteúdo.

Esta abordagem serviu como uma prova de conceito, mas rapidamente se mostrou inadequada para a escala e a dinâmica do catálogo da YSH.

### Fase 2: Scrapers Manuais e a Descoberta do Problema

Na tentativa de escalar, foram criados scrapers que salvavam o conteúdo HTML de páginas de produtos para análise posterior.

- **Ferramentas:** `scripts/extract_resources_from_manual_scrapers.py`
- **Estratégia:** Navegar manualmente até as páginas dos produtos, salvar o HTML e depois executar um script para parsear esses arquivos locais em busca de links de imagens e PDFs.
- **Resultado:**
    - **Sucesso em PDFs:** Conseguiu extrair 54 links de manuais e datasheets.
    - **Falha total em Imagens:** **0% de sucesso**. O relatório `data/products-resources/MANUAL_SCRAPING_REPORT.md` documentou que as imagens não eram encontradas porque os sites dos fabricantes (como Huawei, Deye, etc.) renderizam as imagens dinamicamente com JavaScript. O HTML estático salvo não continha os URLs das imagens finais.

Essa fase foi fundamental para diagnosticar o problema central: a necessidade de uma solução de scraping que pudesse interpretar JavaScript, ou seja, um "browser headless".

### Fase 3: Scraper Dinâmico com Playwright

Para resolver a falha da Fase 2, foi desenvolvida uma solução de scraping moderna e robusta, capaz de simular um navegador real.

- **Ferramentas Principais:**
    - `scripts/scrape_dynamic_images.py`: O orquestrador principal que lê o inventário de produtos e coordena a captura.
    - `scripts/playwright_scraper.py`: Uma camada de abstração que encapsula a lógica de automação do browser, inicializando o Playwright, navegando para páginas, aguardando elementos e extraindo o HTML renderizado.
- **Estratégia:**
    1. O orquestrador busca um produto no inventário.
    2. Utiliza o `playwright_scraper` para abrir a página do produto em um navegador Chromium headless.
    3. O scraper aguarda a renderização completa do JavaScript, incluindo o carregamento de imagens (inclusive as de *lazy loading*).
    4. Implementa estratégias de extração específicas para cada fabricante (ex: `HuaweiScraper`, `DeyeScraper`), procurando por imagens em seletores CSS conhecidos.
    5. Valida as imagens encontradas (ex: tamanho mínimo de 200x200 pixels) para evitar ícones e logos.
    6. Envia as URLs válidas para um downloader assíncrono.
- **Estado Atual:** O código está totalmente implementado, mas sua execução **não está gerando resultados**, indicando um problema no processo de execução, bloqueio por parte dos sites ou um erro silencioso. Este é o **principal GAP** na infraestrutura de imagens atualmente.

---

## 4. Pipeline de Processamento e Otimização

Uma vez que uma imagem é capturada, ela entra em um pipeline de múltiplos estágios para garantir que seja normalizada, otimizada para a web e aprimorada em qualidade. Este pipeline também evoluiu, resultando em um conjunto de ferramentas robustas e especializadas.

### Estágio 1: Normalização Padrão - `image_processor.py`

Esta foi a primeira ferramenta de processamento, criada com um requisito específico em mente: atender às especificações do Meta Commerce.

-   **Ferramenta:** `scripts/image_processor.py`
-   **Função:**
    1.  Recebe uma imagem recém-baixada.
    2.  Converte a imagem para o modo RGB, removendo canais de transparência.
    3.  Remove todos os metadados EXIF para reduzir o tamanho do arquivo e proteger a privacidade.
    4.  Cria duas versões da imagem com *letterboxing* (adicionando bordas brancas para manter a proporção):
        -   **Primária:** 1024x1024 pixels.
        -   **Secundária:** 600x600 pixels.
    5.  Salva as imagens em formato JPEG com qualidade otimizada.
-   **Tecnologia:** `Pillow`.
-   **Propósito:** Garantir que todas as imagens tenham um formato e dimensões consistentes para compatibilidade com plataformas de terceiros.

### Estágio 2: Geração de Imagens Responsivas - `generate-responsive-images.py`

Com a necessidade de otimizar a performance do frontend, foi criado um script para gerar múltiplas versões de cada imagem, permitindo que o navegador carregue o tamanho mais apropriado para cada dispositivo.

-   **Ferramenta:** `scripts/generate-responsive-images.py`
-   **Função:**
    1.  Lê uma imagem de alta resolução.
    2.  Gera um conjunto de imagens em formato WebP, mantendo a proporção original:
        -   `original`: Cópia em WebP da imagem original.
        -   `large`: 1200px de largura (para desktops).
        -   `medium`: 800px de largura (para tablets).
        -   `thumb`: 400px de largura (para dispositivos móveis).
-   **Tecnologia:** `Pillow`, `OpenCV`.
-   **Propósito:** Melhorar o tempo de carregamento das páginas (LCP - Largest Contentful Paint) e a experiência do usuário em diferentes dispositivos.

### Estágio 3: Otimização Avançada e Melhoria de Qualidade - `optimize-product-images.py`

Este é o script mais sofisticado do pipeline, focado não apenas em otimizar, mas em **melhorar a qualidade visual** da imagem original.

-   **Ferramenta:** `scripts/optimize-product-images.py`
-   **Função:** Executa um pipeline de aprimoramento de imagem em lote e em paralelo:
    1.  **Denoise:** Remove ruído da imagem usando algoritmos avançados (`cv2.fastNlMeansDenoisingColored`), com parâmetros ajustados para preservar detalhes finos em textos e logos.
    2.  **Melhora de Contraste:** Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) para melhorar o contraste de forma adaptativa e natural.
    3.  **Saturação de Cores:** Aumenta a vivacidade das cores.
    4.  **Sharpening:** Aplica um filtro *unsharp mask* para aumentar a nitidez e a percepção de detalhe.
    5.  **Conversão para Formatos Modernos:** Salva a imagem final em WebP ou AVIF, com compressão de alta qualidade e método lento (`method=6`) para máxima eficiência.
    6.  **Processamento Paralelo:** Utiliza `ProcessPoolExecutor` para processar múltiplas imagens em paralelo, aproveitando todos os núcleos de CPU disponíveis.
-   **Tecnologia:** `Pillow-SIMD`, `OpenCV`, `scikit-image`, `numpy`, `joblib`.
-   **Propósito:** Produzir a imagem da mais alta qualidade possível para o catálogo, garantindo que os produtos sejam apresentados da melhor forma, ao mesmo tempo em que se minimiza o tamanho do arquivo.

### Scripts de Manutenção

-   **`scripts/migrate-image-map-to-webp.py`**: Um script utilitário que demonstra a evolução do pipeline, criado para migrar o `product_image_map.json` existente para usar as novas imagens no formato WebP, mostrando a capacidade de adaptação e manutenção da infraestrutura.

---

## 5. Camada de Inteligência Artificial (IA)

Além da captura e processamento, a infraestrutura de imagens incorpora uma camada de inteligência para automatizar a análise, classificação e, futuramente, a própria captura de imagens.

### Análise de Imagens com IA Local

Para extrair metadados valiosos diretamente das imagens dos produtos, foi desenvolvido um sistema de análise baseado em modelos de visão locais.

-   **Ferramenta:** `scripts/test-ai-image-analysis.py`
-   **Tecnologia:**
    -   **Ollama:** Permite a execução de grandes modelos de linguagem (LLMs) localmente.
    -   **LLaVA (Large Language and Vision Assistant):** Um modelo de visão multimodal capaz de "ver" uma imagem e responder a perguntas sobre ela.
-   **Função:**
    1.  Recebe o caminho de uma imagem de produto.
    2.  Envia a imagem para o modelo LLaVA através do Ollama.
    3.  Usa um **prompt estruturado** para fazer perguntas específicas sobre a imagem, como:
        -   "Este é um packshot de produto com fundo branco?"
        -   "Quais são os ângulos visíveis (frontal, lateral, traseiro)?"
        -   "A imagem contém texto ou logos?"
        -   "Qual a qualidade percebida da imagem (baixa, média, alta)?"
    4.  Recebe uma resposta em formato JSON com os metadados extraídos.
-   **Propósito:** Automatizar a classificação de imagens, identificar as melhores fotos de produtos (packshots), e enriquecer o catálogo com metadados que seriam difíceis de obter manualmente.

### Estratégia de Captura Autônoma com Agentes de IA

Para escalar a captura de imagens a um nível de automação quase total, foi criado um documento estratégico que serve como um "mega-prompt" para agentes de IA.

-   **Documento:** `docs/ai-ml/mega-prompt-image-capture.md`
-   **Propósito:** Fornecer um conjunto detalhado de instruções, heurísticas e regras para um agente de IA (como Gemini ou um assistente da OpenAI) realizar a tarefa de encontrar e classificar imagens de produtos de forma autônoma.
-   **Conteúdo Principal:**
    -   **Sistema de Pontuação de Imagens:** Define uma pontuação de 0 a 10 para classificar a relevância de uma imagem (ex: 10 para um packshot técnico de alta resolução, 7 para um diagrama, 5 para uma imagem contextual, 0 para um banner).
    -   **Heurísticas de Navegação:** Ensina o agente a identificar páginas de produtos em vez de páginas de marketing, a lidar com seletores de região/idioma e a encontrar galerias de imagens.
    -   **Template de Metadados:** Especifica o formato de saída desejado para cada imagem encontrada, incluindo URL, pontuação de qualidade, especificações técnicas visíveis, etc.
-   **Visão:** Este documento é a base para a **próxima geração de scrapers**, onde um agente de IA, em vez de um script com seletores CSS fixos, navegará de forma inteligente pelos sites dos fabricantes para encontrar as melhores imagens.

### A Evolução Perdida

-   **Referência:** O arquivo `INDEX.md` menciona um documento chamado `docs/AI_IMAGE_EVOLUTION.md`.
-   **Análise:** Este arquivo não foi encontrado no workspace, mas sua existência sugere que havia um plano para documentar a evolução do uso de IA na infraestrutura de imagens. Seu conteúdo provavelmente detalharia a jornada desde os primeiros experimentos até a implementação da estratégia de agentes autônomos. A recriação deste documento, com base nas ferramentas existentes, pode ser um passo futuro valioso.

---

## 6. Fluxo de Dados e Monitoramento

O gerenciamento eficaz das imagens depende de um fluxo de dados bem definido e de um sistema de monitoramento que forneça visibilidade em tempo real sobre o status da operação.

### Fluxo de Dados (Ciclo de Vida da Imagem)

1.  **Entrada:** O processo começa com um SKU de produto do inventário (`products_inventory_raw.json`).
2.  **Captura (Scraping):**
    *   O `scrape_dynamic_images.py` usa o SKU para construir uma URL de busca ou acessar uma página de produto conhecida.
    *   Ele utiliza o `playwright_scraper` para renderizar a página.
    *   URLs de imagens e PDFs são extraídas.
3.  **Download:** As URLs são passadas para um downloader assíncrono, que baixa os arquivos para um diretório temporário.
4.  **Processamento e Otimização:**
    *   As imagens baixadas são alimentadas no pipeline de processamento (`image_processor.py`, `generate-responsive-images.py`, `optimize-product-images.py`).
    *   As imagens são normalizadas, redimensionadas, aprimoradas e salvas nos diretórios finais (ex: `static/images-responsive/`).
5.  **Mapeamento e Persistência:**
    *   O `product_image_map.json` é o "banco de dados" central que associa os SKUs aos caminhos de suas respectivas imagens (original, large, medium, thumb). Este arquivo de 7617 linhas é um artefato crítico que representa o estado consolidado do mapeamento de imagens de todo o catálogo.
    *   O `products_inventory_dynamic_enriched.json` é atualizado para refletir que o produto agora possui imagens e/ou datasheets.
6.  **Análise (Opcional):** As imagens processadas podem ser enviadas para o `test-ai-image-analysis.py` para extrair metadados adicionais, que podem ser armazenados de volta no mapa de produtos ou em um banco de dados separado.

### Monitoramento

A visibilidade sobre a saúde e o progresso do sistema de scraping é fornecida por duas ferramentas principais:

1.  **Monitor de Console em Tempo Real:**
    *   **Ferramenta:** `scripts/monitor_scraping.py`
    *   **Função:** Um script executado em modo `--watch` que atualiza o console a cada poucos segundos com métricas vitais:
        -   Contagem de recursos manuais (PDFs, imagens).
        -   Estatísticas de cobertura do inventário (quantos produtos têm datasheets/imagens).
        -   Contagem de arquivos e tamanho total do diretório de imagens baixadas.
    *   **Propósito:** Fornecer feedback imediato durante a execução dos scrapers, permitindo que os desenvolvedores vejam o progresso (ou a falta dele) em tempo real. Foi essa ferramenta que rapidamente diagnosticou a falha do scraper dinâmico ao mostrar "0 arquivos, 0.00 MB" consistentemente.

2.  **Dashboard de Monitoramento Centralizado:**
    *   **Ferramenta:** `config/grafana/dashboards/scraping-overview.json`
    *   **Função:** Um dashboard pré-configurado para o Grafana, projetado para visualizar métricas de longo prazo a partir de um sistema de monitoramento (como Prometheus).
    *   **Métricas Visualizadas:**
        -   Taxa de sucesso de scraping (%).
        -   Imagens baixadas por hora.
        -   Uso de cotas de API (Gemini, OpenAI).
        -   Contagem de produtos por fabricante.
        -   Log de erros de scraping.
        -   Latência de processamento em pipelines de dados (Pathway).
    *   **Propósito:** Oferecer uma visão macro e histórica da saúde do sistema, identificar tendências e diagnosticar problemas de performance ou de cota de API. Embora o dashboard esteja definido, a infraestrutura para coletar e expor essas métricas (via Prometheus) ainda precisa ser totalmente integrada com os scripts de scraping.

---

## 7. Estado Atual, Gaps e Recomendações

Esta seção final consolida a análise da infraestrutura, destacando o que funciona, o que está quebrado e qual o caminho a seguir.

### ✅ O Que Funciona

1.  **Pipeline de Processamento e Otimização:** A cadeia de ferramentas (`image_processor.py`, `generate-responsive-images.py`, `optimize-product-images.py`) é **madura, robusta e eficiente**. Ela é capaz de pegar qualquer imagem de entrada e transformá-la em múltiplos formatos otimizados e de alta qualidade, pronta para uso no frontend e em plataformas de terceiros.
2.  **Mapeamento de Imagens:** O `product_image_map.json` serve como um banco de dados de imagens centralizado e funcional, embora precise ser populado com novos dados.
3.  **Análise por IA:** A capacidade de analisar imagens com modelos locais (`test-ai-image-analysis.py`) está implementada e funciona, fornecendo uma base sólida para a classificação automática de imagens.
4.  **Monitoramento:** O monitor de console (`monitor_scraping.py`) provou seu valor ao diagnosticar rapidamente a falha do scraper dinâmico. O dashboard Grafana está pronto para ser integrado.

### ❌ Gaps Críticos

1.  **FALHA NA CAPTURA DINÂMICA (GAP PRINCIPAL):** O `scrape_dynamic_images.py` **não está funcionando**. Apesar de ter sido executado, ele não produziu nenhum resultado (0 imagens, 0 PDFs). A cobertura de imagens de produtos permanece em **0%**. A causa raiz é desconhecida, mas pode ser:
    *   Erros silenciosos no código do Playwright.
    *   Bloqueio por parte dos sites dos fabricantes (detecção de bot, CAPTCHAs).
    *   Problemas de timeout ou de rede.
    *   Seletores CSS incorretos ou desatualizados para os fabricantes.
2.  **Integração do Monitoramento Avançado:** As métricas definidas no dashboard Grafana (`scraping-overview.json`) não estão sendo ativamente coletadas e enviadas para um sistema como o Prometheus. O monitoramento atual é apenas local (console).
3.  **Documentação da Evolução da IA:** O arquivo `AI_IMAGE_EVOLUTION.md`, que deveria contar a história da aplicação de IA, está faltando.

### 🚀 Recomendações e Próximos Passos

A prioridade absoluta é consertar a camada de captura de imagens. As recomendações estão ordenadas por prioridade:

1.  **Debug Urgente do `scrape_dynamic_images.py` (Prioridade Máxima):**
    *   **Passo 1: Adicionar Logging Detalhado:** Modificar o script para registrar cada etapa: inicialização do browser, navegação para a URL, seletores CSS tentados, número de elementos encontrados, erros de timeout, etc.
    *   **Passo 2: Executar em Modo Headful:** Rodar o Playwright com `headless=False` para observar visualmente o comportamento do navegador. Isso ajudará a identificar se CAPTCHAs ou pop-ups estão bloqueando a execução.
    *   **Passo 3: Testar com um Único Produto:** Modificar o script para focar em um único produto de um único fabricante (ex: um inversor da Huawei) para isolar o problema.
    *   **Passo 4: Revisar Seletores CSS:** Verificar se os seletores CSS para cada fabricante ainda são válidos, inspecionando manualmente as páginas dos produtos.

2.  **Integrar o Monitoramento com Prometheus/Grafana:**
    *   Adicionar uma biblioteca cliente do Prometheus aos scripts de scraping e processamento.
    *   Expor as métricas chave (imagens processadas, erros, tempo de execução) em um endpoint `/metrics`.
    *   Configurar o Prometheus para coletar essas métricas e o Grafana para visualizá-las, ativando o `scraping-overview.json`.

3.  **Recriar a Documentação da IA:**
    *   Com base nas ferramentas existentes, criar o documento `AI_IMAGE_EVOLUTION.md` para registrar o conhecimento e a estratégia de IA.

4.  **Implementar o Agente de IA Autônomo:**
    *   Como um objetivo de longo prazo, usar o `mega-prompt-image-capture.md` para implementar um agente de IA que possa substituir gradualmente os scrapers baseados em seletores CSS, tornando o sistema mais resiliente a mudanças nos sites dos fabricantes.
