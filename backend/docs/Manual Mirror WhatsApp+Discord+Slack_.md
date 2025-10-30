

# **Manual de Desenvolvimento: Aplicação Unificada de Mensagens (WhatsApp, Discord, Slack) com Next.js, FastAPI e Arquitetura Serverless**

## **Capítulo 1: Introdução e Visão Geral do Projeto**

Este manual detalha o processo de desenvolvimento de uma aplicação robusta e escalável que espelha funcionalidades de plataformas de mensagens populares como WhatsApp, Discord e Slack. O objetivo é criar uma interface unificada onde os usuários possam interagir com suas contas dessas três plataformas em um único local. A arquitetura proposta combina um frontend moderno construído com Next.js e Shadcn/ui, um backend serverless performático em Python com FastAPI, um banco de dados PostgreSQL confiável, e práticas de desenvolvimento ágil como automação de fluxos de trabalho e Infraestrutura como Código (IaC).  
A escolha dessas tecnologias visa otimizar a performance, a experiência do desenvolvedor (DX), a escalabilidade e a manutenibilidade da aplicação. O Next.js oferece renderização do lado do servidor (SSR) e geração de sites estáticos (SSG), resultando em interfaces rápidas e otimizadas para SEO. Shadcn/ui, por sua vez, permite a criação de interfaces de usuário elegantes e personalizáveis, construídas sobre primitivas Radix UI e Tailwind CSS, com a vantagem de que os componentes são copiados para o projeto, permitindo total controle e customização.1  
O backend com FastAPI em modo serverless garante escalabilidade automática e custos otimizados, pagando-se apenas pelo uso. FastAPI é conhecido por sua alta performance e facilidade de desenvolvimento de APIs, aproveitando type hints do Python para validação de dados e geração automática de documentação OpenAPI.3 O PostgreSQL foi escolhido por sua robustez, funcionalidades avançadas e suporte a transações complexas, essencial para gerenciar dados de múltiplas plataformas de mensagens.  
A utilização de um monorepo gerenciado pelo Turborepo facilitará o compartilhamento de código, a consistência entre o frontend e o backend (especialmente tipos TypeScript gerados a partir do OpenAPI do FastAPI) e a otimização dos processos de build e deploy.5 A automação de fluxos de trabalho, incluindo a geração de clientes de API e a integração contínua/entrega contínua (CI/CD), será crucial para manter a agilidade e a qualidade do desenvolvimento. A Infraestrutura como Código (IaC) com Terraform garantirá que o provisionamento e a gestão da infraestrutura sejam versionáveis, repetíveis e automatizados.  
Este manual servirá como um guia compreensivo, cobrindo desde a configuração inicial do ambiente de desenvolvimento até o deployment e manutenção da aplicação, com foco em melhores práticas e otimizações.

## **Capítulo 2: Arquitetura da Aplicação**

A arquitetura da aplicação "Mirror WhatsApp+Discord+Slack" foi concebida para ser modular, escalável e de fácil manutenção, aproveitando as forças de cada tecnologia escolhida.

### **2.1. Visão Geral da Arquitetura**

O sistema será composto por três componentes principais:

1. **Frontend:** Uma aplicação Next.js responsável pela interface do usuário, interação e apresentação dos dados agregados das plataformas de mensagens. Utilizará Shadcn/ui para os componentes visuais.  
2. **Backend:** Uma API serverless construída com FastAPI (Python), responsável pela lógica de negócios, integração com as APIs das plataformas de mensagens (WhatsApp, Discord, Slack), gerenciamento de autenticação de usuários e persistência de dados.  
3. **Banco de Dados:** Uma instância PostgreSQL para armazenar informações dos usuários, configurações de contas vinculadas, tokens de acesso (criptografados) e, potencialmente, um cache de mensagens (considerando as políticas de cada plataforma).

A comunicação entre o frontend e o backend ocorrerá via requisições HTTP (RESTful API). O backend, por sua vez, se comunicará com as APIs externas do WhatsApp, Discord e Slack. Para atualizações em tempo real do backend para o frontend (por exemplo, novas mensagens recebidas), serão utilizados WebSockets ou Server-Sent Events (SSE), com o FastAPI gerenciando as conexões e o Next.js consumindo esses eventos.  
*Diagrama da Arquitetura (Alto Nível):*

Snippet de código

graph TD  
    A\[Usuário\] \--\> B(Frontend \- Next.js \+ Shadcn/ui);  
    B \--\> C{API Gateway};  
    C \--\> D;  
    D \--\> E;  
    D \--\> F\[API do WhatsApp\];  
    D \--\> G;  
    D \--\> H;  
    F \--\> D;  
    G \--\> D;  
    H \--\> D;

    subgraph "Plataformas Externas"  
        F  
        G  
        H  
    end

    subgraph "Nossa Aplicação"  
        B  
        C  
        D  
        E  
    end

### **2.2. Componentes Detalhados**

* **Frontend (Next.js \+ Shadcn/ui):**  
  * **Responsabilidades:** Interface do usuário, gerenciamento de estado local (e.g., Zustand ou React Query), autenticação do usuário (interagindo com o backend), exibição de mensagens agregadas, envio de mensagens através do backend, configuração de contas vinculadas.  
  * **Tecnologias Chave:** Next.js (App Router), React, TypeScript, Shadcn/ui, Tailwind CSS.  
  * A estrutura de componentes do Shadcn/ui permitirá a criação de uma interface de usuário coesa e personalizável, onde os desenvolvedores têm controle total sobre o código dos componentes, pois eles são adicionados diretamente ao projeto.1  
* **Backend (FastAPI Serverless):**  
  * **Responsabilidades:**  
    * Autenticação e autorização de usuários da aplicação (e.g., JWT).  
    * Gerenciamento seguro (criptografia) e atualização de tokens OAuth das plataformas externas (WhatsApp, Discord, Slack).  
    * Abstração das APIs das plataformas de mensagens, fornecendo endpoints unificados para o frontend.  
    * Recebimento de webhooks das plataformas para atualizações em tempo real (novas mensagens, status, etc.).  
    * Envio de mensagens para as plataformas em nome do usuário.  
    * Lógica de agregação e formatação de dados de mensagens.  
    * Gerenciamento de conexões WebSocket/SSE para atualizações em tempo real para o frontend.  
  * **Tecnologias Chave:** FastAPI, Python, Pydantic (para validação de dados e modelos), SQLAlchemy ou SQLModel (para interação com o banco de dados), python-multipart para formulários OAuth2.7  
  * A natureza serverless (e.g., AWS Lambda, Vercel Functions) garante que o backend escale automaticamente com a demanda e otimize custos.4  
* **Banco de Dados (PostgreSQL):**  
  * **Responsabilidades:**  
    * Armazenar dados dos usuários da aplicação (perfis, credenciais de login da nossa aplicação).  
    * Armazenar tokens de acesso e refresh tokens (criptografados) para as plataformas WhatsApp, Discord e Slack vinculadas por cada usuário.  
    * Manter o mapeamento entre usuários da nossa aplicação e suas identidades nas plataformas externas.  
    * Potencialmente, armazenar metadados de mensagens ou um cache temporário, respeitando as políticas de privacidade e termos de serviço de cada plataforma.  
  * **Tecnologias Chave:** PostgreSQL. A escolha entre SQLAlchemy e SQLModel para interagir com o PostgreSQL será detalhada posteriormente, mas ambas oferecem suporte assíncrono robusto.9  
* **Monorepo (Turborepo):**  
  * **Responsabilidades:** Gerenciar o código do frontend, backend e pacotes compartilhados (e.g., tipos TypeScript, configurações de lint) em um único repositório. Otimizar builds, testes e processos de desenvolvimento.  
  * **Tecnologias Chave:** Turborepo, pnpm (ou Yarn/npm workspaces).  
  * O Turborepo agiliza os builds incrementais e o cache local e distribuído, economizando tempo de desenvolvimento.6

### **2.3. Fluxo de Dados e Interações**

1. **Autenticação do Usuário na Aplicação:**  
   * O usuário se registra/loga na aplicação "Mirror" através do frontend.  
   * O frontend envia as credenciais para o backend FastAPI.  
   * O backend valida as credenciais, gera um JWT para o usuário da aplicação "Mirror" e o retorna ao frontend.  
   * O frontend armazena o JWT (e.g., em cookies HttpOnly ou localStorage, dependendo da estratégia de segurança) e o envia em requisições subsequentes.  
2. **Vinculação de Contas Externas (Exemplo: Discord):**  
   * No frontend, o usuário inicia o processo de vinculação da conta Discord.  
   * O frontend redireciona o usuário para a página de autorização OAuth2 do Discord.  
   * Após a autorização, o Discord redireciona de volta para um endpoint de callback no backend FastAPI, com um código de autorização.  
   * O backend FastAPI troca o código de autorização por tokens de acesso e refresh do Discord.  
   * O backend armazena esses tokens de forma segura (criptografados) no PostgreSQL, associados ao usuário da aplicação "Mirror".  
3. **Recebimento de Mensagens (Exemplo: Nova mensagem no WhatsApp):**  
   * A API do WhatsApp envia um webhook para um endpoint configurado no backend FastAPI.  
   * O backend FastAPI processa o webhook, identifica o usuário correspondente e a nova mensagem.  
   * O backend armazena/atualiza a mensagem (ou metadados) no PostgreSQL, se aplicável.  
   * O backend envia uma notificação em tempo real (via WebSocket/SSE) para o frontend do usuário conectado.  
   * O frontend recebe a notificação e atualiza a interface para exibir a nova mensagem.  
4. **Envio de Mensagens (Exemplo: Enviar mensagem para um canal Slack):**  
   * No frontend, o usuário redige uma mensagem e seleciona o destino (um canal Slack).  
   * O frontend envia a solicitação de envio para o backend FastAPI.  
   * O backend FastAPI recupera os tokens de acesso do Slack para o usuário (do PostgreSQL, descriptografando-os).  
   * O backend utiliza a API do Slack para enviar a mensagem.  
   * O backend informa ao frontend o status do envio.

### **2.4. Considerações de Escalabilidade e Performance**

* **Backend Serverless:** A arquitetura serverless do FastAPI permite escalabilidade horizontal automática, lidando com picos de tráfego sem provisionamento manual de servidores.8  
* **Banco de Dados:** O PostgreSQL é capaz de lidar com grandes volumes de dados e conexões concorrentes. O uso de um serviço gerenciado de PostgreSQL (e.g., AWS RDS, Neon) pode simplificar a escalabilidade e manutenção.  
* **Frontend Otimizado:** O Next.js com SSR/SSG e otimizações de build garante tempos de carregamento rápidos.  
* **Comunicação em Tempo Real:** WebSockets ou SSE serão usados para evitar polling constante, reduzindo a carga no servidor e melhorando a latência para atualizações em tempo real.12 A escolha entre WebSockets (bidirecional) e SSE (unidirecional servidor-cliente) dependerá da necessidade de comunicação do cliente para o servidor através do mesmo canal de tempo real. Para simples notificações do servidor, SSE pode ser mais leve.12  
* **Caching:** O Turborepo implementa caching de builds.6 O frontend pode implementar caching de dados com React Query ou SWR. O backend pode utilizar caching em memória (e.g., Redis, se necessário) para dados frequentemente acessados.

A modularidade da arquitetura permite que cada componente seja escalado e otimizado independentemente, conforme necessário. A clara separação de responsabilidades entre frontend, backend e as integrações de API externas facilita o desenvolvimento paralelo e a manutenção.

## **Capítulo 3: Configuração do Ambiente de Desenvolvimento**

A configuração de um ambiente de desenvolvimento consistente e eficiente é crucial para o sucesso do projeto. Este capítulo detalha os passos para configurar o monorepo com Turborepo, o frontend Next.js, o backend FastAPI e as ferramentas de desenvolvimento associadas.

### **3.1. Ferramentas e Pré-requisitos**

Antes de iniciar, certifique-se de ter as seguintes ferramentas instaladas:

* **Node.js:** Versão LTS mais recente (e.g., 20.x ou superior).  
* **pnpm:** Gerenciador de pacotes recomendado para monorepos com Turborepo (alternativamente, Yarn ou npm com workspaces).  
* **Python:** Versão 3.9 ou superior.  
* **uv:** Um instalador e resolvedor de pacotes Python extremamente rápido, recomendado para gerenciar dependências Python.14 Alternativamente, Poetry ou PDM podem ser usados.16  
* **Docker e Docker Compose:** Para executar o PostgreSQL e outros serviços localmente de forma isolada.  
* **Git:** Para controle de versão.  
* **Turborepo CLI:** Pode ser instalado globalmente ou usado via npx.

### **3.2. Estrutura do Monorepo com Turborepo**

O Turborepo será utilizado para gerenciar o monorepo, otimizando os processos de build e facilitando o compartilhamento de código.6 A estrutura de diretórios sugerida é:

/  
├── apps/  
│   ├── web/          \# Aplicação Next.js (Frontend)  
│   │   ├── app/  
│   │   ├── public/  
│   │   ├── components/ui/ \# Componentes Shadcn/ui  
│   │   ├── next.config.js  
│   │   ├── package.json  
│   │   └── tsconfig.json  
│   └── api/          \# Aplicação FastAPI (Backend)  
│       ├── app/      \# Código principal da API (routers, services, models)  
│       ├── tests/  
│       ├── pyproject.toml \# ou requirements.txt gerenciado por uv  
│       └── Dockerfile    \# Para build da imagem (opcional, se não usar Vercel Functions)  
├── packages/  
│   ├── ui/           \# Pacote de componentes UI compartilhados (se necessário além de Shadcn)  
│   │   ├── src/  
│   │   ├── package.json  
│   │   └── tsconfig.json  
│   ├── config/       \# Configurações compartilhadas (ESLint, Prettier, TypeScript)  
│   │   ├── eslint-preset.js  
│   │   └── tsconfig.base.json  
│   └── api-client/   \# Cliente TypeScript gerado a partir do OpenAPI do FastAPI  
│       ├── src/  
│       ├── package.json  
│       └── tsconfig.json  
├── pnpm-workspace.yaml \# Configuração do workspace pnpm  
├── package.json        \# package.json raiz  
└── turbo.json          \# Configuração do Turborepo

* **apps/**: Contém as aplicações principais (frontend web e backend api).  
* **packages/**: Contém pacotes reutilizáveis:  
  * ui: Componentes React customizados, se necessário, que podem ser usados pelo apps/web.  
  * config: Configurações centralizadas de ESLint, Prettier e TypeScript (tsconfig.base.json) para garantir consistência.18  
  * api-client: Cliente TypeScript gerado automaticamente a partir da especificação OpenAPI do backend FastAPI, garantindo type safety entre frontend e backend.3

#### **3.2.1. Inicializando o Monorepo**

1. Crie o diretório raiz do projeto: mkdir mirror-app && cd mirror-app  
2. Inicialize um projeto pnpm: pnpm init  
3. Crie o arquivo pnpm-workspace.yaml na raiz com o seguinte conteúdo para definir os workspaces 20:  
   YAML  
   packages:  
     \- 'apps/\*'  
     \- 'packages/\*'

4. Instale o Turborepo como uma dependência de desenvolvimento no root package.json:  
   pnpm add turbo \--save-dev \-w  
5. Crie o arquivo turbo.json na raiz. Uma configuração inicial básica pode ser 11:  
   JSON  
   {  
     "$schema": "https://turborepo.org/schema.json",  
     "globalDependencies": \["\*\*/.env.\*local"\],  
     "pipeline": {  
       "build": {  
         "dependsOn": \["^build"\],  
         "outputs": \[".next/\*\*", "\!.next/cache/\*\*", "dist/\*\*", ".vercel/output/\*\*"\]  
       },  
       "lint": {  
         "outputs":  
       },  
       "dev": {  
         "cache": false,  
         "persistent": true  
       },  
       "test": {  
         "dependsOn": \["build"\],  
         "outputs": \["coverage/\*\*"\]  
       },  
       "clean": {  
         "cache": false  
       }  
     }  
   }

   Esta configuração define tarefas comuns como build, lint, dev e test. A dependsOn: \["^build"\] indica que a tarefa build em um pacote depende da conclusão da tarefa build em suas dependências internas.21 outputs define os artefatos que o Turborepo deve cachear.22

### **3.3. Configuração do Frontend (Next.js e Shadcn/ui)**

1. Criar a Aplicação Next.js:  
   Navegue até o diretório apps e crie a aplicação Next.js:  
   cd apps  
   pnpm create next-app web \--typescript \--tailwind \--eslint \--app \--src-dir \--import-alias "@/\*"  
   Isso criará uma nova aplicação Next.js chamada web usando TypeScript, Tailwind CSS, ESLint, o App Router, um diretório src, e um alias de importação @/\*.  
2. Instalar Shadcn/ui:  
   Navegue até o diretório apps/web: cd web  
   Inicialize o Shadcn/ui 24:  
   pnpm dlx shadcn-ui@latest init  
   Siga as instruções, configurando o caminho para os componentes (e.g., src/components/ui) e outros padrões. Isso criará o diretório components.json e as pastas necessárias.  
3. Adicionar Componentes Shadcn/ui:  
   Adicione os componentes necessários conforme o design da aplicação. Por exemplo:  
   pnpm dlx shadcn-ui@latest add button card input avatar sheet dialog dropdown-menu scroll-area  
   Os componentes serão adicionados ao diretório src/components/ui.24  
4. Configurar package.json em apps/web:  
   Adicione scripts para dev, build, start, lint e test.  
   JSON  
   // apps/web/package.json  
   {  
     "name": "web",  
     "version": "0.1.0",  
     "private": true,  
     "scripts": {  
       "dev": "next dev",  
       "build": "next build",  
       "start": "next start",  
       "lint": "next lint",  
       "test": "jest" // Exemplo, configure o Jest ou Vitest  
     },  
     "dependencies": {  
       //... Next.js, React, Tailwind, Shadcn/ui helpers  
       "next": "14.x.x",  
       "react": "^18",  
       "react-dom": "^18",  
       "lucide-react": "...",  
       "class-variance-authority": "...",  
       "clsx": "...",  
       "tailwind-merge": "...",  
       "@radix-ui/...": "..." // Dependências do Shadcn  
     },  
     "devDependencies": {  
       //... ESLint, TypeScript, PostCSS, Autoprefixer, Jest/Vitest  
       "@types/node": "^20",  
       "@types/react": "^18",  
       "@types/react-dom": "^18",  
       "typescript": "^5",  
       "eslint": "^8",  
       "eslint-config-next": "14.x.x",  
       "postcss": "^8",  
       "tailwindcss": "^3.4.1"  
     }  
   }

### **3.4. Configuração do Backend (FastAPI e Python)**

1. Criar a Estrutura do Projeto FastAPI:  
   No diretório apps/api, crie a seguinte estrutura:  
   apps/api/  
   ├── app/  
   │   ├── \_\_init\_\_.py  
   │   ├── main.py         \# Ponto de entrada da aplicação FastAPI  
   │   ├── core/           \# Configurações, segurança  
   │   │   ├── \_\_init\_\_.py  
   │   │   └── config.py  
   │   ├── db/             \# Lógica de banco de dados (SQLModel/SQLAlchemy, sessões)  
   │   │   ├── \_\_init\_\_.py  
   │   │   └── session.py  
   │   ├── models/         \# Modelos de dados (Pydantic/SQLModel)  
   │   │   └── \_\_init\_\_.py  
   │   ├── schemas/        \# Esquemas Pydantic para request/response  
   │   │   └── \_\_init\_\_.py  
   │   ├── crud/           \# Funções CRUD  
   │   │   └── \_\_init\_\_.py  
   │   └── routers/        \# Módulos de rotas da API  
   │       ├── \_\_init\_\_.py  
   │       └── auth.py     \# Exemplo de rota de autenticação  
   ├── tests/              \# Testes unitários e de integração  
   │   └── \_\_init\_\_.py  
   ├──.env                \# Variáveis de ambiente locais  
   ├──.gitignore  
   ├── pyproject.toml      \# Para gerenciamento de dependências com uv/Poetry/PDM  
   └── README.md

   Esta estrutura modular organiza o código por funcionalidade, facilitando a manutenção e escalabilidade.14  
2. Gerenciamento de Dependências Python com uv:  
   uv é recomendado por sua velocidade.14 No diretório apps/api:  
   * Inicialize um ambiente virtual (opcional, mas recomendado): uv venv  
   * Ative o ambiente virtual: source.venv/bin/activate (Linux/macOS) ou .venv\\Scripts\\activate (Windows).  
   * Instale as dependências principais:  
     uv pip install fastapi uvicorn\[standard\] pydantic sqlalchemy asyncpg psycopg2-binary python-jose\[cryptography\] passlib\[bcrypt\] python-multipart cryptography requests-oauthlib httpx-oauth  
     * fastapi: O framework web.3  
     * uvicorn\[standard\]: Servidor ASGI para rodar FastAPI.17  
     * pydantic: Para validação de dados.28  
     * sqlalchemy: ORM para interagir com PostgreSQL.9  
     * asyncpg, psycopg2-binary: Drivers assíncronos e síncronos para PostgreSQL. asyncpg é crucial para operações assíncronas com SQLAlchemy.10  
     * python-jose\[cryptography\]: Para manipulação de JWT.29  
     * passlib\[bcrypt\]: Para hashing de senhas.29  
     * python-multipart: Para parsing de form data, necessário para OAuth2 password flow.7  
     * cryptography: Para criptografar tokens de API externos.32  
     * requests-oauthlib / httpx-oauth: Para interagir com provedores OAuth2 externos (WhatsApp, Discord, Slack).33  
   * Gere o requirements.txt a partir do pyproject.toml se estiver usando uv com pyproject.toml, ou mantenha as dependências no pyproject.toml se usar Poetry/PDM. Para uv puro, pode-se usar uv pip freeze \> requirements.txt.  
   * Para desenvolvimento, adicione linters e formatadores: uv pip install ruff black mypy \--group dev (se uv suportar grupos como PDM, ou adicione ao dev-dependencies no pyproject.toml).  
3. Configurar package.json em apps/api para Scripts Turborepo:  
   Embora seja um projeto Python, para integrá-lo ao pipeline do Turborepo, um package.json simples é necessário em apps/api para definir scripts que o Turborepo possa executar.  
   JSON  
   // apps/api/package.json  
   {  
     "name": "api",  
     "version": "0.1.0",  
     "private": true,  
     "scripts": {  
       "dev": "uv run uvicorn app.main:app \--host 0.0.0.0 \--port 8000 \--reload",  
       "lint": "uv run ruff check. && uv run black. \--check && uv run mypy.",  
       "format": "uv run ruff check. \--fix && uv run black.",  
       "test": "uv run pytest",  
       "build:openapi": "uv run python app/core/generate\_openapi.py", // Script para gerar openapi.json  
       "build:lambda": "uv run python scripts/package\_lambda.py" // Script para empacotar para Lambda  
     }  
   }

   * Os scripts dev, lint, format, test usam uv run para executar comandos Python dentro do ambiente virtual gerenciado pelo uv (ou poetry run, pdm run se estiver usando essas ferramentas).15  
   * build:openapi: Este script customizado (a ser criado) irá gerar o openapi.json a partir da aplicação FastAPI.  
   * build:lambda: Este script customizado (a ser criado) irá empacotar a aplicação FastAPI e suas dependências em um arquivo.zip para deploy no AWS Lambda.

### **3.5. Configuração do Pacote api-client**

Este pacote irá conter o cliente TypeScript gerado a partir do openapi.json do backend.

1. Criar a Estrutura do Pacote:  
   Em packages/api-client:  
   packages/api-client/  
   ├── src/                \# Código gerado do cliente  
   │   └── index.ts  
   ├── package.json  
   ├── tsconfig.json  
   └── openapi-ts.config.ts \# Configuração para @hey-api/openapi-ts

2. **Configurar package.json em packages/api-client:**  
   JSON  
   // packages/api-client/package.json  
   {  
     "name": "@repo/api-client",  
     "version": "0.1.0",  
     "private": true,  
     "main": "./src/index.ts",  
     "types": "./src/index.ts",  
     "scripts": {  
       "generate:client": "openapi-ts \--config./openapi-ts.config.ts",  
       "clean": "rm \-rf src/\*"  
     },  
     "devDependencies": {  
       "@hey-api/openapi-ts": "^0.x.x", // Use a versão mais recente  
       "typescript": "^5"  
     }  
   }

   O script generate:client usa a CLI @hey-api/openapi-ts para gerar o cliente.37  
3. **Configurar openapi-ts.config.ts:**  
   TypeScript  
   // packages/api-client/openapi-ts.config.ts  
   import { defineConfig } from '@hey-api/openapi-ts';

   export default defineConfig({  
     input: '../../apps/api/openapi.json', // Caminho para o openapi.json gerado pelo backend  
     output: './src',  
     client: '@hey-api/client-fetch', // ou '@hey-api/client-axios'  
     // Mais configurações conforme necessário  
   });

   Este arquivo configura o gerador de cliente, especificando o local do openapi.json e o diretório de saída para o cliente gerado.37

### **3.6. Configuração do Pacote config**

Este pacote centraliza as configurações de linting e TypeScript.

1. **Criar packages/config/eslint-preset.js:**  
   JavaScript  
   // packages/config/eslint-preset.js  
   module.exports \= {  
     extends: \["next/core-web-vitals", "eslint:recommended", "plugin:prettier/recommended"\],  
     // Adicione regras customizadas se necessário  
   };

2. **Criar packages/config/tsconfig.base.json:**  
   JSON  
   // packages/config/tsconfig.base.json  
   {  
     "compilerOptions": {  
       "target": "es2017",  
       "lib": \["dom", "dom.iterable", "esnext"\],  
       "allowJs": true,  
       "skipLibCheck": true,  
       "strict": true,  
       "forceConsistentCasingInFileNames": true,  
       "noEmit": true,  
       "esModuleInterop": true,  
       "module": "esnext",  
       "moduleResolution": "bundler", // ou "node" dependendo da versão do TS/Node  
       "resolveJsonModule": true,  
       "isolatedModules": true,  
       "jsx": "preserve",  
       "incremental": true,  
       "plugins": \[  
         {  
           "name": "next"  
         }  
       \]  
     },  
     "include":,  
     "exclude": \["node\_modules"\]  
   }

3. **Configurar package.json em packages/config:**  
   JSON  
   // packages/config/package.json  
   {  
     "name": "@repo/config",  
     "version": "0.1.0",  
     "private": true,  
     "files": \[  
       "eslint-preset.js",  
       "tsconfig.base.json"  
     \],  
     "devDependencies": {  
       "eslint-config-next": "14.x.x",  
       "eslint-plugin-prettier": "...",  
       "eslint-config-prettier": "..."  
     }  
   }

As aplicações e outros pacotes no monorepo irão estender essas configurações base em seus respectivos eslintrc.js e tsconfig.json.

### **3.7. Configuração do Docker para PostgreSQL**

Crie um arquivo docker-compose.yml na raiz do projeto para rodar o PostgreSQL localmente:

YAML

version: '3.8'  
services:  
  postgres\_db:  
    image: postgres:15  
    container\_name: mirror\_app\_postgres  
    environment:  
      POSTGRES\_USER: admin  
      POSTGRES\_PASSWORD: password  
      POSTGRES\_DB: mirror\_app\_db  
    ports:  
      \- "5432:5432"  
    volumes:  
      \- postgres\_data:/var/lib/postgresql/data  
    restart: unless-stopped

volumes:  
  postgres\_data:

Execute docker-compose up \-d para iniciar o container do PostgreSQL. As credenciais e o nome do banco de dados devem ser referenciados nos arquivos .env do backend.

### **3.8. Variáveis de Ambiente**

Cada aplicação (apps/web, apps/api) deve ter seu próprio arquivo .env.local (para Next.js) ou .env (para FastAPI) para armazenar variáveis de ambiente específicas do desenvolvimento local. Estes arquivos devem ser incluídos no .gitignore global.

* **apps/web/.env.local:**  
  NEXT\_PUBLIC\_API\_BASE\_URL=http://localhost:8000/api/v1

* **apps/api/.env:**  
  DATABASE\_URL=postgresql+asyncpg://admin:password@localhost:5432/mirror\_app\_db  
  SECRET\_KEY=your\_strong\_secret\_key\_for\_jwt  
  ALGORITHM=HS256  
  ACCESS\_TOKEN\_EXPIRE\_MINUTES=30  
  REFRESH\_TOKEN\_EXPIRE\_DAYS=7  
  \# API Keys para WhatsApp, Discord, Slack (serão adicionadas posteriormente)  
  WHATSAPP\_API\_TOKEN=  
  DISCORD\_CLIENT\_ID=  
  DISCORD\_CLIENT\_SECRET=  
  SLACK\_CLIENT\_ID=  
  SLACK\_CLIENT\_SECRET=  
  \# Fernet key for encrypting external tokens  
  FERNET\_ENCRYPTION\_KEY=your\_fernet\_key\_here

  A FERNET\_ENCRYPTION\_KEY deve ser gerada de forma segura (e.g., Fernet.generate\_key()) e armazenada de forma segura em produção (e.g., AWS Secrets Manager, HashiCorp Vault).32

Com esta configuração, o ambiente de desenvolvimento está pronto. O Turborepo gerenciará as tarefas, o Next.js servirá o frontend, o FastAPI o backend, e o Docker o banco de dados. A comunicação entre o frontend e o backend durante o desenvolvimento local pode ser direta ou através de um proxy configurado no Next.js, se necessário (detalhado no Capítulo 6).

## **Capítulo 4: Desenvolvimento do Backend com FastAPI**

O backend, construído com FastAPI, é o coração da aplicação, responsável por toda a lógica de negócios, integrações com APIs externas e gerenciamento de dados. Este capítulo aborda a implementação dos principais componentes do backend.

### **4.1. Modelos de Dados (Pydantic e SQLModel/SQLAlchemy)**

Pydantic será usado extensivamente para validação de dados de entrada e saída nas rotas da API e para configurações.28 Para a interação com o banco de dados PostgreSQL, SQLModel é uma opção que combina Pydantic e SQLAlchemy, oferecendo uma experiência de desenvolvimento coesa com FastAPI.9 Alternativamente, SQLAlchemy puro pode ser usado para maior flexibilidade e maturidade, especialmente em cenários complexos ou quando a documentação do SQLModel é insuficiente.9 Dada a natureza do projeto e a necessidade de operações assíncronas, a escolha deve priorizar o suporte robusto a async/await.  
**Considerações SQLModel vs. SQLAlchemy (Async):**

* **SQLModel:**  
  * **Prós:** Integração nativa com Pydantic, sintaxe mais concisa para CRUD e modelos, bom para a produtividade em cenários comuns com FastAPI.9  
  * **Contras:** Documentação menos extensa que SQLAlchemy, pode faltar funcionalidades para casos de uso muito avançados ou específicos, e a maturidade para cenários assíncronos complexos pode ser uma preocupação para alguns desenvolvedores.9 A compatibilidade com versões mais recentes do SQLAlchemy também pode ser um fator.39  
* **SQLAlchemy (com Pydantic para schemas de API):**  
  * **Prós:** Extremamente maduro, documentação vasta, grande comunidade, suporte robusto a operações assíncronas (com AsyncSession), flexibilidade total para queries complexas e funcionalidades de banco de dados avançadas.9  
  * **Contras:** Curva de aprendizado mais íngreme, pode exigir mais boilerplate para definir modelos de tabela e schemas Pydantic separadamente, embora isso também ofereça uma separação clara de responsabilidades.9

**Recomendação:** Para este projeto, iniciar com **SQLAlchemy puro** para a camada de ORM e Pydantic para os schemas de API é a abordagem mais segura e flexível, garantindo acesso a todas as funcionalidades do SQLAlchemy e um ecossistema de suporte mais amplo, especialmente para operações assíncronas complexas e migrações com Alembic.9  
**Exemplo de Modelos (SQLAlchemy e Pydantic):**

* **apps/api/app/models/user.py (Modelos SQLAlchemy):**  
  Python  
  from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary  
  from sqlalchemy.orm import relationship  
  from sqlalchemy.sql import func  
  from app.db.base\_class import Base \# Base declarativa do SQLAlchemy

  class User(Base):  
      \_\_tablename\_\_ \= "users"  
      id \= Column(Integer, primary\_key=True, index=True)  
      email \= Column(String, unique=True, index=True, nullable=False)  
      hashed\_password \= Column(String, nullable=False)  
      full\_name \= Column(String, index=True)  
      is\_active \= Column(Boolean(), default=True)  
      created\_at \= Column(DateTime(timezone=True), server\_default=func.now())  
      updated\_at \= Column(DateTime(timezone=True), onupdate=func.now())

      linked\_accounts \= relationship("LinkedAccount", back\_populates="owner")

  class LinkedAccount(Base):  
      \_\_tablename\_\_ \= "linked\_accounts"  
      id \= Column(Integer, primary\_key=True, index=True)  
      user\_id \= Column(Integer, ForeignKey("users.id"), nullable=False)  
      platform\_name \= Column(String, nullable=False) \# "whatsapp", "discord", "slack"  
      platform\_user\_id \= Column(String, nullable=False) \# ID do usuário na plataforma externa  
      encrypted\_access\_token \= Column(LargeBinary, nullable=False) \# Tokens criptografados  
      encrypted\_refresh\_token \= Column(LargeBinary, nullable=True)  
      scopes \= Column(String, nullable=True) \# JSON string ou CSV de escopos  
      expires\_at \= Column(DateTime(timezone=True), nullable=True)  
      created\_at \= Column(DateTime(timezone=True), server\_default=func.now())  
      updated\_at \= Column(DateTime(timezone=True), onupdate=func.now())

      owner \= relationship("User", back\_populates="linked\_accounts")

  \# Adicionar mais modelos conforme necessário: MessageCache, PlatformChannel, etc.

* **apps/api/app/schemas/user.py (Schemas Pydantic):**  
  Python  
  from pydantic import BaseModel, EmailStr  
  from typing import Optional, List  
  from datetime import datetime

  class UserBase(BaseModel):  
      email: EmailStr  
      full\_name: Optional\[str\] \= None

  class UserCreate(UserBase):  
      password: str

  class UserUpdate(UserBase):  
      password: Optional\[str\] \= None

  class UserInDBBase(UserBase):  
      id: int  
      is\_active: bool  
      created\_at: datetime  
      updated\_at: Optional\[datetime\] \= None

      class Config:  
          orm\_mode \= True \# Para SQLAlchemy, ou \`from\_attributes \= True\` em Pydantic v2+

  class User(UserInDBBase):  
      pass

  class LinkedAccountBase(BaseModel):  
      platform\_name: str  
      platform\_user\_id: str  
      scopes: Optional\[str\] \= None  
      expires\_at: Optional\[datetime\] \= None

  class LinkedAccountCreate(LinkedAccountBase):  
      access\_token: str \# Recebido em plain text, será criptografado antes de salvar  
      refresh\_token: Optional\[str\] \= None \# Recebido em plain text

  class LinkedAccount(LinkedAccountBase):  
      id: int  
      user\_id: int  
      created\_at: datetime  
      updated\_at: Optional\[datetime\] \= None

      class Config:  
          orm\_mode \= True \# ou \`from\_attributes \= True\`

A separação entre modelos de banco de dados (SQLAlchemy) e schemas de API (Pydantic) permite que a API exponha apenas os dados necessários e valide as entradas de forma independente da estrutura do banco.40

### **4.2. Configuração do Banco de Dados (SQLAlchemy Async)**

* **apps/api/app/db/session.py:**  
  Python  
  from sqlalchemy.ext.asyncio import create\_async\_engine, AsyncSession, async\_sessionmaker  
  from sqlalchemy.orm import sessionmaker  
  from app.core.config import settings \# Supondo que settings.DATABASE\_URL exista

  DATABASE\_URL \= settings.DATABASE\_URL

  async\_engine \= create\_async\_engine(  
      DATABASE\_URL,  
      pool\_pre\_ping=True,  
      \# echo=True, \# Descomente para debugging SQL  
  )

  AsyncSessionFactory \= async\_sessionmaker(  
      bind=async\_engine,  
      autoflush=False,  
      expire\_on\_commit=False,  
      class\_=AsyncSession  
  )

  async def get\_async\_session() \-\> AsyncGenerator:  
      async with AsyncSessionFactory() as session:  
          yield session

  Este setup configura um engine assíncrono e uma fábrica de sessões para SQLAlchemy, crucial para operações de I/O não bloqueantes com o banco de dados.10 A get\_async\_session será usada como uma dependência FastAPI para injetar sessões de banco de dados nas rotas.  
* **apps/api/app/db/base.py (para inicialização de tabelas):**  
  Python  
  from app.db.base\_class import Base  
  from app.models.user import User, LinkedAccount \# Importar todos os modelos

  \# Esta função pode ser chamada ao iniciar a aplicação (para desenvolvimento)  
  \# ou gerenciada por Alembic em produção.  
  async def init\_db(engine):  
      async with engine.begin() as conn:  
          \# await conn.run\_sync(Base.metadata.drop\_all) \# Cuidado em produção\!  
          await conn.run\_sync(Base.metadata.create\_all)

  Alembic é a ferramenta recomendada para gerenciar migrações de schema em produção.

### **4.3. Autenticação de Usuários da Aplicação (JWT)**

A autenticação será baseada em JWT (JSON Web Tokens).

* **apps/api/app/core/security.py:**  
  Python  
  from datetime import datetime, timedelta, timezone  
  from typing import Optional, Any  
  from jose import JWTError, jwt  
  from passlib.context import CryptContext  
  from pydantic import ValidationError

  from app.core.config import settings  
  from app.schemas.token import TokenPayload \# Schema Pydantic para o payload do token

  pwd\_context \= CryptContext(schemes=\["bcrypt"\], deprecated="auto")

  ALGORITHM \= settings.ALGORITHM  
  ACCESS\_TOKEN\_EXPIRE\_MINUTES \= settings.ACCESS\_TOKEN\_EXPIRE\_MINUTES  
  SECRET\_KEY \= settings.SECRET\_KEY \# Deve ser uma string segura

  def create\_access\_token(subject: Any, expires\_delta: Optional\[timedelta\] \= None) \-\> str:  
      if expires\_delta:  
          expire \= datetime.now(timezone.utc) \+ expires\_delta  
      else:  
          expire \= datetime.now(timezone.utc) \+ timedelta(minutes=ACCESS\_TOKEN\_EXPIRE\_MINUTES)  
      to\_encode \= {"exp": expire, "sub": str(subject)}  
      encoded\_jwt \= jwt.encode(to\_encode, SECRET\_KEY, algorithm=ALGORITHM)  
      return encoded\_jwt

  def verify\_password(plain\_password: str, hashed\_password: str) \-\> bool:  
      return pwd\_context.verify(plain\_password, hashed\_password)

  def get\_password\_hash(password: str) \-\> str:  
      return pwd\_context.hash(password)

  def decode\_token(token: str) \-\> Optional:  
      try:  
          payload \= jwt.decode(token, SECRET\_KEY, algorithms=)  
          token\_data \= TokenPayload(\*\*payload) \# Valida com Pydantic  
          if token\_data.exp \< datetime.now(timezone.utc):  
              return None \# Token expirado  
          return token\_data  
      except (JWTError, ValidationError):  
          return None

  Este módulo lida com a criação de tokens de acesso, hashing e verificação de senhas.29 A SECRET\_KEY deve ser forte e gerenciada de forma segura.  
* **Dependência para obter usuário atual (apps/api/app/api/deps.py):**  
  Python  
  from fastapi import Depends, HTTPException, status  
  from fastapi.security import OAuth2PasswordBearer  
  from sqlalchemy.ext.asyncio import AsyncSession  
  from typing import Optional

  from app.core.security import decode\_token  
  from app.db.session import get\_async\_session  
  from app.models.user import User  
  from app.crud.user import crud\_user \# Supondo que crud\_user.get\_by\_email exista  
  from app.schemas.token import TokenPayload

  reusable\_oauth2 \= OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

  async def get\_current\_user(  
      session: AsyncSession \= Depends(get\_async\_session),  
      token: str \= Depends(reusable\_oauth2)  
  ) \-\> User:  
      token\_data \= decode\_token(token)  
      if not token\_data or not token\_data.sub:  
          raise HTTPException(  
              status\_code=status.HTTP\_403\_FORBIDDEN,  
              detail="Could not validate credentials",  
          )  
      user \= await crud\_user.get\_by\_email(session, email=token\_data.sub) \# Ou por ID se 'sub' for ID  
      if not user:  
          raise HTTPException(status\_code=404, detail="User not found")  
      return user

  async def get\_current\_active\_user(  
      current\_user: User \= Depends(get\_current\_user),  
  ) \-\> User:  
      if not current\_user.is\_active:  
          raise HTTPException(status\_code=400, detail="Inactive user")  
      return current\_user

  Estas dependências FastAPI são usadas para proteger rotas e obter o usuário autenticado a partir do token JWT.7

### **4.4. Gerenciamento de Tokens OAuth Externos**

Para cada plataforma (WhatsApp, Discord, Slack), a aplicação precisará armazenar e gerenciar tokens OAuth (access e refresh tokens) de forma segura.

* Criptografia de Tokens:  
  A biblioteca cryptography (especificamente Fernet) será usada para criptografar os tokens antes de armazená-los no PostgreSQL.32  
  * **apps/api/app/core/encryption.py:**  
    Python  
    from cryptography.fernet import Fernet, InvalidToken  
    from app.core.config import settings

    \# A FERNET\_ENCRYPTION\_KEY deve ser uma chave de 32 bytes, URL-safe, base64-encoded.  
    \# Gerar com Fernet.generate\_key() e armazenar de forma segura (e.g., AWS Secrets Manager).  
    \# Para desenvolvimento, pode estar no.env, mas NUNCA em hardcode em produção.  
    try:  
        cipher\_suite \= Fernet(settings.FERNET\_ENCRYPTION\_KEY.encode())  
    except Exception as e:  
        \# Logar erro e potencialmente impedir a inicialização da app se a chave for inválida/ausente  
        print(f"Erro ao inicializar Fernet: {e}. Certifique-se que FERNET\_ENCRYPTION\_KEY está configurada.")  
        \# Em um cenário real, poderia levantar uma exceção customizada ou sair.  
        \# Para este exemplo, vamos permitir que continue, mas com funcionalidade de criptografia quebrada.  
        cipher\_suite \= None

    def encrypt\_data(data: str) \-\> bytes:  
        if not cipher\_suite:  
            raise ValueError("Fernet cipher não inicializado. Verifique FERNET\_ENCRYPTION\_KEY.")  
        return cipher\_suite.encrypt(data.encode())

    def decrypt\_data(encrypted\_data: bytes) \-\> str:  
        if not cipher\_suite:  
            raise ValueError("Fernet cipher não inicializado. Verifique FERNET\_ENCRYPTION\_KEY.")  
        try:  
            return cipher\_suite.decrypt(encrypted\_data).decode()  
        except InvalidToken:  
            \# Logar a tentativa de decriptografia falha  
            raise ValueError("Token de criptografia inválido ou chave incorreta.")  
        except Exception as e:  
            \# Logar outro erro de decriptografia  
            raise ValueError(f"Erro ao descriptografar: {e}")

  * **Gerenciamento da Chave Fernet:** A FERNET\_ENCRYPTION\_KEY é crítica. Em produção, deve ser gerenciada por um serviço como AWS Secrets Manager ou HashiCorp Vault e injetada como variável de ambiente na função Lambda/aplicação FastAPI.38 A rotação de chaves pode ser gerenciada usando MultiFernet se necessário.32  
* Fluxo de Refresh Token para APIs Externas:  
  Uma classe ou conjunto de utilitários será responsável por:  
  1. Recuperar o refresh\_token criptografado do LinkedAccount do usuário.  
  2. Descriptografá-lo.  
  3. Fazer uma requisição para o endpoint de token da plataforma externa (e.g., Google, Slack) usando o refresh\_token para obter um novo access\_token (e possivelmente um novo refresh\_token). Bibliotecas como requests-oauthlib ou httpx-oauth podem auxiliar nisso.33  
  4. Criptografar os novos tokens.  
  5. Atualizar os tokens e o expires\_at no registro LinkedAccount do banco de dados.  
  6. Este processo deve ser acionado quando um access\_token expira ou está prestes a expirar.  
  * **apps/api/app/services/oauth\_client\_service.py (Exemplo conceitual):**  
    Python  
    import httpx  
    from datetime import datetime, timedelta, timezone  
    from app.models.user import LinkedAccount  
    from app.core.encryption import encrypt\_data, decrypt\_data  
    from app.db.session import AsyncSession  
    from app.crud.linked\_account import crud\_linked\_account \# CRUD para LinkedAccount

    \# Configurações específicas da plataforma (URLs de token, client\_id, client\_secret)  
    \# viriam de app.core.config.settings  
    PLATFORM\_CONFIGS \= {  
        "discord": {  
            "token\_url": "https://discord.com/api/oauth2/token",  
            "client\_id": settings.DISCORD\_CLIENT\_ID,  
            "client\_secret": settings.DISCORD\_CLIENT\_SECRET,  
        },  
        "slack": {  
            "token\_url": "https://slack.com/api/oauth2.v2.access",  
             "client\_id": settings.SLACK\_CLIENT\_ID,  
             "client\_secret": settings.SLACK\_CLIENT\_SECRET,  
        }  
        \# Adicionar WhatsApp (Cloud API usa tokens de acesso permanentes ou de longa duração,  
        \# o refresh pode ser diferente ou não aplicável da mesma forma)  
    }

    async def refresh\_oauth\_token(  
        db: AsyncSession, linked\_account: LinkedAccount  
    ) \-\> Optional\[str\]: \# Retorna o novo access\_token ou None  
        if not linked\_account.encrypted\_refresh\_token:  
            return None

        platform\_config \= PLATFORM\_CONFIGS.get(linked\_account.platform\_name)  
        if not platform\_config:  
            \# Logar plataforma não suportada  
            return None

        try:  
            refresh\_token \= decrypt\_data(linked\_account.encrypted\_refresh\_token)  
        except ValueError:  
            \# Logar falha na decriptografia  
            return None \# Ou forçar re-autenticação

        data \= {  
            "grant\_type": "refresh\_token",  
            "refresh\_token": refresh\_token,  
            "client\_id": platform\_config\["client\_id"\],  
            "client\_secret": platform\_config\["client\_secret"\],  
        }

        async with httpx.AsyncClient() as client:  
            try:  
                response \= await client.post(platform\_config\["token\_url"\], data=data)  
                response.raise\_for\_status() \# Levanta exceção para 4xx/5xx  
                token\_data \= response.json()

                new\_access\_token \= token\_data\["access\_token"\]  
                \# Algumas plataformas retornam um novo refresh\_token, outras não  
                new\_refresh\_token \= token\_data.get("refresh\_token", refresh\_token)  
                expires\_in \= token\_data.get("expires\_in") \# Segundos

                update\_data \= {  
                    "encrypted\_access\_token": encrypt\_data(new\_access\_token),  
                    "encrypted\_refresh\_token": encrypt\_data(new\_refresh\_token),  
                    "expires\_at": datetime.now(timezone.utc) \+ timedelta(seconds=expires\_in) if expires\_in else None,  
                }  
                await crud\_linked\_account.update(db, db\_obj=linked\_account, obj\_in=update\_data)  
                return new\_access\_token  
            except httpx.HTTPStatusError as e:  
                \# Logar erro na requisição de refresh  
                \# Se o refresh token for inválido (e.g., revogado), pode ser necessário  
                \# marcar a conta vinculada como necessitando de re-autenticação.  
                print(f"Erro ao atualizar token para {linked\_account.platform\_name}: {e}")  
                if e.response.status\_code in : \# Bad request ou Unauthorized  
                    \# Potencialmente invalidar o linked\_account ou notificar o usuário  
                    pass  
                return None  
            except Exception as e:  
                \# Logar erro genérico  
                print(f"Exceção ao atualizar token: {e}")  
                return None

    Este serviço encapsula a lógica de refresh, que pode ser chamada por outros serviços antes de fazer chamadas de API para as plataformas externas.33

### **4.5. Integração com APIs Externas (WhatsApp, Discord, Slack)**

Para cada plataforma, serão desenvolvidos módulos de serviço que encapsulam a lógica de comunicação com suas respectivas APIs.

#### **4.5.1. Integração com WhatsApp (Cloud API)**

* **Referência Principal:** A API oficial do WhatsApp Business Cloud, hospedada pela Meta.51 A documentação em https://github.com/dimitrianoudi/whatsapp\_api foi mencionada na query, mas o link estava inacessível.58 Portanto, o foco será na API oficial da Meta.  
* **Autenticação:** Requer um token de acesso permanente ou de longa duração gerado através do Facebook Developer Portal.51 Este token será armazenado de forma segura (criptografado) no LinkedAccount.  
* **Funcionalidades Chave:**  
  * **Envio de Mensagens:**  
    * Endpoint: POST /\<WHATSAPP\_BUSINESS\_PHONE\_NUMBER\_ID\>/messages.55  
    * Tipos de Mensagens: Texto, mídia (imagem, vídeo, áudio, documento, sticker), contatos, localização, templates interativos (botões, listas, fluxos).55  
    * Mensagens de Template: Necessárias para iniciar conversas com clientes ou enviar notificações fora da janela de 24 horas. Devem ser pré-aprovadas pela Meta.51  
    * Mensagens de Sessão (Free-form): Podem ser enviadas em resposta a uma mensagem do cliente, dentro de uma janela de 24 horas.51  
  * **Recebimento de Mensagens (Webhooks):**  
    * Configurar um endpoint no FastAPI para receber notificações de webhook da WhatsApp Cloud API.53  
    * Tipos de Notificações: Mensagens recebidas (texto, mídia, localização, cliques em botões), status de mensagens enviadas (entregue, lida).53  
    * O payload do webhook contém o ID da conta de negócios do WhatsApp, ID do número de telefone e os detalhes da mensagem/status.53  
  * **Gerenciamento de Perfil de Negócios:** Atualizar informações do perfil (endereço, descrição, email, websites, foto do perfil).51  
  * **Outras Funcionalidades:** Upload/download de mídia, verificação em duas etapas, registro de remetentes.51  
* **Considerações:**  
  * **Rate Limiting:** A Cloud API suporta até 80 mps por número de telefone por padrão, com upgrades automáticos para 1000 mps sob certas condições. Limites de taxa de uso de caso de negócios e limites de mensagens de template também se aplicam.57  
  * **Políticas:** Aderência estrita às políticas de negócios e comércio do WhatsApp é crucial para evitar bloqueios.61  
  * **Números de Teste:** Para desenvolvimento, números de teste podem ser usados, mas os destinatários precisam ser registrados no console do Facebook Developer.51  
  * **Comparativo Cloud API vs. On-Premise API:** A Cloud API é hospedada pela Meta, mais fácil de configurar e escalar, com custos operacionais menores. A On-Premise API (Business API tradicional) oferece mais controle e customização, mas exige auto-hospedagem e manutenção.52 Para este projeto serverless, a Cloud API é a escolha natural.

#### **4.5.2. Integração com Discord**

* **Referência Principal:** Documentação oficial da API do Discord ([discord.com/developers/docs/intro](https://discord.com/developers/docs/intro)).62  
* **Autenticação:** OAuth2. O fluxo de Authorization Code Grant é o mais comum.64 O backend obterá access\_token e refresh\_token que serão armazenados de forma segura.  
  * Escopos OAuth2 necessários: identify, email, guilds, messages.read (para ler DMs e canais onde o bot está), rpc.notifications.read (potencialmente para notificações), webhook.incoming (se for usar webhooks para enviar mensagens como o bot). Escopos específicos dependerão das funcionalidades implementadas.  
* **Funcionalidades Chave:**  
  * **Envio de Mensagens:**  
    * Para canais de servidor: POST /channels/{channel.id}/messages. Requer permissões adequadas do bot no servidor/canal.  
    * Para DMs: POST /users/@me/channels (para criar ou obter um canal de DM com um usuário), seguido de POST /channels/{channel.id}/messages.  
    * A API do Discord permite o envio de mensagens de texto, embeds, arquivos, componentes (botões, select menus).66  
  * **Recebimento de Mensagens (Gateway ou Webhooks):**  
    * **Gateway API (WebSockets):** Para bots que precisam de atualizações em tempo real sobre eventos como novas mensagens, presença de usuários, etc. O backend se conectaria ao Gateway do Discord. Evento MESSAGE\_CREATE para novas mensagens.66  
    * **Interactions Endpoint (Webhooks):** Para receber interações de comandos de barra (slash commands) e componentes de mensagem. O Discord envia um POST HTTP para um endpoint configurado no FastAPI.66  
    * Para espelhar mensagens de usuários (não apenas de bots), o uso de um "self-bot" (contra os Termos de Serviço do Discord) seria necessário, o que não é recomendado. A abordagem mais viável é usar um bot oficial que tenha acesso aos canais/DMs relevantes, ou focar em interações onde o usuário explicitamente interage com a aplicação "Mirror".  
    * A comunidade discute a necessidade de uma API de mensagens pessoais (DMs) para notificações, similar a webhooks, mas para usuários.68 Ferramentas como Pipedream oferecem triggers para novas mensagens, indicando possíveis formas de integração, embora possam depender de bots.69  
  * **Obtenção de Informações:**  
    * Usuário: GET /users/@me (com token OAuth2 do usuário).  
    * Servidores (Guilds): GET /users/@me/guilds.  
    * Canais: GET /guilds/{guild.id}/channels.  
    * Membros: GET /guilds/{guild.id}/members/{user.id}.  
* **Considerações:**  
  * **Rate Limiting:** A API do Discord possui rate limits globais (e.g., 50 requisições/segundo por bot) e por rota. As respostas da API incluem headers como X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-RateLimit-Reset-After, e X-RateLimit-Bucket que devem ser respeitados para evitar erros 429\.70  
  * **Intents do Gateway:** Ao usar o Gateway, é preciso declarar os "intents" (intenções) que o bot precisa para receber determinados eventos (e.g., GUILD\_MESSAGES para mensagens em servidores, DIRECT\_MESSAGES para DMs). Alguns intents são privilegiados e requerem aprovação do Discord para bots em mais de 100 servidores.  
  * **Políticas:** Respeitar os Termos de Serviço e Políticas de Desenvolvedor do Discord é fundamental.

#### **4.5.3. Integração com Slack**

* **Referência Principal:** Documentação oficial da API do Slack (api.slack.com e docs.slack.dev).72  
* **Autenticação:** OAuth2. O fluxo de Authorization Code Grant é usado para obter tokens de acesso (usuário e/ou bot).74  
  * Escopos OAuth2: chat:write (para enviar mensagens), channels:history, groups:history, im:history, mpim:history (para ler mensagens de canais públicos, privados, DMs, DMs em grupo respectivamente), users:read, channels:read, etc..76  
* **Funcionalidades Chave:**  
  * **Envio de Mensagens:**  
    * Método Web API: chat.postMessage para enviar mensagens para canais, DMs, etc..77  
    * Suporta texto formatado com mrkdwn, blocos (Block Kit) para layouts ricos e interativos, anexos.73  
    * chat.postEphemeral para mensagens efêmeras visíveis apenas a um usuário específico em um canal.78  
  * **Recebimento de Mensagens (Events API ou Socket Mode):**  
    * **Events API (HTTP POST):** Slack envia eventos (como message.channels, message.groups, message.im, message.mpim) para um Request URL (endpoint no FastAPI) configurado na sua app Slack.76 Requer subscrição aos eventos desejados.  
    * **Socket Mode:** Alternativa à Events API via HTTP, onde os eventos são enviados por uma conexão WebSocket gerenciada pela app Slack. Útil se expor um endpoint HTTP público for problemático (e.g., firewalls corporativos).79  
    * A RTM (Real Time Messaging) API é legada e não recomendada para novas apps.78  
  * **Recuperação de Histórico de Mensagens:**  
    * conversations.history para obter mensagens de um canal.76  
    * conversations.replies para obter respostas de uma thread.76  
    * Recentemente, houve atualizações nos rate limits para esses métodos para apps não-Marketplace.82  
  * **Block Kit:** Framework de UI para criar mensagens ricas e interativas, modais e App Home.72  
* **Considerações:**  
  * **Rate Limiting:** A Web API do Slack tem tiers de rate limits (Tier 1, 2, 3, 4, Special). Por exemplo, chat.postMessage geralmente permite 1 mensagem/segundo por canal, com tolerância a bursts curtos.83 A Events API tem um limite de 30.000 entregas/hora por workspace.83  
  * **Permissões (Escopos):** A funcionalidade da app é diretamente ligada aos escopos OAuth concedidos durante a instalação.79  
  * **Verificação de Request (Events API):** Requisições da Events API devem ser verificadas usando a signing secret para garantir que vêm do Slack.

### **4.6. WebSockets/SSE para Atualizações em Tempo Real no Frontend**

O backend FastAPI precisará notificar o frontend Next.js sobre novas mensagens ou atualizações recebidas das plataformas externas.

* **FastAPI WebSockets:**  
  * FastAPI tem suporte nativo para WebSockets via Starlette.84  
  * **Autenticação da Conexão WebSocket:** Um token JWT (o mesmo usado para autenticação da API HTTP da aplicação "Mirror") pode ser passado como query parameter ou em uma mensagem inicial após a conexão para autenticar o cliente WebSocket.84  
  * **Gerenciamento de Conexões:** Uma classe ConnectionManager no FastAPI pode manter um registro de conexões WebSocket ativas, mapeando-as para user\_ids. Isso permite enviar mensagens para clientes específicos.86  
    Python  
    \# apps/api/app/services/websocket\_manager.py (Exemplo conceitual)  
    from fastapi import WebSocket  
    from typing import Dict, List

    class ConnectionManager:  
        def \_\_init\_\_(self):  
            self.active\_connections: Dict\] \= {} \# user\_id:

        async def connect(self, websocket: WebSocket, user\_id: str):  
            await websocket.accept()  
            if user\_id not in self.active\_connections:  
                self.active\_connections\[user\_id\] \=  
            self.active\_connections\[user\_id\].append(websocket)

        def disconnect(self, websocket: WebSocket, user\_id: str):  
            if user\_id in self.active\_connections:  
                self.active\_connections\[user\_id\].remove(websocket)  
                if not self.active\_connections\[user\_id\]:  
                    del self.active\_connections\[user\_id\]

        async def send\_personal\_message(self, message: str, user\_id: str):  
            if user\_id in self.active\_connections:  
                for connection in self.active\_connections\[user\_id\]:  
                    await connection.send\_text(message)

        async def broadcast\_to\_user(self, message: dict, user\_id: str):  
            \# Similar a send\_personal\_message, mas pode enviar JSON  
            if user\_id in self.active\_connections:  
                for connection in self.active\_connections\[user\_id\]:  
                    await connection.send\_json(message)

    manager \= ConnectionManager()

  * **Roteamento de Mensagens de Webhooks:** Quando o FastAPI recebe um webhook de uma plataforma externa (e.g., nova mensagem do WhatsApp), ele processa a mensagem, identifica o user\_id da aplicação "Mirror" correspondente e usa o ConnectionManager para enviar a atualização para o(s) cliente(s) WebSocket desse usuário.  
  * **Escalabilidade:** Em um ambiente serverless com múltiplas instâncias do FastAPI, um ConnectionManager em memória não funcionará para broadcast entre instâncias. Para escalar, seria necessário um backplane de mensagens como Redis Pub/Sub. Cada instância FastAPI se inscreveria no Redis para mensagens destinadas aos seus usuários conectados e publicaria mensagens no Redis quando um evento de webhook fosse recebido.89  
* **Server-Sent Events (SSE):**  
  * Alternativa mais simples para comunicação unidirecional (servidor para cliente).12  
  * FastAPI pode implementar SSE usando StreamingResponse.  
  * Menor overhead que WebSockets se a comunicação bidirecional não for estritamente necessária pelo mesmo canal.  
  * A lógica de mapeamento user\_id para conexões SSE e o uso de um backplane (Redis) para escalar seriam semelhantes aos WebSockets.

**Escolha:** WebSockets oferecem comunicação bidirecional, o que pode ser útil para futuras funcionalidades (e.g., indicadores de "digitando"). Se apenas notificações do servidor para o cliente forem necessárias inicialmente, SSE é uma opção mais leve. Dada a complexidade potencial de uma aplicação de "espelhamento", WebSockets podem oferecer mais flexibilidade a longo prazo. A implementação inicial pode focar em WebSockets com um ConnectionManager em memória, com planos de integrar Redis se a escala exigir.

### **4.7. Geração de OpenAPI Schema**

FastAPI gera automaticamente um schema OpenAPI (v3) a partir dos modelos Pydantic e das rotas da API.3 Este schema estará disponível por padrão em /openapi.json.  
Um script Python pode ser usado para salvar este schema em um arquivo, que será consumido pelo gerador de cliente TypeScript.

* **apps/api/app/core/generate\_openapi.py:**  
  Python  
  import json  
  from pathlib import Path  
  from app.main import app \# Importar a instância FastAPI

  \# Caminho relativo à raiz do monorepo ou do pacote api  
  \# Ajustar conforme a estrutura e onde o script é executado  
  OUTPUT\_PATH \= Path(\_\_file\_\_).parent.parent.parent / "openapi.json" 

  def generate\_openapi\_schema():  
      openapi\_schema \= app.openapi()  
      \# Opcional: Adicionar/modificar campos no schema, como servers, info, etc.  
      \# openapi\_schema\["servers"\] \=

      with open(OUTPUT\_PATH, "w") as f:  
          json.dump(openapi\_schema, f, indent=2)  
      print(f"OpenAPI schema gerado em: {OUTPUT\_PATH}")

  if \_\_name\_\_ \== "\_\_main\_\_":  
      generate\_openapi\_schema()

  Este script será executado como parte do pipeline de build do Turborepo (definido em apps/api/package.json como build:openapi).

A arquitetura do backend é projetada para ser robusta, segura e escalável, com clara separação de responsabilidades e forte tipagem para facilitar o desenvolvimento e a manutenção.

## **Capítulo 5: Desenvolvimento do Frontend com Next.js e Shadcn/ui**

O frontend será a interface principal com o usuário, construída com Next.js para performance e experiência de desenvolvimento, e Shadcn/ui para uma interface de usuário moderna e personalizável.

### **5.1. Estrutura de Pastas e Componentes**

Dentro de apps/web/src/:

* **app/**: Diretório principal do App Router do Next.js.  
  * (auth)/ : Rotas relacionadas à autenticação (login, registro, callback OAuth).  
  * (main)/ : Layout principal da aplicação após login, contendo a interface de mensagens.  
    * layout.tsx: Layout principal com navegação (sidebar para plataformas, lista de conversas).  
    * page.tsx: Página principal, possivelmente um dashboard ou a primeira conversa ativa.  
    * \[platform\]/\[conversationId\]/page.tsx: Rota dinâmica para exibir mensagens de uma conversa específica.  
  * api/ : Route Handlers do Next.js, se necessário para proxy ou operações do lado do servidor do frontend.  
* **components/**: Componentes React reutilizáveis.  
  * ui/: Componentes Shadcn/ui adicionados via CLI.24  
  * shared/: Componentes customizados compartilhados pela aplicação (e.g., MessageItem, ConversationList, PlatformIcon).  
  * feature/: Componentes específicos de funcionalidades (e.g., AccountLinker, MessageComposer).  
* **lib/**: Utilitários, hooks customizados, configurações de API client.  
  * api.ts: Instância configurada do cliente API gerado (do pacote @repo/api-client).  
  * auth.ts: Funções relacionadas à autenticação no frontend (e.g., wrappers para NextAuth.js).  
  * hooks/: Hooks React customizados (e.g., useWebSocketMessages).  
  * utils.ts: Funções utilitárias gerais.  
* **contexts/**: Contextos React para gerenciamento de estado global, se necessário (alternativa ao Zustand/Jotai).  
* **styles/**: Estilos globais (e.g., globals.css para Tailwind).  
* **types/**: Definições de tipos TypeScript específicas do frontend (tipos de UI, estado local), complementando os tipos do @repo/api-client.

### **5.2. Autenticação de Usuários (NextAuth.js)**

NextAuth.js (agora Auth.js) será usado para gerenciar a autenticação do usuário no frontend, integrando-se com o backend FastAPI para validação de credenciais e manipulação de JWT.

* Configuração do NextAuth.js:  
  Em apps/web/src/app/api/auth/\[...nextauth\]/route.ts (ou pages/api/auth/\[...nextauth\].ts se usando Pages Router, mas App Router é o foco):  
  TypeScript  
  // apps/web/src/app/api/auth/\[...nextauth\]/route.ts  
  import NextAuth, { NextAuthOptions, User as NextAuthUser } from "next-auth";  
  import CredentialsProvider from "next-auth/providers/credentials";  
  import { JWT } from "next-auth/jwt";

  // Estender o tipo User e JWT para incluir tokens do backend  
  interface BackendTokens {  
    access\_token: string;  
    refresh\_token?: string; // Se o backend FastAPI retornar refresh tokens  
    expires\_at: number; // Timestamp de expiração do access\_token  
  }

  interface CustomUser extends NextAuthUser, BackendTokens {  
    id: string; // ID do usuário da nossa aplicação  
  }

  interface CustomJWT extends JWT, BackendTokens {  
    id: string;  
  }

  export const authOptions: NextAuthOptions \= {  
    providers:,  
    session: {  
      strategy: "jwt", // Usar JWT para sessões do NextAuth  
    },  
    callbacks: {  
      async jwt({ token, user, account }) {  
        // \`user\` só está presente no login inicial  
        if (account && user) {  
          const customUser \= user as CustomUser;  
          token.accessToken \= customUser.access\_token;  
          token.refreshToken \= customUser.refresh\_token;  
          token.accessTokenExpires \= customUser.expires\_at;  
          token.userId \= customUser.id; // Adiciona o ID do usuário ao token NextAuth  
          token.email \= customUser.email;  
          return token;  
        }

        // Em requisições subsequentes, token já existe. Verificar se o access token expirou.  
        const customToken \= token as CustomJWT;  
        if (customToken.accessTokenExpires && Date.now() / 1000 \< customToken.accessTokenExpires) {  
          return customToken; // Token ainda é válido  
        }

        // Access token expirou, tentar refresh se houver refresh token  
        if (\!customToken.refreshToken) {  
          console.error("Access token expirado e sem refresh token.");  
          return {...customToken, error: "RefreshAccessTokenError" as const };  
        }

        try {  
          // Chamar endpoint de refresh token do backend FastAPI  
          const response \= await fetch(\`${process.env.NEXT\_PUBLIC\_API\_BASE\_URL}/users/login/refresh-token\`, {  
            method: "POST",  
            headers: { "Content-Type": "application/json" },  
            body: JSON.stringify({ refresh\_token: customToken.refreshToken }),  
          });

          if (\!response.ok) {  
            console.error("Falha ao atualizar token:", response.status, await response.text());  
            // Invalidar sessão se o refresh falhar  
            return {...customToken, error: "RefreshAccessTokenError" as const };  
          }

          const refreshedTokens: { access\_token: string; refresh\_token?: string; expires\_in: number; } \= await response.json();  
          const new\_expires\_at \= Math.floor(Date.now() / 1000\) \+ refreshedTokens.expires\_in;

          return {  
           ...customToken,  
            accessToken: refreshedTokens.access\_token,  
            refreshToken: refreshedTokens.refresh\_token?? customToken.refreshToken, // Usar novo refresh token se fornecido  
            accessTokenExpires: new\_expires\_at,  
            error: null, // Limpar erro anterior  
          };  
        } catch (error) {  
          console.error("Erro ao tentar atualizar token:", error);  
          return {...customToken, error: "RefreshAccessTokenError" as const };  
        }  
      },  
      async session({ session, token }) {  
        const customToken \= token as CustomJWT;  
        if (customToken.accessToken) {  
          session.accessToken \= customToken.accessToken; // Expor o access\_token do backend para a sessão do cliente  
          session.user.id \= customToken.userId;  
          session.user.email \= customToken.email;  
          session.error \= customToken.error; // Propagar erro de refresh  
        }  
        return session;  
      },  
    },  
    pages: {  
      signIn: '/login', // Página de login customizada  
    },  
    secret: process.env.NEXTAUTH\_SECRET, // Chave secreta para assinar os JWTs do NextAuth  
  };

  const handler \= NextAuth(authOptions);  
  export { handler as GET, handler as POST };

  Este fluxo utiliza o CredentialsProvider para autenticar contra o backend FastAPI.43 O backend FastAPI é responsável por emitir JWTs de acesso (e opcionalmente de refresh). O NextAuth.js então gerencia sua própria sessão JWT, que pode *conter* os tokens do backend. O callback jwt é crucial para persistir os tokens do backend e implementar a lógica de refresh. O token de acesso do backend é então disponibilizado para o cliente através do callback session.  
* Provedor de Sessão:  
  Envolver a aplicação com \<SessionProvider\> em apps/web/src/app/providers.tsx (ou similar, para manter o layout.tsx como Server Component):  
  TypeScript  
  // apps/web/src/app/providers.tsx  
  "use client";  
  import { SessionProvider } from "next-auth/react";  
  import { ReactNode } from "react";

  export function Providers({ children }: { children: ReactNode }) {  
    return \<SessionProvider\>{children}\</SessionProvider\>;  
  }

  E usar em apps/web/src/app/layout.tsx:  
  TypeScript  
  // apps/web/src/app/layout.tsx  
  import { Providers } from "./providers";  
  //... outros imports  
  export default function RootLayout({ children }: { children: React.ReactNode }) {  
    return (  
      \<html lang="en" suppressHydrationWarning\>  
        \<body\>  
          \<Providers\>{children}\</Providers\>  
        \</body\>  
      \</html\>  
    );  
  }

* Páginas de Login e Componentes de UI:  
  Criar uma página de login customizada (apps/web/src/app/(auth)/login/page.tsx) usando componentes Shadcn/ui (Input, Button, Card).  
  Usar signIn() e signOut() de next-auth/react para gerenciar o fluxo de login/logout.  
  O hook useSession() fornecerá o estado da sessão e o token de acesso do backend.

### **5.3. Vinculação de Contas Externas (OAuth2 Flow)**

O frontend iniciará o fluxo OAuth2 para cada plataforma externa (Discord, Slack, WhatsApp).

1. Interface de Vinculação:  
   Uma seção nas configurações do usuário permitirá vincular/desvincular contas.  
   Para cada plataforma, um botão "Conectar com \[Plataforma\]" iniciará o fluxo.  
2. Iniciando o Fluxo OAuth2:  
   Ao clicar em "Conectar com Discord", por exemplo:  
   * O frontend faz uma requisição ao backend FastAPI (e.g., GET /api/v1/auth/discord/login-url).  
   * O backend FastAPI constrói a URL de autorização do Discord com os client\_id, redirect\_uri (apontando para um endpoint de callback no FastAPI), response\_type=code, e os escopos necessários.  
   * O backend retorna essa URL para o frontend.  
   * O frontend redireciona o usuário para a URL de autorização do Discord.  
3. **Callback Handling:**  
   * Após o usuário autorizar, o Discord redireciona para o redirect\_uri do backend FastAPI com um code.  
   * O backend FastAPI troca esse code por access\_token e refresh\_token do Discord.  
   * O backend armazena esses tokens (criptografados) no PostgreSQL, associados ao usuário logado na aplicação "Mirror".  
   * O backend redireciona o usuário de volta para uma página de sucesso/configurações no frontend.

Este fluxo é similar para Slack. Para WhatsApp (Cloud API), a "vinculação" envolve configurar o número de telefone e obter o token de acesso permanente através do portal de desenvolvedores do Facebook, um processo que pode ser mais manual ou guiado pela UI da aplicação "Mirror", mas o token final ainda será armazenado pelo backend.51

### **5.4. Interface de Mensagens Unificada**

Esta é a funcionalidade central do frontend.

* **Layout Principal:**  
  * Uma sidebar para selecionar a plataforma (WhatsApp, Discord, Slack) e a conta vinculada (se houver múltiplas por plataforma).  
  * Uma segunda sidebar/lista para exibir conversas/canais da plataforma/conta selecionada.  
  * A área principal para exibir as mensagens da conversa/canal ativo e um compositor de mensagens.  
* **Componentes Shadcn/ui para Chat:** 1  
  * ScrollArea: Para a lista de mensagens.  
  * Avatar: Para fotos de perfil dos remetentes.  
  * Card ou divs estilizadas com Tailwind: Para cada balão de mensagem.  
  * Input / Textarea: Para o compositor de mensagens.  
  * Button: Para enviar mensagens, anexar arquivos.  
  * DropdownMenu, Dialog, Sheet: Para ações de mensagem, informações do perfil, configurações.  
  * Tooltip: Para informações adicionais (e.g., timestamp exato).  
  * Para uma interface de chat mais completa, bibliotecas como shadcn-chat 105 ou assistant-ui 2 podem oferecer componentes de chat reutilizáveis e personalizáveis construídos sobre Shadcn/ui.  
* **Renderização de Mensagens de Múltiplas Fontes:**  
  * **Estrutura de Dados Unificada:** O backend FastAPI deve transformar as mensagens das diferentes plataformas em uma estrutura de dados de mensagem unificada (mas flexível) antes de enviá-las ao frontend. Essa estrutura deve incluir:  
    * id: ID único da mensagem na nossa aplicação.  
    * platformMessageId: ID original da mensagem na plataforma.  
    * platform: "whatsapp", "discord", "slack".  
    * senderName: Nome do remetente.  
    * senderAvatarUrl: URL do avatar do remetente.  
    * senderPlatformId: ID do remetente na plataforma.  
    * content: Conteúdo da mensagem (texto).  
    * timestamp: Timestamp do envio.  
    * isOwnMessage: Booleano indicando se a mensagem foi enviada pelo usuário logado.  
    * type: Tipo de mensagem (e.g., "text", "image", "file", "system", "discord\_embed").  
    * mediaUrl: URL para mídias.  
    * reactions: Array de reações.  
    * metadata: Objeto para dados específicos da plataforma (e.g., thread\_ts do Slack, embeds do Discord).  
  * Componente de Mensagem Polimórfico/Dinâmico:  
    Criar um componente MessageItem.tsx que renderiza a mensagem de forma diferente com base no campo platform e type.  
    TypeScript  
    // Exemplo conceitual em apps/web/src/components/shared/MessageItem.tsx  
    interface UnifiedMessage {  
      //... campos definidos acima  
      platform: 'whatsapp' | 'discord' | 'slack';  
      type: 'text' | 'image' | 'file' | 'discord\_embed' | 'slack\_block\_kit';  
      metadata?: any;  
    }

    const MessageItem \= ({ message }: { message: UnifiedMessage }) \=\> {  
      const renderContent \= () \=\> {  
        switch (message.platform) {  
          case 'whatsapp':  
            // Renderizar conteúdo específico do WhatsApp (e.g., templates, botões)  
            if (message.type \=== 'image') return \<img src={message.mediaUrl} alt="WhatsApp Image" /\>;  
            return \<p\>{message.content}\</p\>;  
          case 'discord':  
            // Renderizar embeds do Discord, markdown específico  
            if (message.type \=== 'discord\_embed' && message.metadata?.embeds) {  
              // return \<DiscordEmbedComponent embeds={message.metadata.embeds} /\>;  
            }  
            return \<p\>{message.content}\</p\>; // Simplificado  
          case 'slack':  
            // Renderizar blocos do Slack (Block Kit)  
            if (message.type \=== 'slack\_block\_kit' && message.metadata?.blocks) {  
              // return \<SlackBlockKitRenderer blocks={message.metadata.blocks} /\>;  
            }  
            return \<p\>{message.content}\</p\>; // Simplificado  
          default:  
            return \<p\>{message.content}\</p\>;  
        }  
      };

      return (  
        \<div className={\`message ${message.isOwnMessage? 'own' : 'other'}\`}\>  
          \<Avatar\>  
            {/\* \<AvatarImage src={message.senderAvatarUrl} /\> \*/}  
            {/\* \<AvatarFallback\>{message.senderName.substring(0, 2)}\</AvatarFallback\> \*/}  
          \</Avatar\>  
          \<div\>  
            \<strong\>{message.senderName}\</strong\>  
            {renderContent()}  
            \<span\>{new Date(message.timestamp).toLocaleTimeString()}\</span\>  
          \</div\>  
        \</div\>  
      );  
    };

    Esta abordagem permite que cada plataforma tenha sua própria lógica de renderização para tipos de mensagens específicos, mantendo um componente MessageItem unificado. Componentes especializados como DiscordEmbedComponent ou SlackBlockKitRenderer seriam criados para lidar com a complexidade da renderização desses formatos.  
* **Gerenciamento de Estado com React Query/SWR ou Zustand:**  
  * Para buscar e armazenar em cache listas de conversas e mensagens.  
  * Para gerenciar o estado da UI, como a conversa/plataforma ativa.  
  * Zustand pode ser usado para um estado global mais simples, enquanto React Query/SWR são excelentes para o gerenciamento de estado do servidor.

### **5.5. Conexão com Backend (WebSockets/SSE) para Tempo Real**

O frontend precisa estabelecer uma conexão WebSocket (ou SSE) com o backend FastAPI para receber atualizações em tempo real.

* **Hook useWebSocketMessages:**  
  TypeScript  
  // apps/web/src/lib/hooks/useWebSocketMessages.ts  
  import { useEffect, useState } from 'react';  
  import { useSession } from 'next-auth/react'; // Para obter o token de acesso

  interface RealTimeMessage { /\*... definir estrutura da mensagem recebida via WS... \*/ }

  export function useWebSocketMessages(onMessageCallback: (message: RealTimeMessage) \=\> void) {  
    const { data: session } \= useSession();  
    const \[isConnected, setIsConnected\] \= useState(false);

    useEffect(() \=\> {  
      if (\!session?.accessToken) {  
        // Não conectar se não houver token de acesso (usuário não logado ou token indisponível)  
        return;  
      }

      // A URL do WebSocket pode precisar incluir o token de acesso para autenticação  
      // Ex: ws://localhost:8000/ws/updates?token=${session.accessToken}  
      // Ou o token pode ser enviado como a primeira mensagem após a conexão.  
      const wsUrl \= \`ws://localhost:8000/api/v1/ws/updates?token=${session.accessToken}\`;  
      const socket \= new WebSocket(wsUrl);

      socket.onopen \= () \=\> {  
        console.log('WebSocket connected');  
        setIsConnected(true);  
        // Opcional: Enviar uma mensagem de autenticação se o token não estiver na URL  
        // socket.send(JSON.stringify({ type: 'auth', token: session.accessToken }));  
      };

      socket.onmessage \= (event) \=\> {  
        try {  
          const messageData \= JSON.parse(event.data as string) as RealTimeMessage;  
          onMessageCallback(messageData);  
        } catch (error) {  
          console.error('Failed to parse WebSocket message:', error);  
        }  
      };

      socket.onclose \= (event) \=\> {  
        console.log('WebSocket disconnected:', event.reason, event.code);  
        setIsConnected(false);  
        // Lógica de reconexão pode ser implementada aqui (e.g., com backoff exponencial)  
      };

      socket.onerror \= (error) \=\> {  
        console.error('WebSocket error:', error);  
        setIsConnected(false);  
      };

      return () \=\> {  
        socket.close();  
      };  
    }, \[session, onMessageCallback\]); // Reconectar se a sessão (token) mudar

    return { isConnected };  
  }

  Este hook encapsula a lógica de conexão WebSocket, incluindo autenticação (passando o JWT da aplicação "Mirror" como query parameter, por exemplo) e manipulação de mensagens. O backend FastAPI validará este token antes de aceitar a conexão WebSocket.84  
* Integração nos Componentes:  
  Os componentes que exibem mensagens ou listas de conversas usarão este hook para receber atualizações e re-renderizar conforme necessário.

O desenvolvimento do frontend focará na criação de uma experiência de usuário fluida e responsiva, com uma clara separação de responsabilidades entre componentes e uma forte integração com o backend para dados e atualizações em tempo real. A flexibilidade do Shadcn/ui e a robustez do Next.js fornecerão uma base sólida para esta interface complexa.

## **Capítulo 6: Monorepo e Fluxos de Trabalho de Automação**

A utilização de um monorepo gerenciado pelo Turborepo é fundamental para este projeto, permitindo o desenvolvimento coeso do frontend Next.js e do backend Python/FastAPI, além de pacotes compartilhados. Este capítulo detalha a configuração do Turborepo e os fluxos de automação para otimizar o desenvolvimento.

### **6.1. Configuração Detalhada do turbo.json**

O arquivo turbo.json na raiz do monorepo define os pipelines de tarefas, suas dependências e como o cache deve ser tratado.11

JSON

// turbo.json  
{  
  "$schema": "https://turborepo.org/schema.json",  
  "globalDependencies": \[  
    "\*\*/.env.\*local",  
    "\*\*/.env"  
  \],  
  "globalEnv":,  
  "pipeline": {  
    "clean": {  
      "cache": false  
    },  
    // Backend (FastAPI) Tasks  
    "api\#lint": {  
      "outputs":, // Linters geralmente não produzem artefatos para cache  
      "dependsOn":  
    },  
    "api\#test": {  
      "outputs": \["coverage/\*\*"\], // Cachear relatórios de cobertura  
      "dependsOn": \["^build"\] // Depende do build de dependências internas (se houver)  
    },  
    "api\#build:openapi": {  
      "doc": "Gera o openapi.json a partir do código FastAPI.",  
      "dependsOn":, // Depende implicitamente dos arquivos Python em apps/api  
      "inputs": \["apps/api/app/\*\*/\*.py", "apps/api/pyproject.toml", "apps/api/uv.lock"\], // Ou poetry.lock  
      "outputs": \["apps/api/openapi.json"\]  
    },  
    "api\#build:lambda": {  
      "doc": "Empacota a aplicação FastAPI para deploy no AWS Lambda.",  
      "dependsOn": \["^build"\], // Depende do build de dependências internas (se houver)  
      "inputs": \["apps/api/app/\*\*/\*.py", "apps/api/scripts/package\_lambda.py", "apps/api/pyproject.toml", "apps/api/uv.lock"\],  
      "outputs": \["apps/api/dist/lambda\_function.zip"\] // Artefato de deploy \[22, 23, 116, 117\]  
    },  
    "api\#dev": {  
      "cache": false,  
      "persistent": true  
    },  
    // API Client (TypeScript) Generation Task  
    "api-client\#generate:client": {  
      "doc": "Gera o cliente TypeScript a partir do openapi.json.",  
      "dependsOn": \["api\#build:openapi"\],  
      "inputs": \["packages/api-client/openapi-ts.config.ts", "apps/api/openapi.json"\],  
      "outputs": \["packages/api-client/src/\*\*"\] // Diretório de saída do cliente gerado  
    },  
    // Frontend (Next.js) Tasks  
    "web\#lint": {  
      "outputs":  
    },  
    "web\#test": {  
      "outputs": \["coverage/\*\*"\],  
      "dependsOn": \["^build"\]  
    },  
    "web\#build": {  
      "dependsOn": \["^build", "api-client\#generate:client"\], // Garante que o cliente API está atualizado  
      "outputs": \[".next/\*\*", "\!.next/cache/\*\*", ".vercel/output/\*\*"\],  
      "env":  
    },  
    "web\#dev": {  
      "cache": false,  
      "persistent": true  
      // "with": \["api\#dev"\] // Se quiser iniciar o backend junto automaticamente (requer config adicional) \[110\]  
    },  
    // Tarefa de build global  
    "build": {  
      "dependsOn": \["^build", "api-client\#generate:client"\],  
      "outputs": \[  
        "apps/web/.next/\*\*",   
        "apps/web/.vercel/output/\*\*",  
        "apps/api/dist/\*\*",   
        "apps/api/openapi.json",  
        "packages/api-client/src/\*\*"  
      \]  
    },  
    "deploy": {  
        "dependsOn": \["build"\]  
        // Scripts de deploy específicos seriam chamados aqui ou em CI/CD  
    }  
  }  
}

* **globalDependencies e globalEnv**: Definem arquivos e variáveis de ambiente que, se alterados, podem invalidar o cache de todas as tarefas.21  
* **pipeline**: Define as tarefas e suas dependências.  
  * **api\#lint, api\#test**: Tarefas de lint e teste para o backend. outputs para api\#test podem incluir relatórios de cobertura.  
  * **api\#build:openapi**: Gera o openapi.json. inputs são os arquivos Python relevantes e de dependência. outputs é o openapi.json gerado.18  
  * **api\#build:lambda**: Empacota a aplicação FastAPI para Lambda. inputs incluem o código da aplicação e scripts de empacotamento. outputs é o arquivo .zip resultante.22  
  * **api-client\#generate:client**: Gera o cliente TypeScript. Crucialmente, dependsOn: \["api\#build:openapi"\] garante que o openapi.json seja gerado antes. inputs incluem o openapi.json e a configuração do gerador. outputs são os arquivos do cliente gerado.18  
  * **web\#build**: Build do frontend Next.js. dependsOn: \["^build", "api-client\#generate:client"\] assegura que quaisquer pacotes internos compartilhados sejam construídos e que o cliente API esteja atualizado antes do build do frontend.  
  * **web\#dev e api\#dev**: Tarefas de desenvolvimento com cache: false e persistent: true.121 A opção with do Turborepo 2.5+ poderia ser usada para iniciar o backend junto com o frontend automaticamente.110  
  * **build (global)**: Uma tarefa de build agregada que depende do build de todas as dependências internas e da geração do cliente API.  
* Gerenciamento de Virtual Environments Python com Turborepo:  
  Turborepo em si não gerencia virtual environments Python. Os scripts definidos no package.json de apps/api devem ser responsáveis por invocar comandos Python usando o gerenciador de pacotes/ambientes escolhido (e.g., uv run..., poetry run..., ou ativando um venv explicitamente antes de rodar o script Python).15  
  * Por exemplo, o script apps/api/package.json\#dev: "dev": "source.venv/bin/activate && uvicorn app.main:app \--reload" (se não usar uv run).  
  * Com uv, uv run \<comando\> executa o comando dentro do ambiente gerenciado pelo uv para o projeto atual, simplificando isso.15

### **6.2. Scripts package.json para Tarefas Python**

Conforme definido na seção 3.4, o apps/api/package.json conterá scripts como:

JSON

// apps/api/package.json  
{  
  "name": "api",  
  //...  
  "scripts": {  
    "dev": "uv run uvicorn app.main:app \--host 0.0.0.0 \--port 8000 \--reload",  
    "lint": "uv run ruff check. && uv run black. \--check && uv run mypy.",  
    "format": "uv run ruff check. \--fix && uv run black.",  
    "test": "uv run pytest tests/",  
    "build:openapi": "uv run python app/core/generate\_openapi.py",  
    "build:lambda": "uv run python scripts/package\_lambda.py",  
    "build": "pnpm run build:openapi && pnpm run build:lambda" // Tarefa de build agregada para a API  
  }  
}

Turborepo executará esses scripts. Por exemplo, turbo run api\#lint executará o script lint definido acima.122

### **6.3. Automação da Geração de Cliente API TypeScript**

Este é um fluxo de trabalho de automação crucial para manter a consistência entre o backend e o frontend.

1. **Geração do openapi.json pelo FastAPI:**  
   * O script apps/api/app/core/generate\_openapi.py (detalhado no Capítulo 4.7) é responsável por gerar o openapi.json a partir da instância da aplicação FastAPI.  
   * A tarefa api\#build:openapi no turbo.json executa este script.  
   * inputs: apps/api/app/\*\*/\*.py (e arquivos de dependência como pyproject.toml, uv.lock). Qualquer alteração nesses arquivos (e.g., uma nova rota, mudança em um modelo Pydantic) invalidará o cache para esta tarefa, forçando a regeneração do openapi.json.  
   * outputs: apps/api/openapi.json. O Turborepo cacheará este arquivo.  
2. **Geração do Cliente TypeScript com @hey-api/openapi-ts:**  
   * O pacote packages/api-client tem um script generate:client em seu package.json: "generate:client": "openapi-ts \--config./openapi-ts.config.ts".37  
   * A tarefa api-client\#generate:client no turbo.json executa este script.  
   * dependsOn: \["api\#build:openapi"\]: Garante que o openapi.json esteja atualizado antes de gerar o cliente.  
   * inputs: packages/api-client/openapi-ts.config.ts e o próprio apps/api/openapi.json. Se o openapi.json mudar (porque o api\#build:openapi foi executado), o cache para api-client\#generate:client será invalidado, e o cliente será regenerado.  
   * outputs: packages/api-client/src/\*\*. O Turborepo cacheará os arquivos do cliente gerado.  
3. **Consumo no Frontend:**  
   * A aplicação Next.js (apps/web) adiciona @repo/api-client como uma dependência de workspace (e.g., "@repo/api-client": "workspace:\*") em seu package.json.  
   * A tarefa web\#build no turbo.json tem dependsOn: \["api-client\#generate:client"\]. Isso garante que o frontend sempre seja construído com a versão mais recente do cliente API.

Este encadeamento de dependências e a correta definição de inputs e outputs no turbo.json são essenciais. Se um desenvolvedor alterar uma rota ou modelo Pydantic no backend FastAPI:

1. O inputs de api\#build:openapi muda.  
2. turbo run build (ou dev) irá re-executar api\#build:openapi, gerando um novo openapi.json.  
3. O novo openapi.json muda o inputs de api-client\#generate:client.  
4. api-client\#generate:client é re-executado, gerando um novo cliente TypeScript.  
5. Os arquivos alterados em packages/api-client/src/ invalidam o cache para web\#build (devido à dependência do workspace).  
6. web\#build (ou o servidor de desenvolvimento do Next.js) usará o cliente API atualizado, refletindo as mudanças do backend e fornecendo type safety.

Este fluxo automatizado reduz drasticamente a chance de desalinhamento entre frontend e backend e melhora a DX.3

### **6.4. Pre-commit Hooks (Husky \+ lint-staged)**

Para manter a qualidade e consistência do código, pre-commit hooks são recomendados.

1. Instalação:  
   Na raiz do monorepo:  
   pnpm add husky lint-staged \--save-dev \-w  
   npx husky init (ou o comando equivalente para pnpm se husky init não funcionar bem com pnpm, pode ser necessário configurar manualmente)  
2. **Configurar lint-staged no package.json raiz:**  
   JSON  
   // package.json (raiz)  
   {  
     //...  
     "lint-staged": {  
       "apps/web/\*\*/\*.{ts,tsx}": \[  
         "pnpm \--filter web lint \--fix", // Executa o script lint do app web  
         "pnpm \--filter web format"      // Executa o script format do app web (se existir)  
       \],  
       "packages/ui/\*\*/\*.{ts,tsx}": \[ // Exemplo para um pacote UI  
         "pnpm \--filter @repo/ui lint \--fix"  
       \],  
       "packages/api-client/\*\*/\*.{ts,tsx}":,  
       "apps/api/\*\*/\*.py": \[  
         "pnpm \--filter api format", // Executa o script format (ruff \--fix, black) do app api  
         "pnpm \--filter api lint"    // Executa o script lint (ruff, mypy) do app api  
       \],  
       "\*.{json,md,yaml,yml}": \[  
         "prettier \--write"  
       \]  
     }  
   }

   A configuração do lint-staged deve invocar os scripts de lint e formatação definidos nos package.json de cada workspace (apps/web, apps/api, etc.) usando os filtros do pnpm (--filter \<nome\_do\_pacote\>).  
3. Configurar o Hook de Pre-commit do Husky:  
   Edite o arquivo .husky/pre-commit:  
   Bash  
   \#\!/bin/sh

. "$(dirname "$0")/\_/husky.sh"

pnpm exec lint-staged \--concurrent false  
\`\`\`  
Isso garante que \`lint-staged\` seja executado antes de cada commit, aplicando automaticamente formatação e verificações de lint. A menção de "Pre-commit hooks" em \[14\] sugere que esta é uma prática valiosa no contexto de templates full-stack.

### **6.5. Proxy de Desenvolvimento para API Backend (Next.js)**

Durante o desenvolvimento local, o frontend Next.js (rodando, por exemplo, na porta 3000\) precisará fazer requisições para o backend FastAPI (rodando, por exemplo, na porta 8000). Para evitar problemas de CORS e simplificar a configuração de URLs de API no frontend, um proxy pode ser configurado no Next.js.

* **Configuração em next.config.js (apps/web/next.config.mjs):**  
  JavaScript  
  // apps/web/next.config.mjs  
  /\*\* @type {import('next').NextConfig} \*/  
  const nextConfig \= {  
    reactStrictMode: true,  
    //... outras configurações  
    async rewrites() {  
      return;  
    },  
  };

  export default nextConfig;

  Com esta configuração, qualquer requisição feita pelo frontend para /api/v1/... será automaticamente encaminhada para http://localhost:8000/api/v1/... pelo servidor de desenvolvimento do Next.js.3 Isso só se aplica ao ambiente de desenvolvimento. Em produção, o frontend fará requisições diretamente para a URL pública do backend implantado.

A combinação do Turborepo com fluxos de trabalho automatizados, como a geração de cliente API e pre-commit hooks, cria um ambiente de desenvolvimento robusto, eficiente e com alta DX, essencial para um projeto com a complexidade de espelhar múltiplas plataformas de mensagens.

## **Capítulo 7: Estratégia de Implantação Serverless**

A implantação da aplicação "Mirror" será focada em arquiteturas serverless para garantir escalabilidade, resiliência e otimização de custos. O backend FastAPI será implantado no AWS Lambda (ou Vercel Functions como alternativa), e o frontend Next.js no Vercel (ou AWS S3/CloudFront).

### **7.1. FastAPI no AWS Lambda**

Implantar uma aplicação FastAPI no AWS Lambda requer um adaptador para traduzir os eventos do Lambda para o formato ASGI que o FastAPI entende.

#### **7.1.1. Empacotamento com uv para Lambda**

O objetivo é criar um arquivo .zip contendo a aplicação FastAPI e todas as suas dependências.

1. Script de Empacotamento (apps/api/scripts/package\_lambda.py):  
   Este script Python automatizará o processo.  
   Python  
   \# apps/api/scripts/package\_lambda.py  
   import os  
   import shutil  
   import subprocess  
   import zipfile  
   from pathlib import Path

   ROOT\_DIR \= Path(\_\_file\_\_).parent.parent \# Raiz de apps/api  
   APP\_DIR \= ROOT\_DIR / "app"  
   DIST\_DIR \= ROOT\_DIR / "dist"  
   DEPLOYMENT\_PACKAGE\_DIR \= DIST\_DIR / "lambda\_package"  
   ZIP\_FILE\_NAME \= "lambda\_function.zip"  
   ZIP\_FILE\_PATH \= DIST\_DIR / ZIP\_FILE\_NAME

   REQUIREMENTS\_FILE \= ROOT\_DIR / "requirements.txt" \# Gerado por 'uv pip freeze \> requirements.txt' ou 'uv pip compile'

   def run\_command(command, cwd=None):  
       print(f"Executando: {' '.join(command)}")  
       process \= subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)  
       stdout, stderr \= process.communicate()  
       if process.returncode\!= 0:  
           print(f"Erro ao executar comando: {' '.join(command)}")  
           print(f"STDOUT: {stdout.decode()}")  
           print(f"STDERR: {stderr.decode()}")  
           raise Exception(f"Comando falhou: {' '.join(command)}")  
       print(stdout.decode())

   def create\_deployment\_package():  
       \# 1\. Limpar diretórios de saída anteriores  
       if DIST\_DIR.exists():  
           shutil.rmtree(DIST\_DIR)  
       DIST\_DIR.mkdir(parents=True, exist\_ok=True)  
       DEPLOYMENT\_PACKAGE\_DIR.mkdir(parents=True, exist\_ok=True)

       \# 2\. Instalar dependências no diretório de empacotamento  
       \# Assegurar que requirements.txt está atualizado antes de rodar este script  
       \# (pode ser um passo anterior no pipeline do Turborepo ou CI/CD)  
       \# Exemplo: uv pip freeze \> apps/api/requirements.txt  
       if not REQUIREMENTS\_FILE.exists():  
           print(f"ERRO: {REQUIREMENTS\_FILE} não encontrado. Gere-o primeiro.")  
           \# Opcional: Gerar requirements.txt aqui se não for feito antes  
           \# run\_command(, cwd=ROOT\_DIR)  
           \# ou, se usando pyproject.toml com uv:  
           \# run\_command()  
           \# Para produção, é melhor compilar requirements.txt para a plataforma Lambda alvo:  
           \# uv pip compile pyproject.toml \-o requirements.txt \--python-platform manylinux2014\_x86\_64 \--python-version 3.10 (ou a versão do Lambda)  
           \# E então:  
           \# uv pip install \-r requirements.txt \--target./deployment\_package  
           \# Este exemplo simplificado assume que requirements.txt existe e é compatível.  
           \# Para dependências nativas, \`sam build \--use-container\` é mais robusto (ver Seção 9.3).  
           raise FileNotFoundError(f"{REQUIREMENTS\_FILE} não encontrado.")

       print(f"Instalando dependências de {REQUIREMENTS\_FILE} em {DEPLOYMENT\_PACKAGE\_DIR}")  
       run\_command()

       \# 3\. Copiar código da aplicação  
       print(f"Copiando código da aplicação de {APP\_DIR} para {DEPLOYMENT\_PACKAGE\_DIR}")  
       \# shutil.copytree(APP\_DIR, DEPLOYMENT\_PACKAGE\_DIR / "app", dirs\_exist\_ok=True)  
       \# Copia o conteúdo de APP\_DIR para DEPLOYMENT\_PACKAGE\_DIR/app  
       target\_app\_dir \= DEPLOYMENT\_PACKAGE\_DIR / "app"  
       if target\_app\_dir.exists(): \# Limpa se já existir do passo de dependências (improvável com \--target)  
           shutil.rmtree(target\_app\_dir)  
       shutil.copytree(APP\_DIR, target\_app\_dir, dirs\_exist\_ok=True)

       \# 4\. Criar arquivo.zip  
       print(f"Criando arquivo zip em {ZIP\_FILE\_PATH}")  
       with zipfile.ZipFile(ZIP\_FILE\_PATH, 'w', zipfile.ZIP\_DEFLATED) as zf:  
           for root, \_, files in os.walk(DEPLOYMENT\_PACKAGE\_DIR):  
               for file in files:  
                   file\_path \= Path(root) / file  
                   archive\_name \= file\_path.relative\_to(DEPLOYMENT\_PACKAGE\_DIR)  
                   zf.write(file\_path, archive\_name)

       print("Pacote de deployment criado com sucesso\!")

   if \_\_name\_\_ \== "\_\_main\_\_":  
       create\_deployment\_package()

   Este script instala dependências usando uv pip install \--target e copia o código da aplicação para uma pasta, depois compacta tudo.15  
   A tarefa api\#build:lambda no turbo.json (definida no Capítulo 6\) executará este script. O outputs para esta tarefa será \["apps/api/dist/lambda\_function.zip"\] para que o Turborepo possa cachear o artefato.22  
   Para dependências com compilação nativa, o uso de sam build \--use-container (detalhado na Seção 9.3) é uma abordagem mais robusta, pois compila dentro de um ambiente similar ao Lambda.134 Se uv for usado diretamente, deve-se garantir que as wheels baixadas sejam compatíveis com a arquitetura e o sistema operacional do Lambda (e.g., manylinux).

#### **7.1.2. Adaptadores de Implantação: Mangum vs. AWS Lambda Web Adapter**

* **Mangum:**  
  * Um adaptador leve que converte eventos do AWS API Gateway (e outros triggers) em requisições ASGI para o FastAPI.126  
  * **Uso:** Adicionar mangum às dependências e no main.py da FastAPI:  
    Python  
    \# apps/api/app/main.py  
    from fastapi import FastAPI  
    from mangum import Mangum

    app \= FastAPI(title="MirrorApp API", openapi\_url="/api/v1/openapi.json")  
    \#... suas rotas...

    \# O handler que o Lambda irá chamar  
    handler \= Mangum(app, lifespan="off") \# lifespan="on" pode ser usado para startups/shutdowns

    O handler é o ponto de entrada que o AWS Lambda invocará.  
  * **Prós:** Simples de configurar para deployments baseados em.zip, bom desempenho para a maioria dos casos.  
  * **Contras:** Menos flexibilidade comparado a rodar um container completo, a experiência de desenvolvimento local pode não espelhar 100% o ambiente Lambda sem emulação.  
* **AWS Lambda Web Adapter:**  
  * Permite rodar aplicações web (incluindo FastAPI com Uvicorn) em Lambda, seja em um container Docker ou como um Lambda Layer com um.zip.140  
  * **Uso (com.zip e Lambda Layer):** O Web Adapter é adicionado como uma Lambda Layer. A aplicação FastAPI é empacotada normalmente, e o Web Adapter lida com a invocação.  
  * **Uso (com Container):** O Dockerfile da aplicação FastAPI incluiria o Web Adapter.  
    Dockerfile  
    \# Exemplo de Dockerfile para FastAPI com Web Adapter  
    FROM public.ecr.aws/docker/library/python:3.10-slim-buster  
    WORKDIR /var/task  
    COPY \--from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter \# Adiciona o adapter  
    COPY./requirements.txt.  
    RUN pip install \-r requirements.txt \--no-cache-dir  
    COPY./app /var/task/app  
    \# Variáveis de ambiente como PORT podem ser configuradas no Lambda  
    CMD

  * **Prós:** Permite rodar a aplicação web quase sem modificações, desenvolvimento local mais próximo do ambiente de produção (se usando containers localmente), pode lidar com inicializações mais complexas.  
  * **Contras:** Pode ter uma curva de aprendizado ligeiramente maior, especialmente se for o primeiro contato com containers no Lambda. Cold starts podem ser mais impactados se a imagem do container for grande ou a inicialização da aplicação for lenta, embora o Web Adapter tente mitigar isso.140  
* **Recomendação:**  
  * Para um início rápido e deployment via .zip gerenciado pelo script package\_lambda.py e uv, **Mangum** é mais direto.137  
  * Se a aplicação se tornar complexa, exigir um ambiente de execução mais customizado, ou se a equipe já estiver confortável com containers, o **AWS Lambda Web Adapter** com deployment de container oferece mais flexibilidade.140  
  * A escolha também pode depender da estratégia de IaC (AWS SAM/CDK), pois ambos os adaptadores podem ser configurados.

#### **7.1.3. Otimização de Cold Start (2024/2025)**

Cold starts são uma consideração importante para aplicações serverless, especialmente as interativas.140

* **Tamanho do Pacote:** Manter o .zip ou a imagem do container o menor possível. Usar uv para instalar apenas as dependências de produção.  
* **Provisioned Concurrency:** Para endpoints críticos com requisitos de baixa latência, configurar Provisioned Concurrency no Lambda. Isso mantém um número de instâncias pré-aquecidas, mas incorre em custos adicionais.146  
* **AWS Lambda SnapStart:** Atualmente disponível para Java, mas o conceito de "priming" (pré-inicialização) é relevante. Para Python, isso se traduz em:  
  * Otimizar o tempo de importação de módulos.  
  * Inicializar conexões de banco de dados ou outros recursos de forma lazy (preguiçosa) ou de maneira eficiente durante a fase de init do Lambda.  
  * Otimizar o código Python para inicialização rápida.144  
* **Escolha da Memória:** Alocar memória suficiente para a função Lambda. Mais memória também significa mais CPU, o que pode reduzir o tempo de inicialização. Testar diferentes configurações é essencial.  
* **Reutilização de Conexões:** Manter conexões de banco de dados (e outras conexões de rede) fora do handler da função para que possam ser reutilizadas entre invocações na mesma instância aquecida. O AsyncSessionFactory configurado anteriormente já auxilia nisso.  
* **Monitoramento:** Usar AWS X-Ray e CloudWatch Logs para identificar gargalos de cold start.

A otimização de cold start é um processo contínuo. As estratégias mais eficazes em 2024/2025 continuam focadas em reduzir o tamanho do artefato, otimizar o código de inicialização e usar recursos como Provisioned Concurrency quando o custo-benefício justifica.146

### **7.2. Implantação do Frontend Next.js**

* **Vercel (Recomendado):**  
  * Vercel é a plataforma dos criadores do Next.js e oferece a integração mais fluida, com otimizações de build, Edge Network global, e CI/CD integrados.3  
  * **Configuração para Monorepo:** No dashboard do Vercel, ao importar o projeto do GitHub, especificar o "Root Directory" como apps/web.109  
  * **Build Command:** Vercel geralmente detecta Next.js e usa next build. Para monorepos com Turborepo, o comando de build no Vercel pode ser configurado para cd../.. && pnpm turbo run build \--filter=web para garantir que as dependências do workspace e o cache do Turborepo sejam utilizados corretamente.109  
  * **Output Directory:** Automaticamente detectado como .next.  
  * **Variáveis de Ambiente:** Configurar NEXT\_PUBLIC\_API\_BASE\_URL (apontando para a URL do backend FastAPI implantado) e NEXTAUTH\_URL, NEXTAUTH\_SECRET no Vercel.  
  * **Turborepo Remote Caching:** Vercel oferece Remote Caching gratuito que se integra automaticamente com builds do Turborepo na plataforma.23  
* **Alternativa: AWS S3 \+ CloudFront:**  
  * Exportar a aplicação Next.js como um site estático (next build && next export se não houver SSR/rotas de API Next.js, ou usar soluções como OpenNext/Serverless Next.js para SSR no Lambda@Edge) e hospedar no S3 com distribuição via CloudFront.139  
  * Mais complexo de configurar e otimizar para todas as funcionalidades do Next.js (ISR, Image Optimization, etc.) comparado ao Vercel.

### **7.3. Configuração do API Gateway para FastAPI Lambda**

Se o backend FastAPI for implantado no AWS Lambda, o Amazon API Gateway será usado para expor os endpoints HTTP.

* **Tipo de API:** HTTP API (mais barato e mais rápido para casos de uso serverless) ou REST API (mais funcionalidades, como transformação de requests/responses).  
* **Integração Lambda:** Configurar uma integração do tipo "Lambda Function" apontando para a função FastAPI.  
* **Rotas:** Mapear rotas do API Gateway (e.g., ANY /{proxy+}) para a função Lambda. O FastAPI lidará com o roteamento interno.  
* **Autorização:** Pode-se configurar autorizadores Lambda (usando o JWT da aplicação "Mirror") ou usar outras formas de autenticação do API Gateway.  
* **Domínios Customizados:** Configurar um domínio customizado para a API.

### **7.4. Implantação do Backend FastAPI no Vercel (Alternativa)**

FastAPI pode ser implantado como Vercel Serverless Functions, aproveitando o runtime Python do Vercel.159

* **Estrutura:** O código FastAPI (apps/api/app) seria colocado dentro de um diretório api na raiz do projeto Vercel (ou no root directory configurado para o backend no Vercel, e.g., apps/api). Vercel trata arquivos .py no diretório api (ou subdiretórios) como serverless functions.3  
  * Para um monorepo, o "Root Directory" para o projeto Vercel do backend seria apps/api.  
  * Um único arquivo de entrada, e.g., apps/api/index.py (ou apps/api/api/index.py se Vercel buscar recursivamente), conteria a instância da app FastAPI:  
    Python  
    \# apps/api/index.py (ou apps/api/api/index.py)  
    from app.main import app \# Assumindo que app.main.app é sua instância FastAPI  
    \# Vercel irá procurar por uma variável 'app' que seja uma aplicação ASGI/WSGI.

* **Dependências:** Vercel usa requirements.txt ou Pipfile com Pipfile.lock.159 uv pode ser usado para gerar requirements.txt a partir do pyproject.toml ou uv.lock como parte do script de build.  
  * uv pip compile pyproject.toml \-o requirements.txt \--python-version 3.12 (ou a versão Python configurada no Vercel).  
* **Configuração vercel.json (na raiz de apps/api ou na raiz do monorepo com rootDirectory):**  
  JSON  
  // Exemplo de vercel.json em apps/api, se for um projeto Vercel separado  
  // Ou na raiz do monorepo com configurações de build para múltiplos apps  
  {  
    "version": 2,  
    "builds":,  
    "routes":,  
    "functions": {  
      "index.py": { // Ou o nome do seu arquivo de entrada  
        "runtime": "python3.12" // Especificar a versão do Python \[159\]  
      }  
    }  
    // Configurações de environment variables, etc.  
  }

  Se estiver usando Turborepo e implantando o monorepo inteiro em um único projeto Vercel (menos comum para backends Python separados), a configuração do Vercel precisaria distinguir os builds do frontend e backend. Mais comumente, seriam projetos Vercel separados para apps/web e apps/api.  
* Build Command no Vercel (para apps/api):  
  uv pip install \-r requirements.txt \--no-deps && \<outros comandos de build se necessário\>  
  O Vercel instala as dependências do requirements.txt automaticamente. Se uv

#### **Referências citadas**

1. Shadcn UI for Beginners: The Ultimate Step-by-Step Tutorial \- CodeParrot, acessado em junho 8, 2025, [https://codeparrot.ai/blogs/shadcn-ui-for-beginners-the-ultimate-guide-and-step-by-step-tutorial](https://codeparrot.ai/blogs/shadcn-ui-for-beginners-the-ultimate-guide-and-step-by-step-tutorial)  
2. A Curated List of shadcn/ui-like React Component Collections \- DEV Community, acessado em junho 8, 2025, [https://dev.to/keitam83/a-curated-list-of-shadcnui-like-react-component-collections-44pa](https://dev.to/keitam83/a-curated-list-of-shadcnui-like-react-component-collections-44pa)  
3. Rapid Development with Next.js \+ FastAPI \+ Vercel \+ Neon Postgres \- Wolk, acessado em junho 8, 2025, [https://www.wolk.work/blog/posts/rapid-development-with-next-js-fastapi-vercel-neon-postgres](https://www.wolk.work/blog/posts/rapid-development-with-next-js-fastapi-vercel-neon-postgres)  
4. Host your Python app for $1.28 a month | Pulumi Blog, acessado em junho 8, 2025, [https://www.pulumi.com/blog/serverless-api/](https://www.pulumi.com/blog/serverless-api/)  
5. Full-Stack SaaS Starter Template with Bun & Next.js \- Bstack \- NextGen JavaScript, acessado em junho 8, 2025, [https://next.jqueryscript.net/next-js/full-stack-saas-template/](https://next.jqueryscript.net/next-js/full-stack-saas-template/)  
6. What is Turborepo and Why Should You Care? \- Refine dev, acessado em junho 8, 2025, [https://refine.dev/blog/how-to-use-turborepo/](https://refine.dev/blog/how-to-use-turborepo/)  
7. Security \- First Steps \- FastAPI, acessado em junho 8, 2025, [https://fastapi.tiangolo.com/tutorial/security/first-steps/](https://fastapi.tiangolo.com/tutorial/security/first-steps/)  
8. Best Serverless Functions: AWS vs. Vercel vs. Azure in 2025 \- Research AIMultiple, acessado em junho 8, 2025, [https://research.aimultiple.com/serverless-functions/](https://research.aimultiple.com/serverless-functions/)  
9. SQLModel vs SQLAlchemy in 2025 : r/FastAPI \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/FastAPI/comments/1je0xqn/sqlmodel\_vs\_sqlalchemy\_in\_2025/](https://www.reddit.com/r/FastAPI/comments/1je0xqn/sqlmodel_vs_sqlalchemy_in_2025/)  
10. Asynchronous Database Sessions in FastAPI with SQLAlchemy \- DEV Community, acessado em junho 8, 2025, [https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e](https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e)  
11. Turborepo, acessado em junho 8, 2025, [https://turborepo.com/](https://turborepo.com/)  
12. Streaming in Next.js 15: WebSockets vs Server-Sent Events | HackerNoon, acessado em junho 8, 2025, [https://hackernoon.com/streaming-in-nextjs-15-websockets-vs-server-sent-events](https://hackernoon.com/streaming-in-nextjs-15-websockets-vs-server-sent-events)  
13. Realtime Dashboard with FastAPI, Streamlit and Next.js \- Part 3 Next.js Dashboard, acessado em junho 8, 2025, [https://jaehyeon.me/blog/2025-03-04-realtime-dashboard-3/](https://jaehyeon.me/blog/2025-03-04-realtime-dashboard-3/)  
14. vintasoftware/nextjs-fastapi-template: State of the art project template that integrates Next.js, Zod, FastAPI for full-stack TypeScript \+ Python projects. \- GitHub, acessado em junho 8, 2025, [https://github.com/vintasoftware/nextjs-fastapi-template](https://github.com/vintasoftware/nextjs-fastapi-template)  
15. Share Python Scripts Like a Pro: uv and PEP 723 for Easy Deployment | thisDaveJ, acessado em junho 8, 2025, [https://thisdavej.com/share-python-scripts-like-a-pro-uv-and-pep-723-for-easy-deployment/](https://thisdavej.com/share-python-scripts-like-a-pro-uv-and-pep-723-for-easy-deployment/)  
16. Introduction to PDM: A Python Project and Dependency Manager | Better Stack Community, acessado em junho 8, 2025, [https://betterstack.com/community/guides/scaling-python/pdm-explained/](https://betterstack.com/community/guides/scaling-python/pdm-explained/)  
17. Tips for managing FastAPI project \#2491 \- GitHub, acessado em junho 8, 2025, [https://github.com/fastapi/fastapi/discussions/2491](https://github.com/fastapi/fastapi/discussions/2491)  
18. TypeScript \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/guides/tools/typescript](https://turborepo.com/docs/guides/tools/typescript)  
19. ESLint \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/guides/tools/eslint](https://turborepo.com/docs/guides/tools/eslint)  
20. Structuring a repository \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/crafting-your-repository/structuring-a-repository](https://turborepo.com/docs/crafting-your-repository/structuring-a-repository)  
21. Configuring turbo.json | Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/reference/configuration](https://turborepo.com/docs/reference/configuration)  
22. Configuring tasks | Turborepo, acessado em junho 8, 2025, [https://turbo.build/docs/crafting-your-repository/configuring-tasks](https://turbo.build/docs/crafting-your-repository/configuring-tasks)  
23. Caching \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/crafting-your-repository/caching](https://turborepo.com/docs/crafting-your-repository/caching)  
24. Next.js \- Shadcn UI, acessado em junho 8, 2025, [https://ui.shadcn.com/docs/installation/next](https://ui.shadcn.com/docs/installation/next)  
25. fastapi/full-stack-fastapi-template: Full stack, modern web ... \- GitHub, acessado em junho 8, 2025, [https://github.com/tiangolo/full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql)  
26. acessado em dezembro 31, 1969, [https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app)  
27. acessado em dezembro 31, 1969, [https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app/app](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app)  
28. How to secure APIs built with FastAPI: A complete guide \- Escape.tech, acessado em junho 8, 2025, [https://escape.tech/blog/how-to-secure-fastapi-api/](https://escape.tech/blog/how-to-secure-fastapi-api/)  
29. Securing FastAPI with JWT Token-based Authentication | TestDriven.io, acessado em junho 8, 2025, [https://testdriven.io/blog/fastapi-jwt-auth/](https://testdriven.io/blog/fastapi-jwt-auth/)  
30. acessado em dezembro 31, 1969, [https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app/app/core/security.py](https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/core/security.py)  
31. acessado em dezembro 31, 1969, [https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app/app/core/security.py](https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/core/security.py)  
32. Fernet (symmetric encryption) — Cryptography 46.0.0.dev1 documentation, acessado em junho 8, 2025, [https://cryptography.io/en/latest/fernet/](https://cryptography.io/en/latest/fernet/)  
33. Refreshing tokens in OAuth 2 \- Requests-OAuthlib, acessado em junho 8, 2025, [https://requests-oauthlib.readthedocs.io/en/latest/examples/real\_world\_example\_with\_refresh.html](https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example_with_refresh.html)  
34. Problems with Token refreshing. · Issue \#264 · requests/requests-oauthlib \- GitHub, acessado em junho 8, 2025, [https://github.com/requests/requests-oauthlib/issues/264](https://github.com/requests/requests-oauthlib/issues/264)  
35. Examples on how to implement the OAuth2 authorization code flow using FastAPI \- GitHub, acessado em junho 8, 2025, [https://github.com/lukasthaler/fastapi-oauth-examples](https://github.com/lukasthaler/fastapi-oauth-examples)  
36. vanshpatelx/multi-lang-turborepo: Multi Language turbo repo setup \- golang, rust, python, typescript \- GitHub, acessado em junho 8, 2025, [https://github.com/vanshpatelx/multi-lang-turborepo](https://github.com/vanshpatelx/multi-lang-turborepo)  
37. hey-api/openapi-ts: The OpenAPI to TypeScript codegen. Generate clients, SDKs, validators, and more. Support \- GitHub, acessado em junho 8, 2025, [https://github.com/hey-api/openapi-ts](https://github.com/hey-api/openapi-ts)  
38. How to protect sensitive configuration data \- LabEx, acessado em junho 8, 2025, [https://labex.io/tutorials/wireshark-how-to-protect-sensitive-configuration-data-419465](https://labex.io/tutorials/wireshark-how-to-protect-sensitive-configuration-data-419465)  
39. Best practices for FastAPI projects with SQLModel ORM and PostgreSQL database \#9936, acessado em junho 8, 2025, [https://github.com/fastapi/fastapi/discussions/9936](https://github.com/fastapi/fastapi/discussions/9936)  
40. SQLModel vs native SQL Alchemy ORM for a web backend? : r/Python \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/Python/comments/1br19x3/sqlmodel\_vs\_native\_sql\_alchemy\_orm\_for\_a\_web/](https://www.reddit.com/r/Python/comments/1br19x3/sqlmodel_vs_native_sql_alchemy_orm_for_a_web/)  
41. Looking for SQL ORM for FastAPI · Issue \#53 \- GitHub, acessado em junho 8, 2025, [https://github.com/zhanymkanov/fastapi-best-practices/issues/53](https://github.com/zhanymkanov/fastapi-best-practices/issues/53)  
42. OAuth2 with Password (and hashing), Bearer with JWT tokens ..., acessado em junho 8, 2025, [https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)  
43. Next.js store JWT from external API to use it for calls to that API \- Stack Overflow, acessado em junho 8, 2025, [https://stackoverflow.com/questions/77826240/next-js-store-jwt-from-external-api-to-use-it-for-calls-to-that-api](https://stackoverflow.com/questions/77826240/next-js-store-jwt-from-external-api-to-use-it-for-calls-to-that-api)  
44. acessado em dezembro 31, 1969, [https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app/app/api/deps.py](https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/api/deps.py)  
45. acessado em dezembro 31, 1969, [https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project\_slug%7D%7D/backend/app/app/api/deps.py](https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/api/deps.py)  
46. How-To Fernet Encrypt / Store / Decrypt OAuth Tokens in DynamoDB (Python) \- Questions, acessado em junho 8, 2025, [https://developer.squareup.com/forums/t/how-to-fernet-encrypt-store-decrypt-oauth-tokens-in-dynamodb-python/12696](https://developer.squareup.com/forums/t/how-to-fernet-encrypt-store-decrypt-oauth-tokens-in-dynamodb-python/12696)  
47. Help with refresh tokens \- FastAPI \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/FastAPI/comments/1h876z7/help\_with\_refresh\_tokens/](https://www.reddit.com/r/FastAPI/comments/1h876z7/help_with_refresh_tokens/)  
48. OAuth2 Example | Logout and Refresh Token : r/FastAPI \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/FastAPI/comments/1fed43y/oauth2\_example\_logout\_and\_refresh\_token/](https://www.reddit.com/r/FastAPI/comments/1fed43y/oauth2_example_logout_and_refresh_token/)  
49. The Developer's Guide to Refresh Token Rotation \- Descope, acessado em junho 8, 2025, [https://www.descope.com/blog/post/refresh-token-rotation](https://www.descope.com/blog/post/refresh-token-rotation)  
50. OAuth2 scopes \- FastAPI, acessado em junho 8, 2025, [https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)  
51. WhatsApp Business Cloud \- Apps Documentation, acessado em junho 8, 2025, [https://apps.make.com/whatsapp-business-cloud](https://apps.make.com/whatsapp-business-cloud)  
52. Comparing WhatsApp API, Cloud API & Official API: Key Differences Explained, acessado em junho 8, 2025, [https://www.go4whatsup.com/blog/comparing-whatsapp-api-cloud-api-official-api-key-differences-explained/](https://www.go4whatsup.com/blog/comparing-whatsapp-api-cloud-api-official-api-key-differences-explained/)  
53. Webhooks \- WhatsApp Cloud API \- Meta for Developers, acessado em junho 8, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks/](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks/)  
54. Webhooks \- WhatsApp Cloud API \- Documentation \- Meta for Developers, acessado em junho 8, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components/](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components/)  
55. Messaging \- WhatsApp Cloud API \- Meta for Developers, acessado em junho 8, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages/](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages/)  
56. Messages \- WhatsApp Cloud API \- Meta for Developers, acessado em junho 8, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages/](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages/)  
57. Overview \- WhatsApp Cloud API \- Meta for Developers, acessado em junho 8, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/overview/](https://developers.facebook.com/docs/whatsapp/cloud-api/overview/)  
58. acessado em dezembro 31, 1969, [https://github.com/dimitrianoudi/whatsapp\_api](https://github.com/dimitrianoudi/whatsapp_api)  
59. WhatsApp Business API: Automate Customer Messaging \- Infobip, acessado em junho 8, 2025, [https://www.infobip.com/whatsapp-business/api](https://www.infobip.com/whatsapp-business/api)  
60. Whatsapp Business API documentation, acessado em junho 8, 2025, [https://docs.1msg.io/](https://docs.1msg.io/)  
61. WhatsApp Business API: overview, limits and pricing \[2024\] \- Elfsight, acessado em junho 8, 2025, [https://elfsight.com/blog/whatsapp-business-api-overview/](https://elfsight.com/blog/whatsapp-business-api-overview/)  
62. Official Discord API Documentation \- GitHub, acessado em junho 8, 2025, [https://github.com/discord/discord-api-docs](https://github.com/discord/discord-api-docs)  
63. Community Resources | Documentation | Discord Developer Portal, acessado em junho 8, 2025, [https://discord.com/developers/docs/developer-tools/community-resources](https://discord.com/developers/docs/developer-tools/community-resources)  
64. Authentication | Discord Social SDK, acessado em junho 8, 2025, [https://discord.com/developers/docs/social-sdk/authentication.html](https://discord.com/developers/docs/social-sdk/authentication.html)  
65. OAuth Grant Types, acessado em junho 8, 2025, [https://oauth.net/2/grant-types/](https://oauth.net/2/grant-types/)  
66. Interactions | Documentation | Discord Developer Portal, acessado em junho 8, 2025, [https://discord.com/developers/docs/interactions/receiving-and-responding](https://discord.com/developers/docs/interactions/receiving-and-responding)  
67. discord api endpoints \- GitHub Gist, acessado em junho 8, 2025, [https://gist.github.com/hackermondev/5c928ca12b4f4e6320100b11f798c23b](https://gist.github.com/hackermondev/5c928ca12b4f4e6320100b11f798c23b)  
68. Personal Messages API \- Discord Support, acessado em junho 8, 2025, [https://support.discord.com/hc/en-us/community/posts/21233703405463-Personal-Messages-API](https://support.discord.com/hc/en-us/community/posts/21233703405463-Personal-Messages-API)  
69. New Message (Instant) from Discord API \- Pipedream, acessado em junho 8, 2025, [https://pipedream.com/apps/discord/triggers/new-message](https://pipedream.com/apps/discord/triggers/new-message)  
70. Rate Limits | Documentation | Discord Developer Portal, acessado em junho 8, 2025, [https://discord.com/developers/docs/topics/rate-limits](https://discord.com/developers/docs/topics/rate-limits)  
71. Handling API rate limits \- Comprehensive Guide to Discord Bot Development with discord.py, acessado em junho 8, 2025, [https://app.studyraid.com/en/read/7183/176829/handling-api-rate-limits](https://app.studyraid.com/en/read/7183/176829/handling-api-rate-limits)  
72. Slack Developer Docs: Slack platform overview, acessado em junho 8, 2025, [https://docs.slack.dev/](https://docs.slack.dev/)  
73. Block Kit \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/block-kit](https://api.slack.com/block-kit)  
74. oauth.v2.access method \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/methods/oauth.v2.access](https://api.slack.com/methods/oauth.v2.access)  
75. OAuth 2.0 | Swagger Docs, acessado em junho 8, 2025, [https://swagger.io/docs/specification/v3\_0/authentication/oauth2/](https://swagger.io/docs/specification/v3_0/authentication/oauth2/)  
76. Retrieving messages \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/messaging/retrieving](https://api.slack.com/messaging/retrieving)  
77. chat.postMessage method \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/methods/chat.postMessage](https://api.slack.com/methods/chat.postMessage)  
78. Messages \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/surfaces/messages](https://api.slack.com/surfaces/messages)  
79. Events API | Slack, acessado em junho 8, 2025, [https://api.slack.com/events-api](https://api.slack.com/events-api)  
80. Legacy: Real Time Messaging API | Slack, acessado em junho 8, 2025, [https://api.slack.com/legacy/rtm](https://api.slack.com/legacy/rtm)  
81. Real Time Messaging (RTM) | Java Slack SDK, acessado em junho 8, 2025, [https://tools.slack.dev/java-slack-sdk/guides/rtm/](https://tools.slack.dev/java-slack-sdk/guides/rtm/)  
82. Rate limit changes for non-Marketplace apps \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq](https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq)  
83. Rate Limits \- Slack API, acessado em junho 8, 2025, [https://api.slack.com/apis/rate-limits](https://api.slack.com/apis/rate-limits)  
84. WebSockets \- FastAPI, acessado em junho 8, 2025, [https://fastapi.tiangolo.com/advanced/websockets/](https://fastapi.tiangolo.com/advanced/websockets/)  
85. WebSockets \- FastAPI, acessado em junho 8, 2025, [https://fastapi.tiangolo.com/reference/websockets/](https://fastapi.tiangolo.com/reference/websockets/)  
86. FastAPI and WebSockets: A Comprehensive Guide \- Orchestra, acessado em junho 8, 2025, [https://www.getorchestra.io/guides/fastapi-and-websockets-a-comprehensive-guide](https://www.getorchestra.io/guides/fastapi-and-websockets-a-comprehensive-guide)  
87. Websockets on FastAPI: Implementing a simple chat with rooms in 20 minutes, acessado em junho 8, 2025, [https://dev.to/amverum/websockets-on-fastapi-implementing-a-simple-chat-with-rooms-in-20-minutes-26hj](https://dev.to/amverum/websockets-on-fastapi-implementing-a-simple-chat-with-rooms-in-20-minutes-26hj)  
88. gonzalo123/asgi\_ws: Creating a standalone WebSocket Server with FastApi and JWT Authentication in Python \- GitHub, acessado em junho 8, 2025, [https://github.com/gonzalo123/asgi\_ws](https://github.com/gonzalo123/asgi_ws)  
89. How to trigger a SSE With fastapi \- Stack Overflow, acessado em junho 8, 2025, [https://stackoverflow.com/questions/79418087/how-to-trigger-a-sse-with-fastapi](https://stackoverflow.com/questions/79418087/how-to-trigger-a-sse-with-fastapi)  
90. Generate Clients \- FastAPI, acessado em junho 8, 2025, [https://fastapi.tiangolo.com/advanced/generate-clients/](https://fastapi.tiangolo.com/advanced/generate-clients/)  
91. Generating API clients in monorepos with FastAPI & Next.js \- Vinta Software, acessado em junho 8, 2025, [https://www.vintasoftware.com/blog/nextjs-fastapi-monorepo](https://www.vintasoftware.com/blog/nextjs-fastapi-monorepo)  
92. How to generate an OpenAPI document with FastAPI \- Speakeasy, acessado em junho 8, 2025, [https://www.speakeasy.com/openapi/frameworks/fastapi](https://www.speakeasy.com/openapi/frameworks/fastapi)  
93. Getting Started \- NextAuth.js, acessado em junho 8, 2025, [https://next-auth.js.org/getting-started/example](https://next-auth.js.org/getting-started/example)  
94. fastapi auth in production \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/FastAPI/comments/1f3xwvj/fastapi\_auth\_in\_production/](https://www.reddit.com/r/FastAPI/comments/1f3xwvj/fastapi_auth_in_production/)  
95. Next.js and FastAPI Authentication : r/nextjs \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/nextjs/comments/1hwwxqx/nextjs\_and\_fastapi\_authentication/](https://www.reddit.com/r/nextjs/comments/1hwwxqx/nextjs_and_fastapi_authentication/)  
96. Credentials | NextAuth.js, acessado em junho 8, 2025, [https://next-auth.js.org/providers/credentials](https://next-auth.js.org/providers/credentials)  
97. How to Manage Backend JWT Access Tokens in Next Auth and Next.js 13 \- YouTube, acessado em junho 8, 2025, [https://m.youtube.com/watch?v=fYObrr3jf0w\&t=17s](https://m.youtube.com/watch?v=fYObrr3jf0w&t=17s)  
98. Explain how to use your own JWT token in next-auth Credentials provider (Not created by next-auth) · Issue \#11295 \- GitHub, acessado em junho 8, 2025, [https://github.com/nextauthjs/next-auth/issues/11295](https://github.com/nextauthjs/next-auth/issues/11295)  
99. acessado em dezembro 31, 1969, [https://docs.authjs.dev/guides/providers/credentials](https://docs.authjs.dev/guides/providers/credentials)  
100. acessado em dezembro 31, 1969, [https://authjs.dev/guides/providers/credentials-provider](https://authjs.dev/guides/providers/credentials-provider)  
101. 2-fly-4-ai/awesome-shadcnui: The largest list online of awesome things related to shadcn/ui \- GitHub, acessado em junho 8, 2025, [https://github.com/2-fly-4-ai/awesome-shadcnui](https://github.com/2-fly-4-ai/awesome-shadcnui)  
102. A curated list of awesome things related to shadcn/ui. \- GitHub, acessado em junho 8, 2025, [https://github.com/birobirobiro/awesome-shadcn-ui](https://github.com/birobirobiro/awesome-shadcn-ui)  
103. 10 Awesome shadcn/ui Components I Tried (So Far) \- Hugging Face, acessado em junho 8, 2025, [https://huggingface.co/blog/lynn-mikami/awesome-shadcn-ui-components](https://huggingface.co/blog/lynn-mikami/awesome-shadcn-ui-components)  
104. Prompts & Integrations \- Lovable Documentation, acessado em junho 8, 2025, [https://docs.lovable.dev/integrations/prompt-integrations](https://docs.lovable.dev/integrations/prompt-integrations)  
105. jakobhoeg/shadcn-chat: CLI for adding customizable and re-usable chat components to your applications. Build beautiful chat interfaces in minutes. \- GitHub, acessado em junho 8, 2025, [https://github.com/jakobhoeg/shadcn-chat](https://github.com/jakobhoeg/shadcn-chat)  
106. 10 Awesome Shadcn/UI Components that You're Gonna Love \- Apidog, acessado em junho 8, 2025, [https://apidog.com/blog/awesome-shadcn-ui-components/](https://apidog.com/blog/awesome-shadcn-ui-components/)  
107. Show HN: Nue – Apps lighter than a React button | Hacker News, acessado em junho 8, 2025, [https://news.ycombinator.com/item?id=43543241](https://news.ycombinator.com/item?id=43543241)  
108. Simplest way to build Real Time Chat (Next.js 15, Shadcn, Supabase UI) \- YouTube, acessado em junho 8, 2025, [https://www.youtube.com/watch?v=CVKG05x35sA](https://www.youtube.com/watch?v=CVKG05x35sA)  
109. Deploy a Turborepo App to Vercel \- Dotenv, acessado em junho 8, 2025, [https://www.dotenv.org/docs/frameworks/turborepo/vercel](https://www.dotenv.org/docs/frameworks/turborepo/vercel)  
110. Turborepo 2.5, acessado em junho 8, 2025, [https://turborepo.com/blog/turbo-2-5](https://turborepo.com/blog/turbo-2-5)  
111. acessado em dezembro 31, 1969, [https://github.com/vintasoftware/nextjs-fastapi-template/blob/main/turbo.json](https://github.com/vintasoftware/nextjs-fastapi-template/blob/main/turbo.json)  
112. acessado em dezembro 31, 1969, [https://github.com/SanKirDev/turborepo-fastapi-nextjs-prisma-docker](https://github.com/SanKirDev/turborepo-fastapi-nextjs-prisma-docker)  
113. acessado em dezembro 31, 1969, [https://github.com/ThePrimeagen/turborepo-rust-example/blob/main/turbo.json](https://github.com/ThePrimeagen/turborepo-rust-example/blob/main/turbo.json)  
114. cording12/next-fast-turbo: A Turborepo featuring a Next.js frontend, FastAPI backend and a fully built and annotated Mintlify documentation site. \- GitHub, acessado em junho 8, 2025, [https://github.com/cording12/next-fast-turbo](https://github.com/cording12/next-fast-turbo)  
115. acessado em dezembro 31, 1969, [https://github.com/cording12/next-fast-turbo/blob/main/turbo.json](https://github.com/cording12/next-fast-turbo/blob/main/turbo.json)  
116. Caching | Turborepo, acessado em junho 8, 2025, [https://turborepo.org/docs/core-concepts/caching\#defining-outputs](https://turborepo.org/docs/core-concepts/caching#defining-outputs)  
117. acessado em dezembro 31, 1969, [https://turborepo.org/docs/reference/command-line-interface/run\#--outputs](https://turborepo.org/docs/reference/command-line-interface/run#--outputs)  
118. Generating TypeScript Types with OpenAPI for REST API Consumption | PullRequest Blog, acessado em junho 8, 2025, [https://www.pullrequest.com/blog/generating-typescript-types-with-openapi-for-rest-api-consumption/](https://www.pullrequest.com/blog/generating-typescript-types-with-openapi-for-rest-api-consumption/)  
119. openapi-typescript/turbo.json at main \- GitHub, acessado em junho 8, 2025, [https://github.com/openapi-ts/openapi-typescript/blob/main/turbo.json](https://github.com/openapi-ts/openapi-typescript/blob/main/turbo.json)  
120. turbo build \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/llms.txt](https://turborepo.com/llms.txt)  
121. Turborepo in Next.js: Guide for Faster & Smarter Builds \- DEV Community, acessado em junho 8, 2025, [https://dev.to/abhinandan-verma/turborepo-in-nextjs-guide-for-faster-smarter-builds-539f](https://dev.to/abhinandan-verma/turborepo-in-nextjs-guide-for-faster-smarter-builds-539f)  
122. Running tasks | Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/crafting-your-repository/running-tasks](https://turborepo.com/docs/crafting-your-repository/running-tasks)  
123. Understanding Code Management with Monorepos and Turborepo. \- GeeksforGeeks, acessado em junho 8, 2025, [https://www.geeksforgeeks.org/mern/understanding-code-management-with-monorepos-and-turborepo/](https://www.geeksforgeeks.org/mern/understanding-code-management-with-monorepos-and-turborepo/)  
124. nextjs-fastapi-template/README.md at main \- GitHub, acessado em junho 8, 2025, [https://github.com/vintasoftware/nextjs-fastapi-template/blob/main/README.md](https://github.com/vintasoftware/nextjs-fastapi-template/blob/main/README.md)  
125. How to use FastApi with NextJs? \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/FastAPI/comments/11d8k7u/how\_to\_use\_fastapi\_with\_nextjs/](https://www.reddit.com/r/FastAPI/comments/11d8k7u/how_to_use_fastapi_with_nextjs/)  
126. Using uv with AWS Lambda \- Astral Docs, acessado em junho 8, 2025, [https://docs.astral.sh/uv/guides/integration/aws-lambda/](https://docs.astral.sh/uv/guides/integration/aws-lambda/)  
127. How can I migrate from Poetry to UV package manager? \- Stack Overflow, acessado em junho 8, 2025, [https://stackoverflow.com/questions/79118841/how-can-i-migrate-from-poetry-to-uv-package-manager](https://stackoverflow.com/questions/79118841/how-can-i-migrate-from-poetry-to-uv-package-manager)  
128. Simple Serverless FastAPI with AWS Lambda \- deadbearcode, acessado em junho 8, 2025, [https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/](https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/)  
129. acessado em dezembro 31, 1969, [https://docs.astral.sh/uv/faq/](https://docs.astral.sh/uv/faq/)  
130. Manage Dependencies \- PDM, acessado em junho 8, 2025, [https://pdm-project.org/latest/usage/dependency/](https://pdm-project.org/latest/usage/dependency/)  
131. acessado em dezembro 31, 1969, [https://aws.amazon.com/blogs/compute/packaging-python-dependencies-for-aws-lambda-with-serverless-functions/](https://aws.amazon.com/blogs/compute/packaging-python-dependencies-for-aws-lambda-with-serverless-functions/)  
132. \[turborepo\] Cannot understand what outputs in turbo.json means. \#4568 \- GitHub, acessado em junho 8, 2025, [https://github.com/vercel/turbo/discussions/4568](https://github.com/vercel/turbo/discussions/4568)  
133. Remote Caching | Turborepo, acessado em junho 8, 2025, [https://turbo.build/docs/core-concepts/remote-caching](https://turbo.build/docs/core-concepts/remote-caching)  
134. Serverless FastAPI application deployed in AWS Lambda using AWS SAM \- GitHub, acessado em junho 8, 2025, [https://github.com/tzelleke/aws-sam-fastapi](https://github.com/tzelleke/aws-sam-fastapi)  
135. sam build \- AWS Serverless Application Model, acessado em junho 8, 2025, [https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html)  
136. Default build with AWS SAM \- AWS Serverless Application Model \- AWS Documentation, acessado em junho 8, 2025, [https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-build.html](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-build.html)  
137. Building a serverless GenAI API with FastAPI, AWS, and CircleCI, acessado em junho 8, 2025, [https://circleci.com/blog/building-a-serverless-genai-api/](https://circleci.com/blog/building-a-serverless-genai-api/)  
138. AWS Lambda With Magnum and FastAPI | My (Work)Space, acessado em junho 8, 2025, [https://blog.popescul.com/posts/2025/03/26/aws-lambda-with-magnum-and-fastapi/](https://blog.popescul.com/posts/2025/03/26/aws-lambda-with-magnum-and-fastapi/)  
139. How do you host your projects? \- Indie Hackers, acessado em junho 8, 2025, [https://www.indiehackers.com/post/how-do-you-host-your-projects-fb7e90ab07](https://www.indiehackers.com/post/how-do-you-host-your-projects-fb7e90ab07)  
140. I Tried Running an MCP Server on AWS Lambda… Here's What Happened \- Ran The Builder, acessado em junho 8, 2025, [https://www.ranthebuilder.cloud/post/mcp-server-on-aws-lambda](https://www.ranthebuilder.cloud/post/mcp-server-on-aws-lambda)  
141. AWS Lambda successfully called with 'Function URL', but not with 'API Gateway', acessado em junho 8, 2025, [https://stackoverflow.com/questions/78243198/aws-lambda-successfully-called-with-function-url-but-not-with-api-gateway](https://stackoverflow.com/questions/78243198/aws-lambda-successfully-called-with-function-url-but-not-with-api-gateway)  
142. Deploy FastAPI on AWS Lambda | In 9 MINUTES \- YouTube, acessado em junho 8, 2025, [https://m.youtube.com/watch?v=7-CvGFJNE\_o\&t=0s](https://m.youtube.com/watch?v=7-CvGFJNE_o&t=0s)  
143. How to Deploy FastAPI on AWS Lambda \- YouTube, acessado em junho 8, 2025, [https://www.youtube.com/watch?v=b0XCH04K8eQ](https://www.youtube.com/watch?v=b0XCH04K8eQ)  
144. Serverless DeepSeek R1 Inference with FastAPI and Lambda SnapStart \- GitHub, acessado em junho 8, 2025, [https://github.com/aws-samples/sample-chatbot-lambda-snapstart](https://github.com/aws-samples/sample-chatbot-lambda-snapstart)  
145. aws-lambda-web-adapter/examples/fastapi/README.md at main \- GitHub, acessado em junho 8, 2025, [https://github.com/awslabs/aws-lambda-web-adapter/blob/main/examples/fastapi/README.md](https://github.com/awslabs/aws-lambda-web-adapter/blob/main/examples/fastapi/README.md)  
146. AWS Lambda Cold Start: What It Is & Practical Ways to Reduce It \- Ran The Builder, acessado em junho 8, 2025, [https://www.ranthebuilder.cloud/post/is-aws-lambda-cold-start-still-an-issue-in-2024](https://www.ranthebuilder.cloud/post/is-aws-lambda-cold-start-still-an-issue-in-2024)  
147. Optimizing cold start performance of AWS Lambda using advanced priming strategies with SnapStart, acessado em junho 8, 2025, [https://aws.amazon.com/blogs/compute/optimizing-cold-start-performance-of-aws-lambda-using-advanced-priming-strategies-with-snapstart/](https://aws.amazon.com/blogs/compute/optimizing-cold-start-performance-of-aws-lambda-using-advanced-priming-strategies-with-snapstart/)  
148. Integrating Terraform with Vercel, acessado em junho 8, 2025, [https://vercel.com/guides/integrating-terraform-with-vercel](https://vercel.com/guides/integrating-terraform-with-vercel)  
149. How to deploy next js frontend \+ Fastapi and claude ai backend app on vercel? \- Reddit, acessado em junho 8, 2025, [https://www.reddit.com/r/nextjs/comments/1ielf5e/how\_to\_deploy\_next\_js\_frontend\_fastapi\_and\_claude/](https://www.reddit.com/r/nextjs/comments/1ielf5e/how_to_deploy_next_js_frontend_fastapi_and_claude/)  
150. Next.js FastAPI Starter \- Vercel, acessado em junho 8, 2025, [https://vercel.com/templates/next.js/nextjs-fastapi-starter](https://vercel.com/templates/next.js/nextjs-fastapi-starter)  
151. acessado em dezembro 31, 1969, [https://vintasoftware.github.io/nextjs-fastapi-template/deployment/fastapi\_backend/](https://vintasoftware.github.io/nextjs-fastapi-template/deployment/fastapi_backend/)  
152. acessado em dezembro 31, 1969, [https://github.com/orgs/vercel/discussions/4933](https://github.com/orgs/vercel/discussions/4933)  
153. acessado em dezembro 31, 1969, [https://github.com/cording12/next-fast-turbo/tree/main/apps/api](https://github.com/cording12/next-fast-turbo/tree/main/apps/api)  
154. acessado em dezembro 31, 1969, [https://github.com/cording12/next-fast-turbo/blob/main/vercel.json](https://github.com/cording12/next-fast-turbo/blob/main/vercel.json)  
155. GitHub Actions \- Turborepo, acessado em junho 8, 2025, [https://turborepo.com/docs/guides/ci-vendors/github-actions](https://turborepo.com/docs/guides/ci-vendors/github-actions)  
156. Terraform module for building and deploying Next.js apps to AWS. Supports SSR (Lambda), Static (S3) and API (Lambda) pages. \- GitHub, acessado em junho 8, 2025, [https://github.com/milliHQ/terraform-aws-next-js](https://github.com/milliHQ/terraform-aws-next-js)  
157. dealmore/next-js/aws \- Terraform Registry, acessado em junho 8, 2025, [https://registry.terraform.io/modules/dealmore/next-js/aws/latest](https://registry.terraform.io/modules/dealmore/next-js/aws/latest)  
158. NaumanMunir9/aws-cloudfront-s3-website-terraform: Deploy NextJS App to S3 and CloudFront with Github Actions, acessado em junho 8, 2025, [https://github.com/NaumanMunir9/aws-cloudfront-s3-website-terraform](https://github.com/NaumanMunir9/aws-cloudfront-s3-website-terraform)  
159. Using the Python Runtime with Vercel Functions, acessado em junho 8, 2025, [https://vercel.com/docs/functions/runtimes/python](https://vercel.com/docs/functions/runtimes/python)  
160. Configuring projects with vercel.json, acessado em junho 8, 2025, [https://vercel.com/docs/project-configuration](https://vercel.com/docs/project-configuration)  
161. Using the Python Runtime with Vercel Functions, acessado em junho 8, 2025, [https://vercel.com/docs/functions/serverless-functions/runtimes/python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)  
162. Build Output API \- Vercel, acessado em junho 8, 2025, [https://vercel.com/docs/build-output-api/v3](https://vercel.com/docs/build-output-api/v3)