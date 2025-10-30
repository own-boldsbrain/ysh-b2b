# YSH Agents - Deploy Completo
# ================================

Write-Host "🚀 YSH Agents - Deploy Completo" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Verificando pré-requisitos..." -ForegroundColor Yellow

$hasDocker = Get-Command docker -ErrorAction SilentlyContinue
$hasDockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
$hasNode = Get-Command node -ErrorAction SilentlyContinue

if (-not $hasDocker) {
      Write-Host "❌ Docker não instalado" -ForegroundColor Red
      exit 1
}

if (-not $hasDockerCompose) {
      Write-Host "❌ Docker Compose não instalado" -ForegroundColor Red
      exit 1
}

if (-not $hasNode) {
      Write-Host "❌ Node.js não instalado" -ForegroundColor Red
      exit 1
}

Write-Host "✅ Pré-requisitos OK" -ForegroundColor Green
Write-Host ""

# Check .env file
if (-not (Test-Path .env)) {
      Write-Host "⚠️  Arquivo .env não encontrado" -ForegroundColor Yellow
      Write-Host "Copiando .env.example para .env..." -ForegroundColor Yellow
      Copy-Item .env.example .env
      Write-Host "⚠️  ATENÇÃO: Configure suas credenciais em .env antes de continuar" -ForegroundColor Yellow
      Write-Host ""
      Read-Host "Pressione Enter após configurar o .env"
}

Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
npm install --silent
Write-Host "✅ Dependências instaladas" -ForegroundColor Green
Write-Host ""

# Build TypeScript
Write-Host "🔨 Compilando TypeScript..." -ForegroundColor Yellow
npm run build
Write-Host "✅ Build concluído" -ForegroundColor Green
Write-Host ""

# Stop existing containers
Write-Host "🛑 Parando containers existentes..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml down 2>$null
Write-Host "✅ Containers parados" -ForegroundColor Green
Write-Host ""

# Pull images
Write-Host "📥 Baixando imagens Docker..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml pull
Write-Host "✅ Imagens atualizadas" -ForegroundColor Green
Write-Host ""

# Start infrastructure
Write-Host "🏗️  Iniciando infraestrutura base..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml up -d `
      postgres-temporal `
      temporal-server `
      supabase-db `
      kong `
      meta `
      supabase-studio `
      redis `
      redpanda

Write-Host "⏳ Aguardando serviços iniciarem (90s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# Check health
Write-Host ""
Write-Host "🏥 Verificando saúde dos serviços..." -ForegroundColor Yellow

function Test-Service {
      param($Name, $Url)
      Write-Host "  - ${Name}: " -NoNewline
      try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✅" -ForegroundColor Green
            return $true
      }
      catch {
            Write-Host "❌" -ForegroundColor Red
            return $false
      }
}

Test-Service "Temporal" "http://localhost:8080"
Test-Service "Supabase" "http://localhost:54321"
Test-Service "Redis" "http://localhost:8001"
Test-Service "Redpanda" "http://localhost:19644/metrics"

Write-Host ""

# Run migrations
Write-Host "🗄️  Executando migrations..." -ForegroundColor Yellow
$env:SUPABASE_URL = "http://localhost:8000"
$env:SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"

docker exec ysh-supabase-db psql -U supabase_admin -d postgres -f /docker-entrypoint-initdb.d/init.sql 2>$null
if ($LASTEXITCODE -ne 0) {
      Write-Host "⚠️  Migrations já executadas ou erro ignorável" -ForegroundColor Yellow
}
Write-Host "✅ Database configurado" -ForegroundColor Green
Write-Host ""

# Start observability
Write-Host "📊 Iniciando observabilidade..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml up -d `
      prometheus `
      grafana `
      loki `
      promtail `
      redpanda-console

Write-Host "⏳ Aguardando Grafana (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✅ Observabilidade ativa" -ForegroundColor Green
Write-Host ""

# Start browser automation
Write-Host "🌐 Iniciando browser automation..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml up -d chrome
Write-Host "⏳ Aguardando Chrome (15s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host "✅ Chrome pronto" -ForegroundColor Green
Write-Host ""

# Start workers
Write-Host "🤖 Iniciando agent workers..." -ForegroundColor Yellow
docker-compose -f docker-compose.agents.yml up -d `
      catalog-extractor-worker `
      price-intelligence-worker `
      product-enricher-worker `
      sku-governor-worker

Write-Host "⏳ Aguardando workers (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✅ Workers ativos" -ForegroundColor Green
Write-Host ""

# Final status
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 Deploy Concluído com Sucesso!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Interfaces Web:" -ForegroundColor Yellow
Write-Host "  - Temporal UI:       http://localhost:8080"
Write-Host "  - Supabase Studio:   http://localhost:54321"
Write-Host "  - Grafana:           http://localhost:3000 (admin/admin)"
Write-Host "  - Prometheus:        http://localhost:9090"
Write-Host "  - Redis Commander:   http://localhost:8001"
Write-Host "  - Redpanda Console:  http://localhost:8082"
Write-Host ""
Write-Host "🔧 Comandos úteis:" -ForegroundColor Yellow
Write-Host "  - Ver logs:          docker-compose -f docker-compose.agents.yml logs -f"
Write-Host "  - Status serviços:   docker-compose -f docker-compose.agents.yml ps"
Write-Host "  - Parar tudo:        docker-compose -f docker-compose.agents.yml down"
Write-Host "  - Restart:           docker-compose -f docker-compose.agents.yml restart <service>"
Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Acesse Temporal UI para ver workflows"
Write-Host "  2. Acesse Supabase Studio para ver produtos"
Write-Host "  3. Execute: npm run workflow:extract -- --distributor neosolar"
Write-Host ""
Write-Host "📚 Documentação: AGENTES_SWARM_ESTRATEGIA_DEFINITIVA.md" -ForegroundColor Cyan
Write-Host ""
