#!/usr/bin/env pwsh
# YSH Solar B2B - Infrastructure Bootstrap Script
# Inicia todos os serviços necessários para cobertura 360º

Write-Host "🚀 YSH Solar B2B - Iniciando Infraestrutura Unificada" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se Docker está rodando
Write-Host "✅ Verificando Docker..." -ForegroundColor Yellow
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop primeiro." -ForegroundColor Red
      exit 1
}

# 2. Parar containers conflitantes
Write-Host "🛑 Parando containers antigos..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml down 2>$null
docker-compose -f .deploy/docker-compose.agents.yml down 2>$null

# 3. Criar diretórios de configuração necessários
Write-Host "📁 Criando diretórios de configuração..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path config | Out-Null
New-Item -ItemType Directory -Force -Path config/grafana/provisioning/datasources | Out-Null
New-Item -ItemType Directory -Force -Path config/grafana/provisioning/dashboards | Out-Null
New-Item -ItemType Directory -Force -Path config/grafana/dashboards | Out-Null
New-Item -ItemType Directory -Force -Path temporal-dynamicconfig | Out-Null
New-Item -ItemType Directory -Force -Path init-scripts | Out-Null

# 4. Criar arquivo de configuração mínima do Kong se não existir
if (-not (Test-Path "config/kong.yml")) {
      Write-Host "📝 Criando config/kong.yml..." -ForegroundColor Yellow
      @"
_format_version: "2.1"
_transform: true

services:
  - name: supabase-db
    url: http://postgres-supabase:5432
    routes:
      - name: db-route
        paths:
          - /db
"@ | Out-File -FilePath config/kong.yml -Encoding UTF8
}

# 5. Criar configuração do Prometheus
if (-not (Test-Path "config/prometheus.yml")) {
      Write-Host "📝 Criando config/prometheus.yml..." -ForegroundColor Yellow
      @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'temporal'
    static_configs:
      - targets: ['temporal-server:7233']
  
  - job_name: 'redpanda'
    static_configs:
      - targets: ['redpanda:9644']
"@ | Out-File -FilePath config/prometheus.yml -Encoding UTF8
}

# 6. Criar configuração do Loki
if (-not (Test-Path "config/loki.yml")) {
      Write-Host "📝 Criando config/loki.yml..." -ForegroundColor Yellow
      @"
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks
"@ | Out-File -FilePath config/loki.yml -Encoding UTF8
}

# 7. Criar configuração do Promtail
if (-not (Test-Path "config/promtail.yml")) {
      Write-Host "📝 Criando config/promtail.yml..." -ForegroundColor Yellow
      @"
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log
"@ | Out-File -FilePath config/promtail.yml -Encoding UTF8
}

# 8. Criar configuração do Redpanda Console
if (-not (Test-Path "config/redpanda-console.yml")) {
      Write-Host "📝 Criando config/redpanda-console.yml..." -ForegroundColor Yellow
      @"
kafka:
  brokers:
    - redpanda:9092
  schemaRegistry:
    enabled: true
    urls:
      - http://redpanda:8081
"@ | Out-File -FilePath config/redpanda-console.yml -Encoding UTF8
}

# 9. Criar dynamic config do Temporal
if (-not (Test-Path "temporal-dynamicconfig/development-sql.yaml")) {
      Write-Host "📝 Criando temporal-dynamicconfig/development-sql.yaml..." -ForegroundColor Yellow
      @"
system.enableReadFromSecondaryDatabase:
  - value: false
    constraints: {}
"@ | Out-File -FilePath temporal-dynamicconfig/development-sql.yaml -Encoding UTF8
}

# 10. Criar script de inicialização do Supabase
if (-not (Test-Path "init-scripts/supabase-init.sql")) {
      Write-Host "📝 Criando init-scripts/supabase-init.sql..." -ForegroundColor Yellow
      @"
-- YSH Solar B2B - Database Initialization
-- Cria bancos de dados necessários para Huginn e Grafana

CREATE DATABASE huginn;
CREATE DATABASE grafana;

-- Extensions necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Schema para dados de produtos dos distribuidores
CREATE SCHEMA IF NOT EXISTS distributor_data;

-- Tabela de distribuidores
CREATE TABLE IF NOT EXISTS distributor_data.distributors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS distributor_data.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    distributor_id UUID NOT NULL REFERENCES distributor_data.distributors(id),
    external_id VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    manufacturer VARCHAR(100),
    image_url TEXT,
    product_url TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(distributor_id, external_id)
);

-- Tabela de histórico de preços
CREATE TABLE IF NOT EXISTS distributor_data.product_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES distributor_data.products(id),
    price_cents INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'BRL',
    in_stock BOOLEAN DEFAULT true,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de sincronizações
CREATE TABLE IF NOT EXISTS distributor_data.sync_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    distributor_id UUID NOT NULL REFERENCES distributor_data.distributors(id),
    status VARCHAR(50) NOT NULL,
    products_found INTEGER,
    products_created INTEGER,
    products_updated INTEGER,
    errors_count INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_products_distributor ON distributor_data.products(distributor_id);
CREATE INDEX idx_products_sku ON distributor_data.products(sku);
CREATE INDEX idx_products_category ON distributor_data.products(category);
CREATE INDEX idx_prices_product ON distributor_data.product_prices(product_id);
CREATE INDEX idx_prices_recorded_at ON distributor_data.product_prices(recorded_at);
CREATE INDEX idx_sync_runs_distributor ON distributor_data.sync_runs(distributor_id);

-- Inserir distribuidores iniciais
INSERT INTO distributor_data.distributors (name, slug, base_url) VALUES
    ('Fortlev Solar', 'fortlev', 'https://fortlevsolar.com.br'),
    ('Neosolar', 'neosolar', 'https://loja.neosolar.com.br'),
    ('Solfácil', 'solfacil', 'https://marketplace.solfacil.com.br'),
    ('Fotus Energia', 'fotus', 'https://fotusenergia.com.br'),
    ('Odex Distribuidora', 'odex', 'https://odexdistribuidora.com.br'),
    ('Edeltec Solar', 'edeltec', 'https://edeltecsolar.com.br'),
    ('Dynamis Solar', 'dynamis', 'https://dynamissolar.com.br')
ON CONFLICT (slug) DO NOTHING;

GRANT ALL PRIVILEGES ON SCHEMA distributor_data TO supabase_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA distributor_data TO supabase_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA distributor_data TO supabase_admin;
"@ | Out-File -FilePath init-scripts/supabase-init.sql -Encoding UTF8
}

# 11. Iniciar serviços essenciais primeiro (infra)
Write-Host ""
Write-Host "🐳 Iniciando camada de infraestrutura..." -ForegroundColor Cyan
docker-compose -f docker-compose.unified.yml up -d `
      postgres-temporal `
      postgres-supabase `
      redis `
      redpanda

Write-Host "⏳ Aguardando health checks (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 12. Iniciar serviços de orquestração
Write-Host ""
Write-Host "⚡ Iniciando Temporal Workflow Engine..." -ForegroundColor Cyan
docker-compose -f docker-compose.unified.yml up -d temporal-server

Write-Host "⏳ Aguardando Temporal inicializar (20s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 13. Iniciar serviços de suporte
Write-Host ""
Write-Host "🔧 Iniciando serviços de suporte..." -ForegroundColor Cyan
docker-compose -f docker-compose.unified.yml up -d `
      kong `
      meta `
      supabase-studio `
      redpanda-console `
      chrome `
      huginn `
      ollama

Write-Host "⏳ Aguardando serviços de suporte (15s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 14. Iniciar observabilidade
Write-Host ""
Write-Host "📊 Iniciando stack de observabilidade..." -ForegroundColor Cyan
docker-compose -f docker-compose.unified.yml up -d `
      prometheus `
      loki `
      promtail `
      grafana

Write-Host "⏳ Aguardando Grafana (10s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 15. Status final
Write-Host ""
Write-Host "📋 Status dos Serviços:" -ForegroundColor Cyan
Write-Host ""
docker-compose -f docker-compose.unified.yml ps

Write-Host ""
Write-Host "✅ Infraestrutura Iniciada com Sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs de Acesso:" -ForegroundColor Cyan
Write-Host "  • Temporal UI:        http://localhost:8080" -ForegroundColor White
Write-Host "  • Supabase Studio:    http://localhost:54321" -ForegroundColor White
Write-Host "  • Grafana:            http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  • Huginn:             http://localhost:3001" -ForegroundColor White
Write-Host "  • RedisInsight:       http://localhost:8001" -ForegroundColor White
Write-Host "  • Redpanda Console:   http://localhost:8082" -ForegroundColor White
Write-Host "  • Prometheus:         http://localhost:9090" -ForegroundColor White
Write-Host "  • Ollama:             http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "📦 Próximos Passos:" -ForegroundColor Yellow
Write-Host "  1. Baixar modelos Ollama: docker exec ysh-ollama ollama pull llama3" -ForegroundColor White
Write-Host "  2. Executar extração Fortlev: cd mcp-servers && npx tsx extract-fortlev-full.ts" -ForegroundColor White
Write-Host "  3. Iniciar workers: docker-compose -f docker-compose.unified.yml up -d" -ForegroundColor White
Write-Host ""
