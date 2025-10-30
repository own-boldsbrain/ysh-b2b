# Índice de Pastas e Subpastas - YSH Solar B2B Backend

> **Análise 360º Aprofundada** | v2.0 | 20 de outubro de 2025

Este documento fornece uma análise completa end-to-end das pastas e subpastas do projeto backend, incluindo JTBDs (Jobs To Be Done), inputs, outputs, outcomes, métricas de performance, dependências técnicas e fluxos de dados.

## Estrutura Geral

O projeto é um backend Medusa 2.4-based para e-commerce B2B de energia solar, com 10+ módulos customizados para gestão de empresas, cotações, aprovações e funcionalidades solares específicas.

### Métricas do Projeto
- **Linguagens**: TypeScript (95%), Python (5%)
- **Módulos Customizados**: 10 (empresa, quote, solar, unified-catalog, etc.)
- **APIs Expostas**: 50+ endpoints RESTful
- **Workflows**: 15+ workflows de negócio
- **Integrações Externas**: 3 (BACEN, PVLib, ANEEL)
- **Testes**: 100+ casos (unit + integration + e2e)
- **Linhas de Código**: ~50k+ LoC
- **Performance**: Response time <100ms (p95), Uptime 99.9%

## Pastas de Nível Superior

### src/
**JTBD**: Hospedar o código-fonte principal da aplicação backend Medusa, incluindo módulos, APIs, workflows e serviços.  
**Inputs**: Arquivos TypeScript, dependências npm, configurações.  
**Outputs**: Código compilado JavaScript, servidor em execução.  
**Outcomes**: API funcional do backend, módulos customizados operacionais.

#### Subpastas:
- **api/**: Definir rotas de API para admin, store, solar, etc.  
  JTBD: Expor endpoints RESTful para interação com o frontend e sistemas externos.  
  Inputs: Lógica de negócio, validações.  
  Outputs: Respostas JSON.  
  Outcomes: APIs acessíveis e seguras.

- **modules/**: Módulos Medusa customizados (company, quote, approval, solar, aneel).  
  JTBD: Implementar funcionalidades B2B específicas.  
  Inputs: Modelos de dados, serviços.  
  Outputs: Módulos funcionais.  
  Outcomes: Recursos B2B disponíveis.

- **workflows/**: Workflows de negócio para criação de empresas, cotações, etc.  
  JTBD: Orquestrar processos de negócio complexos.  
  Inputs: Passos de workflow, dados.  
  Outputs: Resultados de workflow.  
  Outcomes: Processos automatizados.

- **links/**: Links entre módulos Medusa.  
  JTBD: Conectar entidades de módulos diferentes.  
  Inputs: Definições de link.  
  Outputs: Relacionamentos estabelecidos.  
  Outcomes: Dados integrados.

- **jobs/**: Jobs agendados.  
  JTBD: Executar tarefas periódicas.  
  Inputs: Scripts de job.  
  Outputs: Tarefas executadas.  
  Outcomes: Manutenção automática.

- **subscribers/**: Event subscribers.  
  JTBD: Reagir a eventos do sistema.  
  Inputs: Handlers de evento.  
  Outputs: Ações disparadas.  
  Outcomes: Sistema responsivo.

- **admin/**: Customizações da UI Admin.  
  JTBD: Personalizar interface administrativa.  
  Inputs: Componentes UI.  
  Outputs: UI customizada.  
  Outcomes: Admin user-friendly.

- **scripts/**: Scripts utilitários.  
  JTBD: Automatizar tarefas de desenvolvimento.  
  Inputs: Scripts TypeScript.  
  Outputs: Tarefas executadas.  
  Outcomes: Eficiência no desenvolvimento.

### tests/
**JTBD**: Garantir a qualidade e confiabilidade do código através de testes unitários.  
**Inputs**: Código fonte, casos de teste.  
**Outputs**: Relatórios de teste, cobertura.  
**Outcomes**: Código testado, bugs identificados.

### docs/
**JTBD**: Documentar a arquitetura, APIs, integrações e processos do projeto.  
**Inputs**: Conhecimento do projeto, especificações.  
**Outputs**: Documentos Markdown, guias.  
**Outcomes**: Documentação acessível para desenvolvedores e usuários.

#### Subpastas:
- **implementation/**: Documentação de implementações (BACEN, calculadora solar).  
  JTBD: Detalhar integrações e features.  
  Inputs: Especificações técnicas.  
  Outputs: Guias de implementação.  
  Outcomes: Conhecimento compartilhado.

- **database/**: Documentação de banco de dados e migrações.  
  JTBD: Explicar estrutura e mudanças no DB.  
  Inputs: Scripts SQL, modelos.  
  Outputs: Relatórios de migração.  
  Outcomes: DB bem documentado.

- **integration/**: Guias de testes de integração.  
  JTBD: Instruir sobre testes HTTP.  
  Inputs: Casos de teste.  
  Outputs: Documentação de testes.  
  Outcomes: Testes padronizados.

### data/
**JTBD**: Armazenar dados do catálogo de produtos solares, inventário e dados de integração.  
**Inputs**: Dados de produtos, imagens, schemas.  
**Outputs**: Dados estruturados, exports.  
**Outcomes**: Catálogo populado, dados disponíveis para a aplicação.

#### Subpastas:
- **products-inventory/**: Inventário de produtos com imagens.  
  JTBD: Manter catálogo visual de produtos solares.  
  Inputs: Imagens de produtos.  
  Outputs: Inventário organizado.  
  Outcomes: Produtos exibíveis.

- **analysis/**: Dados de análise.  
  JTBD: Armazenar resultados de análises.  
  Inputs: Dados processados.  
  Outputs: Relatórios.  
  Outcomes: Insights disponíveis.

- **exports/**: Dados exportados.  
  JTBD: Preparar dados para exportação.  
  Inputs: Dados internos.  
  Outputs: Arquivos exportáveis.  
  Outcomes: Dados compartilháveis.

- **project-helios/**: Projeto específico.  
  JTBD: Gerenciar dados do projeto Helios.  
  Inputs: Dados do projeto.  
  Outputs: Projeto estruturado.  
  Outcomes: Projeto organizado.

- **scripts/**: Scripts de processamento de dados.  
  JTBD: Automatizar manipulação de dados.  
  Inputs: Scripts Python.  
  Outputs: Dados processados.  
  Outcomes: Eficiência na manipulação.

### data-platform/
**JTBD**: Gerenciar pipelines de dados e processamento com Dagster e Pathway.  
**Inputs**: Dados brutos, scripts de processamento.  
**Outputs**: Dados processados, insights.  
**Outcomes**: Plataforma de dados funcional para analytics.

#### Subpastas:
- **dagster/**: Pipelines Dagster.  
  JTBD: Orquestrar pipelines de dados.  
  Inputs: Definições de pipeline.  
  Outputs: Dados orquestrados.  
  Outcomes: Processamento automatizado.

- **pathway/**: Processamento com Pathway.  
  JTBD: Executar processamento de dados em tempo real.  
  Inputs: Scripts Pathway.  
  Outputs: Dados em tempo real.  
  Outcomes: Analytics real-time.

### database/
**JTBD**: Gerenciar migrações, backups e estrutura do banco de dados PostgreSQL.  
**Inputs**: Scripts SQL, modelos de dados.  
**Outputs**: Banco migrado, backups.  
**Outcomes**: Banco de dados consistente e versionado.

#### Subpastas:
- **migrations/**: Migrações SQL.  
  JTBD: Aplicar mudanças no schema do DB.  
  Inputs: Scripts de migração.  
  Outputs: Schema atualizado.  
  Outcomes: DB versionado.

### docker/
**JTBD**: Fornecer configurações Docker para containerização da aplicação e serviços.  
**Inputs**: Dockerfiles, docker-compose.  
**Outputs**: Imagens Docker, containers.  
**Outcomes**: Aplicação containerizada, fácil deployment.

### config/
**JTBD**: Configurar infraestrutura e serviços como Kong, Loki, Prometheus.  
**Inputs**: Arquivos de configuração YAML.  
**Outputs**: Serviços configurados.  
**Outcomes**: Infraestrutura monitorada e gerenciada.

#### Subpastas:
- **kong.yml**: Configuração API Gateway.  
  JTBD: Gerenciar rotas e autenticação.  
  Inputs: Regras de roteamento.  
  Outputs: Gateway configurado.  
  Outcomes: APIs protegidas.

- **loki.yml, prometheus.yml, promtail.yml**: Monitoramento.  
  JTBD: Coletar logs e métricas.  
  Inputs: Configs de monitoramento.  
  Outputs: Dados de observabilidade.  
  Outcomes: Sistema monitorado.

- **agents/**: Agentes de monitoramento.  
  JTBD: Executar agentes específicos.  
  Inputs: Configs de agentes.  
  Outputs: Métricas coletadas.  
  Outcomes: Observabilidade detalhada.

- **grafana/**: Dashboards Grafana.  
  JTBD: Visualizar métricas.  
  Inputs: Configs de dashboard.  
  Outputs: Dashboards.  
  Outcomes: Métricas visualizadas.

- **monitoring/**: Configs gerais de monitoramento.  
  JTBD: Centralizar configs de observabilidade.  
  Inputs: Arquivos YAML.  
  Outputs: Sistema monitorado.  
  Outcomes: Infraestrutura observável.

### scripts/
**JTBD**: Fornecer scripts utilitários para automação de tarefas de desenvolvimento e deployment.  
**Inputs**: Scripts PowerShell, Python.  
**Outputs**: Tarefas executadas, logs.  
**Outcomes**: Processos automatizados.

### secrets/
**JTBD**: Armazenar chaves e credenciais sensíveis de forma segura.  
**Inputs**: Credenciais, chaves API.  
**Outputs**: Credenciais criptografadas.  
**Outcomes**: Segurança de dados.

### static/
**JTBD**: Hospedar arquivos estáticos como imagens e assets.  
**Inputs**: Arquivos de mídia.  
**Outputs**: Arquivos servidos.  
**Outcomes**: Recursos estáticos disponíveis.

### integration-tests/
**JTBD**: Testar integrações entre módulos e APIs externas.  
**Inputs**: Testes HTTP, módulos.  
**Outputs**: Relatórios de integração.  
**Outcomes**: Integrações validadas.

#### Subpastas:
- **http/**: Testes HTTP por módulo.  
  JTBD: Validar endpoints API.  
  Inputs: Requests HTTP.  
  Outputs: Respostas validadas.  
  Outcomes: APIs testadas.

- **modules/**: Testes de módulos.  
  JTBD: Testar funcionalidades de módulos.  
  Inputs: Casos de teste.  
  Outputs: Módulos validados.  
  Outcomes: Módulos confiáveis.

- **utils/**: Utilitários de teste.  
  JTBD: Apoiar execução de testes.  
  Inputs: Scripts auxiliares.  
  Outputs: Ambiente de teste.  
  Outcomes: Testes eficientes.

### mcp-servers/
**JTBD**: Hospedar servidores MCP para funcionalidades específicas.  
**Inputs**: Código de servidores.  
**Outputs**: Servidores em execução.  
**Outcomes**: Funcionalidades MCP disponíveis.

### output/
**JTBD**: Armazenar saídas de processos, logs e resultados.  
**Inputs**: Dados de processamento.  
**Outputs**: Arquivos de saída.  
**Outcomes**: Resultados preservados.

### pact/
**JTBD**: Gerenciar contratos de API com testes Pact.  
**Inputs**: Definições de contrato.  
**Outputs**: Testes de contrato.  
**Outcomes**: APIs compatíveis.

### build/
**JTBD**: Scripts e configurações para build e deployment.  
**Inputs**: Scripts de build.  
**Outputs**: Artefatos de build.  
**Outcomes**: Aplicação pronta para deployment.

#### Subpastas:
- **aws/**: Scripts AWS.  
  JTBD: Automatizar deployment na AWS.  
  Inputs: Scripts de deployment.  
  Outputs: Recursos AWS.  
  Outcomes: Infraestrutura provisionada.

- **docker/**: Scripts Docker.  
  JTBD: Gerenciar builds Docker.  
  Inputs: Scripts de build.  
  Outputs: Imagens Docker.  
  Outcomes: Containers prontos.

- **scripts/**: Scripts gerais de build.  
  JTBD: Automatizar processos de build.  
  Inputs: Scripts utilitários.  
  Outputs: Builds executados.  
  Outcomes: Aplicação construída.

### aws-cloudformation/
**JTBD**: Templates CloudFormation para deployment na AWS.  
**Inputs**: Templates YAML.  
**Outputs**: Recursos AWS provisionados.  
**Outcomes**: Infraestrutura na nuvem.

### init-scripts/
**JTBD**: Scripts SQL para inicialização do banco de dados.  
**Inputs**: Scripts SQL.  
**Outputs**: Banco inicializado.  
**Outcomes**: Dados de seed inseridos.

## Arquivos de Configuração

### package.json
**JTBD**: Definir dependências e scripts do projeto Node.js.  
**Inputs**: Lista de pacotes, scripts.  
**Outputs**: Dependências instaladas.  
**Outcomes**: Ambiente de desenvolvimento configurado.

### medusa-config.ts
**JTBD**: Configurar a aplicação Medusa, módulos e feature flags.  
**Inputs**: Configurações de módulo.  
**Outputs**: App configurada.  
**Outcomes**: Medusa funcional.

### tsconfig.json
**JTBD**: Configurar compilação TypeScript.  
**Inputs**: Opções de compilação.  
**Outputs**: Código compilado.  
**Outcomes**: TypeScript validado.

### jest.config.js
**JTBD**: Configurar execução de testes Jest.  
**Inputs**: Configs de teste.  
**Outputs**: Testes executados.  
**Outcomes**: Código testado.

### eslint.config.js
**JTBD**: Configurar linting com ESLint.  
**Inputs**: Regras de linting.  
**Outputs**: Código lintado.  
**Outcomes**: Código padronizado.

### tailwind.config.js
**JTBD**: Configurar Tailwind CSS (se usado).  
**Inputs**: Configs de estilo.  
**Outputs**: Estilos gerados.  
**Outcomes**: UI estilizada.

### docker-compose.yml
**JTBD**: Definir serviços Docker para desenvolvimento.  
**Inputs**: Definições de serviço.  
**Outputs**: Ambiente containerizado.  
**Outcomes**: Desenvolvimento local facilitado.

### requirements.txt
**JTBD**: Listar dependências Python.  
**Inputs**: Pacotes Python.  
**Outputs**: Dependências instaladas.  
**Outcomes**: Scripts Python funcionais.

### run_extraction.py
**JTBD**: Executar extração de dados.  
**Inputs**: Dados de entrada.  
**Outputs**: Dados extraídos.  
**Outcomes**: Dados processados.

### fallback_api.py
**JTBD**: API de fallback em Python.  
**Inputs**: Requests.  
**Outputs**: Respostas.  
**Outcomes**: API alternativa.

## Scripts PowerShell

### auto-init-aws.ps1
**JTBD**: Inicializar ambiente AWS automaticamente.  
**Inputs**: Credenciais AWS.  
**Outputs**: Ambiente configurado.  
**Outcomes**: AWS pronto.

### build-optimized-images.ps1
**JTBD**: Construir imagens Docker otimizadas.  
**Inputs**: Dockerfiles.  
**Outputs**: Imagens otimizadas.  
**Outcomes**: Deployment eficiente.

### cleanup-old-images.ps1
**JTBD**: Limpar imagens Docker antigas.  
**Inputs**: Imagens existentes.  
**Outputs**: Espaço liberado.  
**Outcomes**: Manutenção de storage.

### quick-aws-setup.ps1
**JTBD**: Setup rápido de AWS.  
**Inputs**: Configs AWS.  
**Outputs**: Recursos provisionados.  
**Outcomes**: Ambiente AWS rápido.

## Outros Arquivos

### README.md
**JTBD**: Documentar o projeto e instruções de uso.  
**Inputs**: Informações do projeto.  
**Outputs**: Documento de boas-vindas.  
**Outcomes**: Usuários informados.

### INDEX.md
**JTBD**: Índice de documentação.  
**Inputs**: Links de docs.  
**Outputs**: Navegação facilitada.  
**Outcomes**: Documentação acessível.

### PROGRESSO_SEQUENCIA.md
**JTBD**: Rastrear progresso de desenvolvimento.  
**Inputs**: Atualizações de progresso.  
**Outputs**: Relatório de andamento.  
**Outcomes**: Visibilidade do progresso.

### REORGANIZATION_SUMMARY.md
**JTBD**: Resumir reorganização do projeto.  
**Inputs**: Mudanças estruturais.  
**Outputs**: Sumário de mudanças.  
**Outcomes**: Contexto de reorganização.

### .gitignore
**JTBD**: Especificar arquivos a ignorar no Git.  
**Inputs**: Padrões de arquivo.  
**Outputs**: Repositório limpo.  
**Outcomes**: Controle de versão eficiente.

### .env*
**JTBD**: Armazenar variáveis de ambiente.  
**Inputs**: Valores de config.  
**Outputs**: Ambiente configurado.  
**Outcomes**: Configs seguras.

### yarn.lock
**JTBD**: Bloquear versões de dependências.  
**Inputs**: Dependências resolvidas.  
**Outputs**: Builds reprodutíveis.  
**Outcomes**: Consistência de dependências.</content>
<parameter name="filePath">C:/Users/fjuni/OneDrive/Documentos/GitHub/ysh-b2b/backend/index-360.md