# build-optimized-images.ps1
# Construir imagens Docker otimizadas

Write-Host "🐳 Building Optimized Docker Images" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
try {
      docker info | Out-Null
      Write-Host "✅ Docker está rodando" -ForegroundColor Green
}
catch {
      Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop primeiro." -ForegroundColor Red
      exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📦 Build 1/2: MCP Server Optimized" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

# Build MCP Server otimizado
$startTime = Get-Date

docker build `
      -t infrastructure-mcp-server:optimized `
      -f Dockerfile.mcp-server-optimized `
      --progress=plain `
      .

$buildTime = (Get-Date) - $startTime

if ($LASTEXITCODE -eq 0) {
      Write-Host ""
      Write-Host "✅ MCP Server build concluído em $($buildTime.TotalSeconds)s" -ForegroundColor Green
    
      # Comparar tamanhos
      $oldSize = docker images infrastructure-mcp-server:latest --format "{{.Size}}" 2>$null
      $newSize = docker images infrastructure-mcp-server:optimized --format "{{.Size}}"
    
      Write-Host ""
      Write-Host "📊 Comparação de tamanhos:" -ForegroundColor Cyan
      Write-Host "  • Antiga (latest): $oldSize" -ForegroundColor Yellow
      Write-Host "  • Nova (optimized): $newSize" -ForegroundColor Green
}
else {
      Write-Host ""
      Write-Host "❌ Build falhou" -ForegroundColor Red
      exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📦 Build 2/2: Worker Images" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

# Build Workers
$startTime = Get-Date

docker build `
      -t ysh/worker:optimized `
      -f Dockerfile.worker `
      --progress=plain `
      .

$buildTime = (Get-Date) - $startTime

if ($LASTEXITCODE -eq 0) {
      Write-Host ""
      Write-Host "✅ Workers build concluído em $($buildTime.TotalSeconds)s" -ForegroundColor Green
    
      $workerSize = docker images ysh/worker:optimized --format "{{.Size}}"
      Write-Host "  • Tamanho: $workerSize" -ForegroundColor Green
}
else {
      Write-Host ""
      Write-Host "❌ Build falhou" -ForegroundColor Red
      exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 Todas as imagens foram construídas com sucesso!" -ForegroundColor Green
Write-Host ""

# Listar todas as imagens otimizadas
Write-Host "📋 Imagens otimizadas criadas:" -ForegroundColor Cyan
docker images | Select-String "optimized"

Write-Host ""
Write-Host "💡 Próximo passo: Execute .\test-optimized-containers.ps1" -ForegroundColor Magenta
