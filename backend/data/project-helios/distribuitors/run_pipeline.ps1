# =========================================
# YSH B2B - ANEEL Distribuidoras 360°
# Pipeline Completo de Extração e QA
# =========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔋 ANEEL DISTRIBUIDORAS 360°" -ForegroundColor Cyan
Write-Host "Pipeline Completo de Extração Territorial" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando ambiente..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python não encontrado" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Verificar dependências críticas
$packagesNeeded = @("playwright", "pandas", "google-generativeai", "openai")
$missingPackages = @()

foreach ($package in $packagesNeeded) {
    $check = python -c "import $($package -replace '-','_')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "⚠️  Dependências faltando: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "Execute primeiro: .\install_dependencies.ps1" -ForegroundColor Yellow
    $install = Read-Host "Instalar agora? (s/N)"
    if ($install -eq "s" -or $install -eq "S") {
        .\install_dependencies.ps1
    } else {
        exit 1
    }
}

Write-Host "✅ Todas as dependências instaladas" -ForegroundColor Green
Write-Host ""

# Menu de opções
Write-Host "📋 OPÇÕES DE EXECUÇÃO:" -ForegroundColor Cyan
Write-Host "  1. Extração completa (todas as distribuidoras)" -ForegroundColor White
Write-Host "  2. Extração limitada (primeiras 10)" -ForegroundColor White
Write-Host "  3. Apenas Quality Assurance (dados existentes)" -ForegroundColor White
Write-Host "  4. Pipeline completo (Extração + QA)" -ForegroundColor White
Write-Host "  5. Visualizar relatório existente" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Escolha uma opção (1-5)"

switch ($opcao) {
    "1" {
        Write-Host ""
        Write-Host "🚀 EXTRAÇÃO COMPLETA INICIADA" -ForegroundColor Green
        Write-Host "⚠️  Isso pode levar várias horas dependendo do número de distribuidoras" -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "Confirmar? (s/N)"
        if ($confirm -ne "s" -and $confirm -ne "S") {
            Write-Host "❌ Operação cancelada" -ForegroundColor Red
            exit 0
        }
        
        Write-Host ""
        python aneel_territorial_extractor.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Extração concluída com sucesso" -ForegroundColor Green
            Write-Host "📊 Executando Quality Assurance..." -ForegroundColor Yellow
            Write-Host ""
            python quality_assurance.py
        } else {
            Write-Host "❌ Erro na extração" -ForegroundColor Red
            exit 1
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "🚀 EXTRAÇÃO LIMITADA (10 primeiras)" -ForegroundColor Green
        Write-Host ""
        
        # Criar versão temporária do script com limite
        $scriptContent = Get-Content aneel_territorial_extractor.py -Raw
        $modifiedScript = $scriptContent -replace '(df_to_extract = df\[)', '$1.head(10)#'
        
        $tempScript = "aneel_territorial_extractor_limited.py"
        $modifiedScript | Out-File -FilePath $tempScript -Encoding UTF8
        
        python $tempScript
        Remove-Item $tempScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Extração concluída" -ForegroundColor Green
            Write-Host "📊 Executando Quality Assurance..." -ForegroundColor Yellow
            Write-Host ""
            python quality_assurance.py
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "📊 QUALITY ASSURANCE" -ForegroundColor Green
        Write-Host ""
        
        if (!(Test-Path "aneel_distribuidoras_360_territorial_enriched.csv")) {
            Write-Host "❌ Arquivo de dados não encontrado" -ForegroundColor Red
            Write-Host "Execute primeiro a opção 1 ou 2 para extrair os dados" -ForegroundColor Yellow
            exit 1
        }
        
        python quality_assurance.py
    }
    
    "4" {
        Write-Host ""
        Write-Host "🚀 PIPELINE COMPLETO" -ForegroundColor Green
        Write-Host ""
        
        $numDistribuidoras = Read-Host "Quantas distribuidoras processar? (Digite 'todas' ou um número)"
        
        if ($numDistribuidoras -eq "todas") {
            Write-Host "⚠️  Processando TODAS as distribuidoras" -ForegroundColor Yellow
            python aneel_territorial_extractor.py
        } else {
            try {
                $limit = [int]$numDistribuidoras
                Write-Host "⚠️  Processando primeiras $limit distribuidoras" -ForegroundColor Yellow
                
                # Criar versão temporária com limite customizado
                $scriptContent = Get-Content aneel_territorial_extractor.py -Raw
                $modifiedScript = $scriptContent -replace '(df_to_extract = df\[)', "`$1.head($limit)#"
                
                $tempScript = "aneel_territorial_extractor_custom.py"
                $modifiedScript | Out-File -FilePath $tempScript -Encoding UTF8
                
                python $tempScript
                Remove-Item $tempScript
            } catch {
                Write-Host "❌ Número inválido" -ForegroundColor Red
                exit 1
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Extração concluída" -ForegroundColor Green
            Write-Host "📊 Executando Quality Assurance..." -ForegroundColor Yellow
            Write-Host ""
            python quality_assurance.py
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "✅ PIPELINE COMPLETO CONCLUÍDO" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "📂 Arquivos gerados:" -ForegroundColor Cyan
                Write-Host "  - aneel_distribuidoras_360_territorial_enriched.csv" -ForegroundColor White
                Write-Host "  - aneel_distribuidoras_360_territorial_enriched.json" -ForegroundColor White
                Write-Host "  - aneel_distribuidoras_validations.csv" -ForegroundColor White
                Write-Host "  - quality_report.json" -ForegroundColor White
                Write-Host "  - QUALITY_REPORT.md" -ForegroundColor White
                Write-Host ""
                
                $viewReport = Read-Host "Visualizar relatório de qualidade? (s/N)"
                if ($viewReport -eq "s" -or $viewReport -eq "S") {
                    if (Test-Path "QUALITY_REPORT.md") {
                        Get-Content "QUALITY_REPORT.md" | Write-Host
                    }
                }
            }
        } else {
            Write-Host "❌ Erro no pipeline" -ForegroundColor Red
            exit 1
        }
    }
    
    "5" {
        Write-Host ""
        Write-Host "📄 VISUALIZAR RELATÓRIO" -ForegroundColor Green
        Write-Host ""
        
        if (Test-Path "QUALITY_REPORT.md") {
            Get-Content "QUALITY_REPORT.md" | Write-Host
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Cyan
            
            # Estatísticas rápidas do quality_report.json
            if (Test-Path "quality_report.json") {
                $report = Get-Content "quality_report.json" -Raw | ConvertFrom-Json
                
                Write-Host "📊 ESTATÍSTICAS RÁPIDAS:" -ForegroundColor Cyan
                Write-Host "  Total de registros: $($report.total_records)" -ForegroundColor White
                Write-Host "  Score médio: $([math]::Round($report.quality_metrics.score_medio, 1))/100" -ForegroundColor White
                Write-Host ""
                Write-Host "Distribuição por status:" -ForegroundColor Yellow
                
                foreach ($status in $report.status_distribution.PSObject.Properties) {
                    $pct = [math]::Round(($status.Value / $report.total_records) * 100, 1)
                    Write-Host "  - $($status.Name): $($status.Value) ($pct%)" -ForegroundColor White
                }
            }
        } else {
            Write-Host "❌ Relatório não encontrado" -ForegroundColor Red
            Write-Host "Execute primeiro a opção 3 ou 4" -ForegroundColor Yellow
        }
    }
    
    default {
        Write-Host "❌ Opção inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Processo finalizado" -ForegroundColor Green
Write-Host ""
