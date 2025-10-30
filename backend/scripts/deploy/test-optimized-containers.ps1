# test-optimized-containers.ps1
# Testar containers otimizados

Write-Host "🧪 Testing Optimized Containers" -ForegroundColor Cyan
Write-Host ""

# Parar containers antigos se existirem
Write-Host "🛑 Parando containers antigos..." -ForegroundColor Yellow
docker stop mcp-server-test 2>$null
docker rm mcp-server-test 2>$null

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 Iniciando MCP Server Optimized" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

# Iniciar container otimizado
docker run -d `
      --name mcp-server-test `
      -p 8001:8000 `
      infrastructure-mcp-server:optimized

if ($LASTEXITCODE -eq 0) {
      Write-Host "✅ Container iniciado" -ForegroundColor Green
}
else {
      Write-Host "❌ Falha ao iniciar container" -ForegroundColor Red
      exit 1
}

# Aguardar startup
Write-Host ""
Write-Host "⏳ Aguardando 5 segundos para startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar health
Write-Host ""
Write-Host "🏥 Verificando health check..." -ForegroundColor Yellow

$maxAttempts = 10
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts -and -not $healthy) {
      $attempt++
    
      try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        
            if ($response.StatusCode -eq 200) {
                  $healthy = $true
                  Write-Host "  ├─ Tentativa $attempt/$maxAttempts: ✅ Healthy (200 OK)" -ForegroundColor Green
            }
      }
      catch {
            Write-Host "  ├─ Tentativa $attempt/$maxAttempts: ⏳ Aguardando..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
      }
}

if ($healthy) {
      Write-Host "  └─ ✅ Container está saudável!" -ForegroundColor Green
}
else {
      Write-Host "  └─ ❌ Container não respondeu após $maxAttempts tentativas" -ForegroundColor Red
    
      Write-Host ""
      Write-Host "📋 Logs do container:" -ForegroundColor Yellow
      docker logs mcp-server-test --tail 50
    
      exit 1
}

# Mostrar estatísticas
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 Estatísticas do Container" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

docker stats --no-stream mcp-server-test

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Teste concluído com sucesso!" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 Endpoints disponíveis:" -ForegroundColor Cyan
Write-Host "  • Health: http://localhost:8001/health" -ForegroundColor White
Write-Host ""

Write-Host "💡 Comandos úteis:" -ForegroundColor Magenta
Write-Host "  • Ver logs: docker logs -f mcp-server-test" -ForegroundColor Gray
Write-Host "  • Parar: docker stop mcp-server-test" -ForegroundColor Gray
Write-Host "  • Remover: docker rm mcp-server-test" -ForegroundColor Gray
