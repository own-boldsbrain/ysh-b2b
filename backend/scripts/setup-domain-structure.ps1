# Script para criar estrutura completa de domínios DDD
# Fase 1 - Backend Restructuring Plan

$baseDir = "C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\src"

$domains = @(
      "catalog",
      "pricing", 
      "quotes",
      "approvals",
      "company",
      "orders",
      "financing",
      "energy-aneel",
      "solar-simulations",
      "integrations",
      "platform",
      "observability"
)

$layers = @("domain", "application", "infrastructure", "interfaces")

Write-Host "🏗️  Criando estrutura de domínios DDD..." -ForegroundColor Cyan

foreach ($domain in $domains) {
      Write-Host "  📦 Criando domínio: $domain" -ForegroundColor Yellow
    
      foreach ($layer in $layers) {
            $path = "$baseDir\domains\$domain\$layer"
            New-Item -ItemType Directory -Force -Path $path | Out-Null
        
            # Criar README.md em cada camada
            $readmePath = "$path\README.md"
            $readmeContent = @"
# $domain / $layer

**Domínio:** $domain  
**Camada:** $layer

## Responsabilidades

$(if ($layer -eq "domain") {
"- Entidades, Value Objects, Aggregates
- Domain Events
- Domain Services
- Repository Interfaces"
} elseif ($layer -eq "application") {
"- Use Cases / Application Services
- Command Handlers
- Query Handlers
- DTOs de entrada/saída"
} elseif ($layer -eq "infrastructure") {
"- Implementações de Repositories
- Adaptadores para APIs externas
- Persistência (DB, cache)
- Event Publishers/Subscribers"
} else {
"- Controllers (API routes)
- Validators
- Request/Response DTOs
- API Documentation"
})

## Status

⚠️ **Em construção** - Fase 1 da reestruturação

---
*Criado em: $(Get-Date -Format "dd/MM/yyyy HH:mm")*
"@
            Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
      }
}

# Criar shared
Write-Host "`n🔧 Criando diretório shared..." -ForegroundColor Cyan
$sharedDirs = @("errors", "auth", "validation", "events", "cache", "utils", "types")
foreach ($dir in $sharedDirs) {
      $path = "$baseDir\shared\$dir"
      New-Item -ItemType Directory -Force -Path $path | Out-Null
      Write-Host "  ✅ $dir" -ForegroundColor Green
}

# Criar index principal do shared
$sharedIndexPath = "$baseDir\shared\index.ts"
$sharedIndexContent = @"
/**
 * Shared utilities and common code across all domains
 * 
 * @module shared
 */

export * from "./errors"
export * from "./auth"
export * from "./validation"
export * from "./events"
export * from "./cache"
export * from "./utils"
export * from "./types"
"@
Set-Content -Path $sharedIndexPath -Value $sharedIndexContent -Encoding UTF8

Write-Host "`n✅ Estrutura de domínios criada com sucesso!" -ForegroundColor Green
Write-Host "`n📊 Resumo:" -ForegroundColor Cyan
Write-Host "  - Domínios: $($domains.Count)" -ForegroundColor White
Write-Host "  - Camadas por domínio: $($layers.Count)" -ForegroundColor White
Write-Host "  - Total de diretórios: $($domains.Count * $layers.Count + $sharedDirs.Count)" -ForegroundColor White
Write-Host "`n📁 Localização: $baseDir\domains\" -ForegroundColor Gray
