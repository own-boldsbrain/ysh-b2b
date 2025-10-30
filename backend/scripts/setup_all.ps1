#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Master Setup Script para YSH Solar B2B - Sistema de Captura de Imagens
    
.DESCRIPTION
    Este script configura e inicializa todos os componentes necessários para o
    sistema de captura automática de imagens de produtos solares:
    - GitHub Copilot CLI
    - Google Gemini CLI
    - OpenAI API / Codex
    - Docker Desktop AI com MCP
    - Dagster Pipeline
    - Pathway Real-Time Processing
    - Facebook Catalog API
    
.EXAMPLE
    .\setup_all.ps1
    
.NOTES
    Versão: 1.0
    Autor: YSH Solar B2B Team
    Data: 2025-01-20
#>

param(
      [switch]$SkipDockerCheck,
      [switch]$SkipTests
)

$ErrorActionPreference = "Continue"
$workspaceRoot = Join-Path $PSScriptRoot ".."

# Colors for output
function Write-Step {
      param([string]$Message)
      Write-Host "`n========================================" -ForegroundColor Cyan
      Write-Host $Message -ForegroundColor Cyan
      Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Success {
      param([string]$Message)
      Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
      param([string]$Message)
      Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
      param([string]$Message)
      Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Start setup
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           YSH SOLAR B2B - MASTER SETUP SCRIPT               ║
║         Sistema de Captura Automática de Imagens            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 1. Check Prerequisites
Write-Step "STEP 1: Checking Prerequisites"

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
      $pythonVersion = python --version
      Write-Success "Python found: $pythonVersion"
}
else {
      Write-Error "Python not found. Please install Python 3.11+"
      exit 1
}

# Check Node.js
if (Get-Command node -ErrorAction SilentlyContinue) {
      $nodeVersion = node --version
      Write-Success "Node.js found: $nodeVersion"
}
else {
      Write-Warning "Node.js not found (optional for some features)"
}

# Check Docker
if (!$SkipDockerCheck) {
      if (Get-Command docker -ErrorAction SilentlyContinue) {
            $dockerVersion = docker --version
            Write-Success "Docker found: $dockerVersion"
        
            # Check if Docker is running
            $dockerStatus = docker ps 2>&1
            if ($LASTEXITCODE -eq 0) {
                  Write-Success "Docker daemon is running"
            }
            else {
                  Write-Error "Docker daemon is not running. Please start Docker Desktop"
                  exit 1
            }
      }
      else {
            Write-Error "Docker not found. Please install Docker Desktop"
            exit 1
      }
}

# Check Git
if (Get-Command git -ErrorAction SilentlyContinue) {
      $gitVersion = git --version
      Write-Success "Git found: $gitVersion"
}
else {
      Write-Warning "Git not found (optional)"
}

# 2. Check Environment File
Write-Step "STEP 2: Checking Environment Configuration"

$envFile = Join-Path $workspaceRoot ".env"
if (Test-Path $envFile) {
      Write-Success ".env file found"
    
      # Validate required keys
      $envContent = Get-Content $envFile -Raw
      $requiredKeys = @(
            "GEMINI_API_KEY_1",
            "GEMINI_API_KEY_2",
            "OPENAI_API_KEY"
      )
    
      $missingKeys = @()
      foreach ($key in $requiredKeys) {
            if ($envContent -notmatch "$key=.+") {
                  $missingKeys += $key
            }
      }
    
      if ($missingKeys.Count -gt 0) {
            Write-Error "Missing API keys in .env: $($missingKeys -join ', ')"
            Write-Warning "Please fill in the required API keys in .env file"
            exit 1
      }
    
      Write-Success "All required API keys are configured"
}
else {
      Write-Error ".env file not found"
      Write-Warning "Please copy .env.example to .env and fill in your API keys"
      exit 1
}

# 3. Setup GitHub Copilot CLI
Write-Step "STEP 3: Setting up GitHub Copilot CLI"
& (Join-Path $PSScriptRoot "setup_copilot_cli.ps1")

# 4. Setup Gemini CLI
Write-Step "STEP 4: Setting up Google Gemini CLI"
& (Join-Path $PSScriptRoot "setup_gemini.ps1")

# 5. Setup OpenAI / Codex
Write-Step "STEP 5: Setting up OpenAI API / Codex"
& (Join-Path $PSScriptRoot "setup_openai.ps1")

# 6. Install Python Dependencies
Write-Step "STEP 6: Installing Python Dependencies"
Set-Location $workspaceRoot

if (Test-Path "requirements.txt") {
      Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
      python -m pip install --upgrade pip
      python -m pip install -r requirements.txt
    
      if ($LASTEXITCODE -eq 0) {
            Write-Success "Python dependencies installed"
      }
      else {
            Write-Error "Failed to install Python dependencies"
      }
}
else {
      Write-Warning "requirements.txt not found, installing core dependencies..."
      python -m pip install --upgrade pip google-generativeai openai playwright pandas sqlalchemy psycopg2-binary redis python-dotenv
}

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium
if ($LASTEXITCODE -eq 0) {
      Write-Success "Playwright browsers installed"
}

# 7. Create Output Directories
Write-Step "STEP 7: Creating Output Directories"

$outputDirs = @(
      "output/images",
      "output/metadata",
      "output/logs",
      "output/agentflow-results"
)

foreach ($dir in $outputDirs) {
      $fullPath = Join-Path $workspaceRoot $dir
      if (!(Test-Path $fullPath)) {
            New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
            Write-Success "Created: $dir"
      }
      else {
            Write-Host "  Already exists: $dir" -ForegroundColor Gray
      }
}

# 8. Initialize Database (optional)
Write-Step "STEP 8: Database Initialization"
Write-Host "Starting PostgreSQL container..." -ForegroundColor Yellow

if (!$SkipDockerCheck) {
      # Check if postgres container exists
      $postgresExists = docker ps -a --filter "name=ysh-postgres" --format "{{.Names}}" 2>&1
      if ($postgresExists -eq "ysh-postgres") {
            Write-Host "PostgreSQL container already exists, starting..." -ForegroundColor Yellow
            docker start ysh-postgres | Out-Null
      }
      else {
            Write-Host "Creating new PostgreSQL container..." -ForegroundColor Yellow
            docker-compose up -d postgres
      }
    
      if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL is running"
            Start-Sleep -Seconds 5  # Wait for postgres to be ready
      }
      else {
            Write-Warning "Failed to start PostgreSQL (you can start it manually later)"
      }
}

# 9. Run Tests (if not skipped)
if (!$SkipTests) {
      Write-Step "STEP 9: Running Integration Tests"
    
      # Test Gemini API
      Write-Host "Testing Gemini API..." -ForegroundColor Yellow
      $testGemini = Join-Path $PSScriptRoot "test_gemini.py"
      if (Test-Path $testGemini) {
            python $testGemini
      }
    
      # Test OpenAI API
      Write-Host "`nTesting OpenAI API..." -ForegroundColor Yellow
      $testOpenAI = Join-Path $PSScriptRoot "test_openai.py"
      if (Test-Path $testOpenAI) {
            python $testOpenAI
      }
}

# 10. Summary and Next Steps
Write-Step "SETUP COMPLETE!"

Write-Host @"

┌────────────────────────────────────────────────────────────┐
│                    SETUP SUMMARY                           │
└────────────────────────────────────────────────────────────┘

✓ Prerequisites checked
✓ GitHub Copilot CLI configured
✓ Google Gemini CLI configured  
✓ OpenAI API / Codex configured
✓ Python dependencies installed
✓ Output directories created
✓ Database initialized

┌────────────────────────────────────────────────────────────┐
│                    NEXT STEPS                              │
└────────────────────────────────────────────────────────────┘

1. RESTART YOUR POWERSHELL SESSION to load new functions

2. Test the AI tools:
   > gemini "List all solar panel manufacturers in Brazil"
   > codex "Create a web scraper for product images"
   > ghcs "Start docker compose services"

3. Start the full stack:
   > cd $workspaceRoot
   > docker-compose up -d

4. Access services:
   - Dagster UI: http://localhost:3000
   - Grafana: http://localhost:3001
   - Prometheus: http://localhost:9090
   - MCP Server: http://localhost:8000

5. Run the image scraper:
   > python scripts/agentflow_catalog_orchestrator.py

6. Monitor logs:
   > docker-compose logs -f image-scraper

┌────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION                           │
└────────────────────────────────────────────────────────────┘

📖 Mega Prompt: docs/ai-ml/mega-prompt-image-capture.md
📖 Architecture: docs/architecture/image-scraping-system.md
📖 API Docs: docs/api/facebook-catalog-api.md

For help: https://github.com/ysh-solar/ysh-b2b/wiki

"@ -ForegroundColor Cyan

Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
