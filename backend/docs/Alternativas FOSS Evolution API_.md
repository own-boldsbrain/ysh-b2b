

# **Análise Comparativa: As 7 Melhores Alternativas FOSS à Evolution API para Integração com WhatsApp**

## **1\. Sumário Executivo**

**Propósito do Relatório:** Este relatório atende à solicitação de identificar e detalhar as sete principais alternativas de Software Livre e de Código Aberto (FOSS) à Evolution API, uma plataforma de integração com o WhatsApp.  
**Visão Geral da Evolution API:** A Evolution API 1 é uma plataforma abrangente que suporta tanto a API não oficial do WhatsApp baseada em Baileys quanto a API oficial WhatsApp Cloud. Destaca-se por suas extensas integrações incorporadas (Typebot, Chatwoot, Dify, OpenAI, filas de mensagens, S3/Minio) e suas ambições multiplataforma.  
**Desafio das Alternativas FOSS:** As alternativas FOSS concentram-se primariamente na engenharia reversa não oficial do WhatsApp Web. Geralmente, carecem do suporte direto à API Cloud oficial e da mesma amplitude de integrações pré-construídas encontradas na Evolution API. Esta diferença fundamental decorre da natureza das APIs oficiais, que envolvem aprovações, custos e requisitos de negócios específicos gerenciados pela Meta, tornando complexa sua adoção por projetos FOSS comunitários.  
Principais Descobertas \- As 7 Melhores Alternativas: As sete alternativas FOSS selecionadas, cada uma com suas características distintas, são:  
\* go-whatsapp-web-multidevice: Baseada em Go e whatsmeow, destaca-se pelo suporte a MCP para IA.  
\* wppconnect-server: Baseada em Node.js e Puppeteer (via WPPConnect), oferece integrações com Chatwoot e S3.  
\* open-wa/wa-automate-nodejs: Solução em Node.js (provavelmente Puppeteer), com integrações como Node-RED e Twilio.  
\* fazer-ai/baileys-api: Wrapper leve para Baileys em Node.js (Bun/Elysia.js) com integração Chatwoot.  
\* PointerSoftware/Baileys-2025-Rest-API: API baseada em Baileys com dashboard de gerenciamento e persistência PostgreSQL.  
\* Auties00/Cobalt: Biblioteca Java/Kotlin para interação profunda com WhatsApp Web e Mobile.  
\* nizarfadlan/baileys-api: API REST simples baseada em Baileys com suporte a banco de dados Prisma.  
**Tema Central da Recomendação:** A escolha da alternativa ideal depende das necessidades específicas do usuário, como linguagem de programação preferida, integrações desejadas (e a disposição para desenvolvê-las customizadamente) e a tolerância à instabilidade inerente às APIs não oficiais.  
**Estrutura do Relatório:** As seções subsequentes detalharão a Evolution API como referência, a metodologia de seleção das alternativas, uma análise aprofundada de cada uma, uma análise comparativa e, por fim, recomendações e conclusões.

## **2\. Entendendo a Referência: Evolution API**

A Evolution API 1 se posiciona como mais do que uma simples API para WhatsApp, aspirando ser uma plataforma completa de mensagens e integrações. Esta ambição estabelece um patamar elevado para alternativas FOSS, dado que a Evolution API combina flexibilidade de código aberto com funcionalidades frequentemente vistas em soluções comerciais.  
Capacidades Centrais da API WhatsApp:  
A plataforma oferece duas abordagens distintas para a integração com o WhatsApp, permitindo aos usuários uma escolha estratégica baseada em custo, funcionalidades e tolerância a riscos:

* **WhatsApp API \- Baileys (Não Oficial):** 1  
  * Gratuita, baseada no WhatsApp Web e utilizando a biblioteca Baileys.  
  * Fornece uma API RESTful para funcionalidades do WhatsApp Web.  
  * Adequada para chats multi-serviço e bots de atendimento.  
  * Reconhece limitações em comparação com APIs oficiais devido à dependência do WhatsApp Web.  
* **WhatsApp Cloud API (Oficial):** 1  
  * API oficial fornecida pela Meta.  
  * Solução robusta e confiável, projetada para volumes maiores de mensagens e melhor suporte à integração.  
  * Suporta criptografia de ponta a ponta e análises avançadas.  
  * Requer conformidade com as políticas da Meta e potenciais custos associados.

O suporte duplo a APIs é um diferencial estratégico significativo. Enquanto a maioria dos projetos FOSS se concentra exclusivamente em métodos não oficiais – devido aos custos, processos de aprovação da Meta e requisitos de negócios específicos que são difíceis de gerenciar por iniciativas comunitárias – a Evolution API oferece uma flexibilidade comparável à de soluções comerciais, mas dentro de uma estrutura de projeto de código aberto. Isso a torna um benchmark desafiador para alternativas puramente FOSS e não oficiais igualarem em termos de funcionalidades, especialmente no que tange à estabilidade e aos recursos avançados da API oficial.  
Principais Integrações de Terceiros: 1  
A Evolution API se destaca por um ecossistema rico de integrações pré-construídas, o que reduz consideravelmente o esforço de desenvolvimento para casos de uso comuns:

* **Bots Conversacionais:** Typebot (gerenciamento de gatilhos), Dify AI (gerenciamento de gatilhos, múltiplos agentes).  
* **Atendimento ao Cliente:** Chatwoot.  
* **Capacidades de IA:** OpenAI (conversão de áudio para texto, disponível em todas as integrações).  
* **Manipulação de Eventos/Filas de Mensagens:** RabbitMQ, Amazon SQS, Socket.io (eventos WebSocket).  
* **Armazenamento de Mídia:** Amazon S3 / Minio.

Disponibilizar apenas um endpoint de API é uma parte da solução; oferecer conexões prontas para ferramentas populares como Typebot, Chatwoot, OpenAI e filas de mensagens 1 diminui a barreira de entrada para os usuários e permite a rápida implementação de fluxos de trabalho complexos. Alternativas FOSS podem oferecer webhooks ou extensibilidade básica, mas um conjunto de integrações diretas e documentadas representa uma forte proposta de valor que muitos projetos mantidos por voluntários podem não ter recursos para construir e manter.  
**Aspirações Multiplataforma:** 1

* Além do WhatsApp, com suporte futuro planejado para Instagram e Messenger.  
  Isso sinaliza uma ambição de se tornar um hub central para diversos canais de mensagens. Enquanto a solicitação atual foca em alternativas para WhatsApp, o roteiro da Evolution API 1 para incluir Instagram e Messenger sugere uma estratégia de longo prazo para atender a uma gama mais ampla de necessidades de comunicação empresarial. Essa abordagem prospectiva, se bem-sucedida, a diferenciaria ainda mais de projetos FOSS que são tipicamente focados em uma única plataforma.

**Evolution API Lite:** 1

* Versão otimizada para desempenho e simplificada.  
* Focada exclusivamente em conectividade, sem integrações ou recursos de conversão de áudio.  
* Ideal para microsserviços que priorizam simplicidade e eficiência.  
  A existência de uma versão "Lite" demonstra um entendimento de que nem todos os usuários necessitam do conjunto completo de funcionalidades e integrações. Alguns podem priorizar desempenho bruto e sobrecarga mínima. Oferecer essa versão 1 é uma estratégia de produto madura, reconhecendo que uma abordagem única não serve para todos e atendendo a diferentes segmentos do mercado de desenvolvedores, especialmente aqueles que constroem microsserviços ou têm necessidades específicas de alto desempenho.

## **3\. Metodologia para Seleção de Alternativas FOSS**

A seleção das alternativas FOSS à Evolution API foi guiada por um conjunto de critérios principais e fatores de avaliação secundários, visando identificar projetos que não apenas cumpram o requisito fundamental de serem FOSS, mas que também ofereçam funcionalidades comparáveis, especialmente no que tange ao acesso não oficial ao WhatsApp.  
**Critérios Principais:**

* **Licença FOSS:** Todos os projetos selecionados devem possuir uma licença FOSS reconhecida e aprovada pela OSI (Open Source Initiative), como MIT, Apache 2.0, MPL-2.0 ou LGPL. Esta é uma exigência primária do usuário.  
* **Funcionalidade Principal da API WhatsApp:** As alternativas devem fornecer funcionalidades essenciais como envio e recebimento de mensagens, gerenciamento de sessão e manipulação de mídia, de forma comparável à funcionalidade baseada em Baileys da Evolution API.  
* **Auto-Hospedagem (Self-Hostable):** A solução deve ser passível de auto-hospedagem, alinhando-se com o modelo de implantação típico de projetos FOSS.  
* **Provisionamento de API:** É mandatório que exponham uma API HTTP REST (ou interface programática similar) para permitir a integração com outros sistemas.

**Fatores de Avaliação Secundários:**

* **Capacidades/Potencial de Integração:** Preferência por projetos com integrações existentes (especialmente com Chatwoot, S3, IA, filas de mensagens) ou com clara extensibilidade (ex: sistema robusto de webhooks, arquitetura de plugins).  
* **Pilha Tecnológica (Technology Stack):** Busca por diversidade em linguagens de programação (Go, Node.js, Java/Kotlin, Python) para oferecer opções variadas aos desenvolvedores.  
* **Biblioteca WhatsApp Subjacente:** A escolha da biblioteca (Baileys, whatsmeow, whatsapp-web.js, WPPConnect) impacta diretamente a estabilidade e o conjunto de funcionalidades disponíveis.  
* **Saúde e Atividade da Comunidade:** Métricas do GitHub como estrelas, forks, atividade de contribuidores, resolução de issues e atualizações recentes são indicadores da vitalidade de um projeto.2  
* **Qualidade da Documentação:** Documentação clara e abrangente é crucial para a facilidade de uso e adoção.  
* **Facilidade de Configuração e Implantação:** Suporte a Docker e guias de instalação claros são valorizados.  
* **Estabilidade Percebida e Limitações:** Reconhecimento da instabilidade inerente às APIs não oficiais, mas com preferência por aquelas com histórico de adaptação mais rápida às mudanças do WhatsApp.6  
* **Suporte Multiplataforma (Bônus):** Embora não seja um critério primário (dado que o suporte multiplataforma da Evolution API é futuro), quaisquer iniciativas FOSS existentes nessa direção são observadas.

A metodologia reconhece que uma substituição FOSS perfeita e idêntica à Evolution API (especialmente seu suporte à API oficial e amplitude de integrações) é improvável. O foco é encontrar os equivalentes FOSS mais próximos para suas capacidades de API *não oficial* e potencial de integração. A Evolution API apresenta uma combinação singular de suporte a API oficial e não oficial, além de múltiplas integrações.1 Projetos FOSS, por outro lado, tipicamente dependem de métodos não oficiais devido aos custos e ao controle da Meta sobre a API oficial. Portanto, a metodologia prioriza projetos que se destacam no espaço de APIs não oficiais, são genuinamente FOSS e oferecem algum caminho para integrações, mesmo que isso exija mais esforço do usuário em comparação com as soluções pré-construídas da Evolution API. A estabilidade e o suporte comunitário para essas bibliotecas não oficiais (Baileys, whatsmeow, etc.) tornam-se pontos críticos de avaliação.2

## **4\. Análise Detalhada: As 7 Melhores Alternativas FOSS à Evolution API**

A seguir, apresentamos uma análise aprofundada das sete alternativas FOSS selecionadas, avaliando cada uma com base nos critérios estabelecidos. A ordem de apresentação não implica um ranking estrito, mas segue uma progressão lógica para facilitar a compreensão.  
**4.1. go-whatsapp-web-multidevice (por aldinokemal)**

* **A. Visão Geral do Projeto:**  
  * API baseada em Go para a versão Multi-Dispositivos do WhatsApp Web.10  
  * Utiliza a biblioteca whatsmeow.10  
  * Oferece API HTTP REST e suporte a Servidor MCP (Model Context Protocol).10  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * API REST abrangente: envio de diversos tipos de mensagens (texto, mídia, localização, enquete), informações do usuário, gerenciamento de grupos, gerenciamento de mensagens (revogar, reagir, deletar, editar, ler), postagem de status.10  
  * MCP para integração com agentes de IA.10  
  * Webhooks para mensagens recebidas.10  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Utiliza whatsmeow (baseada em WebSocket, similar à Baileys na abordagem, mas biblioteca diferente). Não suporta a API Cloud Oficial do WhatsApp.10  
  * *Cenário de Integração:* Nenhuma integração explícita como Typebot, Chatwoot, Dify, OpenAI, RabbitMQ, SQS, S3/Minio mencionada.10 O MCP fornece um caminho genérico para integração com IA. Webhooks permitem integrações customizadas.  
  * *Suporte Multiplataforma:* Nenhuma menção a suporte para Instagram/Messenger.10  
  * *Versões Leves/Especializadas:* Nenhuma versão "Lite" específica, mas Go é conhecido pela eficiência.10  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: MIT.10  
  * Popularidade: Mais de 884 estrelas, mais de 367 forks.10 12 contribuidores.10  
  * Atividade de Desenvolvimento: Mantido ativamente, lançamento mais recente v6.0.1 (Maio de 2025).10  
  * Documentação: docs/openapi.yml, visualização no SwaggerEditor, arquivo .env de exemplo.10 GitHub Discussions disponível.15  
* **E. Implantação e Facilidade de Uso:**  
  * Suporte a Docker (docker-compose).10  
  * Builds binários para Linux, macOS, Windows (WSL recomendado para Windows).10  
  * Dependências: ffmpeg requerido para instalações sem Docker.10  
  * Armazenamento de sessão: Utiliza volumes Docker mapeados para /app/storages, implicando armazenamento baseado em arquivos.10 Suporta SQLite e PostgreSQL para armazenamento em banco de dados.20  
* **F. Estabilidade e Limitações Conhecidas:**  
  * API não oficial, sujeita a mudanças do WhatsApp.10  
  * Limitações da biblioteca whatsmeow (ex: não pode executar modos MCP e REST API simultaneamente).10  
  * Problemas comuns: "Failed to get device list: unknown user server 'lid'" 14, bugs de resposta automática.14  
* **G. Roadmap e Potencial Futuro:**  
  * "MCP independente estará disponível no futuro".10 Nenhum roadmap público formal encontrado além de melhorias no rastreador de issues.10  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):** 10  
  * POST /send/message com corpo JSON como {"to": "recipient\_id", "message": "text\_content"}. Detalhes no openapi.yml.

Este projeto se destaca para desenvolvedores familiarizados com Go e a biblioteca whatsmeow.2 Seu suporte a servidor MCP 10 é uma oferta única para integrações com IA, uma área de crescente interesse. A linguagem Go 10 frequentemente implica desempenho e eficiência. Contudo, a ausência de integrações diretas e pré-construídas, como as encontradas na Evolution API para Chatwoot ou S3 10, significa que mais desenvolvimento customizado é necessário para equiparar o ecossistema da Evolution API, provavelmente através de webhooks. O desenvolvimento ativo do projeto 10 e a documentação clara 10 são pontos positivos. A limitação de executar o modo REST ou MCP, mas não ambos simultaneamente 10, é uma restrição atual a ser considerada.  
**4.2. wppconnect-server (por wppconnect-team)**

* **A. Visão Geral do Projeto:**  
  * Servidor de API RESTful baseado em Node.js, pronto para uso.21  
  * Utiliza a biblioteca WPPConnect, que por sua vez usa Puppeteer para interagir com o WhatsApp Web.4  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * Múltiplas sessões, envio de diversos tipos de mensagens, lista de contatos, gerenciamento de grupos, gerenciamento de produtos, webhooks.21  
  * Endpoints de API abrangentes documentados via Swagger/Postman.21  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Utiliza WPPConnect (baseado em Puppeteer). Não suporta a API Cloud Oficial do WhatsApp.21  
  * *Cenário de Integração:* Menciona explicitamente integrações com Chatwoot e S3 em sua configuração.21 Socket.io é usado internamente e para fluxos de eventos externos.21 Uma issue no GitHub solicita integração com Typebot.35 Nenhuma menção explícita a RabbitMQ, SQS, Dify, OpenAI além do que poderia ser construído customizadamente.21  
  * *Suporte Multiplataforma:* Nenhuma menção a suporte para Instagram/Messenger.21  
  * *Versões Leves/Especializadas:* Nenhuma versão "Lite" específica mencionada. "API pronta para uso" implica abrangência.21  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: Apache License 2.0.21  
  * Popularidade: Mais de 765 estrelas, mais de 480 forks (servidor).36 (A biblioteca wppconnect em si tem mais de 2.2k estrelas 28).  
  * Atividade de Desenvolvimento: Mantido ativamente, atualizações frequentes da biblioteca WPPConnect subjacente.4  
  * Documentação: Swagger, Postman docs, README extenso no GitHub.21 Canais da comunidade: Discord, Telegram, Grupo WhatsApp, YouTube.21  
* **E. Implantação e Facilidade de Uso:**  
  * Suporte a Docker (Dockerfile, docker-compose.yml).21  
  * Requer Node.js 16.14+.40  
  * Dependências: Puppeteer, Google Chrome.21  
  * Banco de Dados: Suporta MongoDB e Redis para gerenciamento de sessão/estado.21  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Depende do Puppeteer e do WhatsApp Web, portanto sujeito a mudanças pelo WhatsApp.4 O Puppeteer pode ser intensivo em recursos.42  
  * Problemas comuns: Erros de status de conexão, falhas no envio de mensagens, formato de envio de áudio.36 Problemas de tipagem na configuração do projeto.36  
* **G. Roadmap e Potencial Futuro:**  
  * Nenhum roadmap público formal encontrado além de melhorias no rastreador de issues.21 Solicitações de funcionalidades como integração com Typebot 35 sugerem evolução impulsionada pela comunidade.  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):** 21  
  * POST /api/:session/send-message com corpo JSON {"phone": "recipient\_phone", "message": "your\_message"} e autenticação Bearer token.

Este projeto oferece um conjunto abrangente de funcionalidades para automação do WhatsApp usando a biblioteca WPPConnect 21, que é baseada em Puppeteer. O uso de Puppeteer tem suas vantagens, como uma potencial melhoria na simulação da interação humana, mas também desvantagens, como um consumo de recursos mais elevado.42 Seu suporte integrado para Chatwoot, S3 e fluxos de eventos Socket.io 21 o torna um concorrente FOSS mais próximo da Evolution API em termos de integrações prontas para uso para esses serviços específicos. A comunidade ativa 21 e a documentação detalhada 21 são pontos fortes. No entanto, ainda carece da amplitude de outras integrações vistas na Evolution API (como Typebot, Dify, filas de mensagens dedicadas além de eventos Socket.io).  
**4.3. open-wa/wa-automate-nodejs (por OpenWA)**

* **A. Visão Geral do Projeto:**  
  * Biblioteca Node.js para controlar o WhatsApp, apresentada como "a ferramenta mais confiável para chatbots com funcionalidades avançadas".44  
  * Provavelmente utiliza whatsapp-web.js ou uma abordagem similar baseada em Puppeteer (as tags mencionam Puppeteer).45  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * Lista extensa de funções: manipulação de mensagens, mídia, contatos, grupos, suporte multi-dispositivo, atualização de QR, etc..44  
  * CLI para conversão instantânea em API ("Easy API").44  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Baseada em Puppeteer (inferido). Não suporta a API Cloud Oficial do WhatsApp.44  
  * *Cenário de Integração:* Menciona explicitamente integrações com Chatwoot, Node-RED, S3 e Twilio.49 Nenhuma menção explícita a Typebot, RabbitMQ, SQS, Dify, OpenAI.1 Socket.io não é mencionado para fluxos de eventos externos.  
  * *Suporte Multiplataforma:* Nenhuma menção a suporte para Instagram/Messenger.44  
  * *Versões Leves/Especializadas:* wa-decrypt-nodejs é uma biblioteca leve separada para decodificação de mídia deste projeto, para evitar a dependência total do Puppeteer para essa tarefa específica.45 Isso não é uma versão "Lite" da API, mas um utilitário.  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: Hippocratic \+ Do Not Harm Version 1.0.44  
  * Popularidade: Mais de 3.3k estrelas, mais de 632 forks.44  
  * Atividade de Desenvolvimento: Aparentemente ativo, com atualizações recentes mencionadas.45  
  * Documentação: Site oficial de documentação (docs.openwa.dev), Wiki do GitHub.49 Comunidade: Discord, opções de suporte comercial.44  
* **E. Implantação e Facilidade de Uso:**  
  * Suporte a Docker.59  
  * Implantação de código customizado Node.js.44  
  * Dados de sessão armazenados como session.data.json ou via variável de ambiente WA\_SESSION\_DATA.59 Nenhuma menção explícita a banco de dados para escalonamento de sessão além de arquivo/env.44  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Depende do WhatsApp Web não oficial, sujeito a mudanças. Docker em Apple Silicon (ARM) é problemático devido à falta de Google Chrome compatível com ARM.60  
  * Problemas comuns: Problemas de conexão, erros de API (SendLinkWithAutoPreview), erros de Docker, problemas com mp4AsSticker.63  
* **G. Roadmap e Potencial Futuro:**  
  * Possui um roadmap público na Wiki do GitHub.64 Planos para V5 incluem UI para Easy API, Zod para argumentos CLI.63  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):**  
  * client.sendText(message.from, '👋 Hello\!');.44

Este projeto possui uma grande comunidade 44 e um conjunto abrangente de funcionalidades. Sua CLI "Easy API" 44 e integrações explícitas com Node-RED e Twilio (juntamente com Chatwoot e S3) 49 oferecem caminhos de automação únicos, não comumente encontrados em outras alternativas. A biblioteca separada wa-decrypt-nodejs 56 demonstra uma preocupação com a modularidade. A existência de um roadmap público 64 indica um planejamento futuro estruturado. Contudo, a dependência do Puppeteer 48 implica preocupações semelhantes de recursos e estabilidade ao wppconnect-server. O problema de compatibilidade ARM para Docker 60 é uma limitação notável para alguns usuários.  
**4.4. fazer-ai/baileys-api (por fazer-ai)**

* **A. Visão Geral do Projeto:**  
  * Wrapper de API HTTP para a biblioteca Baileys, usando runtime Bun e framework Elysia.js.61  
  * Não é um servidor WhatsApp completo; foca em fornecer uma interface HTTP.61  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * Endpoints básicos de API: status, verificação de autenticação, gerenciamento de conexão (iniciar, atualizar presença, enviar mensagem, ler mensagens, desconectar), logout de todos os administradores.61  
  * Documentação Swagger disponível.61  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Utiliza Baileys. Não suporta a API Cloud Oficial do WhatsApp.61  
  * *Cenário de Integração:* Integração explícita com o fork deles do Chatwoot.61 Nenhuma menção explícita a Typebot, RabbitMQ, SQS, Dify, OpenAI, S3/Minio.1 Socket.io não mencionado para fluxos de eventos externos.  
  * *Suporte Multiplataforma:* Nenhuma menção a Instagram/Messenger.61  
  * *Versões Leves/Especializadas:* Descrito como um wrapper, não armazenando mensagens (além de credenciais de reconexão), implicando um design leve.61 Nenhuma versão "Lite" separada.  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: MIT.61  
  * Popularidade: 10 estrelas, 9 forks, 3 contribuidores.61 (Relativamente pequeno em comparação com outros).  
  * Atividade de Desenvolvimento: Lançamento mais recente v1.10.0 (Junho de 2025).61  
  * Documentação: README, Swagger.61 Nenhum fórum/Discord comunitário específico mencionado.61  
* **E. Implantação e Facilidade de Uso:**  
  * Runtime: Bun. Framework HTTP: Elysia.js.61  
  * Banco de Dados: Redis para armazenamento de sessão e gerenciamento de chaves de API.61  
  * Docker: docker-compose.coolify.yml fornecido para implantação no Coolify, adaptável para outros ambientes Docker.61  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Depende do Baileys, sujeito a mudanças do WhatsApp. Estágio inicial de desenvolvimento, muitas funcionalidades ainda estão sendo implementadas.61  
  * Nenhuma issue aberta no GitHub atualmente.70  
* **G. Roadmap e Potencial Futuro:**  
  * Roadmap: Adicionar suporte para mais funcionalidades do Baileys, adicionar testes unitários.61  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):**  
  * POST /connections/:phoneNumber/send-message. Payload específico via Swagger.

Este projeto é interessante por sua pilha tecnológica moderna (Bun, Elysia.js) 61 e sua filosofia de design clara e leve como um wrapper de API stateless. Sua integração direta com o fork próprio do Chatwoot 61 é uma vantagem para usuários desse ecossistema. A declaração explícita de não armazenar mensagens 61 reforça sua natureza leve, contrastando com soluções que podem oferecer mais funcionalidades, mas também mais sobrecarga. O tamanho menor da comunidade 61 e o estágio inicial de desenvolvimento 61 significam que pode ser menos maduro que outras opções, mas seu roadmap claro 61 demonstra direção.  
**4.5. PointerSoftware/Baileys-2025-Rest-API (por PointerSoftware)**

* **A. Visão Geral do Projeto:**  
  * Wrapper de API REST abrangente para Baileys, com suporte multi-sessão e um dashboard de gerenciamento.76  
  * Baseado em Node.js.76  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * API REST completa para operações do WhatsApp, multi-sessão, dashboard para monitoramento, gerenciamento de chaves de API/webhooks, estatísticas de uso.76  
  * Endpoints para mensagens, chats, grupos, contatos, webhooks.76  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Utiliza Baileys. Não suporta a API Cloud Oficial do WhatsApp.76  
  * *Cenário de Integração:* Suporte a WebSocket para atualizações ao vivo. Nenhuma menção explícita a Typebot, Chatwoot, RabbitMQ, SQS, Dify, OpenAI, S3/Minio.76  
  * *Suporte Multiplataforma:* Nenhuma menção a Instagram/Messenger.76  
  * *Versões Leves/Especializadas:* Nenhuma versão "Lite"; "abrangente" sugere funcionalidades completas.76  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: MIT.76  
  * Popularidade: Baixo número de estrelas/forks em um dos trechos 76, mas parece ser um projeto muito novo ("Baileys-2025").  
  * Atividade de Desenvolvimento: Apresentado como uma API pronta para 2025\.  
  * Documentação: Swagger/OpenAPI interativo, README, GitHub Discussions para suporte.76  
* **E. Implantação e Facilidade de Uso:**  
  * Node.js 20+ requerido.76  
  * Banco de Dados: PostgreSQL para persistência de sessão e mensagens.76  
  * Docker: Configuração com Docker Compose disponível.76  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Depende do Baileys. Desafios gerais de APIs não oficiais se aplicam. Nenhum problema específico listado nos trechos.78  
* **G. Roadmap e Potencial Futuro:**  
  * Nenhum roadmap formal, mas áreas de contribuição como documentação, correções de bugs, novas funcionalidades, traduções, melhorias de UI/UX para o dashboard são mencionadas.76  
* **H. Exemplo de Uso da API (Criar Sessão):** 76  
  * POST /api/sessions com JSON {"sessionId": "my-session-1", "usePairingCode": false} e header X-API-Key.

A inclusão de um dashboard de gerenciamento 76 é uma característica de usabilidade significativa, distinguindo-o de wrappers de API mais básicos. Seu uso de PostgreSQL para persistência 76 sugere uma abordagem mais robusta ao manuseio de dados. Embora seja baseado em Baileys como outros, o foco em uma "solução completa" 76, incluindo uma UI, o torna atraente. O "2025" em seu nome sugere que é moderno e visa estar atualizado. A falta de integrações explícitas além do núcleo do WhatsApp é uma desvantagem em comparação com a Evolution API.  
**4.6. Auties00/Cobalt (por Auties00)**

* **A. Visão Geral do Projeto:**  
  * Biblioteca Java e Kotlin para WhatsApp Web (Companion) e WhatsApp Mobile (Pessoal e Empresarial).80  
  * Visa ser uma API completa.  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * Funcionalidades extensas: gerenciamento de conexão, manipulação de eventos, consulta de dados, envio de diversos tipos de mensagens, gerenciamento de presença, alterações de estado de chat/grupo, 2FA (mobile), chamadas (mobile, sem áudio/vídeo), comunidades, newsletters/canais.80  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Implementação customizada para protocolos WhatsApp Web e Mobile. Não suporta a API Cloud Oficial do WhatsApp.80  
  * *Cenário de Integração:* Nenhuma menção explícita a Typebot, Chatwoot, Dify, OpenAI, RabbitMQ, SQS, S3/Minio, ou Socket.io para fluxos de eventos externos.80 É uma biblioteca, então as integrações seriam customizadas.  
  * *Suporte Multiplataforma:* Focado exclusivamente no WhatsApp (versões Web e Mobile).80  
  * *Versões Leves/Especializadas:* Nenhuma versão "Lite". "Completo" implica abrangência.80  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: MIT.80  
  * Popularidade: Mais de 752 estrelas, mais de 221 forks, 11 contribuidores.80  
  * Atividade de Desenvolvimento: Desenvolvido ativamente por mais de dois anos; mudanças que quebram compatibilidade esperadas até v1.0.80  
  * Documentação: Javadocs disponíveis, README.80 GitHub Discussions para interação com a comunidade.89  
* **E. Implantação e Facilidade de Uso:**  
  * Java 21+ requerido; compilação nativa GraalVM suportada.80  
  * Maven/Gradle para instalação.80  
  * Dados de sessão serializados para arquivos protobuf por padrão, serializador customizado possível.80  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Risco de banimento se usado para spam.80  
  * Mudanças que quebram compatibilidade entre lançamentos até v1.0.80  
  * Operações assíncronas requerem manuseio cuidadoso (CompletableFuture).80  
  * Atualizações de localização ao vivo não suportadas pelo WhatsApp multi-dispositivo.80  
  * Geração de miniaturas/duração de mídia depende de ffmpeg/ffprobe.80  
  * Problemas: Suporte Android, problemas de proxy, falhas de socket, bugs na criação de grupos.84  
* **G. Roadmap e Potencial Futuro:**  
  * Objetivo de alcançar v1.0 com um design de API estável.80 Nenhum roadmap público detalhado encontrado.  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):**  
  * whatsapp.sendMessage(info.chatJid(), "Automatic answer", info).80

Cobalt é único por sua base Java/Kotlin 80 e sua ambição de suportar tanto os protocolos WhatsApp Web quanto Mobile.80 Isso o torna um forte candidato para desenvolvedores no ecossistema JVM ou aqueles que precisam emular o comportamento do cliente móvel. A extensa lista de funcionalidades, incluindo comunidades e newsletters 80, é impressionante. No entanto, sendo uma biblioteca, requer mais configuração para exposição da API em comparação com projetos de servidor. O aviso sobre mudanças que quebram compatibilidade até a v1.0 80 é importante para usuários que buscam estabilidade. Sua falta de integrações pré-construídas 80 é um tema comum para alternativas FOSS focadas em bibliotecas.  
**4.7. nizarfadlan/baileys-api (por nizarfadlan)**

* **A. Visão Geral do Projeto:**  
  * API REST simples para WhatsApp com suporte multi-dispositivo, baseada em Baileys.91  
  * Projeto Node.js (TypeScript).91  
  * Continuado de @ookamiiixd/baileys-api.91  
* **B. Conjunto de Funcionalidades e Capacidades da API:**  
  * API REST básica para funções do WhatsApp.  
  * Suporta webhooks e Socket.io para eventos (do exemplo .env).91  
* **C. Comparação com a Evolution API:**  
  * *Abordagem da API WhatsApp:* Utiliza Baileys.  
  * *Cenário de Integração:* Menciona webhooks e Socket.io no .env.example 91, sugerindo capacidades de fluxo de eventos. Nenhuma menção explícita a Typebot, Chatwoot, Dify, OpenAI, RabbitMQ, SQS, S3/Minio.  
  * *Suporte Multiplataforma:* Nenhuma menção.  
  * *Versões Leves/Especializadas:* "API REST simples para WhatsApp" implica foco na funcionalidade principal.  
* **D. Credenciais FOSS e Saúde da Comunidade:**  
  * Licença: MIT.91  
  * Popularidade: Mais de 161 estrelas, mais de 114 forks.91  
  * Atividade de Desenvolvimento: README atualizado 2 meses antes do trecho.91  
  * Documentação: README fornece configuração e uso.91  
* **E. Implantação e Facilidade de Uso:**  
  * Node.js v18.19+ (v20+ recomendado).91  
  * Banco de Dados: Bancos de dados suportados pelo Prisma (MySQL, PostgreSQL testados).91  
  * Configuração envolve clonar, instalar dependências, configurar .env e executar migrações.91  
* **F. Estabilidade e Limitações Conhecidas:**  
  * Depende do Baileys. "Destinado apenas para fins de aprendizado, não use para spam".91  
* **G. Roadmap e Potencial Futuro:**  
  * Nenhum roadmap explícito mencionado. Projeto é uma continuação.  
* **H. Exemplo de Uso da API (Enviar Mensagem de Texto):**  
  * Endpoints de API específicos não detalhados nos trechos de visão geral, exigiriam verificação do código/documentação.

Este projeto oferece uma API REST direta baseada em Baileys com o benefício adicional do Prisma para interação com banco de dados (MySQL/PostgreSQL) 91, o que pode ser útil para armazenamento persistente além de simples arquivos de sessão. Sua continuação de um projeto anterior sugere algum nível de maturidade. O aviso de "fins de aprendizado" 91 é comum para APIs não oficiais, mas deve ser levado em consideração. Seu tamanho de comunidade 91 é respeitável. A inclusão de Socket.io em seu exemplo .env 91 é uma vantagem para necessidades de eventos em tempo real.

## **5\. Análise Comparativa e Perspectivas Estratégicas**

A escolha de uma alternativa FOSS à Evolution API requer uma análise cuidadosa das funcionalidades oferecidas em relação às necessidades específicas do projeto. Nenhuma solução FOSS individual repli\_ca perfeitamente a oferta abrangente da Evolution API, que combina acesso a API oficial e não oficial com uma vasta gama de integrações e uma visão multiplataforma.1 As alternativas FOSS, por sua natureza e limitações de recursos típicas, tendem a se especializar. Algumas focam em uma linguagem específica (Go 10; Java 80), outras na facilidade de uso com um painel de controle (PointerSoftware 76), e outras ainda em integrações específicas (wppconnect-server com Chatwoot/S3 21).  
Os usuários devem, portanto, estar cientes de que a seleção de uma alternativa FOSS provavelmente envolverá a renúncia a algumas conveniências ou à amplitude da Evolution API, particularmente o canal da API oficial e a extensa lista de integrações prontas para uso. A "melhor" alternativa será altamente dependente das prioridades específicas do usuário: preferência de linguagem, necessidade de integrações específicas (e disposição para construí-las, se ausentes), nível de estabilidade desejado (compreendendo que todas as APIs não oficiais carregam riscos) e suporte da comunidade.  
**Tabela 1: Matriz de Funcionalidades das 7 Principais Alternativas FOSS vs. Evolution API**

| Alternativa | Biblioteca Subjacente | Linguagem Principal | Suporte API Cloud Oficial | Integrações Chave (Chatwoot, S3, OpenAI, Typebot, Filas Msg, Socket.io Ext., Dify) | Multi-Plataforma (Insta/Msg) | Versão Lite | Licença FOSS |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Evolution API (Referência)** | Baileys / API Cloud | TypeScript | Sim | Chatwoot, S3/Minio, OpenAI, Typebot, RabbitMQ/SQS, Socket.io, Dify | Planejado | Sim | AGPL-3.0 |
| go-whatsapp-web-multidevice | whatsmeow | Go | Não | Webhooks (Extensível); MCP para IA | Não | Não | MIT |
| wppconnect-server | WPPConnect (Puppeteer) | TypeScript | Não | Chatwoot, S3, Socket.io (Extensível); Typebot (solicitado) | Não | Não | Apache-2.0 |
| open-wa/wa-automate-nodejs | Puppeteer (provável) | TypeScript | Não | Chatwoot, S3, Node-RED, Twilio (Extensível) | Não | Não (util. separado) | Hippocratic+ |
| fazer-ai/baileys-api | Baileys | TypeScript (Bun) | Não | Chatwoot (fork) (Extensível) | Não | Não | MIT |
| PointerSoftware/Baileys-2025 | Baileys | TypeScript | Não | WebSockets (Extensível) | Não | Não | MIT |
| Auties00/Cobalt | Implementação Customizada | Java/Kotlin | Não | Extensível (biblioteca) | Não | Não | MIT |
| nizarfadlan/baileys-api | Baileys | TypeScript | Não | Webhooks, Socket.io (Extensível) | Não | Não | MIT |

*Nota sobre Integrações Chave: "Extensível" indica que, embora não haja integrações diretas nomeadas para todos os itens, a arquitetura (ex: webhooks, natureza de biblioteca) permite que o usuário as construa.*  
Esta tabela visa fornecer uma comparação direta, destacando rapidamente quais alternativas se aproximam mais das capacidades de integração da Evolution API e conformidade FOSS.  
**Tabela 2: Comparação das Bibliotecas WhatsApp Subjacentes**

| Biblioteca | Tipo | Linguagem Principal | Características Chave | Frequência de Atualização | Atividade Comunitária Notável |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Baileys | WebSocket | TypeScript/JS | Leve, popular, rápida adaptação | Alta | Muito Grande 5 |
| whatsmeow | WebSocket | Go | Eficiente, bom para Go | Média-Alta | Ativa 2 |
| whatsapp-web.js | Puppeteer | JavaScript | Simula navegador, pode ser mais robusto a certas mudanças | Média | Muito Grande 3 |
| WPPConnect | Puppeteer | TypeScript/JS | Foco em exportar funções do WhatsApp Web para Node | Média-Alta | Ativa 4 |
| Implementação Cobalt | WebSocket/Protocolo Nat. | Java/Kotlin | Suporte Web e Mobile, controle granular | Média (até v1.0) | Ativa 80 |

Compreender a tecnologia central que impulsiona cada API é fundamental, pois influencia profundamente a estabilidade, o desempenho e os requisitos de recursos. Diferentes bibliotecas têm históricos distintos na rapidez com que se adaptam às mudanças do WhatsApp Web, um fator crucial na avaliação de risco.6  
**Discussão sobre Trade-offs:**

* **Funcionalidade vs. Estabilidade:** APIs não oficiais oferecem rica funcionalidade mas são propensas a quebrar com atualizações do WhatsApp.6 A Evolution API mitiga isso parcialmente com suporte à API oficial, uma característica que as alternativas FOSS não possuem.  
* **Facilidade de Uso vs. Controle:** Servidores pré-construídos (como wppconnect-server) são mais fáceis de configurar do que bibliotecas (como Auties00/Cobalt), mas oferecem menos controle granular.  
* **Amplitude de Integração vs. Desenvolvimento Customizado:** A Evolution API possui muitas integrações incorporadas.1 A maioria das alternativas FOSS requer mais trabalho customizado para integrações similares, dependendo de webhooks ou codificação direta.10

Considerações para Viabilidade a Longo Prazo e Suporte Comunitário:  
Manutenção ativa, rastreamento responsivo de issues e uma comunidade considerável e prestativa são cruciais para a longevidade de projetos FOSS, especialmente aqueles que lidam com APIs não oficiais.2 Projetos com roadmaps claros (mesmo que informais) e múltiplos contribuidores ativos tendem a ser mais resilientes.

## **6\. Recomendações e Conclusão**

A seleção da alternativa FOSS mais adequada à Evolution API depende intrinsecamente das prioridades e do contexto técnico de cada projeto. Não existe uma solução única que espelhe completamente a combinação de API oficial, API não oficial e o vasto leque de integrações da Evolution API.  
**Orientações Baseadas em Necessidades Específicas:**

* **Para desenvolvedores Go que necessitam de alto desempenho e potencial integração com IA via MCP:** go-whatsapp-web-multidevice. Esteja preparado para menos integrações prontas para uso. Sua base em whatsmeow oferece uma alternativa robusta ao ecossistema Baileys/Puppeteer.  
* **Para desenvolvedores Node.js que desejam um servidor rico em funcionalidades com algumas integrações chave (Chatwoot, S3) e boa comunidade:** wppconnect-server. Compreenda as implicações de recursos do Puppeteer. Seu fluxo de eventos Socket.io é um diferencial.  
* **Para uma grande comunidade Node.js, ferramentas CLI e algumas integrações únicas (Node-RED, Twilio):** open-wa/wa-automate-nodejs. Esteja ciente de sua licença e base em Puppeteer. A existência de um roadmap público é um sinal positivo de planejamento.  
* **Para um wrapper Baileys moderno e leve em Node.js (Bun) com integração Chatwoot:** fazer-ai/baileys-api. Adequado se você valoriza uma abordagem minimalista e ferramentas JS modernas. Seu estágio inicial de desenvolvimento requer atenção.  
* **Para uma API baseada em Baileys com um dashboard de gerenciamento e persistência PostgreSQL:** PointerSoftware/Baileys-2025-Rest-API. Bom para facilidade de uso no gerenciamento de sessões e uma abordagem de dados mais estruturada.  
* **Para desenvolvedores Java/Kotlin que necessitam de interação profunda com WhatsApp (Web & Mobile) e uma biblioteca rica:** Auties00/Cobalt. Requer a construção de seu próprio servidor de API sobre a biblioteca. Sua capacidade de interagir com o protocolo móvel é um diferencial significativo.  
* **Para uma API REST Baileys simples, com suporte a banco de dados:** nizarfadlan/baileys-api. Bom para exposição direta do Baileys com persistência via Prisma.

**Considerações Gerais para Todas as APIs Não Oficiais:**

* **Risco de Bloqueio:** Sempre presente. Use com responsabilidade, evite spam, considere usar números dedicados.7 A estabilidade dessas bibliotecas é um fator crucial, com relatos de que tanto whatsmeow quanto Baileys podem ser alvo de sistemas de detecção do WhatsApp.8  
* **Atualizações do WhatsApp:** Esteja preparado para quebras periódicas e a necessidade de atualizar a biblioteca/servidor. Escolha projetos com manutenção ativa.4  
* **Termos de Serviço:** Compreenda os Termos de Serviço do WhatsApp em relação ao uso de API não oficial.94

**Considerações Finais:**  
O cenário de APIs FOSS para WhatsApp oferece ferramentas poderosas, mas elas vêm com desafios inerentes em comparação com soluções oficiais e pagas. A Evolution API estabelece um padrão elevado com sua abordagem híbrida e integrações ricas. As alternativas FOSS podem atender a muitas necessidades, especialmente para acesso à API não oficial, mas os usuários devem estar preparados para um gerenciamento mais prático e potencial trabalho de integração customizado.  
A decisão final não se resume apenas a funcionalidades, mas também a alinhar-se com a filosofia de um projeto, sua comunidade e a estabilidade de sua tecnologia subjacente. Recomenda-se a prototipagem com as opções mais promissoras para avaliar o ajuste e a tolerância ao risco antes de um comprometimento em larga escala. A "melhor" escolha é altamente dependente da expertise técnica do usuário, dos requisitos do projeto, da tolerância ao risco e do nível desejado de suporte comunitário. O tema recorrente da instabilidade da API não oficial 6 deve ser a nota de cautela final.

#### **Referências citadas**

1. Evolution API is an open-source WhatsApp integration API \- GitHub, acessado em junho 7, 2025, [https://github.com/EvolutionAPI/evolution-api](https://github.com/EvolutionAPI/evolution-api)  
2. tulir/whatsmeow: Go library for the WhatsApp web multidevice API \- GitHub, acessado em junho 7, 2025, [https://github.com/tulir/whatsmeow](https://github.com/tulir/whatsmeow)  
3. pedroslopez/whatsapp-web.js: A WhatsApp client library for NodeJS that connects through the WhatsApp Web browser app \- GitHub, acessado em junho 7, 2025, [https://github.com/pedroslopez/whatsapp-web.js/](https://github.com/pedroslopez/whatsapp-web.js/)  
4. WPPConnect patch release: v1.34.2, acessado em junho 7, 2025, [https://wppconnect-team.github.io/blog/wppconnect/v1.34.2/](https://wppconnect-team.github.io/blog/wppconnect/v1.34.2/)  
5. whiskeysockets/baileys \- NPM, acessado em junho 7, 2025, [https://www.npmjs.com/package/@whiskeysockets/baileys](https://www.npmjs.com/package/@whiskeysockets/baileys)  
6. How reliable is https://github.com/tulir/whatsmeow : r/automation \- Reddit, acessado em junho 7, 2025, [https://www.reddit.com/r/automation/comments/1jeklj1/how\_reliable\_is\_httpsgithubcomtulirwhatsmeow/](https://www.reddit.com/r/automation/comments/1jeklj1/how_reliable_is_httpsgithubcomtulirwhatsmeow/)  
7. What is the best option for integrating with WhatsApp: Official API, Provider, or whatsapp-web.js? : r/brdev \- Reddit, acessado em junho 7, 2025, [https://www.reddit.com/r/brdev/comments/1iq3v2i/qual\_a\_melhor\_op%C3%A7%C3%A3o\_para\_integrar\_com\_whatsapp/?tl=en](https://www.reddit.com/r/brdev/comments/1iq3v2i/qual_a_melhor_op%C3%A7%C3%A3o_para_integrar_com_whatsapp/?tl=en)  
8. ️ "Your account may be at risk" warning affecting clients using WhatsMeow (also reported with Baileys) · Issue \#810 \- GitHub, acessado em junho 7, 2025, [https://github.com/tulir/whatsmeow/issues/810](https://github.com/tulir/whatsmeow/issues/810)  
9. Best Way to Integrate WhatsApp into a SaaS: Official API, Third-Party Providers, or whatsapp-web.js? : r/microsaas \- Reddit, acessado em junho 7, 2025, [https://www.reddit.com/r/microsaas/comments/1iq443p/best\_way\_to\_integrate\_whatsapp\_into\_a\_saas/](https://www.reddit.com/r/microsaas/comments/1iq443p/best_way_to_integrate_whatsapp_into_a_saas/)  
10. aldinokemal/go-whatsapp-web-multidevice: API for Whatsapp Web Multi Device Version, Support UI, Webhook & MCP \- GitHub, acessado em junho 7, 2025, [https://github.com/aldinokemal/go-whatsapp-web-multidevice](https://github.com/aldinokemal/go-whatsapp-web-multidevice)  
11. aldinokemal2104/go-whatsapp-web-multidevice \- Docker Image, acessado em junho 7, 2025, [https://hub.docker.com/r/aldinokemal2104/go-whatsapp-web-multidevice](https://hub.docker.com/r/aldinokemal2104/go-whatsapp-web-multidevice)  
12. Introduction | go-whatsapp-web-multidevice API documentation \- Bump.sh, acessado em junho 7, 2025, [https://bump.sh/aldinokemal/doc/go-whatsapp-web-multidevice/](https://bump.sh/aldinokemal/doc/go-whatsapp-web-multidevice/)  
13. Create a Self-Hosted WhatsApp Gateway with go-whatsapp-web-multidevice, acessado em junho 7, 2025, [https://imanudin.net/2025/05/14/create-a-self-hosted-whatsapp-gateway-with-go-whatsapp-web-multidevice/](https://imanudin.net/2025/05/14/create-a-self-hosted-whatsapp-gateway-with-go-whatsapp-web-multidevice/)  
14. Issues · aldinokemal/go-whatsapp-web-multidevice \- GitHub, acessado em junho 7, 2025, [https://github.com/aldinokemal/go-whatsapp-web-multidevice/issues](https://github.com/aldinokemal/go-whatsapp-web-multidevice/issues)  
15. aldinokemal go-whatsapp-web-multidevice · Discussions \- GitHub, acessado em junho 7, 2025, [https://github.com/aldinokemal/go-whatsapp-web-multidevice/discussions](https://github.com/aldinokemal/go-whatsapp-web-multidevice/discussions)  
16. aldinokemal/sdk-php-whatsapp-web-multidevice \- Packagist, acessado em junho 7, 2025, [https://packagist.org/packages/aldinokemal/sdk-php-whatsapp-web-multidevice](https://packagist.org/packages/aldinokemal/sdk-php-whatsapp-web-multidevice)  
17. some-stars | 我的star列表，每天自动更新 \- GitHub Pages, acessado em junho 7, 2025, [https://rcy1314.github.io/some-stars/](https://rcy1314.github.io/some-stars/)  
18. Image Layer Details \- aldinokemal2104/go-whatsapp-web-multidevice:latest | Docker Hub, acessado em junho 7, 2025, [https://hub.docker.com/layers/aldinokemal2104/go-whatsapp-web-multidevice/latest/images/sha256-89f753d28738b152e4d2707fc5959fec8d90f61305b10cef3fa5ae3bc9b0cd32?context=explore](https://hub.docker.com/layers/aldinokemal2104/go-whatsapp-web-multidevice/latest/images/sha256-89f753d28738b152e4d2707fc5959fec8d90f61305b10cef3fa5ae3bc9b0cd32?context=explore)  
19. Releases · aldinokemal/go-whatsapp-web-multidevice \- GitHub, acessado em junho 7, 2025, [https://github.com/aldinokemal/go-whatsapp-web-multidevice/releases](https://github.com/aldinokemal/go-whatsapp-web-multidevice/releases)  
20. have suport for postgres? · aldinokemal go-whatsapp-web-multidevice · Discussion \#236, acessado em junho 7, 2025, [https://github.com/aldinokemal/go-whatsapp-web-multidevice/discussions/236](https://github.com/aldinokemal/go-whatsapp-web-multidevice/discussions/236)  
21. wppconnect-team/wppconnect-server: Wppconnect Server ... \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team/wppconnect-server](https://github.com/wppconnect-team/wppconnect-server)  
22. whatsapp-bot · GitHub Topics, acessado em junho 7, 2025, [https://github.com/topics/whatsapp-bot](https://github.com/topics/whatsapp-bot)  
23. wppconnect-team \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team](https://github.com/wppconnect-team)  
24. wppconnect-server, acessado em junho 7, 2025, [https://wppconnect-team.github.io/docs/wppconnect-server](https://wppconnect-team.github.io/docs/wppconnect-server)  
25. Introduction | WPPConnect, acessado em junho 7, 2025, [https://wppconnect-team.github.io/docs/projects/wppserver/introduction/](https://wppconnect-team.github.io/docs/projects/wppserver/introduction/)  
26. wppconnect-team/wppconnect \- NPM, acessado em junho 7, 2025, [https://www.npmjs.com/package/@wppconnect-team/wppconnect](https://www.npmjs.com/package/@wppconnect-team/wppconnect)  
27. Choosing the best project \- WPPConnect, acessado em junho 7, 2025, [https://wppconnect-team.github.io/docs/choosing-the-best-project-of-wppconnect-team/](https://wppconnect-team.github.io/docs/choosing-the-best-project-of-wppconnect-team/)  
28. WPPConnect is an open source project developed by the JavaScript community with the aim of exporting functions from WhatsApp Web to the node, which can be used to support the creation of any interaction, such as customer service, media sending, intelligence recognition based on phrases artificial and many other things, use your imagination \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team/wppconnect](https://github.com/wppconnect-team/wppconnect)  
29. WPPConnect download | SourceForge.net, acessado em junho 7, 2025, [https://sourceforge.net/projects/wppconnect.mirror/](https://sourceforge.net/projects/wppconnect.mirror/)  
30. wppconnect-server | WPPConnect, acessado em junho 7, 2025, [https://wppconnect-team.github.io/docs/wppconnect-server/](https://wppconnect-team.github.io/docs/wppconnect-server/)  
31. npm packages \- whatsapp bot \- Socket.dev, acessado em junho 7, 2025, [https://socket.dev/search?e=npm\&q=whatsapp+bot\&page=1](https://socket.dev/search?e=npm&q=whatsapp+bot&page=1)  
32. Introduction | WPPConnect, acessado em junho 7, 2025, [https://wppconnect-team.github.io/docs/](https://wppconnect-team.github.io/docs/)  
33. Enumeration SocketStream \- WPPConnect, acessado em junho 7, 2025, [https://wppconnect.io/wppconnect/enums/SocketStream.html](https://wppconnect.io/wppconnect/enums/SocketStream.html)  
34. Server API \- Socket.IO, acessado em junho 7, 2025, [https://socket.io/docs/v4/server-api/](https://socket.io/docs/v4/server-api/)  
35. Integração Nativa TypeBot · Issue \#1656 · wppconnect-team/wppconnect-server \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team/wppconnect-server/issues/1656](https://github.com/wppconnect-team/wppconnect-server/issues/1656)  
36. Issues · wppconnect-team/wppconnect-server \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team/wppconnect-server/issues](https://github.com/wppconnect-team/wppconnect-server/issues)  
37. acessado em dezembro 31, 1969, [https://github.com/wppconnect-team/wppconnect-server/issues?q=is%3Aissue+Typebot+OR+RabbitMQ+OR+SQS+OR+Socket.io+OR+Dify+OR+OpenAI](https://github.com/wppconnect-team/wppconnect-server/issues?q=is:issue+Typebot+OR+RabbitMQ+OR+SQS+OR+Socket.io+OR+Dify+OR+OpenAI)  
38. wppconnect-team/wppconnect (Raised $70.00) \- Issuehunt, acessado em junho 7, 2025, [https://issuehunt.io/r/wppconnect-team/wppconnect/](https://issuehunt.io/r/wppconnect-team/wppconnect/)  
39. @wppconnect-team/wppconnect \- v1.37.2, acessado em junho 7, 2025, [https://wppconnect.io/wppconnect/](https://wppconnect.io/wppconnect/)  
40. Installation \- WPPConnect, acessado em junho 7, 2025, [https://wppconnect.io/docs/projects/wppserver/installation/](https://wppconnect.io/docs/projects/wppserver/installation/)  
41. wppconnect-server/LICENSE at main \- GitHub, acessado em junho 7, 2025, [https://github.com/wppconnect-team/wppconnect-server/blob/main/LICENSE](https://github.com/wppconnect-team/wppconnect-server/blob/main/LICENSE)  
42. Sometimes whatsapp-web.js hangs and stops receiving messages · Issue \#1567 \- GitHub, acessado em junho 7, 2025, [https://github.com/pedroslopez/whatsapp-web.js/issues/1567](https://github.com/pedroslopez/whatsapp-web.js/issues/1567)  
43. acessado em dezembro 31, 1969, [https://github.com/wppconnect-team/wppconnect-server/issues?q=is%3Aissue+roadmap+OR+%22future+plans%22](https://github.com/wppconnect-team/wppconnect-server/issues?q=is:issue+roadmap+OR+%22future+plans%22)  
44. open-wa/wa-automate-nodejs: The most reliable tool for ... \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-automate-nodejs](https://github.com/open-wa/wa-automate-nodejs)  
45. open-wa \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa](https://github.com/open-wa)  
46. open-wa/wa-automate \- NPM, acessado em junho 7, 2025, [https://www.npmjs.com/package/@open-wa/wa-automate](https://www.npmjs.com/package/@open-wa/wa-automate)  
47. wa-automate-nodejs download | SourceForge.net, acessado em junho 7, 2025, [https://sourceforge.net/projects/wa-automate-nodejs.mirror/](https://sourceforge.net/projects/wa-automate-nodejs.mirror/)  
48. @open-wa/wa-automate \- Codesandbox, acessado em junho 7, 2025, [https://codesandbox.io/p/sandbox/upbeat-field-zcxgt](https://codesandbox.io/p/sandbox/upbeat-field-zcxgt)  
49. open-wa/wa-automate-nodejs, acessado em junho 7, 2025, [https://docs.openwa.dev/](https://docs.openwa.dev/)  
50. Introduction | @open-wa/wa-automate-nodejs, acessado em junho 7, 2025, [https://docs.openwa.dev/docs/intro](https://docs.openwa.dev/docs/intro)  
51. How to Install Open-WA and Integrate with Node-RED for WhatsApp Automation \- YouTube, acessado em junho 7, 2025, [https://www.youtube.com/watch?v=Z9GEg9RX8IY](https://www.youtube.com/watch?v=Z9GEg9RX8IY)  
52. acessado em dezembro 31, 1969, [https://docs.openwa.dev/docs/integrations/overview](https://docs.openwa.dev/docs/integrations/overview)  
53. Best Open Source JavaScript Chat Software \- SourceForge, acessado em junho 7, 2025, [https://sourceforge.net/directory/chat/javascript/](https://sourceforge.net/directory/chat/javascript/)  
54. I built a comprehensive Instagram \+ Messenger chatbot with n8n (with ZERO coding experience) \- and I have NOTHING to sell\! \- Reddit, acessado em junho 7, 2025, [https://www.reddit.com/r/n8n/comments/1k4u0c4/i\_built\_a\_comprehensive\_instagram\_messenger/](https://www.reddit.com/r/n8n/comments/1k4u0c4/i_built_a_comprehensive_instagram_messenger/)  
55. whatsapp bulk message free download \- SourceForge, acessado em junho 7, 2025, [https://sourceforge.net/directory/?q=whatsapp+bulk+message](https://sourceforge.net/directory/?q=whatsapp+bulk+message)  
56. open-wa/wa-decrypt-nodejs: A lightweight implementation of the wa-automate-nodejs media decryption code for NodeJS \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-decrypt-nodejs](https://github.com/open-wa/wa-decrypt-nodejs)  
57. wa-automate-nodejs/LICENSE.md at master \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-automate-nodejs/blob/master/LICENSE.md](https://github.com/open-wa/wa-automate-nodejs/blob/master/LICENSE.md)  
58. open-wa wa-automate-nodejs · Discussions \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-automate-nodejs/discussions](https://github.com/open-wa/wa-automate-nodejs/discussions)  
59. openwa/wa-automate \- Docker Image, acessado em junho 7, 2025, [https://hub.docker.com/r/openwa/wa-automate](https://hub.docker.com/r/openwa/wa-automate)  
60. Get started with wa-automate via Docker, acessado em junho 7, 2025, [https://docs.openwa.dev/docs/get-started/docker](https://docs.openwa.dev/docs/get-started/docker)  
61. fazer-ai/baileys-api: Baileys API for WhatsApp. \- GitHub, acessado em junho 7, 2025, [https://github.com/fazer-ai/baileys-api](https://github.com/fazer-ai/baileys-api)  
62. acessado em dezembro 31, 1969, [https://github.com/open-wa/wa-automate-nodejs/issues?q=is%3Aissue+Kubernetes+OR+scaling+OR+performance+OR+database+OR+security](https://github.com/open-wa/wa-automate-nodejs/issues?q=is:issue+Kubernetes+OR+scaling+OR+performance+OR+database+OR+security)  
63. Issues · open-wa/wa-automate-nodejs \- GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-automate-nodejs/issues](https://github.com/open-wa/wa-automate-nodejs/issues)  
64. Home · open-wa/wa-automate-nodejs Wiki · GitHub, acessado em junho 7, 2025, [https://github.com/open-wa/wa-automate-nodejs/wiki](https://github.com/open-wa/wa-automate-nodejs/wiki)  
65. fazer.ai \- GitHub, acessado em junho 7, 2025, [https://github.com/fazer-ai](https://github.com/fazer-ai)  
66. ChatWoot \+ Facebook \+ Instagram \+ Telegram \[ GUIA COMPLETO \] \- YouTube, acessado em junho 7, 2025, [https://www.youtube.com/watch?v=XYdZjfQir2o](https://www.youtube.com/watch?v=XYdZjfQir2o)  
67. Instagram Messenger API \- Two-Way Conversations \- Gupshup, acessado em junho 7, 2025, [https://www.gupshup.io/resources/blog/messenger-api-for-instagram-a-game-changer-for-brands](https://www.gupshup.io/resources/blog/messenger-api-for-instagram-a-game-changer-for-brands)  
68. WhiskeySockets/Baileys: Lightweight full-featured typescript/javascript WhatsApp Web API \- GitHub, acessado em junho 7, 2025, [https://github.com/WhiskeySockets/Baileys](https://github.com/WhiskeySockets/Baileys)  
69. All books on bookdown.org, acessado em junho 7, 2025, [https://bookdown.org/home/archive/](https://bookdown.org/home/archive/)  
70. Issues · fazer-ai/baileys-api \- GitHub, acessado em junho 7, 2025, [https://github.com/fazer-ai/baileys-api/issues](https://github.com/fazer-ai/baileys-api/issues)  
71. Prekey Pogo: Investigating Security and Privacy Issues in WhatsApp's Handshake Mechanism \- arXiv, acessado em junho 7, 2025, [https://arxiv.org/html/2504.07323v1](https://arxiv.org/html/2504.07323v1)  
72. Case Studies \- Cengage, acessado em junho 7, 2025, [https://assets.cengage.com/gale/tlist/additional/gbib\_rt.xlsx](https://assets.cengage.com/gale/tlist/additional/gbib_rt.xlsx)  
73. Exhibit A | Muslim Advocates, acessado em junho 7, 2025, [https://muslimadvocates.org/wp-content/uploads/2021/12/Facebook-2021.11.17-Exhibits-to-MAs-Opposition-to-Facebooks-Anti-SLAPP-Motion.-pdf.pdf](https://muslimadvocates.org/wp-content/uploads/2021/12/Facebook-2021.11.17-Exhibits-to-MAs-Opposition-to-Facebooks-Anti-SLAPP-Motion.-pdf.pdf)  
74. fazer-ai/baileys-api: Baileys API for WhatsApp. \- GitHub, acessado em junho 7, 2025, [https://github.com/fazer-ai/baileys-api\#roadmap-work-in-progress](https://github.com/fazer-ai/baileys-api#roadmap-work-in-progress)  
75. Dora AI \- Sites beyond imagination, one prompt away., acessado em junho 7, 2025, [https://www.dora.run/ai](https://www.dora.run/ai)  
76. PointerSoftware/Baileys-2025-Rest-API: A comprehensive ... \- GitHub, acessado em junho 7, 2025, [https://github.com/PointerSoftware/Baileys-2025-Rest-API](https://github.com/PointerSoftware/Baileys-2025-Rest-API)  
77. WhatsApp Cloud API: A Step-by-Step Guide for Businesses in 2025 \- Wappbiz, acessado em junho 7, 2025, [https://www.wappbiz.com/blogs/whatsapp-cloud-api/](https://www.wappbiz.com/blogs/whatsapp-cloud-api/)  
78. Riscv Spec | PDF | 64 Bit Computing | Digital Technology \- Scribd, acessado em junho 7, 2025, [https://www.scribd.com/document/427173736/Riscv-Spec](https://www.scribd.com/document/427173736/Riscv-Spec)  
79. PointerSoftware/Baileys-2025-Rest-API: A comprehensive ... \- GitHub, acessado em junho 7, 2025, [https://github.com/PointerSoftware/Baileys-2025-Rest-API\#roadmap](https://github.com/PointerSoftware/Baileys-2025-Rest-API#roadmap)  
80. Auties00/Cobalt: Standalone unofficial fully-featured Whatsapp Web and Mobile API for Java and Kotlin \- GitHub, acessado em junho 7, 2025, [https://github.com/Auties00/Cobalt](https://github.com/Auties00/Cobalt)  
81. Tips to Resolve Common Issues in WhatsApp Cloud API \- Sobot, acessado em junho 7, 2025, [https://www.sobot.io/article/resolve-whatsapp-cloud-api-issues/](https://www.sobot.io/article/resolve-whatsapp-cloud-api-issues/)  
82. WhatsApp Cloud API \- Meta for Developers \- Facebook, acessado em junho 7, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/](https://developers.facebook.com/docs/whatsapp/cloud-api/)  
83. Overly complicated system · Auties00 Cobalt · Discussion \#400 \- GitHub, acessado em junho 7, 2025, [https://github.com/Auties00/Cobalt/discussions/400](https://github.com/Auties00/Cobalt/discussions/400)  
84. Issues · Auties00/Cobalt \- GitHub, acessado em junho 7, 2025, [https://github.com/Auties00/Cobalt/issues](https://github.com/Auties00/Cobalt/issues)  
85. Auties00 Cobalt · Discussions \- GitHub, acessado em junho 7, 2025, [https://github.com/Auties00/Cobalt/discussions](https://github.com/Auties00/Cobalt/discussions)  
86. cobalt \- com.github.auties00 \- Maven Central \- Sonatype, acessado em junho 7, 2025, [https://central.sonatype.com/artifact/com.github.auties00/cobalt](https://central.sonatype.com/artifact/com.github.auties00/cobalt)  
87. cobalt 0.0.9 javadoc (com.github.auties00), acessado em junho 7, 2025, [https://javadoc.io/doc/com.github.auties00/cobalt/latest/index.html](https://javadoc.io/doc/com.github.auties00/cobalt/latest/index.html)  
88. arXiv:2504.07323v1 \[cs.CR\] 9 Apr 2025, acessado em junho 7, 2025, [https://arxiv.org/pdf/2504.07323](https://arxiv.org/pdf/2504.07323)  
89. Auties00 Cobalt General · Discussions \- GitHub, acessado em junho 7, 2025, [https://github.com/Auties00/Cobalt/discussions/categories/general](https://github.com/Auties00/Cobalt/discussions/categories/general)  
90. com.github.auties00:cobalt:0.0.3 \- Maven Central, acessado em junho 7, 2025, [https://central.sonatype.com/artifact/com.github.auties00/cobalt/0.0.3](https://central.sonatype.com/artifact/com.github.auties00/cobalt/0.0.3)  
91. nizarfadlan/baileys-api: Simple WhatsApp REST API with multiple device support \- GitHub, acessado em junho 7, 2025, [https://github.com/nizarfadlan/baileys-api](https://github.com/nizarfadlan/baileys-api)  
92. WEBJS | WAHA \- Devlikeapro, acessado em junho 7, 2025, [https://waha.devlike.pro/docs/engines/webjs/](https://waha.devlike.pro/docs/engines/webjs/)  
93. OSS Report: WhiskeySockets/Baileys \- Dispatch AI, acessado em junho 7, 2025, [https://thedispatch.ai/reports/2468/](https://thedispatch.ai/reports/2468/)  
94. How WhatsApp Business API Works: Official vs Unofficial \- No-Code Start-Up, acessado em junho 7, 2025, [https://nocodestartup.io/en/how-does-the-official-vs-unofficial-whatsapp-business-api-work/](https://nocodestartup.io/en/how-does-the-official-vs-unofficial-whatsapp-business-api-work/)  
95. @open-wa/wa-automate-types-only | Yarn \- Yarn 1, acessado em junho 7, 2025, [https://classic.yarnpkg.com/en/package/@open-wa/wa-automate-types-only](https://classic.yarnpkg.com/en/package/@open-wa/wa-automate-types-only)