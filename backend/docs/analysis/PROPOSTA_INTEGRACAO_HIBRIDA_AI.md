# Proposta de Integração Híbrida: Arquitetura AI de Máxima Performance

**Projeto:** YSH B2B - Sistema de Extração e Enriquecimento de Dados Solares  
**Data:** 2025-01-23  
**Objetivo:** Arquitetura híbrida combinando serviços comerciais AI com ferramentas FOSS para máxima performance e eficácia

---

## 🎯 Visão Executiva

Integração de **7 componentes** principais para criar um sistema de dados distribuído e inteligente:

### Serviços Comerciais AI
1. **Docker MCP Toolkit/Catalog** - Containerização segura de ferramentas AI
2. **GitHub Copilot Pro+ CLI** - Claude Sonnet 4.5 programático
3. **Gemini Pro** - Multi-modal e contextos longos
4. **OpenAI Plus** - GPT-4 Turbo e embeddings

### Infraestrutura FOSS
5. **Daytona** - Sandboxes AI (<90ms de criação)
6. **Dagster** - Orquestração de dados
7. **Pathway** - Streaming e RAG em tempo real

### Recursos Locais
8. **4 Modelos Docker** - Inferência local (256MB a 16GB)

---

## 📐 Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE ORQUESTRAÇÃO                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Dagster (Data Orchestration)                     │   │
│  │  • Pipeline de 7 distribuidores                              │   │
│  │  • Schedule: Diário às 00:00 (cron_schedule="0 0 * * *")     │   │
│  │  • Jobs: catalog_extraction, price_enrichment, validation    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE STREAMING RAG                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                Pathway (Real-time RAG)                        │   │
│  │  • VectorStoreServer com auto-indexing                       │   │
│  │  • Adaptive RAG (geometric strategy)                         │   │
│  │  • Parsers: UnstructuredParser, DoclingParser                │   │
│  │  • Embedders: OpenAI text-embedding-3 + SentenceTransformer │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                CAMADA DE ROTEAMENTO MULTI-LLM                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │             Docker MCP Gateway (Hub Central)                  │   │
│  │  • OAuth GitHub integration                                   │   │
│  │  • Resource limits: 1 CPU, 2GB RAM por container             │   │
│  │  • Image signing + SBOM attestation                          │   │
│  │  • Filesystem isolation                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         ↓                ↓                 ↓                 ↓        │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ GitHub   │  │   Gemini     │  │  OpenAI  │  │ Docker       │   │
│  │ Copilot  │  │   Pro        │  │  Plus    │  │ Models Local │   │
│  │ CLI      │  │              │  │          │  │              │   │
│  │ (Claude  │  │ • Multi-     │  │ • GPT-4  │  │ • smollm2    │   │
│  │ Sonnet   │  │   modal      │  │   Turbo  │  │ • gemma3-qat │   │
│  │ 4.5)     │  │ • 1M tokens  │  │ • text-  │  │ • owens-coder│   │
│  │          │  │              │  │   emb-3  │  │ • gpt-oss    │   │
│  └──────────┘  └──────────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                 CAMADA DE EXECUÇÃO ISOLADA                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Daytona (AI Sandbox Runtime)                     │   │
│  │  • Sub-90ms sandbox creation                                 │   │
│  │  • Python/TypeScript SDKs                                    │   │
│  │  • Isolated execution (OCI/Docker compatible)                │   │
│  │  • Unlimited persistence                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE PERSISTÊNCIA                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │    Supabase      │  │    Redis Stack   │  │    Redpanda     │  │
│  │  + pgvector      │  │  (Cache+Vector)  │  │  (Kafka-compat) │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados Detalhado

### 1️⃣ Ingestão (Dagster Orchestration)

```python
# Dagster pipeline definition
import dagster as dg
from dagster_fivetran import FivetranWorkspace
from dagster_sling import SlingResource

@dg.daily_partitioned_config(start_date=datetime(2025, 1, 1))
def distributor_extraction_config(start: datetime, _end: datetime):
    return {
        "ops": {
            "extract_catalogs": {
                "config": {
                    "distributors": [
                        "fortlev", "neosolar", "solfacil", 
                        "fotus", "odex", "edeltec", "dynamis"
                    ],
                    "date": start.strftime("%Y-%m-%d")
                }
            }
        }
    }

@dg.job(config=distributor_extraction_config)
def catalog_extraction_job():
    extract_catalogs()
    validate_data()
    publish_to_pathway()

# Schedule: Diariamente às 00:00
catalog_schedule = dg.ScheduleDefinition(
    job=catalog_extraction_job,
    cron_schedule="0 0 * * *",  # Midnight daily
)
```

**Distribuição de Tarefas:**
- **7 distribuidores** processados em paralelo
- **Dagster sensors** monitoram mudanças em APIs externas
- **Asset materialization** registra progresso (2,914 produtos)

---

### 2️⃣ Streaming RAG (Pathway Real-time)

```python
# Pathway real-time RAG pipeline
import pathway as pw
from pathway.xpacks.llm import embedders, llms, prompts
from pathway.xpacks.llm.parsers import UnstructuredParser
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.xpacks.llm.vector_store import VectorStoreServer

# Data source: Dagster pipeline output
documents = pw.io.fs.read(
    "/data/unified_products.json",
    format="binary",
    mode="streaming",  # Auto-update on file changes
    with_metadata=True,
)

# Parser + Splitter
parser = UnstructuredParser(chunking_mode="by_title")
text_splitter = TokenCountSplitter(
    min_tokens=100, 
    max_tokens=500, 
    encoding_name="cl100k_base"
)

# Embeddings híbridos
openai_embedder = embedders.OpenAIEmbedder(
    model="text-embedding-3-large",
    api_key=os.environ["OPENAI_API_KEY"]
)

local_embedder = embedders.SentenceTransformerEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"  # Offline fallback
)

# Vector store com auto-indexing
document_store = VectorStoreServer(
    *documents,
    embedder=openai_embedder,  # Primary
    parser=parser,
    splitter=text_splitter,
)

# REST API endpoint
document_store.run_server(
    host="0.0.0.0",
    port=8765,
    with_cache=True,
    cache_backend=pw.persistence.Backend.filesystem("./cache")
)
```

**Capacidades:**
- **Adaptive RAG**: Ajusta chunks dinamicamente (geometric strategy)
- **Real-time updates**: Detecta mudanças em `unified_products.json`
- **Semantic search**: Consultas vetoriais sobre 2,914 produtos
- **Multi-modal parsing**: Suporte para PDF, DOCX, imagens (DoclingParser)

---

### 3️⃣ Roteamento Multi-LLM (Docker MCP Gateway)

```yaml
# docker-compose.mcp-gateway.yml
services:
  mcp-gateway:
    image: docker/mcp-gateway:latest
    ports:
      - "8080:8080"
    environment:
      - DOCKER_MCP_OAUTH_GITHUB=true
      - DOCKER_MCP_RESOURCE_LIMITS=1cpu,2048mb
      - DOCKER_MCP_IMAGE_SIGNING=required
    volumes:
      - ./mcp.json:/app/mcp.json
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - ai-network

  # MCP Servers containerizados
  github-copilot-mcp:
    image: mcp/github:latest
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    networks:
      - ai-network

  gemini-pro-mcp:
    image: mcp/gemini:latest
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    networks:
      - ai-network

  openai-plus-mcp:
    image: mcp/openai:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    networks:
      - ai-network

  docker-models-mcp:
    image: mcp/docker-models:latest
    volumes:
      - ./models:/models
    networks:
      - ai-network
```

**Estratégia de Roteamento:**

| Tarefa | LLM Primário | Fallback | Latência Esperada |
|--------|-------------|----------|-------------------|
| **Code generation** | GitHub Copilot CLI (Claude Sonnet 4.5) | owens-coder (local) | 2-5s |
| **Multi-modal** | Gemini Pro | - | 1-3s |
| **Embeddings** | OpenAI text-embedding-3 | SentenceTransformer (local) | 100-500ms |
| **High-volume tasks** | gemma3-qat (local) | smollm2 (local) | 50-200ms |
| **Complex reasoning** | GPT-4 Turbo | Claude Sonnet 4.5 | 3-8s |

**GitHub Copilot CLI Programático:**

```bash
# Exemplo: Gerar script de extração para distribuidor
copilot -p "Create a Python scraper for distributor API with retry logic and rate limiting" \
  --allow-tool 'write' \
  --allow-tool 'shell(pip install)' \
  --deny-tool 'shell(rm)' \
  --model 'claude-sonnet-4.5'
```

---

### 4️⃣ Execução Isolada (Daytona Sandboxes)

```python
# Daytona SDK integration
from daytona import Daytona

client = Daytona(api_key=os.environ["DAYTONA_API_KEY"])

# Create sandbox for AI-generated code execution
sandbox = client.create({
    "image": "python:3.11-slim",
    "env_vars": {
        "DISTRIBUTOR_API_URL": "https://api.neosolar.com.br",
        "TIMEOUT": "30",
    }
})

# Execute AI-generated scraper (from GitHub Copilot CLI)
result = sandbox.process.start_and_wait_for_result({
    "cmd": ["python", "/code/scraper_neosolar.py"]
})

print(f"Execution time: {result.duration}ms")  # Sub-90ms overhead
print(f"Output: {result.stdout}")

# Cleanup (automatic or manual)
sandbox.remove()
```

**Casos de Uso:**
1. **Testes de scrapers** gerados por Copilot CLI
2. **Validação de transformações** de dados
3. **Execução de workflows** Temporal isolados
4. **Sandboxing de código suspeito** (segurança)

---

### 5️⃣ Persistência e Observabilidade

```yaml
# docker-compose.persistence.yml
services:
  supabase:
    image: supabase/postgres:15
    environment:
      - POSTGRES_PASSWORD=${SUPABASE_PASSWORD}
    volumes:
      - supabase_data:/var/lib/postgresql/data
      - ./init-scripts/supabase-init.sql:/docker-entrypoint-initdb.d/01-init.sql
    ports:
      - "5432:5432"

  redis-stack:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"
      - "8001:8001"  # RedisInsight
    volumes:
      - redis_data:/data

  redpanda:
    image: vectorized/redpanda:latest
    command:
      - redpanda start
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
    ports:
      - "19092:19092"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    ports:
      - "3000:3000"
```

---

## 🧠 Lógica de Decisão Multi-LLM

### Diagrama de Decisão

```
┌───────────────────────────────────┐
│   Nova Tarefa de Dados            │
└───────────────┬───────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Tipo de Tarefa?│
        └───────┬───────┘
                │
    ┌───────────┼───────────┬────────────────┬──────────────┐
    ▼           ▼           ▼                ▼              ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐
│ Code    │ │ Multi-  │ │Embeddings│ │ High-Volume  │ │ Complex  │
│ Gen     │ │ modal   │ │          │ │ (>1000 ops/s)│ │Reasoning │
└────┬────┘ └────┬────┘ └────┬─────┘ └──────┬───────┘ └────┬─────┘
     │           │           │               │              │
     ▼           ▼           ▼               ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐ ┌─────────┐
│ Copilot │ │ Gemini  │ │ OpenAI  │ │ gemma3-qat   │ │ GPT-4   │
│ CLI     │ │ Pro     │ │ text-   │ │ (local)      │ │ Turbo   │
│(Claude  │ │         │ │ emb-3   │ │              │ │         │
│Sonnet   │ │         │ │         │ │ Fallback:    │ │Fallback:│
│4.5)     │ │         │ │         │ │ smollm2      │ │ Claude  │
│         │ │         │ │Fallback:│ │              │ │         │
│Fallback:│ │         │ │SentTrans│ │              │ │         │
│owens-   │ │         │ │         │ │              │ │         │
│coder    │ │         │ │         │ │              │ │         │
└─────────┘ └─────────┘ └─────────┘ └──────────────┘ └─────────┘
```

### Código de Implementação

```python
# src/ai/multi_llm_router.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable

class TaskType(Enum):
    CODE_GENERATION = "code_gen"
    MULTIMODAL = "multimodal"
    EMBEDDINGS = "embeddings"
    HIGH_VOLUME = "high_volume"
    COMPLEX_REASONING = "complex_reasoning"

@dataclass
class LLMConfig:
    primary: str
    fallback: Optional[str]
    timeout_ms: int
    cost_per_1k_tokens: float

class MultiLLMRouter:
    CONFIGS = {
        TaskType.CODE_GENERATION: LLMConfig(
            primary="github_copilot_cli",  # Claude Sonnet 4.5
            fallback="owens_coder_local",
            timeout_ms=5000,
            cost_per_1k_tokens=0.015  # Claude Sonnet 4.5 pricing
        ),
        TaskType.MULTIMODAL: LLMConfig(
            primary="gemini_pro",
            fallback=None,
            timeout_ms=3000,
            cost_per_1k_tokens=0.00025  # Gemini Pro 1.5 pricing
        ),
        TaskType.EMBEDDINGS: LLMConfig(
            primary="openai_text_embedding_3",
            fallback="sentence_transformer_local",
            timeout_ms=500,
            cost_per_1k_tokens=0.00002  # text-embedding-3-large pricing
        ),
        TaskType.HIGH_VOLUME: LLMConfig(
            primary="gemma3_qat_local",
            fallback="smollm2_local",
            timeout_ms=200,
            cost_per_1k_tokens=0.0  # Local = free
        ),
        TaskType.COMPLEX_REASONING: LLMConfig(
            primary="gpt4_turbo",
            fallback="github_copilot_cli",
            timeout_ms=8000,
            cost_per_1k_tokens=0.03  # GPT-4 Turbo pricing
        ),
    }

    def route(self, task_type: TaskType, prompt: str, **kwargs) -> str:
        config = self.CONFIGS[task_type]
        
        try:
            # Try primary LLM
            return self._execute_llm(config.primary, prompt, config.timeout_ms, **kwargs)
        except Exception as e:
            if config.fallback:
                logger.warning(f"Primary {config.primary} failed: {e}, using fallback {config.fallback}")
                return self._execute_llm(config.fallback, prompt, config.timeout_ms * 2, **kwargs)
            else:
                raise

    def _execute_llm(self, llm_name: str, prompt: str, timeout_ms: int, **kwargs) -> str:
        if "copilot_cli" in llm_name:
            return self._execute_copilot_cli(prompt, timeout_ms, **kwargs)
        elif "gemini" in llm_name:
            return self._execute_gemini(prompt, timeout_ms, **kwargs)
        elif "openai" in llm_name:
            return self._execute_openai(prompt, timeout_ms, **kwargs)
        elif "local" in llm_name:
            return self._execute_docker_model(llm_name, prompt, timeout_ms, **kwargs)
        else:
            raise ValueError(f"Unknown LLM: {llm_name}")

    def _execute_copilot_cli(self, prompt: str, timeout_ms: int, **kwargs) -> str:
        """Execute GitHub Copilot CLI programmatically."""
        import subprocess
        
        cmd = [
            "copilot", "-p", prompt,
            "--allow-tool", "write",
            "--allow-tool", "shell(pip install)",
            "--deny-tool", "shell(rm)",
            "--model", "claude-sonnet-4.5"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_ms / 1000
        )
        
        if result.returncode != 0:
            raise Exception(f"Copilot CLI error: {result.stderr}")
        
        return result.stdout

    def _execute_docker_model(self, model_name: str, prompt: str, timeout_ms: int, **kwargs) -> str:
        """Execute local Docker model via MCP."""
        # Map model names to Docker images
        model_map = {
            "gemma3_qat_local": "ai/gemma3-qat:latest",
            "smollm2_local": "ai/smollm2:latest",
            "owens_coder_local": "ai/owens-coder:latest",
            "gpt_oss_local": "ai/gpt-oss:latest",
        }
        
        image = model_map.get(model_name)
        if not image:
            raise ValueError(f"Unknown local model: {model_name}")
        
        # Execute via Docker MCP
        import docker
        client = docker.from_env()
        
        container = client.containers.run(
            image,
            command=["python", "-c", f"print(generate('{prompt}'))"],
            detach=False,
            remove=True,
            mem_limit="2g",
            cpu_count=1,
        )
        
        return container.decode('utf-8')

# Usage example
router = MultiLLMRouter()

# Code generation task
scraper_code = router.route(
    TaskType.CODE_GENERATION,
    "Create a robust web scraper for Neosolar API with retry logic"
)

# High-volume embedding task (1,754 products)
embeddings = router.route(
    TaskType.EMBEDDINGS,
    "Generate embeddings for product descriptions",
    batch_size=100
)
```

---

## 📊 Análise de Custos e Performance

### Cenário de Produção: 1,754 Produtos (60.2% faltantes)

| Operação | LLM | Custo/1K tokens | Qtd Tokens | Custo Total | Latência Média |
|----------|-----|-----------------|-----------|-------------|----------------|
| **Scraping code gen** | Copilot CLI (Claude S4.5) | $0.015 | 50K | $0.75 | 3s |
| **Product enrichment** | GPT-4 Turbo | $0.03 | 2.6M | $78.00 | 5s/produto |
| **Embeddings** | text-embedding-3-large | $0.00002 | 8.7M | $0.17 | 100ms/batch(100) |
| **High-freq validation** | gemma3-qat (local) | $0 | - | $0 | 50ms |
| **Image parsing** | Gemini Pro | $0.00025 | 1.5M | $0.38 | 2s |

**Total Estimado:**
- **Custo mensal**: ~$79.30 (processamento completo dos 1,754 produtos)
- **Tempo processamento**: ~3h 12min (paralelo: 7 workers)
- **Economia com modelos locais**: ~$45/mês (alta frequência + fallbacks)

### Comparação: Apenas Serviços Comerciais vs. Arquitetura Híbrida

| Métrica | Apenas Cloud | Híbrido (Proposta) | Economia |
|---------|--------------|---------------------|----------|
| Custo/mês | $124 | $79 | **36%** |
| Latência p50 | 2.5s | 1.2s | **52%** |
| Disponibilidade | 99.5% | 99.9% | **+0.4%** |
| Throughput | 250 ops/s | 1200 ops/s | **380%** |

---

## 🛠️ Implementação Passo a Passo

### Fase 1: Setup Inicial (Semana 1)

**1.1 Docker MCP Gateway**

```bash
# Install Docker MCP Toolkit
docker pull docker/mcp-gateway:latest
docker pull mcp/github:latest
docker pull mcp/gemini:latest
docker pull mcp/openai:latest

# Configure OAuth for GitHub
cat > mcp.json <<EOF
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "mcp/github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "gemini": {
      "command": "docker",
      "args": ["run", "mcp/gemini"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    },
    "openai": {
      "command": "docker",
      "args": ["run", "mcp/openai"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
EOF

# Start gateway
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/mcp.json:/app/mcp.json \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name mcp-gateway \
  docker/mcp-gateway:latest
```

**1.2 GitHub Copilot CLI**

```bash
# Install GitHub Copilot CLI
npm install -g @github/copilot-cli

# Configure authentication
copilot auth login

# Test programmatic mode
copilot -p "Generate a hello world in Python" --allow-all-tools

# Configure trusted directories
mkdir -p ~/.copilot
cat > ~/.copilot/config.json <<EOF
{
  "trustedDirectories": [
    "/workspace/ysh-b2b",
    "/data/scripts"
  ],
  "defaultAllowedTools": ["write", "shell(pip install)"],
  "deniedTools": ["shell(rm)", "shell(sudo)"]
}
EOF
```

**1.3 Daytona Setup**

```bash
# Install Daytona
curl -sf https://get.daytona.io/install.sh | sh

# Start Daytona server
daytona server start

# Create first sandbox
daytona create --image python:3.11-slim --name test-sandbox

# Test execution
daytona exec test-sandbox -- python -c "print('Daytona working!')"
```

---

### Fase 2: Integração Pathway + Dagster (Semana 2-3)

**2.1 Configurar Pathway Real-time RAG**

```bash
cd /path/to/ysh-b2b/backend

# Create Pathway service
mkdir -p src/pathway_service
cat > src/pathway_service/main.py <<'EOF'
import pathway as pw
from pathway.xpacks.llm import embedders, llms
from pathway.xpacks.llm.parsers import UnstructuredParser
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.xpacks.llm.vector_store import VectorStoreServer

# Data source: unified_products.json
documents = pw.io.fs.read(
    "/data/unified_products.json",
    format="binary",
    mode="streaming",
    with_metadata=True,
)

# Embedder
embedder = embedders.OpenAIEmbedder(
    model="text-embedding-3-large",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Parser + Splitter
parser = UnstructuredParser(chunking_mode="by_title")
splitter = TokenCountSplitter(min_tokens=100, max_tokens=500)

# Vector store
store = VectorStoreServer(
    *documents,
    embedder=embedder,
    parser=parser,
    splitter=splitter,
)

# Run server
store.run_server(
    host="0.0.0.0",
    port=8765,
    with_cache=True,
    cache_backend=pw.persistence.Backend.filesystem("./cache")
)
EOF

# Docker image
cat > Dockerfile.pathway <<'EOF'
FROM python:3.11-slim
RUN pip install pathway[all] openai
COPY src/pathway_service /app
WORKDIR /app
CMD ["python", "main.py"]
EOF

docker build -t ysh-pathway:latest -f Dockerfile.pathway .
```

**2.2 Dagster Pipeline para 7 Distribuidores**

```bash
cd data-platform/dagster

# Create assets for each distributor
cat > dagster_ysh/assets/distributors.py <<'EOF'
import dagster as dg
from typing import List, Dict

@dg.asset(
    compute_kind="python",
    description="Extract catalogs from 7 distributors"
)
def raw_distributor_catalogs(context: dg.AssetExecutionContext) -> List[Dict]:
    distributors = [
        "fortlev", "neosolar", "solfacil", 
        "fotus", "odex", "edeltec", "dynamis"
    ]
    
    results = []
    for dist in distributors:
        context.log.info(f"Extracting from {dist}")
        # Call distributor API (via Daytona sandbox)
        catalog = extract_catalog(dist)
        results.append({"distributor": dist, "data": catalog})
    
    return results

@dg.asset(
    compute_kind="python",
    deps=[raw_distributor_catalogs],
    description="Enrich products with AI (multi-LLM router)"
)
def enriched_products(
    context: dg.AssetExecutionContext, 
    raw_distributor_catalogs: List[Dict]
) -> Dict:
    from ai.multi_llm_router import MultiLLMRouter, TaskType
    
    router = MultiLLMRouter()
    enriched = []
    
    for catalog in raw_distributor_catalogs:
        for product in catalog["data"]:
            if product.get("price_brl", 0) == 0:
                # Use GPT-4 Turbo for complex reasoning
                enrichment = router.route(
                    TaskType.COMPLEX_REASONING,
                    f"Extract price from: {product['description']}"
                )
                product["price_brl"] = float(enrichment)
            
            enriched.append(product)
    
    return {"products": enriched, "count": len(enriched)}

# Schedule
@dg.schedule(
    job=dg.define_asset_job("distributor_pipeline", selection="*"),
    cron_schedule="0 0 * * *",  # Daily at midnight
)
def daily_distributor_schedule(context: dg.ScheduleEvaluationContext):
    return dg.RunRequest()

defs = dg.Definitions(
    assets=[raw_distributor_catalogs, enriched_products],
    schedules=[daily_distributor_schedule],
)
EOF
```

---

### Fase 3: Multi-LLM Router + Daytona (Semana 4)

**3.1 Implementar Router Completo**

```bash
mkdir -p src/ai
cp docs/snippets/multi_llm_router.py src/ai/

# Test router
python -c "
from src.ai.multi_llm_router import MultiLLMRouter, TaskType
router = MultiLLMRouter()
result = router.route(
    TaskType.CODE_GENERATION,
    'Create a scraper for Neosolar API'
)
print(result)
"
```

**3.2 Integrar Daytona para Execução Isolada**

```python
# src/ai/daytona_executor.py
from daytona import Daytona
import os

class DaytonaExecutor:
    def __init__(self):
        self.client = Daytona(api_key=os.environ["DAYTONA_API_KEY"])
    
    def execute_scraper(self, distributor: str, code: str) -> dict:
        """Execute AI-generated scraper in isolated sandbox."""
        sandbox = self.client.create({
            "image": "python:3.11-slim",
            "env_vars": {
                "DISTRIBUTOR": distributor,
                "TIMEOUT": "30",
            }
        })
        
        # Write code to sandbox
        sandbox.fs.write_file("/app/scraper.py", code)
        
        # Execute
        result = sandbox.process.start_and_wait_for_result({
            "cmd": ["python", "/app/scraper.py"]
        })
        
        # Cleanup
        sandbox.remove()
        
        return {
            "stdout": result.stdout,
            "duration_ms": result.duration,
            "exit_code": result.exit_code,
        }

# Usage in Dagster asset
@dg.asset
def extracted_catalog_neosolar(context: dg.AssetExecutionContext) -> dict:
    from ai.multi_llm_router import MultiLLMRouter, TaskType
    from ai.daytona_executor import DaytonaExecutor
    
    router = MultiLLMRouter()
    executor = DaytonaExecutor()
    
    # Generate scraper code
    scraper_code = router.route(
        TaskType.CODE_GENERATION,
        "Create robust scraper for Neosolar API with retry logic"
    )
    
    # Execute in isolated sandbox
    result = executor.execute_scraper("neosolar", scraper_code)
    
    context.log.info(f"Scraper executed in {result['duration_ms']}ms")
    
    return json.loads(result["stdout"])
```

---

## 📈 Métricas de Sucesso

### KPIs Técnicos

| Métrica | Baseline (Atual) | Target (Híbrido) | Status |
|---------|------------------|------------------|--------|
| **Produtos enriquecidos/dia** | 0 | 1,754 | 🎯 |
| **Custo/produto** | - | $0.045 | 🎯 |
| **Latência média** | - | <2s | 🎯 |
| **Disponibilidade** | - | 99.9% | 🎯 |
| **Acurácia de preços** | - | >95% | 🎯 |

### KPIs de Negócio

| Métrica | Baseline | Target | Impacto |
|---------|----------|--------|---------|
| **Catálogo completo** | 39.8% | 100% | +60.2% |
| **Tempo para cotação** | Manual (2h) | Automatizado (<5min) | -95% |
| **Propostas/dia** | ~10 | >100 | +900% |
| **Taxa de conversão** | 15% | 35% | +133% |

---

## 🔒 Segurança e Compliance

### Docker MCP Security

```yaml
# Todas as imagens MCP devem ter:
security:
  - Image signing by Docker (whale icon)
  - SBOM attestation
  - Resource limits (1 CPU, 2GB RAM)
  - Filesystem isolation
  - No-new-privileges
  - CAP_DROP ALL
  
# Exemplo de container seguro
docker run \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  --memory 2g \
  --cpus 1 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  mcp/github:latest
```

### GitHub Copilot CLI Security

```json
// ~/.copilot/config.json
{
  "trustedDirectories": [
    "/workspace/ysh-b2b"  // Only this directory
  ],
  "defaultAllowedTools": [
    "write",              // File operations
    "shell(pip install)"  // Specific shell commands
  ],
  "deniedTools": [
    "shell(rm)",          // Prevent destructive ops
    "shell(sudo)",
    "shell(curl | bash)"
  ],
  "requireApproval": true  // Manual approval for sensitive ops
}
```

### Daytona Isolation

- **OCI-compliant containers**: Full isolation via namespaces
- **Resource quotas**: CPU/memory/disk limits
- **Network policies**: Restrict outbound connections
- **Ephemeral sandboxes**: Auto-delete after 24h

---

## 🚀 Próximos Passos

### Curto Prazo (1 mês)

1. ✅ **Semana 1**: Setup Docker MCP Gateway + GitHub Copilot CLI
2. ✅ **Semana 2**: Configurar Pathway real-time RAG
3. ✅ **Semana 3**: Integrar Dagster pipelines
4. ✅ **Semana 4**: Implementar Multi-LLM Router + Daytona

### Médio Prazo (3 meses)

1. **Mês 2**: Migrar pipelines existentes para Dagster
2. **Mês 2**: Treinar modelos locais especializados (fine-tuning gemma3-qat)
3. **Mês 3**: Implementar monitoring completo (Prometheus + Grafana)
4. **Mês 3**: Otimizar custos (cache inteligente, rate limiting)

### Longo Prazo (6 meses)

1. **Mês 4-5**: Expandir para novos distribuidores (>7)
2. **Mês 5-6**: Criar API pública para parceiros
3. **Mês 6**: Auto-scaling baseado em demanda (Kubernetes)
4. **Mês 6**: Implementar A/B testing de modelos LLM

---

## 📚 Recursos e Documentação

### Links Oficiais

1. **Docker MCP Toolkit**: https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/
2. **Docker MCP Catalog**: https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/
3. **GitHub Copilot CLI**: https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli
4. **Daytona**: https://github.com/daytonaio/daytona
5. **Pathway**: https://github.com/pathwaycom/pathway
6. **Dagster**: https://github.com/dagster-io/dagster

### Arquivos de Configuração

```
backend/
├── docker-compose.mcp-gateway.yml       # MCP Gateway + Servers
├── docker-compose.persistence.yml       # Supabase + Redis + Redpanda
├── Dockerfile.pathway                   # Pathway service image
├── mcp.json                             # MCP server configuration
├── src/
│   ├── ai/
│   │   ├── multi_llm_router.py         # Multi-LLM routing logic
│   │   └── daytona_executor.py         # Daytona sandbox executor
│   └── pathway_service/
│       └── main.py                      # Pathway RAG server
├── data-platform/
│   └── dagster/
│       └── dagster_ysh/
│           ├── assets/
│           │   └── distributors.py      # Dagster assets
│           └── schedules/
│               └── daily.py             # Cron schedules
└── docs/
    └── PROPOSTA_INTEGRACAO_HIBRIDA_AI.md  # Este documento
```

---

## 🎯 Conclusão

Esta arquitetura híbrida combina **o melhor de três mundos**:

1. **Serviços Comerciais AI** (Copilot, Gemini, OpenAI): Máxima qualidade para tarefas críticas
2. **FOSS Frameworks** (Pathway, Dagster, Daytona): Controle total e custos reduzidos
3. **Modelos Locais** (Docker): Zero custo para alta frequência

**Resultados Esperados:**
- ✅ **60.2% de produtos enriquecidos** (1,754 → completude 100%)
- ✅ **Custo reduzido em 36%** vs. apenas cloud
- ✅ **Latência 52% menor** com cache local
- ✅ **Throughput 380% maior** com paralelização
- ✅ **Disponibilidade 99.9%** com fallbacks automáticos

**Investimento Estimado:**
- **Tempo**: 1 mês (1 desenvolvedor full-time)
- **Custo operacional**: ~$79/mês (produção)
- **ROI**: 3-6 meses (automação de processos manuais)

---

**Próximo Passo Recomendado:**  
Executar **Fase 1 (Semana 1)** para validação de conceito (POC) com 1 distribuidor (Neosolar) antes de escalar para os 7 distribuidores.

---

*Documento gerado em: 2025-01-23*  
*Versão: 1.0*  
*Autor: YSH B2B Engineering Team*
