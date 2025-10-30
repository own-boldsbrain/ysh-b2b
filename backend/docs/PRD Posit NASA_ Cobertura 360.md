

# **Documento de Requisitos de Produto (PRD): Plataforma de Inteligência Estratégica da Força de Trabalho "Nexus"**

## **I. Introdução: A Visão Estratégica para a Inteligência da Força de Trabalho**

### **1.1. Visão do Produto**

Criar a "Nexus", uma Plataforma de Inteligência Estratégica da Força de Trabalho de nível empresarial, projetada para transformar os dados de capital humano de uma organização de um registro estático e isolado em um ativo estratégico dinâmico, consultável e preditivo. A visão é capacitar as organizações a mitigar riscos em iniciativas de missão crítica, otimizar o investimento em P\&D e alinhar proativamente as capacidades da força de trabalho com os objetivos futuros.

### **1.2. Proposta de Valor Central**

A Nexus permitirá que as organizações respondam às suas perguntas mais complexas e críticas sobre sua força de trabalho em tempo real. Ela transcende os relatórios tradicionais de RH para fornecer uma visão conectada de 360 graus de habilidades, experiências e relacionamentos, ligando diretamente as pessoas aos resultados estratégicos.

### **1.3. O Imperativo Estratégico (O "Porquê")**

A plataforma aborda diretamente o desafio de se preparar para metas complexas e de longo prazo, exemplificado pela necessidade da NASA de "voltar à Lua e seguir para Marte".1 Isso estabelece o contexto de alto risco para o qual a Nexus foi projetada.  
Fundamentalmente, a Nexus ataca ineficiências organizacionais profundas e quantificáveis. Conforme articulado pela liderança da NASA, estima-se que "30% do total dos fundos de P\&D são gastos para refazer o que já fizemos uma vez" e "54% de nossas decisões são tomadas com informações inconsistentes, incompletas ou inadequadas".2 A Nexus se posiciona como uma solução direta para esse desperdício, tornando o conhecimento e a expertise internos localizáveis e acessíveis.  
A incapacidade de mapear com precisão as competências e experiências internas não é apenas uma questão de gestão de talentos; é um problema financeiro e operacional com consequências diretas. A dificuldade em identificar pessoal com as competências necessárias 1 leva diretamente a um desperdício significativo de recursos em trabalho redundante e a um aumento do risco em projetos críticos.2 Portanto, o retorno sobre o investimento (ROI) da plataforma deve ser enquadrado em termos de economia de custos de P\&D, aceleração dos cronogramas de projetos e redução do risco da missão, elevando sua proposta de valor para além do Diretor de Recursos Humanos e alcançando o C-suite.

## **II. O Domínio do Problema: Silos de Dados e Pontos Cegos Estratégicos**

### **2.1. O Desafio da Complexidade em Organizações Baseadas em Conhecimento**

Organizações de grande escala, como a NASA, acumularam décadas de conhecimento distribuído por "centenas de milhões de documentos, relatórios, lições aprendidas e descobertas de pesquisa científica".3 O problema central é que esses dados estão presos em "silos entre grupos, departamentos, programas e produtos".3  
Este não é apenas um problema de gerenciamento de documentos, mas um desafio de capital humano. A expertise está igualmente isolada, tornando impossível obter uma visão unificada. A dificuldade reside em navegar por "conjuntos de dados amplamente desconectados e isolados em sistemas complexos para tomar decisões de missão crítica".4 A Nexus aplica essa mesma lógica, que foi originalmente usada para conjuntos de dados de engenharia, aos dados de capital humano.

### **2.2. As Limitações dos Sistemas Tradicionais**

Bancos de dados relacionais tradicionais são mal equipados para resolver este problema. Eles são inerentemente "confusos", com uma estrutura rígida de "linhas, colunas, junções", e não foram construídos para modelar os "relacionamentos complexos que existem em uma organização massiva".5 Essa limitação técnica é a causa raiz dos pontos cegos estratégicos que afligem a liderança.

### **2.3. As Consequências da Inação**

As implicações de não abordar essa desconexão de dados são graves e multifacetadas:

* **Risco para Metas Estratégicas:** A consequência primária é a incapacidade de responder com confiança à pergunta: "Ainda temos os conjuntos de habilidades necessários para fazer isso?" para novos projetos ambiciosos.1 Isso introduz um risco incalculável no planejamento de longo prazo.  
* **Atrito e Subutilização de Talentos:** Sem um mecanismo para conectar funcionários qualificados a projetos significativos, as organizações correm o risco de subutilizar seus principais talentos, levando ao desengajamento e ao atrito. A necessidade de um "mercado de talentos" interno destaca essa lacuna crítica entre as habilidades disponíveis e as oportunidades existentes.1  
* **Expertise Oculta:** Habilidades cruciais permanecem não descobertas. A NASA enfrentou o desafio de encontrar pessoas realizando "trabalho do tipo ciência de dados" que não eram formalmente "identificadas como cientistas de dados".1 Isso ilustra a falha fundamental de depender apenas de cargos e registros formais para entender as capacidades de uma força de trabalho.

## **III. Personas-Alvo e Jobs-to-be-Done (JTBD)**

Para garantir que a Nexus resolva problemas do mundo real, a plataforma é projetada em torno das necessidades e motivações de usuários-chave. A matriz a seguir detalha essas personas, o "trabalho" que estão tentando realizar e os resultados que usam para medir o sucesso. Esta abordagem muda o foco do desenvolvimento de "quais recursos construir?" para "que progresso nossos usuários estão tentando fazer?", ancorando cada requisito funcional em um objetivo claro e centrado no usuário.

| Persona | Job Story (História do Trabalho) | Resultados Desejados | Evidência de Suporte |
| :---- | :---- | :---- | :---- |
| **Líder de Missão** (Gerente de Projeto) | "Quando estou montando uma equipe para uma nova missão, quero identificar rapidamente pessoal com uma combinação específica de habilidades técnicas verificadas e experiência em projetos anteriores, para que eu possa minimizar o risco do projeto e acelerar os cronogramas." | \- Tempo reduzido para alocação de pessoal \- Maior confiança na composição da equipe \- Visibilidade de adjacências de habilidades e candidatos "quase perfeitos" | 1 |
| **O Especialista** (Funcionário) | "Quando estou buscando meu próximo desafio de carreira, quero descobrir projetos internos que se alinhem com minhas habilidades e metas de desenvolvimento, para que eu possa aprimorar minha expertise e contribuir de forma mais eficaz para a missão da organização." | \- Recomendações de oportunidades personalizadas \- Visibilidade clara da trajetória de carreira \- Reconhecimento por habilidades especializadas e "ocultas" | 1 |
| **O Estrategista** (Líder de RH/People Analytics) | "Quando estou conduzindo o planejamento de longo prazo da força de trabalho, quero modelar o impacto dos requisitos de missões futuras em nosso inventário de habilidades atual, para que eu possa identificar e abordar proativamente lacunas críticas de capacidade." | \- Análise de lacunas de habilidades baseada em dados \- Modelagem preditiva da força de trabalho \- Justificativa para orçamentos de contratação/treinamento \- Respostas a cenários "e se" | 6 |
| **O Executivo** (Liderança da Agência) | "Quando estou tomando decisões críticas sobre a direção estratégica da agência, quero um painel de controle em tempo real da prontidão de nossa força de trabalho, para que eu possa me comprometer com confiança a metas ambiciosas de longo prazo." | \- Métricas de saúde organizacional de fácil visualização \- Insight sobre a composição e dinâmica da força de trabalho \- Capacidade de responder a perguntas complexas e ad-hoc sobre capital humano | 5 |

## **IV. A Plataforma "Nexus": Conceitos Centrais e Arquitetura**

### **4.1. O Paradigma do Grafo de Conhecimento**

A Nexus é construída sobre uma base de grafo de conhecimento. Ao contrário dos bancos de dados relacionais, um grafo "inverte essa lógica" ao armazenar e conectar nativamente entidades (pessoas, habilidades, projetos) e seus relacionamentos.5 Isso permite que o sistema "escaneie e conecte rapidamente múltiplas camadas de dados da força de trabalho em segundos".9  
A flexibilidade de um grafo é um diferencial chave: "você não precisa de um esquema completo de antemão. Começamos com relacionamentos conhecidos e expandimos à medida que descobrimos mais insights nos dados".5 Esta propriedade suporta um produto ágil e em evolução, capaz de se adaptar a novas fontes de dados e perguntas de negócios.

### **4.2. Visão Geral da Arquitetura Conceitual**

A arquitetura da Nexus é composta por camadas distintas que trabalham em conjunto para transformar dados brutos em inteligência acionável. A interação entre o grafo de conhecimento e a plataforma de ciência de dados é fundamental para o seu poder. O grafo fornece a estrutura de dados limpa e conectada, enquanto a plataforma de ciência de dados oferece as ferramentas para analisar essa estrutura, construir modelos preditivos sobre ela (por exemplo, modelos de atrito 8) e implantar aplicações interativas (painéis Shiny) que permitem aos usuários explorar os insights do grafo. Essa sinergia arquitetônica é um diferencial competitivo chave.

* **Camada de Ingestão de Dados:** Extrai dados de diversas fontes isoladas (bancos de dados de RH, currículos, registros de projetos) para uma área de preparação unificada (por exemplo, AWS S3).5  
* **Camada de Processamento e Enriquecimento de Dados:** Utiliza Modelos de Linguagem Grandes (LLMs) e Processamento de Linguagem Natural (PNL) para extrair entidades (como habilidades) de texto não estruturado, como currículos e descrições de projetos.5  
* **Núcleo do Banco de Dados de Grafo:** O grafo de conhecimento central (por exemplo, Memgraph, Neo4j) onde todas as entidades e relacionamentos são armazenados, indexados e consultados.1  
* **Camada de Aplicação e Análise:** O ecossistema Posit (RStudio) fornece as ferramentas para construir aplicações interativas (Shiny), implantar modelos (Vetiver) e criar APIs (Plumber).10 Este é o "workbench" para cientistas de dados e analistas que interagem com os dados do grafo.  
* **Camada de Apresentação:** Interfaces voltadas para o usuário, incluindo um "Mercado de Talentos" baseado na web, painéis de controle e um chatbot conversacional.1

## **V. Capacidades do Sistema: Entradas do Usuário e Saídas do Sistema**

Esta seção detalha os requisitos funcionais da plataforma Nexus, divididos por módulos. A tabela a seguir resume as principais funcionalidades, definindo as interações do usuário e os resultados esperados do sistema, o que fornece clareza para as equipes de desenvolvimento e garantia de qualidade.

| Módulo | Entradas do Usuário (Inputs) | Processamento do Sistema | Saídas do Sistema (Outputs) |
| :---- | :---- | :---- | :---- |
| **Ingestão e Enriquecimento de Dados Unificados** | Administrador do sistema configura conectores para sistemas de origem (APIs de RH, buckets S3). | Ingestão de dados estruturados (armazém de dados de pessoal) e não estruturados (currículos, registros de projetos). Estabelecimento de pipelines de atualização periódica. | Dados brutos preparados em um data lake central (AWS S3) para processamento. |
| **Extração de Habilidades e Gerenciamento de Ontologia com IA** | Documentos de texto não estruturado (currículos, relatórios de projetos). | Um LLM on-premise (Ollama) processa o texto para extrair habilidades, realizando desambiguação de entidades (por exemplo, "JS" para "JavaScript"). Popula o grafo com nós e relacionamentos. | Um grafo de conhecimento onde os funcionários estão conectados a um rico conjunto de habilidades inferidas, que vai além de seus cargos oficiais. |
| **Mercado de Talentos e Descoberta de Especialistas** | **Líder de Missão:** Insere detalhes do projeto e habilidades necessárias em uma UI. **Especialista:** Cria perfil, lista habilidades e navega por oportunidades. | O banco de dados de grafo combina oportunidades com perfis de funcionários. Algoritmos de similaridade encontram correspondências exatas e parciais. | Lista classificada de candidatos para Líderes de Missão. Lista personalizada de projetos relevantes para Especialistas. |
| **Suíte de Análise Estratégica e Visualização** | **Estrategista/Executivo:** Seleciona parâmetros em um painel interativo (por exemplo, "Mostrar distribuição de habilidades", "Modelar risco de atrito"). | Executa consultas Cypher complexas no grafo. O servidor Posit Connect executa aplicações Shiny para visualização em tempo real. Modelos R/Python geram insights preditivos. | Painéis interativos, relatórios e visualizações que respondem a perguntas estratégicas da força de trabalho. |
| **Interface de Inteligência Conversacional (Chatbot)** | Usuário faz uma pergunta em linguagem natural (por exemplo, "Encontre-me um especialista em análise de dados"). | Implementa uma arquitetura GraphRAG. O LLM traduz a pergunta em uma consulta de grafo (Cypher). Recupera nós e contexto do grafo para gerar uma resposta coerente. | Resposta direta e precisa em linguagem natural, com links para pessoas ou projetos relevantes no sistema. |

### **5.1. Módulo: Ingestão e Enriquecimento de Dados Unificados**

* **Entrada do Usuário:** Um administrador de sistema configura os conectores para os sistemas de origem, como endpoints de API do Sistema de Informação de Recursos Humanos (HRIS) ou buckets S3 para despejo de documentos.  
* **Processo do Sistema:**  
  * Ingere dados estruturados de fontes como o Armazém de Dados de Pessoal interno da NASA.5  
  * Ingere dados não estruturados, como currículos de equipes e descrições de projetos do Registro de Casos de Uso de IA.5  
  * Estabelece um pipeline para atualizações periódicas de dados para garantir que o grafo permaneça atualizado.  
* **Saída do Sistema:** Os dados brutos são preparados em um data lake central (por exemplo, AWS S3), prontos para serem processados pela camada de enriquecimento.

### **5.2. Módulo: Extração de Habilidades e Gerenciamento de Ontologia com IA**

* **Entrada do Usuário:** Documentos de texto não estruturado (currículos, relatórios de projetos) são fornecidos ao sistema.  
* **Processo do Sistema:**  
  * Um LLM on-premise (por exemplo, Ollama) processa o texto para extrair habilidades sem a necessidade de conjuntos de dados rotulados manualmente, acelerando significativamente o processo.5  
  * Utiliza técnicas de PNL para desambiguação de entidades, garantindo consistência (por exemplo, mapeando "JS" para "JavaScript").5  
  * Popula o grafo com nós "Pessoa", "Habilidade" e "Projeto" e cria relacionamentos significativos (por exemplo, (Pessoa)--\>(Habilidade)).  
* **Saída do Sistema:** Um grafo de conhecimento onde os funcionários estão conectados a um rico e inferido conjunto de habilidades e competências, fornecendo uma visão muito mais profunda do que seus cargos oficiais.

### **5.3. Módulo: Mercado de Talentos e Descoberta de Especialistas**

* **Entrada do Usuário (Líder de Missão):** Insere detalhes do projeto, habilidades necessárias e duração em uma interface de usuário do "mercado de talentos".1  
* **Entrada do Usuário (Especialista):** Cria um perfil, lista habilidades e interesses, e navega por oportunidades abertas.1  
* **Processo do Sistema:**  
  * O banco de dados de grafo combina oportunidades com perfis de funcionários usando relacionamentos de habilidades e experiência.  
  * Algoritmos de similaridade comparam perfis de funcionários com as necessidades do projeto para encontrar não apenas correspondências exatas, mas também correspondências "boas o suficiente" que poderiam ser aprimoradas.1  
* **Saída do Sistema:** Uma lista classificada de funcionários candidatos para os Líderes de Missão. Uma lista personalizada de projetos relevantes para os Especialistas.

### **5.4. Módulo: Suíte de Análise Estratégica e Visualização**

* **Entrada do Usuário:** Um Estrategista ou Executivo seleciona parâmetros em um painel (por exemplo, "Mostre-me a distribuição de habilidades para o programa Artemis", "Modele o risco de atrito para engenheiros com 5-10 anos de experiência").  
* **Processo do Sistema:**  
  * O sistema executa consultas Cypher complexas contra o grafo para agregar os dados necessários.  
  * O servidor Posit Connect executa aplicações Shiny que visualizam os resultados da consulta em tempo real.  
  * Modelos em R/Python podem ser executados para gerar insights preditivos (por exemplo, identificar lacunas de habilidades para missões futuras).7  
* **Saída do Sistema:** Painéis interativos, relatórios e visualizações que fornecem respostas a perguntas estratégicas da força de trabalho.

### **5.5. Módulo: Interface de Inteligência Conversacional (Chatbot)**

* **Entrada do Usuário:** O usuário faz uma pergunta em linguagem natural, como "Quem trabalhou em projetos de IA altamente similares nos centros da NASA?" 5 ou "Encontre-me um especialista em análise de dados".1  
* **Processo do Sistema:**  
  * Implementa uma arquitetura GraphRAG (Geração Aumentada por Recuperação de Grafo).5  
  * O LLM primeiro traduz a consulta em linguagem natural para uma consulta de grafo estruturada (por exemplo, Cypher).1  
  * O sistema recupera nós relevantes e seu contexto ("tripletos de contexto") do grafo.  
  * Este contexto é passado de volta para o LLM, que gera uma resposta coerente e contextualizada em linguagem natural.  
* **Saída do Sistema:** Uma resposta direta e precisa à pergunta do usuário, com links para as pessoas ou projetos relevantes no sistema.

## **VI. Requisitos Não Funcionais (NFRs)**

### **6.1. Escalabilidade**

A arquitetura do sistema deve ser projetada para escalar para o alvo da NASA de mais de 500.000 nós e milhões de arestas.5 Isso requer um banco de dados de grafo e uma camada de aplicação horizontalmente escaláveis para lidar com o aumento do volume de dados e da carga de usuários.

### **6.2. Segurança**

* O sistema deve lidar com Informações de Identificação Pessoal (PII) com extremo cuidado.  
* Requer controles de acesso robustos e capacidades de segmentação de dados, potencialmente usando recursos de nível empresarial do banco de dados de grafo para isolar PII, permitindo ainda a análise da estrutura do grafo anonimizada.5  
* A arquitetura deve suportar a implantação em uma nuvem privada (por exemplo, AWS) para manter todos os dados dentro do perímetro seguro da organização.9

### **6.3. Desempenho**

As respostas a consultas para casos de uso interativos, como o chatbot e o localizador de especialistas, devem ser quase em tempo real (sub-segundo) para garantir uma experiência de usuário fluida e responsiva.

### **6.4. Interoperabilidade**

A plataforma deve fornecer APIs bem documentadas para:

* Integrar-se com sistemas de RH externos para ingestão de dados.  
* Permitir que o ecossistema de ciência de dados Posit consulte o grafo e implante modelos/aplicações de forma transparente.10  
* Potencialmente conectar-se com outros sistemas empresariais, como ferramentas de gerenciamento de projetos ou colaboração.

### **6.5. Usabilidade**

As interfaces de usuário para todas as personas devem ser intuitivas, exigindo treinamento mínimo. O chatbot, em particular, deve diminuir a barreira de entrada para usuários casuais que não são analistas de dados especialistas.

## **VII. Roteiro Futuro e Evolução**

### **7.1. Fase 1 (MVP)**

Foco na ingestão de dados principais, extração de habilidades de currículos e na funcionalidade de localizador de especialistas/mercado de talentos para Líderes de Missão e Especialistas.

### **7.2. Fase 2 (Expansão)**

* Introduzir a Suíte de Análise Estratégica para a persona do Estrategista.  
* Lançar a interface de chatbot conversacional.  
* Automatizar completamente os pipelines de dados.5

### **7.3. Fase 3 (Visão)**

* Aprimorar a qualidade e a desambiguação dos dados (por exemplo, resolução avançada de entidades).5  
* Expandir o grafo para incluir metas de aprendizado dos funcionários, tipos de projetos preferidos e classificações de habilidades.5  
* Desenvolver um LLM de RH de propósito geral que possa fornecer insights profundos e contextualizados para a liderança, avançando para uma plataforma de capital humano verdadeiramente preditiva.9

## **VIII. Conclusão**

A plataforma Nexus representa uma mudança fundamental de sistemas de RH reativos para uma gestão proativa e estratégica do capital humano. Ao aproveitar o poder combinado de grafos de conhecimento, inteligência artificial e plataformas avançadas de ciência de dados, a Nexus aborda diretamente os desafios sistêmicos de silos de dados e expertise oculta que impedem a inovação e geram ineficiências significativas em grandes organizações.  
A implementação da Nexus oferece um caminho claro para mitigar riscos em projetos de missão crítica, otimizar a alocação de talentos e, mais importante, garantir que a força de trabalho de uma organização esteja pronta para os desafios do futuro. Ao transformar dados de pessoas em um ativo estratégico e dinâmico, a Nexus capacita a liderança a tomar decisões mais informadas e confiantes, garantindo que os objetivos mais ambiciosos, seja chegar a Marte ou liderar um mercado, estejam ao alcance.

#### **Referências citadas**

1. NASA Turns to People Analytics as It Prepares to Send Humans to ..., acessado em setembro 24, 2025, [https://builtin.com/data-science/nasa-people-analytics-data-science-manned-mars-mission](https://builtin.com/data-science/nasa-people-analytics-data-science-manned-mars-mission)  
2. Capturing, Analyzing, Maintaining, and Disseminating Experimental Data in a Robust Material Information Management System, acessado em setembro 24, 2025, [https://ntrs.nasa.gov/api/citations/20230011548/downloads/ICMAMS23\_ExpData.pdf](https://ntrs.nasa.gov/api/citations/20230011548/downloads/ICMAMS23_ExpData.pdf)  
3. NASA Expert Visualizes Lessons Learned | APPEL Knowledge Services, acessado em setembro 24, 2025, [https://appel.nasa.gov/2017/08/29/nasa-expert-visualizes-lessons-learned/](https://appel.nasa.gov/2017/08/29/nasa-expert-visualizes-lessons-learned/)  
4. case study \- nasa \- Stardog, acessado em setembro 24, 2025, [https://www.stardog.com/img/nasa\_case\_study\_stardog.pdf?\_cchid=6fbcbcf7a3555d3fbcaec3f933b7c6b2](https://www.stardog.com/img/nasa_case_study_stardog.pdf?_cchid=6fbcbcf7a3555d3fbcaec3f933b7c6b2)  
5. How NASA is Using Graph Technology and LLMs to Build a People ..., acessado em setembro 24, 2025, [https://memgraph.com/blog/nasa-memgraph-people-knowledge-graph](https://memgraph.com/blog/nasa-memgraph-people-knowledge-graph)  
6. Customer Stories \- Posit, acessado em setembro 24, 2025, [https://posit.co/about/customer-stories/](https://posit.co/about/customer-stories/)  
7. Data Science Hangout | David Meza, NASA | People analytics for getting to the moon, acessado em setembro 24, 2025, [https://www.youtube.com/watch?v=mr3TmyXOG\_g](https://www.youtube.com/watch?v=mr3TmyXOG_g)  
8. People analytics for getting to the moon \- Posit, acessado em setembro 24, 2025, [https://posit.co/data-science-hangout/45-david-meza/](https://posit.co/data-science-hangout/45-david-meza/)  
9. How NASA is using AI and knowledge graphs to crack the workforce ..., acessado em setembro 24, 2025, [https://www.thepeoplespace.com/practice/articles/how-nasa-using-ai-and-knowledge-graphs-crack-workforce-planning-code](https://www.thepeoplespace.com/practice/articles/how-nasa-using-ai-and-knowledge-graphs-crack-workforce-planning-code)  
10. David Meza \- The RStudio Ecosystem as a Critical Part of NASA Analytics Capabilities, acessado em setembro 24, 2025, [https://www.youtube.com/watch?v=2LDOKPw6EKk](https://www.youtube.com/watch?v=2LDOKPw6EKk)  
11. KNOWLEDGE ARCHITECTURE: IT'S IMPORTANCE TO AN ORGANIZATION \- nasa appel, acessado em setembro 24, 2025, [https://appel.nasa.gov/wp-content/uploads/2016/06/Meza-David.pdf](https://appel.nasa.gov/wp-content/uploads/2016/06/Meza-David.pdf)