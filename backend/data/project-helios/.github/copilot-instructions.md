# Orientações para o Agente de IA - Projeto Helios (HaaS)

Este documento fornece o contexto essencial para que um agente de IA seja produtivo neste workspace.

## 1. Visão Geral da Arquitetura

O **Project Helios** é uma plataforma de **Homologação como Serviço (HaaS)** para o mercado brasileiro de energia solar. O objetivo é automatizar e acelerar o processo burocrático de homologação de projetos fotovoltaicos junto às concessionárias de energia.

O repositório contém tanto a documentação estratégica do negócio quanto a implementação técnica da plataforma principal.

### Componentes Chave:

1.  **Documentação Estratégica (`/`)**: Contém modelos de negócio, análises financeiras e estratégia de go-to-market. É a fonte do "porquê" do projeto.
2.  **Aplicação HaaS (`/haas`)**: O coração técnico do projeto. É uma API **FastAPI** projetada para ser executada em contêineres Docker.
    -   **Configuração**: As configurações são gerenciadas em `haas/app/config.py` e `haas/core/config.py`, utilizando variáveis de ambiente (padrão Pydantic `BaseSettings`).
    -   **Banco de Dados**: Utiliza **PostgreSQL** com **PostGIS** (para dados geoespaciais) e **pgvector** (para busca semântica). O schema é gerenciado pelo **Alembic** (`haas/alembic/`). Os modelos ORM do SQLAlchemy estão em `haas/app/database/models.py`.
    -   **Validação de Dados**: Um pilar central do sistema. Utiliza schemas JSON (`haas/schemas/`) e validadores customizados (`haas/core/validators/` e `haas/validators/`) para garantir a integridade dos dados de entrada. O `INMETROValidator` (`haas/validators/inmetro/`) é um componente crítico reutilizado de um projeto anterior.
    -   **API**: Construída com FastAPI. Os endpoints são definidos em `haas/app/routers/`. A autenticação é baseada em JWT.

## 2. Fluxos de Trabalho do Desenvolvedor

### Configuração do Ambiente

O ambiente de desenvolvimento é baseado em Docker e Python.

1.  **Instalar Dependências**:
    ```bash
    pip install -r haas/requirements.txt
    ```
2.  **Configurar Variáveis de Ambiente**:
    - Copie `haas/.env.example` para `haas/.env` (se existir) e preencha as variáveis, especialmente as de conexão com o banco de dados.

### Executando a Aplicação

-   **Com Docker (Método Preferencial)**:
    - Use `docker-compose -f haas/docker-compose.yml up --build` para iniciar a aplicação e o banco de dados.
    - Existem arquivos de compose alternativos para diferentes configurações de portas (`docker-compose.alt-ports.yml`, `docker-compose.high-ports.yml`).

-   **Localmente (Sem Docker)**:
    - Execute `python haas/run.py` para iniciar o servidor Uvicorn.

### Testes

Os testes são escritos com **Pytest**.

-   **Executar todos os testes**:
    ```bash
    python haas/run_tests.py
    ```
    Ou diretamente com pytest no diretório `haas`:
    ```bash
    pytest
    ```
-   **Configuração de Teste**: `haas/pytest.ini` e `haas/tests/conftest.py`.

## 3. Padrões e Convenções do Projeto

-   **Reutilização de Código**: O projeto valoriza a reutilização. A `Fase 1` foi focada em integrar componentes de um projeto `Homologação` pré-existente, como os validadores e schemas.
-   **Validação por Schema**: A lógica de negócio depende fortemente da validação de dados de entrada contra os schemas JSON definidos em `haas/schemas/`. Ao adicionar um novo fluxo de dados, verifique se um schema correspondente precisa ser criado ou atualizado.
-   **Separação de Domínios**: A estrutura de diretórios em `haas/app` separa responsabilidades (ex: `auth`, `database`, `routers`, `services`). Siga este padrão ao adicionar novas funcionalidades.
-   **Infraestrutura como Código (IaC)**: A infraestrutura na AWS é definida usando CloudFormation (`haas/aws/cloudformation-haas-infrastructure.yml`). Os scripts de deploy estão em PowerShell (`.ps1`).

## 4. Integrações e Dependências Externas

-   **INMETRO**: O sistema se integra com dados do INMETRO para validar certificados de equipamentos. A lógica está encapsulada em `haas/validators/inmetro/`.
-   **Concessionárias de Energia**: Embora a interação direta ainda esteja no roadmap (`Fase 3 - Orchestration`), a base de dados (`haas/schemas/distribuidoras_gd.schema.json`) e a modelagem são projetadas para interagir com diferentes concessionárias.
-   **PostgreSQL com Extensões**: A dependência do PostGIS e pgvector é crítica. Qualquer interação com o banco de dados deve considerar as capacidades dessas extensões.
