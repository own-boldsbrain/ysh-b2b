# cleanup-old-images.ps1
# Remove imagens Docker antigas (2+ anos) para liberar ~10GB

Write-Host "🧹 Docker Image Cleanup - Removendo imagens antigas" -ForegroundColor Cyan
Write-Host ""

# Lista de imagens para remover (baseado na auditoria Task 1)
$oldImages = @(
      "selenium/node-firefox:4.9.0-20230421",
      "selenium/node-edge:4.9.0-20230421",
      "selenium/node-chrome:4.9.0-20230421",
      "selenium/hub:4.9.0-20230421",
      "jupyter/scipy-notebook:lab-4.0.7",
      "neo4j:5.13-community"
)

$totalFreed = 0

foreach ($image in $oldImages) {
      Write-Host "Verificando: $image" -ForegroundColor Yellow
    
      # Verificar se imagem existe
      $exists = docker images -q $image 2>$null
    
      if ($exists) {
            # Obter tamanho antes de remover
            $sizeOutput = docker images $image --format "{{.Size}}"
            Write-Host "  ├─ Tamanho: $sizeOutput" -ForegroundColor Gray
        
            # Remover imagem
            try {
                  docker rmi $image -f 2>$null
                  Write-Host "  └─ ✅ Removida com sucesso" -ForegroundColor Green
                  $totalFreed++
            }
            catch {
                  Write-Host "  └─ ⚠️  Erro ao remover: $_" -ForegroundColor Red
            }
      }
      else {
            Write-Host "  └─ Não encontrada (já removida ou nunca instalada)" -ForegroundColor Gray
      }
      Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 Resumo do Cleanup:" -ForegroundColor Cyan
Write-Host "  • Imagens removidas: $totalFreed de $($oldImages.Count)" -ForegroundColor White
Write-Host ""

# Executar prune para remover dangling images
Write-Host "🗑️  Removendo imagens dangling..." -ForegroundColor Yellow
docker image prune -f

Write-Host ""
Write-Host "✅ Cleanup concluído!" -ForegroundColor Green
Write-Host ""

# Mostrar estatísticas atuais
Write-Host "📈 Uso atual de disco Docker:" -ForegroundColor Cyan
docker system df

Write-Host ""
Write-Host "💡 Dica: Execute 'docker system prune -a' para liberar ainda mais espaço" -ForegroundColor Magenta
