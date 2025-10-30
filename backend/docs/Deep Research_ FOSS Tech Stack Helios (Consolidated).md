

# **Projeto Helios: Um Plano Estratégico para uma Arquitetura Nativa em Nuvem e Impulsionada por FOSS**

## **Resumo Executivo**

Este documento apresenta um plano estratégico abrangente para a arquitetura técnica do Projeto Helios. O objetivo é fornecer um roteiro detalhado para a seleção e implementação de uma pilha de tecnologia baseada em Software Livre e de Código Aberto (FOSS), projetada para escalabilidade, desempenho e segurança. A análise culmina em um conjunto de recomendações acionáveis e fundamentadas em evidências, destinadas a orientar as decisões de arquitetura desde o Produto Mínimo Viável (MVP) até a escala de produção.  
A arquitetura proposta é fundamentada em um modelo de dados híbrido, que combina a robustez transacional de um banco de dados relacional com a capacidade de análise de relacionamento de um banco de dados de grafos. A recomendação central é utilizar o **PostgreSQL** como o sistema de registro (fonte da verdade) para garantir a integridade dos dados e o **Neo4j** como uma camada especializada para consultas de grafos complexas. Os dois sistemas serão sincronizados em tempo real através de um pipeline de Captura de Dados de Mudança (CDC) utilizando **Debezium** e **Apache Kafka**. Esta abordagem implementa o princípio de "Fonte Única da Verdade", inspirado em ferramentas de design colaborativo modernas como o Artifact, garantindo que todos os stakeholders operem com dados consistentes e versionados.  
Para a camada de aplicação, a pilha recomendada consiste em:

* **Backend:** **FastAPI**, um framework Python de alto desempenho, escolhido por sua arquitetura assíncrona, segurança de tipos com Pydantic e ecossistema robusto para APIs de dados intensivos.  
* **Frontend:** **React**, selecionado por seu ecossistema maduro, vasta disponibilidade de talentos e ferramentas robustas, com um padrão de gerenciamento de estado moderno que separa o estado do servidor (**React Query**) do estado do cliente (**Zustand**).

O ciclo de vida de desenvolvimento será gerenciado usando a metodologia **Kanban** para máxima flexibilidade, dentro de uma estrutura de monorepositório poliglota (Python e TypeScript) gerenciada pela ferramenta de construção **Pants**. A automação de CI/CD será implementada com **GitLab CI**, e a infraestrutura como código (IaC) será gerenciada com **Terraform** para orquestração e **Ansible** para configuração. A segurança é um pilar transversal, com práticas recomendadas da OWASP integradas em todas as camadas, desde o endurecimento de contêineres **Docker** até a mitigação de vulnerabilidades de API e o manuseio seguro de tokens JWT.  
Finalmente, o relatório apresenta um plano de implementação em fases, uma análise de custos inicial para o MVP em provedores de nuvem como DigitalOcean e AWS Lightsail, e uma avaliação do mercado de talentos no Brasil para as tecnologias selecionadas. Este plano estratégico visa equipar o Projeto Helios com uma fundação técnica que não é apenas poderosa, mas também pragmática e alinhada com as realidades de orçamento, cronograma e disponibilidade de talentos.  
---

## **Seção 1: Princípios Arquiteturais Fundamentais e Estratégia de Dados**

Esta seção estabelece a filosofia arquitetural central para o Projeto Helios. Argumenta-se que uma aplicação moderna e rica em dados não pode depender de um único paradigma de dados. Em vez disso, deve adotar um modelo híbrido que aproveita as forças distintas de bancos de dados relacionais e de grafos, criando uma arquitetura que combina o "melhor de ambos os mundos".

### **1.1. O Imperativo do Modelo de Dados Híbrido**

A análise dos requisitos do Projeto Helios revela uma necessidade fundamental tanto para a integridade transacional quanto para a travessia de relacionamentos complexos. Um único modelo de banco de dados é inerentemente insuficiente para atender a essas demandas duplas com desempenho e eficiência ótimos. Os bancos de dados relacionais, o padrão da indústria por décadas, são projetados para dados estruturados, garantindo consistência e conformidade ACID, o que é essencial para sistemas financeiros, de saúde e de gerenciamento de inventário.1 No entanto, eles se tornam ineficientes ao lidar com relacionamentos muitos-para-muitos ou estruturas hierárquicas profundas. Consultas que exigem múltiplas operações de junção (JOIN) em grandes tabelas podem se tornar proibitivamente lentas e complexas.2  
Por outro lado, os bancos de dados de grafos são projetados especificamente para modelar e consultar dados conectados. Neles, os relacionamentos são cidadãos de primeira classe, permitindo travessias de "amigos de amigos" ou detecção de padrões de fraude em tempo quase real, operações que são ordens de magnitude mais rápidas do que suas equivalentes em SQL.1 Contudo, eles não são a escolha ideal para operações transacionais simples ou de Criação, Leitura, Atualização e Exclusão (CRUD), onde a sobrecarga de manter uma estrutura de grafo não oferece benefícios.1  
A visão arquitetural para o Projeto Helios é, portanto, uma estratégia de persistência poliglota. Os dados serão armazenados no modelo que melhor se adapta à sua estrutura e padrões de acesso. Esta abordagem está alinhada com os princípios modernos de microsserviços e evita a armadilha do "tamanho único" das arquiteturas monolíticas legadas.2 O objetivo é combinar a conformidade ACID e a integridade de dados de um sistema relacional com o desempenho de travessia de um banco de dados de grafos nativo. Esta decisão de adotar uma arquitetura de dados híbrida não é apenas uma escolha técnica, mas um compromisso estratégico fundamental. Ela introduz uma complexidade operacional calculada em troca de desempenho e capacidade superiores, uma troca que é essencial para a vantagem competitiva do projeto. A escolha de um modelo único levaria a compromissos inaceitáveis: um sistema puramente relacional sofreria com JOINs lentos e complexos para consultas de relacionamento, enquanto um sistema puramente de grafos poderia ser ineficiente para cargas de trabalho transacionais básicas e carecer das ferramentas maduras para integridade de dados que os sistemas relacionais oferecem.1

### **1.2. Padrão Arquitetural Híbrido Proposto: O Modelo de "Sistema de Registro"**

Para implementar essa visão, propõe-se um padrão arquitetural claro, onde cada sistema de banco de dados tem um papel definido, com um mecanismo de sincronização robusto e desacoplado. Este padrão implementa diretamente o princípio da "Fonte Única da Verdade", um conceito central em ferramentas de design colaborativo modernas como o Artifact, que garante que todas as equipes e sistemas acessem os mesmos diagramas, bibliotecas de componentes e documentação.

#### **1.2.1. PostgreSQL como o Núcleo Transacional e Sistema de Registro**

O PostgreSQL servirá como o armazenamento de dados primário e a "fonte da verdade" definitiva para todas as entidades principais do sistema. Essa decisão garante que todas as operações de escrita se beneficiem de sua robusta conformidade ACID (Atomicidade, Consistência, Isolamento e Durabilidade), restrições de integridade de dados e gerenciamento transacional maduro. Isso é crítico para processos de negócios que exigem precisão absoluta, como contas de usuário, registros de projetos e bibliotecas de equipamentos.3 A escolha do PostgreSQL fornece uma fundação estável e confiável sobre a qual o restante da aplicação pode ser construído.

#### **1.2.2. Neo4j para Análises e Consultas de Grafos Especializadas**

Um subconjunto sincronizado e desnormalizado dos dados será replicado para o Neo4j. Este sistema secundário será otimizado para consultas de leitura intensiva e travessias complexas que são ineficientes em SQL. Os casos de uso incluem a análise das interdependências entre integradores, engenheiros, projetos e concessionárias, bem como a descoberta de padrões de desempenho e gargalos.4 Neste padrão, o banco de dados de grafos é tratado como um índice de consulta especializado e de alto desempenho, em vez de ser o armazenamento de dados primário. Isso permite que cada sistema opere em sua capacidade máxima, sem comprometer o outro.

#### **1.2.3. Sincronização de Dados via Captura de Dados de Mudança (CDC)**

O elo crítico entre os dois sistemas será um pipeline de Captura de Dados de Mudança (CDC). A abordagem recomendada utiliza o **Debezium** e o **Apache Kafka**. Este padrão funciona da seguinte maneira:

1. O Debezium se conecta ao PostgreSQL e lê as alterações de dados diretamente do log de transações do banco de dados (Write-Ahead Log \- WAL), que registra todas as inserções, atualizações e exclusões.4  
2. Ele converte essas alterações de baixo nível em eventos estruturados e os publica em um tópico do Apache Kafka.4  
3. Um serviço consumidor, que pode ser parte da aplicação FastAPI ou um microsserviço separado, assina este tópico do Kafka.  
4. À medida que os eventos de mudança são consumidos, o serviço os traduz para a linguagem de consulta do Neo4j (Cypher) e aplica as alterações correspondentes ao banco de dados de grafos.4

Esta abordagem é assíncrona, tolerante a falhas e desacopla completamente os bancos de dados. Ela evita a necessidade de "escritas duplas" na camada de aplicação, que são notoriamente difíceis de gerenciar transacionalmente em sistemas de banco de dados distintos.4 O modelo garante consistência eventual no banco de dados de grafos, mantendo uma forte consistência no armazenamento relacional primário. A implicação mais significativa desta escolha é que a carga operacional se desloca do gerenciamento de um único banco de dados complexo para o gerenciamento de três sistemas críticos e com estado: PostgreSQL, Neo4j e o pipeline Kafka/Debezium. Isso tem um efeito direto nas habilidades da equipe, na infraestrutura de monitoramento e no planejamento de recuperação de desastres. A arquitetura ganha desempenho ao custo de uma maior superfície operacional.

### **1.3. Considerações Iniciais sobre o Modelo de Dados para o Projeto Helios**

Uma etapa preliminar crucial no design do Projeto Helios será a modelagem de dados, identificando quais partes do domínio são mais bem representadas como tabelas estruturadas no PostgreSQL e quais são mais bem modeladas como nós e relacionamentos no Neo4j.

* **Entidades Estruturadas (PostgreSQL):** Entidades com atributos fixos e relacionamentos um-para-muitos simples, como Integradores, Engenheiros, Projetos, Documentos e a biblioteca de Equipamentos (análoga à "Parts Library" do Artifact), são candidatas ideais para tabelas relacionais. A integridade referencial e as restrições de dados do PostgreSQL garantirão a consistência desses dados principais.  
* **Relacionamentos Complexos (Neo4j):** Relacionamentos muitos-para-muitos, hierárquicos ou recursivos são perfeitos para o modelo de grafo. Exemplos incluem (Integrador)--\>(Projeto), (Engenheiro)--\>(Projeto), (Projeto)--\>(Concessionária). Modelar esses como relacionamentos diretos no Neo4j permitirá consultas de travessia rápidas e intuitivas para análise de desempenho e descoberta de padrões.2

Este exercício inicial de modelagem informará o design do esquema para ambos os bancos de dados e a lógica de transformação necessária no pipeline de CDC para mapear corretamente as alterações do modelo relacional para o modelo de grafo.  
---

## **Seção 2: A Camada de Dados: Uma Análise Comparativa de Sistemas de Banco de Dados FOSS**

Esta seção fornece a evidência e a justificativa para a seleção das tecnologias de banco de dados específicas para o núcleo relacional e a camada de grafo, com base em uma avaliação rigorosa das opções FOSS disponíveis.

### **2.1. Núcleo Relacional: Por que o PostgreSQL é a Escolha Ótima para 2025+**

O PostgreSQL se destaca como a escolha superior para o núcleo relacional do Projeto Helios, não apenas como um RDBMS, mas como uma plataforma de dados avançada e extensível.

* **Além de um Simples RDBMS:** O PostgreSQL é um sistema "objeto-relacional", oferecendo recursos avançados que muitas vezes são encontrados apenas em bancos de dados comerciais ou especializados.3 Para o Projeto Helios, isso significa que ele pode lidar nativamente com uma variedade maior de tipos de dados e cargas de trabalho, potencialmente reduzindo a necessidade de outros armazenamentos especializados.  
* **Manuseio Superior de Dados Complexos e Análises:** O suporte do PostgreSQL a tipos de dados avançados, como arrays, tipos geométricos e, especialmente, seu formato de JSON binário altamente eficiente (JSONB), o torna superior ao MariaDB/MySQL para aplicações modernas que lidam com dados semiestruturados.4 Sua indexação avançada (parcial, funcional) e funções analíticas poderosas permitem que ele lide com consultas de relatórios complexas ordens de magnitude mais rápido que os concorrentes. Benchmarks demonstram que o PostgreSQL completa relatórios em 2-4 segundos, em comparação com mais de 15 segundos para o MySQL em cargas de trabalho complexas.4  
* **Extensibilidade e Conformidade com Padrões:** A capacidade de criar funções, tipos de dados e extensões personalizadas torna o PostgreSQL incrivelmente flexível para necessidades futuras. Sua estrita adesão aos padrões SQL garante portabilidade e reduz o aprisionamento tecnológico (vendor lock-in), um princípio chave para um projeto que prioriza FOSS.4

### **2.2. Camada de Grafo: Selecionando o Motor Certo para Dados Conectados**

A seleção de um banco de dados de grafos será baseada em uma estrutura de avaliação multifacetada, incluindo Desempenho, Escalabilidade, Requisitos de Processamento (OLTP vs. OLAP), Documentação/Suporte e a capacidade de testar com dados reais.4

#### **Tabela: Matriz de Recursos de Bancos de Dados de Grafos FOSS (2025)**

Para facilitar uma decisão baseada em dados, a tabela a seguir consolida as informações sobre os principais concorrentes FOSS. Esta matriz estruturada permite uma comparação direta entre as opções, destacando os principais trade-offs. Por exemplo, a maturidade e a popularidade do Neo4j são comparadas com a flexibilidade de backend do JanusGraph ou a conveniência multi-modelo do ArangoDB, que pode apresentar um desempenho de grafo inferior.2 Isso torna a recomendação final transparente e defensável.

| Característica | Neo4j Community | JanusGraph | ArangoDB | NebulaGraph |
| :---- | :---- | :---- | :---- | :---- |
| **Licença** | GPLv3 | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| **Linguagem de Consulta** | Cypher | Gremlin | AQL (ArangoDB Query Language) | openCypher, nGQL |
| **Armazenamento** | Nativo (Index-Free Adjacency) | Não Nativo (plugável: Cassandra, HBase, etc.) | Multi-modelo (Nativo) | Nativo (Otimizado para grafos grandes) |
| **Modelo de Escalabilidade** | Vertical (instância única) | Horizontal (via backend de armazenamento) | Horizontal (Cluster) | Horizontal (Arquitetura Share-Nothing) |
| **Maturidade do Ecossistema** | Muito Alta (líder de mercado) | Alta (apoiado pela The Linux Foundation) | Média a Alta | Média (crescendo rapidamente) |
| **Adequação OLTP/OLAP** | Forte em OLTP (travessias em tempo real) | Flexível, depende do backend | Híbrido (transacional e analítico) | Forte em OLAP (consultas analíticas em larga escala) |
| **Principais Pontos Fortes** | Maturidade, comunidade, Cypher intuitivo 4 | Flexibilidade de backend, escalabilidade massiva 4 | Multi-modelo (grafo, documento, chave-valor) 4 | Desempenho em grafos massivos, código aberto 4 |
| **Principais Pontos Fracos** | Limitações na Community Edition (sem cluster) 4 | Curva de aprendizado (Gremlin), complexidade de configuração 4 | Desempenho de travessia pode ser inferior ao Neo4j 2 | Comunidade menor, menos recursos para iniciantes 4 |

#### **Análise Aprofundada da Recomendação: Neo4j**

O Neo4j é consistentemente classificado como o padrão da indústria devido à sua maturidade, grande comunidade, documentação extensa e à linguagem de consulta Cypher, que é intuitiva e semelhante ao SQL, facilitando a curva de aprendizado para desenvolvedores relacionais.4 Seu armazenamento de grafo nativo oferece alto desempenho para travessias em tempo real.4

* **Análise da Community Edition vs. Enterprise Edition:** Este é um ponto de decisão crítico para um MVP.  
  * **Community Edition (CE):** É uma edição totalmente funcional e gratuita (licença GPLv3) de banco de dados de instância única, adequada para desenvolvimento, provas de conceito e aplicações não críticas.4 Ela pode ser usada para fins comerciais sem taxas de licença, desde que não seja embutida ou revendida.4  
  * **Limitações Críticas para Produção:** A CE carece de recursos empresariais essenciais para um sistema de produção como o Projeto Helios, principalmente **alta disponibilidade (clustering), failover automatizado e backups online**.4 Um banco de dados de instância única representa um ponto único de falha, o que é inaceitável para uma aplicação crítica.  
  * **Conclusão:** O Neo4j CE é adequado para as fases iniciais de desenvolvimento e teste do MVP. No entanto, o roteiro do projeto deve incluir uma migração para a Enterprise Edition (ou para o serviço gerenciado AuraDB) antes de qualquer lançamento em produção que exija alta disponibilidade e segurança dos dados.

### **2.3. Estratégias de Escalabilidade e Alta Disponibilidade de Banco de Dados**

* **Caminhos de Escalabilidade do PostgreSQL:**  
  * **Escalabilidade Vertical:** A abordagem mais simples, envolvendo o aumento de CPU/RAM do servidor de banco de dados. Este é o primeiro passo, mas possui limites finitos.  
  * **Réplicas de Leitura (Streaming Replication):** O método principal para escalar cargas de trabalho de leitura intensiva. Um servidor primário lida com todas as escritas, e seu Write-Ahead Log (WAL) é transmitido para um ou mais servidores de réplica somente leitura. A aplicação pode então direcionar as consultas de leitura para as réplicas, reduzindo a carga no primário.4 Esta deve ser a primeira estratégia de escalabilidade empregada após o esgotamento da escalabilidade vertical.  
  * **Sharding (Particionamento Horizontal):** Uma estratégia mais complexa para escalar cargas de trabalho de escrita intensiva. Os dados são particionados em múltiplos servidores de banco de dados independentes (shards) com base em uma chave de shard. Isso requer lógica no nível da aplicação ou extensões especializadas como o Citus.3 O sharding deve ser considerado uma solução de escalabilidade de longo prazo devido à sua significativa complexidade arquitetural.  
* **Escalabilidade do Neo4j: Causal Clustering (Enterprise Edition)**  
  * **Arquitetura:** A solução de alta disponibilidade do Neo4j é o Causal Clustering, que consiste em Servidores Core e Réplicas de Leitura.4  
  * **Servidores Core:** Lidam com leituras e escritas. Eles usam o **protocolo Raft** para replicar transações e eleger um líder. Uma transação de escrita só é confirmada após a maioria (quórum) dos Servidores Core a ter confirmado, garantindo a segurança dos dados e a tolerância a falhas. Um mínimo de três Servidores Core é necessário para tolerar uma falha ($M \= 2F \+ 1$).4  
  * **Réplicas de Leitura:** Recebem dados dos Servidores Core de forma assíncrona via envio de logs de transação. Elas são usadas para escalar o desempenho de leitura globalmente sem participar do consenso Raft, permitindo uma escalabilidade massiva de leitura em topologias distribuídas.4  
  * **Consistência Causal:** Garante que um cliente será capaz de ler suas próprias escritas, mesmo que a leitura seja atendida por um servidor diferente no cluster. Isso é alcançado através do uso de "bookmarks" que rastreiam a última transação confirmada por um cliente.4

O ecossistema de bancos de dados FOSS, tanto para modelos relacionais quanto de grafos, está maduro o suficiente para que o desafio principal não seja a falta de recursos, mas a complexidade operacional de gerenciar esses recursos avançados (como clustering e replicação) em um ambiente auto-hospedado. Embora o software seja "gratuito", o Custo Total de Propriedade (TCO) não é zero. O custo se desloca das taxas de licenciamento para a sobrecarga operacional: tempo de engenharia para configuração, manutenção, monitoramento e solução de problemas. Isso reforça a importância estratégica da equipe de DevOps (Seção 4\) e sugere que, para um MVP ou uma equipe sem profunda expertise em administração de bancos de dados, um serviço de banco de dados gerenciado (como AWS RDS para PostgreSQL ou Neo4j AuraDB) poderia ser um ponto de partida mais pragmático e econômico, mesmo que o objetivo de longo prazo seja uma pilha FOSS auto-hospedada.  
---

## **Seção 3: A Camada de Aplicação: Selecionando Frameworks FOSS de Alto Desempenho**

Esta seção avalia os frameworks FOSS ideais para a API de backend e a interface de usuário de frontend, priorizando desempenho, experiência do desenvolvedor e maturidade do ecossistema. A tendência atual favorece ferramentas especializadas e de "melhor da categoria" em vez de frameworks monolíticos e abrangentes.

### **3.1. Arquitetura de Backend: O Caso do Python Assíncrono com FastAPI**

* **Comparação de Frameworks (FastAPI vs. Django vs. Flask):**  
  * **Django:** Um framework full-stack "com tudo incluído". Excelente para aplicações monolíticas grandes e ricas em recursos, como plataformas de e-commerce, mas seu ORM e motor de templates podem ser mais lentos e complexos do que o necessário para uma arquitetura de alta performance focada em APIs.5  
  * **Flask:** Um micro-framework minimalista que oferece máxima flexibilidade. É simples e fácil de aprender, mas exige que os desenvolvedores escolham e integrem todos os componentes (ORM, validação, etc.), o que pode levar a um desenvolvimento mais lento e a uma arquitetura inconsistente em um ambiente de equipe.5  
  * **FastAPI:** Um framework moderno e de alto desempenho construído para APIs. Suas principais vantagens são o suporte assíncrono nativo (resultando em um desempenho que supera significativamente Flask e Django), a validação automática de dados via type hints do Python e Pydantic, e a documentação de API interativa automática (Swagger UI/ReDoc).5  
* **Recomendação para o Projeto Helios: FastAPI**  
  * **Desempenho:** A arquitetura assíncrona do FastAPI, construída sobre Starlette e Uvicorn, foi projetada para lidar com dezenas de milhares de requisições por segundo, tornando-o ideal para aplicações de dados intensivos e em tempo real.5  
  * **Experiência do Desenvolvedor e Segurança de Tipos:** Ao aproveitar o Pydantic, o FastAPI impõe uma validação de dados rigorosa em tempo de execução, reduzindo bugs e melhorando a confiabilidade da API. Isso, combinado com a documentação autogerada, acelera drasticamente os ciclos de desenvolvimento e teste.5  
  * **Escalando Implantações de Produção:** O padrão de implantação de produção padrão envolve o uso do **Gunicorn como um gerenciador de processos para executar múltiplos workers Uvicorn**. O Gunicorn fornece paralelismo ao gerar múltiplos processos do sistema operacional (por exemplo, um por núcleo de CPU), enquanto cada worker Uvicorn fornece concorrência ao lidar com milhares de requisições I/O-bound de forma assíncrona dentro de seu único processo. Essa combinação oferece robustez e alta taxa de transferência.5  
* **Padrões de Integração para Bancos de Dados Híbridos:**  
  * **Desafio:** Gerenciar conexões e transações em dois sistemas de banco de dados diferentes (PostgreSQL e Neo4j) dentro de uma única aplicação requer um padrão arquitetural claro para evitar a duplicação de código e garantir a manutenibilidade.  
  * **Melhor Prática:** Utilizar o sistema de injeção de dependência do FastAPI para gerenciar as sessões de banco de dados. Criar dependências separadas e reutilizáveis (get\_postgres\_session e get\_neo4j\_session) que lidam com o ciclo de vida da conexão (abrir, ceder, fechar) para cada banco de dados.5  
  * **Padrão de Repositório:** Abstrair a lógica do banco de dados em uma camada de repositório. Por exemplo, um UserRepository pode ter métodos como get\_by\_email (que consulta o PostgreSQL) e get\_social\_connections (que consulta o Neo4j). Os endpoints da API dependerão desses métodos de repositório, mantendo o código específico do banco de dados isolado da lógica de negócios.5  
  * **Integridade Transacional:** Conforme estabelecido na Seção 1, deve-se evitar tentar implementar transações distribuídas em ambos os bancos de dados a partir da camada de API. Todas as operações de escrita devem ir para a "fonte da verdade" do PostgreSQL. A aplicação não deve escrever diretamente no Neo4j; isso é tratado pelo pipeline de CDC.4

### **3.2. Arquitetura de Frontend: Construindo uma Interface de Usuário Moderna e Performática**

* **Comparação de Frameworks (React vs. Vue vs. Svelte):**  
  * **React:** Dominante no mercado com 39.5% de uso (Stack Overflow 2024), apoiado por um ecossistema massivo de bibliotecas, ferramentas (Next.js, Remix) e um vasto pool de talentos. Sua principal fraqueza é uma curva de aprendizado mais íngreme e mais código boilerplate em comparação com frameworks mais novos.6  
  * **Vue:** Conhecido por sua curva de aprendizado suave, excelente documentação e forte satisfação do desenvolvedor. Mantém uma posição forte (15.4% de uso) e é frequentemente favorecido por startups para produtividade rápida.6 Seu ecossistema é menor que o do React.  
  * **Svelte:** Um framework baseado em compilador que oferece o melhor desempenho bruto e os menores tamanhos de pacote, deslocando o trabalho do tempo de execução para o tempo de compilação. É a "estrela em ascensão", elogiado por sua simplicidade e boilerplate mínimo, mas possui o menor ecossistema e adoção empresarial limitada até o momento.6  
* **Recomendação para o Projeto Helios: React**  
  * **Pragmatismo sobre Pureza:** Embora o Svelte ofereça benchmarks de desempenho superiores (TTI de \~800ms vs. \~1.4s do React), para um projeto grande e complexo como o Helios, os benefícios do ecossistema maduro e extenso do React superam em muito os ganhos de desempenho bruto do Svelte.6 A capacidade de encontrar componentes pré-construídos, documentação extensa e um grande pool de desenvolvedores experientes reduz significativamente o risco do projeto e acelera o tempo de desenvolvimento.7  
* **Arquitetura de Gerenciamento de Estado: Separando o Estado do Servidor e do Cliente**  
  * **O Problema:** Historicamente, bibliotecas como o Redux eram usadas para gerenciar todo o estado da aplicação, incluindo dados buscados de APIs ("estado do servidor"). Isso leva a um boilerplate complexo (ações, redutores, thunks) para gerenciar operações assíncronas como busca, cache e re-busca, que são problemas já resolvidos.8  
  * **A Solução Moderna:** Adotar um padrão de "separação de preocupações".  
    * **React Query (TanStack Query) para o Estado do Servidor:** Esta biblioteca foi criada especificamente para gerenciar todo o ciclo de vida dos dados do servidor. Ela lida automaticamente com busca, cache, atualizações em segundo plano, estratégias de stale-while-revalidate e mutações (atualizações otimistas, tratamento de erros). Isso elimina milhares de linhas de código de gerenciamento de estado manual e simplifica drasticamente os componentes que interagem com a API.8 É a escolha ideal para dashboards com uso intensivo de dados.  
    * **Zustand para o Estado do Cliente:** Para o restante do estado "verdadeiro" do lado do cliente (por exemplo, estado da interface do usuário como "a barra lateral está aberta?", dados de formulário, preferências de tema), usar um gerenciador de estado global leve como o Zustand. O Zustand oferece uma API simples, baseada em hooks, sem o boilerplate do Redux, tornando-o rápido, eficiente e fácil de usar.8  
  * **Benefício Arquitetural:** Essa combinação cria uma arquitetura limpa, escalável e altamente manutenível. Os componentes se tornam mais simples ao delegar o gerenciamento do estado do servidor para os hooks do React Query. O armazenamento de estado global do cliente (Zustand) permanece pequeno e focado, e a separação torna toda a aplicação mais fácil de entender, testar e depurar.8

### **3.3. Fluxo de Trabalho e de Dados Consolidados: Uma Abordagem Inspirada no Artifact**

O modelo operacional do Projeto Helios será fortemente inspirado por ferramentas modernas e colaborativas de ECAD (Electrical Computer-Aided Design) como o Artifact, que são construídas em torno do princípio de uma "Fonte Única da Verdade". Isso garante que todos os stakeholders — integradores, engenheiros e a equipe operacional da plataforma — trabalhem com os mesmos dados consistentes e versionados.  
O diagrama a seguir ilustra o fluxo de dados de ponta a ponta, mapeando os conceitos centrais de fluxo de trabalho do Artifact para a pilha de tecnologia FOSS proposta para o Helios:

\+--------------------------------+       \+-----------------+       \+------------------------------------------+

| Integrador (Frontend React) |-----\> | API FastAPI | \----\> | PostgreSQL (Fonte da Verdade) |  
| \- Submete detalhes do projeto | | \- Validação | | \- Biblioteca de Equipamentos (Peças) |  
| \- Seleciona equipamentos | | \- Lógica de Neg. | | \- Versões do Projeto (Histórico) |  
| \- Visualiza dashboard | | \- Geração de Docs| | \- Dados de Usuários e Integradores |  
| \- Baixa pacote final | \<-----| | \<---- | \- Documentos Gerados |  
\+--------------------------------+       \+-------+---------+       \+---------------------+--------------------+

| |  
| (Consultas de Relacionamento) | (Sincronização via CDC)  
| |  
                                                 v                                       v  
                                         \+-------+---------+                 \+-----------+-----------+

| Neo4j (Grafo) | \<----(Consumidor)| Kafka / Debezium |  
| \- Análise de Redes| \+-----------------------+  
| \- Insights de Des. |  
                                         \+-----------------+

**Detalhamento do Fluxo de Trabalho:**

1. **Entrada e Design (Análogo à Biblioteca e Esquemáticos do Artifact):**  
   * **Ação:** O integrador usa o **frontend React** para criar um novo projeto de homologação. Ele seleciona equipamentos pré-aprovados (painéis solares, inversores) de uma biblioteca de componentes e insere parâmetros específicos do projeto.  
   * **Fluxo de Dados:** O aplicativo React envia esses dados estruturados para o **backend FastAPI**. O backend valida os dados usando modelos Pydantic e grava o novo registro do projeto no banco de dados **PostgreSQL**, que serve como a "fonte única da verdade" canônica.  
2. **Geração Automatizada de Documentos:**  
   * **Ação:** O **backend FastAPI** aciona serviços internos para gerar automaticamente documentos padronizados (por exemplo, memorial descritivo, formulários) com base nos dados do projeto armazenados no PostgreSQL.  
   * **Fluxo de Dados:** Esses documentos gerados são armazenados, e seus metadados são vinculados ao registro do projeto no PostgreSQL.  
3. **Enriquecimento e Análise do Grafo:**  
   * **Ação:** O pipeline de Captura de Dados de Mudança (CDC) (**Debezium** e **Kafka**) detecta o novo registro do projeto no PostgreSQL.10  
   * **Fluxo de Dados:** Um serviço consumidor processa este evento, criando e conectando nós no banco de dados **Neo4j**. Isso constrói o grafo relacional, ligando o Projeto ao Integrador, ao Engenheiro atribuído e à Concessionária relevante.  
4. **Rastreamento de Projetos e Colaboração (Análogo ao Rastreamento e Controle de Versão do Artifact):**  
   * **Ação:** O integrador e o engenheiro atribuído podem visualizar o status do projeto em um painel em tempo real no **frontend React**. Eles podem ver todos os documentos associados, rastrear o status de aprovação e visualizar um histórico completo, no estilo git, de quaisquer alterações ou reenvios.  
   * **Fluxo de Dados:** O painel faz chamadas de API para o **FastAPI**.  
     * Para dados diretos do projeto (status, links de documentos, histórico de versões), o FastAPI consulta o banco de dados **PostgreSQL**.  
     * Para insights relacionais complexos (por exemplo, "Qual é o tempo médio de aprovação deste engenheiro com a CEMIG?"), o FastAPI consulta o banco de dados de grafos **Neo4j**.  
5. **Geração de Saída Final (Análogo à Exportação do Artifact):**  
   * **Ação:** Uma vez que o projeto esteja completo e aprovado, o integrador pode baixar o pacote de homologação final e consolidado.  
   * **Fluxo de Dados:** Uma requisição ao **backend FastAPI** aciona um processo que reúne todos os documentos e metadados necessários do **PostgreSQL**, os empacota e fornece um arquivo para download ao usuário através do **frontend React**.

Este fluxo de trabalho consolidado garante a integridade dos dados ao manter uma única fonte da verdade no PostgreSQL, enquanto aproveita o poder de um banco de dados de grafos para a análise de relacionamentos complexos que fornece a inteligência e o valor central da plataforma HaaS.  
---

## **Seção 4: O Ciclo de Vida de Desenvolvimento e Implantação: Metodologias e Automação FOSS**

Esta seção descreve os processos e ferramentas que governarão como o Projeto Helios é construído, gerenciado e implantado, com foco em eficiência, escalabilidade e colaboração. As escolhas de ferramentas em todo o ciclo de vida de DevOps são profundamente interconectadas e criam um sistema de reforço mútuo.

### **4.1. Metodologia Ágil para um Projeto em Evolução**

* **Scrum vs. Kanban:** O Scrum fornece estrutura através de sprints de duração fixa (2-4 semanas), papéis definidos (Scrum Master, Product Owner) e cerimônias formais. É ideal para projetos com requisitos previsíveis e equipes estáveis.11 O Kanban, em contraste, é um sistema de fluxo contínuo focado em visualizar o trabalho, limitar o trabalho em andamento (WIP) e otimizar o tempo de ciclo. É altamente flexível e permite mudanças de prioridade imediatas.11  
* **Recomendação para o Projeto Helios: Kanban**  
  * **Justificativa:** Para um projeto em estágio inicial, onde os requisitos provavelmente evoluirão e as prioridades podem mudar frequentemente com base no feedback, a flexibilidade do Kanban é uma vantagem significativa. Ele evita a rigidez do planejamento de sprints e permite que a equipe se adapte rapidamente, tornando-o "perfeito para empresas em estágio inicial".12 Dados mostram que 78% das startups com menos de 10 pessoas preferem uma abordagem híbrida Kanban/Lean.12

### **4.2. Estrutura da Base de Código: Uma Estratégia de Monorepositório Poliglota**

* **Por que um Monorepositório?** Para um projeto com componentes de frontend (React/TypeScript) e backend (Python) fortemente acoplados, um monorepositório simplifica o gerenciamento de dependências, permite commits atômicos em todos os serviços e facilita o compartilhamento de código (por exemplo, tipos de dados compartilhados).13  
* **Análise de Ferramentas (Pants vs. Nx vs. Turborepo):**  
  * **Turborepo & Nx:** Ambos são sistemas de construção excelentes e de alto desempenho, otimizados principalmente para o ecossistema JavaScript/TypeScript. Eles oferecem cache avançado e orquestração de tarefas.13 Embora tenham algum suporte para outras linguagens, muitas vezes não é tão profundo ou nativo quanto seu suporte a JS/TS.  
  * **Pants:** Um sistema de construção projetado desde o início para monorepositórios de grande escala e multi-linguagem (poliglota), com suporte nativo e profundo de primeira classe para Python, Go, Java e outros.13 Ele se destaca na inferência automática de dependências, no cache de granularidade fina e na execução apenas das tarefas necessárias com base nas alterações de código.13  
* **Recomendação para o Projeto Helios: Pants**  
  * **Justificativa:** Dada a natureza poliglota do projeto (backend em Python, frontend em TypeScript), o Pants é a escolha superior. Seu suporte forte e nativo a Python é um diferencial chave. Ele fornece uma interface consistente (./pants lint::, ./pants test ::) em todas as linguagens e usa sua análise de dependência para criar artefatos de implantação enxutos e otimizados (por exemplo, binários PEX, imagens Docker), o que é crucial para um CI/CD eficiente.13

### **4.3. Integração e Implantação Contínuas (CI/CD)**

* **Ferramentas (GitLab CI vs. Jenkins):**  
  * **Jenkins:** Um servidor de automação de código aberto altamente personalizável e extensível, com um ecossistema massivo de plugins (\>1800 plugins). No entanto, possui uma curva de aprendizado íngreme, requer configuração e manutenção significativas e pode ter uma alta sobrecarga de desempenho como uma solução auto-hospedada.15  
  * **GitLab CI/CD:** Uma plataforma integrada e completa que combina gerenciamento de código-fonte, CI/CD, rastreamento de problemas e varredura de segurança em uma interface unificada. Utiliza uma configuração simples baseada em YAML (.gitlab-ci.yml) e possui excelente integração com Docker, tornando-o mais fácil de configurar e manter, especialmente para equipes pequenas.15  
* **Recomendação para o Projeto Helios: GitLab CI**  
  * **Justificativa:** A natureza integrada e a facilidade de configuração do GitLab CI proporcionam uma menor carga de manutenção e uma experiência de desenvolvedor mais suave em comparação com o Jenkins, tornando-o uma escolha melhor para um novo projeto.15  
* **Estrutura de Pipeline para Monorepositório:** O pipeline será estruturado usando as palavras-chave include e rules:changes do GitLab. Um arquivo .gitlab-ci.yml raiz atuará como um plano de controle, incluindo condicionalmente arquivos de pipeline separados para o backend e o frontend apenas quando os arquivos em seus respectivos diretórios forem alterados. Isso evita a execução de trabalhos desnecessários e acelera drasticamente o ciclo de CI.15 A sinergia entre as ferramentas é clara: o GitLab CI pode determinar rapidamente *qual* pipeline de alto nível executar (backend ou frontend), e então o Pants pode determinar *quais testes ou tarefas de construção específicas* dentro desse pipeline precisam ser executados. Essa otimização em camadas é a chave para manter a alta velocidade em um grande monorepositório.

### **4.4. Infraestrutura como Código (IaC) e Gerenciamento de Ambiente**

* **Orquestração vs. Gerenciamento de Configuração:** É crucial distinguir entre esses dois conceitos. A **Orquestração** é a atividade do Dia 0 de provisionar a infraestrutura fundamental (VMs, redes, bancos de dados). O **Gerenciamento de Configuração** é a atividade do Dia 1+ de instalar software, gerenciar arquivos e garantir o estado dessa infraestrutura.15  
* **Terraform para Orquestração:** O Terraform é a ferramenta ideal para a orquestração da infraestrutura. Ele usa uma linguagem declarativa (HCL) para definir o estado desejado da infraestrutura em nuvem e gerencia todo o ciclo de vida desses recursos através de seu arquivo de estado. Esta é a ferramenta mais crítica para gerenciar a infraestrutura em nuvem do zero.15 Será usado para provisionar Droplets/VMs, bancos de dados gerenciados, VPCs, etc..15  
* **Ansible para Gerenciamento de Configuração:** O Ansible é uma ferramenta de gerenciamento de configuração sem agente que será usada para configurar os Droplets provisionados, instalar pacotes necessários, gerenciar arquivos de configuração e implantar o código da aplicação.15  
* **Ambiente de Desenvolvimento Local com Docker Compose:** Para garantir a consistência entre o desenvolvimento e a produção, toda a pilha será containerizada. Um arquivo docker-compose.yml definirá os serviços para o backend FastAPI, o frontend React (servido via Nginx para desenvolvimento), o banco de dados PostgreSQL e o banco de dados Neo4j. Isso permite que qualquer desenvolvedor inicie o ambiente de desenvolvimento completo e integrado com um único comando (docker-compose up).13 O arquivo usará volumes para persistência de dados e recarregamento automático de código, e definirá as dependências de serviço com depends\_on e healthcheck para garantir a ordem de inicialização correta.17

---

## **Seção 5: Uma Postura de Segurança Holística para o Projeto Helios**

Esta seção detalha uma estratégia de segurança em múltiplas camadas e de defesa em profundidade, incorporando as melhores práticas desde a camada de infraestrutura até a camada de aplicação. Uma segurança eficaz não é uma única ferramenta ou recurso, mas uma prática generalizada de aplicar o "Princípio do Menor Privilégio" em cada camada da pilha.

### **5.1. Segurança de Infraestrutura e Rede**

* **Segurança de Contêineres:**  
  * **Checklist Priorizado de Segurança Docker (OWASP):** Uma lista de verificação das regras de segurança Docker mais críticas para uma implantação de produção será implementada. A prioridade mais alta é prevenir escapes de contêiner e acesso root ao host. Portanto, regras como "Não exponha o soquete do daemon Docker" (REGRA \#1) e "Defina um usuário não-root" (REGRA \#2) são primordiais.19 A próxima prioridade é minimizar a superfície de ataque dentro do contêiner, usando imagens base mínimas e descartando capacidades desnecessárias do kernel.19 Finalmente, medidas proativas como a varredura de vulnerabilidades devem ser integradas ao pipeline de CI/CD.19 O checklist incluirá:  
    1. Usar imagens base mínimas e confiáveis.  
    2. Executar contêineres como um usuário não-root.  
    3. Não expor o soquete do daemon Docker.  
    4. Descartar capacidades desnecessárias (evitar \--privileged).  
    5. Usar scanners de vulnerabilidade de imagem no CI.  
    6. Implementar cotas de recursos.19  
* **Endurecimento de Bancos de Dados:**  
  * **Checklist de Segurança do PostgreSQL:** Implementar as melhores práticas de segurança, como restringir listen\_addresses, usar scram-sha-256 em vez de md5 ou trust no pg\_hba.conf, revogar permissões PUBLIC padrão, usar SSL para conexões e executar a aplicação com um papel de não-superusuário.22  
  * **Checklist de Segurança do Neo4j:** Forçar a autenticação (dbms.security.auth\_enabled=true), usar controle de acesso baseado em papéis, proteger os conectores de rede com SSL/TLS, restringir o acesso a portas de backup e administrativas com firewalls e garantir que o processo do Neo4j não seja executado como root.22

### **5.2. Segurança de Aplicação e API**

* **Mitigação do Top 10 de Segurança de APIs da OWASP no FastAPI:**  
  * **API1:2023 \- Autorização de Nível de Objeto Quebrada (BOLA):** Ocorre quando um usuário pode acessar objetos que não deveria (por exemplo, /users/123 pode ser alterado para /users/456). A mitigação no FastAPI envolve a criação de uma dependência que busca o objeto solicitado *e* verifica se o usuário autenticado atualmente tem posse ou permissão para acessá-lo antes que a lógica principal do endpoint seja executada.22  
  * **API2:2023 \- Autenticação Quebrada:** Envolve mecanismos de autenticação fracos. A mitigação inclui o uso de hashing de senha forte (por exemplo, bcrypt via passlib), a implementação de JWTs de curta duração e o uso das utilidades de segurança integradas do FastAPI (OAuth2PasswordBearer) para forçar a autenticação em endpoints protegidos.22  
  * **API3:2023 \- Autorização de Nível de Propriedade de Objeto Quebrada (BOPLA):** Inclui Atribuição em Massa (permitindo que um usuário atualize campos que não deveria, como is\_admin) e Exposição Excessiva de Dados (retornando campos sensíveis como hashes de senha). A mitigação no FastAPI é alcançada usando modelos Pydantic separados para entrada (UserCreate, UserUpdate) e saída (UserPublic). Os modelos de entrada incluem apenas os campos que o usuário tem permissão para definir, e os modelos de saída incluem apenas os campos que são seguros para expor.22  
* **Manuseio Seguro de JWT em uma SPA React:**  
  * **A Vulnerabilidade:** Armazenar JWTs no localStorage os torna vulneráveis a roubo por meio de ataques de Cross-Site Scripting (XSS). Armazená-los em cookies padrão torna a aplicação vulnerável a ataques de Cross-Site Request Forgery (CSRF).22  
  * **O Padrão Recomendado: "Token de Acesso em Memória \+ Token de Atualização em Cookie httpOnly"**  
    1. **Login:** O usuário se autentica, e o servidor retorna um *token de acesso* de curta duração no corpo da resposta JSON e um *token de atualização* de longa duração em um cookie seguro, httpOnly, SameSite=Strict.  
    2. **Armazenamento:** A aplicação React armazena o token de acesso em memória (por exemplo, em um armazenamento Zustand). Ela não pode acessar o cookie do token de atualização.  
    3. **Chamadas de API:** Para cada requisição de API, o token de acesso é anexado ao cabeçalho Authorization: Bearer.  
    4. **Expiração do Token:** Quando o token de acesso expira, a API retorna um erro 401 Unauthorized. Um interceptador Axios/fetch captura esse erro e faz uma requisição silenciosa para um endpoint /refresh\_token.  
    5. **Atualização:** O navegador envia automaticamente o cookie seguro do token de atualização com a requisição de atualização. O servidor valida o token de atualização, o revoga (por segurança) e emite um novo token de acesso e um novo token de atualização.  
    6. **Nova Tentativa:** O interceptador recebe o novo token de acesso, o armazena em memória e tenta novamente a requisição original que falhou.  
  * **Benefícios de Segurança:** Este padrão mitiga ambas as ameaças. O XSS não pode roubar o token de atualização httpOnly, e o token de acesso em memória é perdido ao recarregar a página, limitando sua exposição. O SameSite=Strict no cookie oferece forte proteção contra ataques CSRF.22

A aplicação consistente deste princípio de menor privilégio em cada camada — desde a configuração do Dockerfile até a modelagem de dados da API — é o que criará uma postura de segurança verdadeiramente robusta para o Projeto Helios.  
---

## **Seção 6: Recomendações Estratégicas e Roteiro de Implementação**

Esta seção final sintetiza toda a análise anterior em um plano concreto e acionável para o Projeto Helios, abordando tecnologia, processo, custo e estrutura da equipe. A melhor pilha de tecnologia não é apenas sobre superioridade técnica, mas também sobre alinhamento estratégico com as restrições do projeto, incluindo orçamento, cronograma e disponibilidade de talentos.

### **6.1. A Pilha FOSS Recomendada para o Projeto Helios**

| Categoria | Tecnologia Recomendada |
| :---- | :---- |
| **Camada de Dados (Relacional)** | PostgreSQL |
| **Camada de Dados (Grafo)** | Neo4j |
| **Sincronização de Dados** | Debezium \+ Kafka |
| **Framework de Backend** | FastAPI |
| **Framework de Frontend** | React |
| **Gerenciamento de Estado** | React Query \+ Zustand |
| **Metodologia** | Kanban |
| **Ferramenta de Monorepo** | Pants |
| **CI/CD** | GitLab CI |
| **IaC** | Terraform \+ Ansible |
| **Containerização** | Docker |

### **6.2. Plano de Implementação em Fases: Do MVP à Escala**

* **Fase 1: MVP (Meses 1-3):**  
  * **Foco:** Desenvolvimento rápido de recursos e validação de hipóteses.  
  * **Tecnologia:** Utilizar o Neo4j Community Edition. Implantar todos os serviços (FastAPI, React, PostgreSQL, Neo4j) como contêineres em um único e potente Droplet da DigitalOcean ou instância da AWS Lightsail para minimizar a complexidade da infraestrutura. A implantação manual é aceitável nesta fase para acelerar a iteração.  
* **Fase 2: Endurecimento Pré-Produção (Meses 4-5):**  
  * **Foco:** Estabilidade, segurança e automação.  
  * **Tecnologia:** Implementar o pipeline completo de CI/CD com GitLab CI e Pants. Escrever scripts Terraform para provisionar ambientes de homologação e produção separados. Migrar do Neo4j CE para a Enterprise Edition (ou AuraDB) e configurar um Causal Cluster de 3 nós. Implementar réplicas de leitura no PostgreSQL. Implementar o checklist de segurança completo.  
* **Fase 3: Lançamento em Produção e Escala (Mês 6+):**  
  * **Foco:** Monitoramento de desempenho, escalabilidade e alta disponibilidade.  
  * **Tecnologia:** Separar os bancos de dados em serviços gerenciados (por exemplo, DigitalOcean Managed PostgreSQL, Neo4j AuraDB) para descarregar a carga operacional. Implementar monitoramento e alertas robustos. Iniciar testes de carga e escalar as camadas de aplicação e banco de dados conforme necessário, com base no uso real.

### **6.3. Análise de Custo de Implantação Inicial (MVP \- Fase 1\)**

* **Cenário:** Um único servidor executando todos os serviços em contêineres. Um ponto de partida razoável para um MVP é uma máquina com 2-4 vCPUs e 4-8 GB de RAM.  
* **DigitalOcean:** Um Droplet "CPU-Optimized" com 2 vCPUs e 4 GB de RAM custa **$42/mês**. Um Droplet "General Purpose" com 2 vCPUs e 8 GB de RAM custa **$63/mês**.22  
* **AWS Lightsail:** Uma instância Linux com 2 vCPUs e 4 GB de RAM custa **$24/mês**. Uma instância com 2 vCPUs e 8 GB de RAM custa **$44/mês**.22  
* **Recomendação:** Para a fase de MVP, a **AWS Lightsail oferece um ponto de entrada mais econômico**. Uma instância de $24-$44/mês deve ser suficiente para o desenvolvimento e testes iniciais. Os custos aumentarão significativamente na Fase 2 com a introdução de bancos de dados gerenciados e ambientes em cluster.

### **6.4. Considerações sobre Talentos e Equipe: O Mercado de Desenvolvedores no Brasil**

* **Análise de Mercado:** O mercado de tecnologia no Brasil está em franca expansão, com uma projeção de 800.000 novos empregos até 2025, mas com uma significativa escassez de talentos (530.000 profissionais).22 Isso o torna um mercado competitivo para os empregadores.  
* **Demanda por Tecnologia:** A pilha escolhida está perfeitamente alinhada com as habilidades de alta demanda no Brasil. **Python e JavaScript moderno (React, Node.js) comandam os salários mais altos** e são listados como tecnologias "super quentes".22 Este alinhamento é uma vantagem estratégica, pois explora os maiores pools de talentos disponíveis.  
* **Expectativas Salariais (2025):** Desenvolvedores sênior (6+ anos) comandam os salários mais altos. Embora os valores específicos variem, as fontes indicam alta demanda para as tecnologias selecionadas, com desenvolvedores full-stack ganhando entre R$72k e R$120k anualmente, e papéis focados em Python para IA/Dados ganhando ainda mais.22 Empresas que contratam remotamente dos EUA devem esperar oferecer salários competitivos para atrair os melhores talentos.  
* **Considerações Culturais e Logísticas:** O Brasil está em um fuso horário favorável para a colaboração com empresas dos EUA. No entanto, nuances culturais em relação ao equilíbrio entre vida profissional e pessoal, estilos de comunicação e a importância das relações pessoais devem ser consideradas ao construir uma equipe remota.22

Este roteiro estratégico equilibra a excelência técnica com as restrições pragmáticas do mundo real. O plano não é apenas uma lista de tecnologias, mas um mapa que equilibra a arquitetura ideal com as realidades práticas da construção e lançamento de um novo produto, garantindo que o Projeto Helios esteja posicionado para o sucesso a curto e longo prazo.

#### **Referências citadas**

1. CDC setup for Postgres using Debezium and Kafka Connect | by Naren Chowdary Ravilla, acessado em outubro 17, 2025, [https://medium.com/@nanichowdary.ravilla/cdc-setup-for-postgres-using-debezium-and-kafka-connect-dd7a4a0833c3](https://medium.com/@nanichowdary.ravilla/cdc-setup-for-postgres-using-debezium-and-kafka-connect-dd7a4a0833c3)  
2. Causal Clustering in Neo4j \- Neo4j 3.5 Administration, acessado em outubro 17, 2025, [https://neo4j.com/graphacademy/training-admin-35/04-neo4jadmin-3-5-causal-clustering-neo4j/](https://neo4j.com/graphacademy/training-admin-35/04-neo4jadmin-3-5-causal-clustering-neo4j/)  
3. Scalable and Minimalistic FastAPI \+ PostgreSQL Template \- Reddit, acessado em outubro 17, 2025, [https://www.reddit.com/r/FastAPI/comments/1hmbenw/scalable\_and\_minimalistic\_fastapi\_postgresql/](https://www.reddit.com/r/FastAPI/comments/1hmbenw/scalable_and_minimalistic_fastapi_postgresql/)  
4. Enabling CDC with the Fully Managed Debezium PostgreSQL Connector \- Confluent, acessado em outubro 17, 2025, [https://www.confluent.io/blog/cdc-and-data-streaming-capture-database-changes-in-real-time-with-debezium/](https://www.confluent.io/blog/cdc-and-data-streaming-capture-database-changes-in-real-time-with-debezium/)  
5. 098 RDBMS to Neo4j Real Time Data Sync with Debezium and Kafka \- NODES2022 \- Nicolas Mervaillie, Alf \- YouTube, acessado em outubro 17, 2025, [https://www.youtube.com/watch?v=tybfzH-JrdI](https://www.youtube.com/watch?v=tybfzH-JrdI)  
6. Develop & Deploy Fastapi \+ React with Postgres using Docker ..., acessado em outubro 17, 2025, [https://petejadhav.in/tech/deploy-react-fastapi-postgres-app-with-docker/](https://petejadhav.in/tech/deploy-react-fastapi-postgres-app-with-docker/)  
7. React app with FastAPI, SQLAlchemy, PostgreSQL, and Docker-Compose (a tutorial) \[part 1: setup\] \- Joe Min, acessado em outubro 17, 2025, [https://josephmin.medium.com/react-app-with-fastapi-sqlalchemy-postgresql-and-docker-compose-a-tutorial-part-1-setup-5e3c26fcbdf0](https://josephmin.medium.com/react-app-with-fastapi-sqlalchemy-postgresql-and-docker-compose-a-tutorial-part-1-setup-5e3c26fcbdf0)  
8. How GraphRAG Works Step-By-Step: From Graph Creation to ..., acessado em setembro 30, 2025, [https://pub.towardsai.net/how-microsofts-graphrag-works-step-by-step-b15cada5c209](https://pub.towardsai.net/how-microsofts-graphrag-works-step-by-step-b15cada5c209)  
9. Neo4j Graph Database Platform, acessado em outubro 17, 2025, [https://neo4j.com/product/neo4j-graph-database/](https://neo4j.com/product/neo4j-graph-database/)  
10. Postgres CDC with Debezium: Complete tutorial \- Sequin Blog, acessado em outubro 17, 2025, [https://blog.sequinstream.com/postgres-cdc-with-debezium-complete-step-by-step-tutorial/](https://blog.sequinstream.com/postgres-cdc-with-debezium-complete-step-by-step-tutorial/)  
11. Outputs \- GraphRAG \- Microsoft Open Source, acessado em setembro 30, 2025, [https://microsoft.github.io/graphrag/index/outputs/](https://microsoft.github.io/graphrag/index/outputs/)  
12. FastAPI Best Practices : r/Python \- Reddit, acessado em outubro 17, 2025, [https://www.reddit.com/r/Python/comments/wrt7om/fastapi\_best\_practices/](https://www.reddit.com/r/Python/comments/wrt7om/fastapi_best_practices/)  
13. Debezium connector for PostgreSQL, acessado em outubro 17, 2025, [https://debezium.io/documentation/reference/stable/connectors/postgresql.html](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)  
14. Dockerizing FastAPI with Postgres, Uvicorn, and Traefik | TestDriven.io, acessado em outubro 17, 2025, [https://testdriven.io/blog/fastapi-docker-traefik/](https://testdriven.io/blog/fastapi-docker-traefik/)  
15. Full stack, modern web application template. Using FastAPI, React, SQLModel, PostgreSQL, Docker, GitHub Actions, automatic HTTPS and more., acessado em outubro 17, 2025, [https://github.com/fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)  
16. How To Use Terraform With Your Team \- DigitalOcean, acessado em outubro 17, 2025, [https://www.digitalocean.com/community/tutorials/how-to-use-terraform-within-your-team](https://www.digitalocean.com/community/tutorials/how-to-use-terraform-within-your-team)  
17. Zustand and TanStack Query: The Dynamic Duo That Simplified My React State Management | by Blueprintblog | JavaScript in Plain English, acessado em outubro 17, 2025, [https://javascript.plainenglish.io/zustand-and-tanstack-query-the-dynamic-duo-that-simplified-my-react-state-management-e71b924efb90](https://javascript.plainenglish.io/zustand-and-tanstack-query-the-dynamic-duo-that-simplified-my-react-state-management-e71b924efb90)  
18. FastAPI Security Essentials: Using OAuth2 and JWT for Authentication | by Suganthi, acessado em outubro 17, 2025, [https://medium.com/@suganthi2496/fastapi-security-essentials-using-oauth2-and-jwt-for-authentication-7e007d9d473c](https://medium.com/@suganthi2496/fastapi-security-essentials-using-oauth2-and-jwt-for-authentication-7e007d9d473c)  
19. FastAPI in Containers \- Docker, acessado em outubro 17, 2025, [https://fastapi.tiangolo.com/deployment/docker/](https://fastapi.tiangolo.com/deployment/docker/)  
20. Deploying Graph RAG in Production | by Bijit Ghosh \- Medium, acessado em setembro 30, 2025, [https://medium.com/@bijit211987/deploying-graph-rag-in-production-92cd8fff48db](https://medium.com/@bijit211987/deploying-graph-rag-in-production-92cd8fff48db)  
21. Upgrade Community to Enterprise \- Upgrade and Migration Guide \- Neo4j, acessado em outubro 17, 2025, [https://neo4j.com/docs/upgrade-migration-guide/current/version-5/ce-to-ee/](https://neo4j.com/docs/upgrade-migration-guide/current/version-5/ce-to-ee/)  
22. microsoft/graphrag: A modular graph-based Retrieval-Augmented Generation (RAG) system, acessado em setembro 30, 2025, [https://github.com/microsoft/graphrag](https://github.com/microsoft/graphrag)